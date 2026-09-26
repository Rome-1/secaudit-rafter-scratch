# Fix for Context Timeout Errors Returning Wrong GRPC Status Codes

## Problem Summary
Flipt was returning incorrect GRPC status codes (`Internal` and `Unauthenticated`) when context timeout/cancellation errors occurred, instead of the appropriate `DeadlineExceeded` and `Canceled` codes. This affected metrics and made it difficult to distinguish between actual internal errors and client-side timeouts.

## Root Causes Identified
1. **ErrorUnaryInterceptor**: Did not handle `context.Canceled` or `context.DeadlineExceeded` errors, causing them to fall through to `codes.Internal`
2. **Auth middleware**: Masked context errors by returning `codes.Unauthenticated` for any error during token validation, including timeouts
3. **Deprecated interceptor chain**: Using deprecated `grpc_middleware.WithUnaryServerChain` instead of the modern `grpc.ChainUnaryInterceptor`

## Changes Made

### 1. Enhanced ErrorUnaryInterceptor (`/app/internal/server/middleware/grpc/middleware.go`)
- **Added import**: `"errors"` package for proper error chain unwrapping
- **Added context error handling**: 
  - `context.Canceled` → `codes.Canceled`
  - `context.DeadlineExceeded` → `codes.DeadlineExceeded`
- **Positioned correctly**: Context error checks happen after existing status error checks but before custom error type checks
- **Used `errors.Is()`**: Properly handles wrapped context errors (e.g., `fmt.Errorf("db error: %w", context.Canceled)`)

### 2. Enhanced Auth Middleware (`/app/internal/server/auth/middleware.go`)
- **Added import**: `"errors"` package
- **Added context error preservation**: Before returning `errUnauthenticated`, check if the error is context-related:
  - `context.Canceled` → `codes.Canceled` 
  - `context.DeadlineExceeded` → `codes.DeadlineExceeded`
- **Maintained existing behavior**: Non-context errors still return `codes.Unauthenticated`

### 3. Updated GRPC Server Setup (`/app/internal/cmd/grpc.go`)
- **Replaced deprecated middleware**: `grpc_middleware.WithUnaryServerChain(interceptors...)` → `grpc.ChainUnaryInterceptor(interceptors...)`
- **Removed unused import**: `grpc_middleware "github.com/grpc-ecosystem/go-grpc-middleware"`

## Expected Behavior Changes

| Scenario | Before | After |
|----------|---------|--------|
| Client cancels request mid-flight | `codes.Internal` | `codes.Canceled` ✅ |
| Request exceeds client timeout | `codes.Internal` | `codes.DeadlineExceeded` ✅ |  
| Auth service times out | `codes.Unauthenticated` | `codes.DeadlineExceeded` ✅ |
| Database timeout during auth | `codes.Unauthenticated` | `codes.DeadlineExceeded` ✅ |
| Wrapped context errors | `codes.Internal` | `codes.Canceled`/`codes.DeadlineExceeded` ✅ |
| Actual auth failures | `codes.Unauthenticated` | `codes.Unauthenticated` (unchanged) |
| Other errors | Various codes | Various codes (unchanged) |

## Error Chain Handling
The implementation uses `errors.Is()` which properly traverses error chains to detect wrapped context errors. This handles cases where context errors are wrapped by other operations (e.g., database drivers, network libraries).

## Performance Impact
- **Minimal overhead**: Context error checks are O(1) and only occur on error paths
- **No impact on success paths**: Happy path performance is unaffected
- **Efficient error traversal**: `errors.Is()` efficiently walks error chains

## Backward Compatibility
- **Preserved existing error handling**: All existing error type mappings remain unchanged
- **No breaking changes**: API and behavior for non-context errors is identical
- **Graceful degradation**: If context errors somehow aren't detected, they fall through to existing error handling

## Testing
- ✅ Build successful with no compilation errors
- ✅ All existing tests pass
- ✅ Proper error precedence verified
- ✅ Both middleware and auth interceptors handle context errors
- ✅ Modern GRPC interceptor chain in use

## Benefits for Monitoring and Operations
1. **Better metrics**: Context timeouts no longer pollute internal error metrics
2. **Clearer debugging**: Proper GRPC codes make it easier to diagnose timeout vs server issues
3. **Client-friendly**: Clients receive appropriate status codes for retry logic
4. **Load testing accuracy**: Timeout errors during load testing are properly categorized

This fix ensures that Flipt returns the correct GRPC status codes for context-related errors, improving observability and client experience during high-load scenarios or when network conditions cause timeouts.