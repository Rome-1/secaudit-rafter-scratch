package auth

import (
        "context"
        "fmt"
        "net/http"
        "strings"
        "time"

        "go.flipt.io/flipt/internal/containers"
        authrpc "go.flipt.io/flipt/rpc/flipt/auth"
        "go.uber.org/zap"
        "google.golang.org/grpc"
        "google.golang.org/grpc/codes"
        "google.golang.org/grpc/metadata"
        "google.golang.org/grpc/status"
)

const (
        authenticationHeaderKey = "authorization"
        cookieHeaderKey         = "grpcgateway-cookie"
        fliptClientTokenKey     = "flipt_client_token"
)

var errUnauthenticated = status.Error(codes.Unauthenticated, "request was not authenticated")

// InterceptorOptions contains configuration for the UnaryInterceptor
type InterceptorOptions struct {
        skippedServers []any
}

// WithServerSkipsAuthentication configures the authentication interceptor to skip
// authentication when the provided server instance matches the intercepted call's server instance
func WithServerSkipsAuthentication(server any) containers.Option[InterceptorOptions] {
        return func(opts *InterceptorOptions) {
                opts.skippedServers = append(opts.skippedServers, server)
        }
}

type authenticationContextKey struct{}

// Authenticator is the minimum subset of an authentication provider
// required by the middleware to perform lookups for Authentication instances
// using a obtained clientToken.
type Authenticator interface {
        GetAuthenticationByClientToken(ctx context.Context, clientToken string) (*authrpc.Authentication, error)
}

// GetAuthenticationFrom is a utility for extracting an Authentication stored
// on a context.Context instance
func GetAuthenticationFrom(ctx context.Context) *authrpc.Authentication {
        auth := ctx.Value(authenticationContextKey{})
        if auth == nil {
                return nil
        }

        return auth.(*authrpc.Authentication)
}

// clientTokenFromAuthorization extracts the client token from an authorization header value.
// It verifies that the string starts with "Bearer " and returns the token substring.
// Returns errUnauthenticated if the format is invalid.
func clientTokenFromAuthorization(auth string) (string, error) {
        const bearerPrefix = "Bearer "
        if !strings.HasPrefix(auth, bearerPrefix) {
                return "", errUnauthenticated
        }
        return strings.TrimPrefix(auth, bearerPrefix), nil
}

// cookieFromMetadata constructs an http.Request with headers populated from grpcgateway-cookie
// to ensure correct parsing of multiple cookies. Returns only the cookie matching the given key.
func cookieFromMetadata(md metadata.MD, key string) (*http.Cookie, error) {
        cookies := md.Get(cookieHeaderKey)
        if len(cookies) == 0 {
                return nil, fmt.Errorf("no cookies found in metadata")
        }

        // Create a dummy request to parse cookies properly
        req := &http.Request{Header: http.Header{}}
        for _, cookieValue := range cookies {
                req.Header.Add("Cookie", cookieValue)
        }

        // Find the specific cookie
        cookie, err := req.Cookie(key)
        if err != nil {
                return nil, fmt.Errorf("cookie %q not found: %w", key, err)
        }

        return cookie, nil
}

// clientTokenFromMetadata first attempts to extract the token from the authorization header.
// If no valid Bearer token is found, it falls back to parsing the cookie.
func clientTokenFromMetadata(md metadata.MD) (string, error) {
        // First try to get token from authorization header
        authHeaders := md.Get(authenticationHeaderKey)
        if len(authHeaders) > 0 {
                return clientTokenFromAuthorization(authHeaders[0])
        }

        // Fall back to cookie
        cookie, err := cookieFromMetadata(md, fliptClientTokenKey)
        if err != nil {
                return "", fmt.Errorf("failed to extract token from cookie: %w", err)
        }

        if cookie.Value == "" {
                return "", fmt.Errorf("cookie %q has empty value", fliptClientTokenKey)
        }

        return cookie.Value, nil
}

// UnaryInterceptor is a grpc.UnaryServerInterceptor which extracts a clientToken found
// within the authorization field on the incoming requests metadata or from cookies.
// The authorization header value is expected to be in the form "Bearer <clientToken>".
// If no authorization header is present, it will attempt to extract the token from cookies.
func UnaryInterceptor(logger *zap.Logger, authenticator Authenticator, opts ...containers.Option[InterceptorOptions]) grpc.UnaryServerInterceptor {
        var options InterceptorOptions
        containers.ApplyAll(&options, opts...)

        return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
                // Check if current server should skip authentication
                for _, skippedServer := range options.skippedServers {
                        if info.Server == skippedServer {
                                logger.Debug("skipping authentication for server", zap.String("method", info.FullMethod))
                                return handler(ctx, req)
                        }
                }

                md, ok := metadata.FromIncomingContext(ctx)
                if !ok {
                        logger.Error("unauthenticated", zap.String("reason", "metadata not found on context"))
                        return ctx, errUnauthenticated
                }

                clientToken, err := clientTokenFromMetadata(md)
                if err != nil {
                        logger.Error("unauthenticated", zap.String("reason", "failed to extract client token"), zap.Error(err))
                        return ctx, errUnauthenticated
                }

                auth, err := authenticator.GetAuthenticationByClientToken(ctx, clientToken)
                if err != nil {
                        logger.Error("unauthenticated",
                                zap.String("reason", "error retrieving authentication for client token"),
                                zap.Error(err))
                        return ctx, errUnauthenticated
                }

                if auth.ExpiresAt != nil && auth.ExpiresAt.AsTime().Before(time.Now()) {
                        logger.Error("unauthenticated",
                                zap.String("reason", "authorization expired"),
                                zap.String("authentication_id", auth.Id),
                        )
                        return ctx, errUnauthenticated
                }

                return handler(context.WithValue(ctx, authenticationContextKey{}, auth), req)
        }
}
