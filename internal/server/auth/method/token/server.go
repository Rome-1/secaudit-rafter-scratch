package token

import (
        "context"
        "fmt"

        "go.flipt.io/flipt/internal/server/audit"
        serverauth "go.flipt.io/flipt/internal/server/auth"
        storageauth "go.flipt.io/flipt/internal/storage/auth"
        "go.flipt.io/flipt/rpc/flipt/auth"
        "go.uber.org/zap"
        "google.golang.org/grpc"
)

const (
        storageMetadataNameKey        = "io.flipt.auth.token.name"
        storageMetadataDescriptionKey = "io.flipt.auth.token.description"
)

// Server is an implementation of auth.AuthenticationMethodTokenServiceServer
//
// It is used to create static tokens within the backing AuthenticationStore.
type Server struct {
        logger *zap.Logger
        store  storageauth.Store

        tokenCreatedEnabled bool

        auth.UnimplementedAuthenticationMethodTokenServiceServer
}

type Option func(*Server)

// WithTokenCreatedEnabled sets the option for enabling token:created audit logging for the token server.
func WithTokenCreatedEnabled(enabled bool) Option {
        return func(s *Server) {
                s.tokenCreatedEnabled = enabled
        }
}

// NewServer constructs and configures a new *Server.
func NewServer(logger *zap.Logger, store storageauth.Store, opts ...Option) *Server {
        s := &Server{
                logger: logger,
                store:  store,
        }

        for _, opt := range opts {
                opt(s)
        }

        return s
}

// RegisterGRPC registers the server as an Server on the provided grpc server.
func (s *Server) RegisterGRPC(server *grpc.Server) {
        auth.RegisterAuthenticationMethodTokenServiceServer(server, s)
}

// CreateToken adapts and delegates the token request to the backing AuthenticationStore.
//
// Implicitly, the Authentication created will be of type auth.Method_TOKEN.
// Name and Description are both stored in Authentication.Metadata.
// Given the token is created successfully, the generate clientToken string is returned.
// Along with the created Authentication, which includes it's identifier and associated timestamps.
func (s *Server) CreateToken(ctx context.Context, req *auth.CreateTokenRequest) (*auth.CreateTokenResponse, error) {
        clientToken, authentication, err := s.store.CreateAuthentication(ctx, &storageauth.CreateAuthenticationRequest{
                Method:    auth.Method_METHOD_TOKEN,
                ExpiresAt: req.ExpiresAt,
                Metadata: map[string]string{
                        storageMetadataNameKey:        req.GetName(),
                        storageMetadataDescriptionKey: req.GetDescription(),
                },
        })
        if err != nil {
                return nil, fmt.Errorf("attempting to create token: %w", err)
        }

        if s.tokenCreatedEnabled {
                actor := serverauth.ActorFromContext(ctx)
                event := audit.NewEvent(audit.TokenType, audit.Create, actor, authentication.Metadata)
                event.AddToSpan(ctx)
        }

        return &auth.CreateTokenResponse{
                ClientToken:    clientToken,
                Authentication: authentication,
        }, nil
}
