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
        authenticationHeaderKey     = "authorization"
        grpcGatewayCookieHeaderKey  = "grpcgateway-cookie"
        fliptClientTokenCookieName  = "flipt_client_token"
)

var errUnauthenticated = status.Error(codes.Unauthenticated, "request was not authenticated")

type authenticationContextKey struct{}

// InterceptorOptions are configuration options for the UnaryInterceptor.
// It supports configuring which servers should bypass authentication.
type InterceptorOptions struct {
        skippedServers []any
}

// WithServerSkipsAuthentication configures the interceptor to skip authentication
// when the provided server matches the intercepted call's server instance.
func WithServerSkipsAuthentication(server any) containers.Option[InterceptorOptions] {
        return func(o *InterceptorOptions) {
                o.skippedServers = append(o.skippedServers, server)
        }
}

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

// clientTokenFromAuthorization validates and extracts a token from an Authorization header value.
// It only accepts the exact format "Bearer <token>" with a capital B and a single space.
// Any other format is rejected with errUnauthenticated.
func clientTokenFromAuthorization(auth string) (string, error) {
        if !strings.HasPrefix(auth, "Bearer ") {
            return "", errUnauthenticated
        }
        token := strings.TrimPrefix(auth, "Bearer ")
        // reject multiple spaces or empty tokens
        if token == "" || strings.HasPrefix(token, " ") {
            return "", errUnauthenticated
        }
        return token, nil
}

// cookieFromMetadata constructs an http.Request with headers populated from
// grpcgateway-cookie metadata to ensure correct parsing of multiple cookies.
// It returns only the cookie matching the given key.
func cookieFromMetadata(md metadata.MD, key string) (*http.Cookie, error) {
        cookies := md.Get(grpcGatewayCookieHeaderKey)
        if len(cookies) == 0 {
                return nil, http.ErrNoCookie
        }

        req := &http.Request{Header: http.Header{}}
        for _, c := range cookies {
                // Add each cookie header value - http.Request will parse them collectively
                req.Header.Add("Cookie", c)
        }

        ck, err := req.Cookie(key)
        if err != nil {
                return nil, err
        }
        return ck, nil
}

// clientTokenFromMetadata first attempts to extract the client token from the
// Authorization header. If no valid Bearer token is found, it falls back to
// parsing the flipt_client_token cookie from grpcgateway-cookie metadata.
func clientTokenFromMetadata(md metadata.MD) (string, error) {
        // Prefer Authorization header if present
        if vals := md.Get(authenticationHeaderKey); len(vals) > 0 && vals[0] != "" {
                if token, err := clientTokenFromAuthorization(vals[0]); err == nil {
                        return token, nil
                }
                // fall through to cookie parsing if header invalid
        }

        ck, err := cookieFromMetadata(md, fliptClientTokenCookieName)
        if err != nil || ck == nil || ck.Value == "" {
                return "", errUnauthenticated
        }

        return ck.Value, nil
}

// UnaryInterceptor is a grpc.UnaryServerInterceptor which extracts a clientToken found
// within the authorization field on the incoming requests metadata.
// The fields value is expected to be in the form "Bearer <clientToken>".
func UnaryInterceptor(logger *zap.Logger, authenticator Authenticator, opts ...containers.Option[InterceptorOptions]) grpc.UnaryServerInterceptor {
        var options InterceptorOptions
        containers.ApplyAll(&options, opts...)

        return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
                // Check if this server should skip authentication
                if info != nil {
                        for _, s := range options.skippedServers {
                                if info.Server == s {
                                        logger.Debug("skipping authentication for server")
                                        return handler(ctx, req)
                                }
                        }
                }

                md, ok := metadata.FromIncomingContext(ctx)
                if !ok {
                        logger.Error("unauthenticated", zap.String("reason", "metadata not found on context"))
                        return ctx, errUnauthenticated
                }

                clientToken, err := clientTokenFromMetadata(md)
                if err != nil {
                        // Log a clear failure reason
                        if authVals := md.Get(authenticationHeaderKey); len(authVals) == 0 || authVals[0] == "" {
                                logger.Error("unauthenticated", zap.String("reason", "no authorization provided and cookie missing"))
                        } else {
                                logger.Error("unauthenticated", zap.String("reason", "authorization malformed or cookie missing"))
                        }
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
