# Authentication Bypass Vulnerability Fix

## Summary
Fixed a critical authentication bypass vulnerability in the Subsonic API middleware where invalid authentication attempts could bypass proper validation.

## The Vulnerability
The `authenticate` middleware in `/app/server/subsonic/middlewares.go` had the following issues:

1. **Delayed Error Handling**: When user lookup failed (user not found or database error), the code logged the error but continued execution instead of returning immediately.

2. **Nil Pointer Dereference Risk**: The code called `validateCredentials(usr, ...)` even when `usr` was `nil` (user not found), which could cause:
   - Nil pointer dereference if credentials were provided (accessing `usr.Password` or `usr.UserName`)
   - Masking of the original "user not found" error with "invalid credentials" error

3. **Inconsistent Error Response**: The centralized error checking at the end meant errors were not consistently reported with the appropriate Subsonic error code (40).

## The Fix
Modified the `authenticate` function to:

1. **Immediate Error Return for Reverse Proxy Auth**: 
   - Lines 96-104: When user lookup fails in reverse proxy mode, immediately send error response with code 40 and return

2. **Immediate Error Return for Subsonic Auth**:
   - Lines 118-126: When user lookup fails in subsonic mode, immediately send error response with code 40 and return
   - Lines 129-133: When credential validation fails, immediately send error response with code 40 and return

3. **Removed Centralized Error Check**: 
   - Removed the redundant `if err != nil` check that was after both auth paths, since errors are now handled immediately

## Security Benefits

1. **No Nil Pointer Dereference**: `validateCredentials` is only called when `usr` is guaranteed to be non-nil
2. **Consistent Error Responses**: All authentication failures immediately return with code 40
3. **Proper Error Propagation**: Errors are caught and reported at the point they occur
4. **No Information Leakage**: Authentication failures don't reveal whether the username exists or not (all return the same error code 40)

## Testing
All existing tests pass, including:
- `/app/server/subsonic/middlewares_test.go` - Tests for authentication middleware
- All subsonic API tests
- All server tests

The fix ensures:
- Valid credentials still allow access
- Invalid username returns code 40
- Invalid password returns code 40 
- Missing credentials return code 40
- No crashes or nil pointer dereferences occur
