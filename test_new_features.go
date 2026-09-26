package main

import (
"context"
"fmt"
"time"

"go.flipt.io/flipt/internal/server/auth"
"go.flipt.io/flipt/internal/storage/auth/memory"
authrpc "go.flipt.io/flipt/rpc/flipt/auth"
authreq "go.flipt.io/flipt/internal/storage/auth"
"go.uber.org/zap/zaptest"
"google.golang.org/grpc"
"google.golang.org/grpc/metadata"
"google.golang.org/protobuf/types/known/timestamppb"
)

func main() {
fmt.Println("Testing new authentication features...")

// Setup authenticator
authenticator := memory.NewStore()
logger := zaptest.NewLogger(nil)

// Create a valid auth token
clientToken, storedAuth, err := authenticator.CreateAuthentication(
context.TODO(),
&authreq.CreateAuthenticationRequest{Method: authrpc.Method_METHOD_TOKEN},
)
if err != nil {
fmt.Printf("Failed to create authentication: %v\n", err)
return
}

fmt.Printf("Created client token: %s\n", clientToken[:10]+"...")

// Test 1: Cookie-based authentication
fmt.Println("\n=== Test 1: Cookie-based Authentication ===")
md1 := metadata.MD{
"grpcgateway-cookie": []string{fmt.Sprintf("flipt_client_token=%s; other_cookie=value", clientToken)},
}

ctx1 := metadata.NewIncomingContext(context.Background(), md1)

var retrievedCtx1 context.Context
handler1 := func(ctx context.Context, req interface{}) (interface{}, error) {
retrievedCtx1 = ctx
return nil, nil
}

interceptor1 := auth.UnaryInterceptor(logger, authenticator)
_, err1 := interceptor1(ctx1, nil, &grpc.UnaryServerInfo{}, handler1)

if err1 != nil {
fmt.Printf("Cookie auth failed: %v\n", err1)
} else {
retrievedAuth := auth.GetAuthenticationFrom(retrievedCtx1)
if retrievedAuth != nil && retrievedAuth.Id == storedAuth.Id {
fmt.Println("✅ Cookie authentication successful!")
} else {
fmt.Println("❌ Cookie authentication failed - wrong auth object")
}
}

// Test 2: Header takes precedence over cookie
fmt.Println("\n=== Test 2: Header Precedence ===")

// Create another token for the cookie
cookieToken, _, err := authenticator.CreateAuthentication(
context.TODO(),
&authreq.CreateAuthenticationRequest{Method: authrpc.Method_METHOD_TOKEN},
)
if err != nil {
fmt.Printf("Failed to create cookie authentication: %v\n", err)
return
}

md2 := metadata.MD{
"authorization": []string{"Bearer " + clientToken},
"grpcgateway-cookie": []string{fmt.Sprintf("flipt_client_token=%s", cookieToken)},
}

ctx2 := metadata.NewIncomingContext(context.Background(), md2)

var retrievedCtx2 context.Context
handler2 := func(ctx context.Context, req interface{}) (interface{}, error) {
retrievedCtx2 = ctx
return nil, nil
}

_, err2 := interceptor1(ctx2, nil, &grpc.UnaryServerInfo{}, handler2)

if err2 != nil {
fmt.Printf("Header precedence test failed: %v\n", err2)
} else {
retrievedAuth := auth.GetAuthenticationFrom(retrievedCtx2)
if retrievedAuth != nil && retrievedAuth.Id == storedAuth.Id {
fmt.Println("✅ Header takes precedence over cookie!")
} else {
fmt.Println("❌ Header precedence failed - got cookie auth instead")
}
}

// Test 3: Server skipping
fmt.Println("\n=== Test 3: Server Skipping ===")

type TestServer struct{}
skipServer := &TestServer{}

interceptor3 := auth.UnaryInterceptor(logger, authenticator, auth.WithServerSkipsAuthentication(skipServer))

// No metadata at all
ctx3 := context.Background()

var retrievedCtx3 context.Context
handler3 := func(ctx context.Context, req interface{}) (interface{}, error) {
retrievedCtx3 = ctx
return nil, nil
}

info3 := &grpc.UnaryServerInfo{Server: skipServer, FullMethod: "/test.Service/TestMethod"}
_, err3 := interceptor3(ctx3, nil, info3, handler3)

if err3 != nil {
fmt.Printf("Server skipping failed: %v\n", err3)
} else {
fmt.Println("✅ Server skipping successful!")
}

// Test 4: Expired token
fmt.Println("\n=== Test 4: Expired Token ===")

expiredToken, _, err := authenticator.CreateAuthentication(
context.TODO(),
&authreq.CreateAuthenticationRequest{
Method:    authrpc.Method_METHOD_TOKEN,
ExpiresAt: timestamppb.New(time.Now().UTC().Add(-time.Hour)),
},
)
if err != nil {
fmt.Printf("Failed to create expired authentication: %v\n", err)
return
}

md4 := metadata.MD{
"authorization": []string{"Bearer " + expiredToken},
}

ctx4 := metadata.NewIncomingContext(context.Background(), md4)

_, err4 := interceptor1(ctx4, nil, &grpc.UnaryServerInfo{}, handler1)

if err4 != nil {
fmt.Println("✅ Expired token correctly rejected!")
} else {
fmt.Println("❌ Expired token was accepted")
}

fmt.Println("\n=== All tests completed ===")
}