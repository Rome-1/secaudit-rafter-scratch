package auth

import (
        "context"
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
        cookieMetadataKey       = "grpcgateway-cookie"
        clientTokenCookieName   = "flipt_client_token"
)

var errUnauthenticated = status.Error(codes.Unauthenticated, "request was not authenticated")

type authenticationContextKey struct{}

// Authenticator is the minimum subset of an authentication provider
// required by the middleware to perform lookups for Authentication instances
// using a obtained clientToken.
type Authenticator interface {
        GetAuthenticationByClientToken(ctx context.Context, clientToken string) (*authrpc.Authentication, error)
}

// InterceptorOptions contains configuration options for the UnaryInterceptor
type InterceptorOptions struct {
        skippedServers []any
}

// WithServerSkipsAuthentication returns an option that configures the interceptor
// to skip authentication when the provided server instance matches the intercepted
// call's server instance
func WithServerSkipsAuthentication(server any) containers.Option[InterceptorOptions] {
        return func(opts *InterceptorOptions) {
                opts.skippedServers = append(opts.skippedServers, server)
        }
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

// clientTokenFromAuthorization extracts the client token from the authorization header.
// It must verify that the string starts with "Bearer ". If so, it returns the token substring;
// otherwise, it returns errUnauthenticated.
func clientTokenFromAuthorization(auth string) (string, error) {
        if !strings.HasPrefix(auth, "Bearer ") {
                return "", errUnauthenticated
        }
        return strings.TrimPrefix(auth, "Bearer "), nil
}

// cookieFromMetadata extracts a cookie value from metadata by constructing an http.Request
// with headers populated from grpcgateway-cookie metadata.
func cookieFromMetadata(md metadata.MD, key string) (string, error) {
        cookieHeaders := md.Get(cookieMetadataKey)
        if len(cookieHeaders) == 0 {
                return "", errUnauthenticated
        }

        // Construct an http.Request to properly parse cookies
        req := &http.Request{
                Header: http.Header{},
        }

        // Add all cookie headers
        for _, cookieHeader := range cookieHeaders {
                req.Header.Add("Cookie", cookieHeader)
        }

        // Parse and find the specific cookie
        cookie, err := req.Cookie(key)
        if err != nil {
                return "", errUnauthenticated
        }

        return cookie.Value, nil
}

// clientTokenFromMetadata attempts to extract the client token from metadata.
// It first tries the authorization header with Bearer format, then falls back
// to parsing cookies for the flipt_client_token.
func clientTokenFromMetadata(md metadata.MD) (string, error) {
        // First, try to get token from authorization header
        authHeaders := md.Get(authenticationHeaderKey)
        if len(authHeaders) > 0 {
                token, err := clientTokenFromAuthorization(authHeaders[0])
                if err == nil {
                        return token, nil
                }
                // If authorization header is present but malformed, return error
                // Don't fall back to cookie in this case
                return "", err
        }

        // If no authorization header, try to get token from cookie
        token, err := cookieFromMetadata(md, clientTokenCookieName)
        if err != nil {
                return "", errUnauthenticated
        }

        return token, nil
}

// UnaryInterceptor is a grpc.UnaryServerInterceptor which extracts a clientToken found
// within the authorization field on the incoming requests metadata or from cookies.
// The authorization field value is expected to be in the form "Bearer <clientToken>".
// If not present, it falls back to extracting from the flipt_client_token cookie.
func UnaryInterceptor(logger *zap.Logger, authenticator Authenticator, opts ...containers.Option[InterceptorOptions]) grpc.UnaryServerInterceptor {
        var options InterceptorOptions
        containers.ApplyAll(&options, opts...)

        return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
                // Check if the current server should skip authentication
                for _, skippedServer := range options.skippedServers {
                        if info.Server == skippedServer {
                                logger.Debug("skipping authentication for server",
                                        zap.String("method", info.FullMethod),
                                )
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
                        logger.Error("unauthenticated", zap.String("reason", "no valid authorization or cookie found"))
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
