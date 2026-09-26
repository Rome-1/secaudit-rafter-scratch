# Implementation Summary: Reject requests earlier if the CSRF cookie token has the wrong format

## Changes Made

### 1. Modified `_get_token()` method
- **Change**: Removed the try/except block that caught `InvalidTokenFormat` and generated a new token
- **Reason**: Allow `InvalidTokenFormat` to bubble up so it can be handled differently in `process_request()` and `process_view()`
- **Added**: Check if `request.META['CSRF_COOKIE']` already exists (set by `process_request()` or `rotate_token()`) and return it instead of reading from cookies again

### 2. Modified `process_request()` method
- **Change**: Added try/except to catch `InvalidTokenFormat` from `_get_token()`
- **Behavior**: 
  - When caught, marks the request with `csrf_cookie_invalid_format` attribute containing the reason
  - Generates a new token and sets `csrf_cookie_needs_reset = True`
  - Sets the new token in `request.META['CSRF_COOKIE']`
- **Reason**: For GET/HEAD requests, we want to generate a new token. For POST requests, we want to mark the issue so `process_view()` can reject with a specific message.

### 3. Modified `process_view()` method
- **Change**: Added check for `csrf_cookie_invalid_format` attribute and try/except for `InvalidTokenFormat`
- **Behavior**:
  - First checks if `request.csrf_cookie_invalid_format` exists (set by `process_request()`)
  - If it exists, rejects immediately with message: "CSRF cookie {reason}."
  - Also catches `InvalidTokenFormat` from `_get_token()` (for edge cases) and rejects with the same format
- **Reason**: Reject POST requests early with specific error messages about the cookie format

## Benefits

1. **Early Rejection**: POST requests with invalid CSRF cookie format are rejected immediately in `process_view()` without unnecessary token generation or comparison
2. **Specific Error Messages**: Error messages distinguish between:
   - "CSRF cookie has invalid characters."
   - "CSRF cookie has incorrect length."
   - "CSRF token has invalid characters." (for non-cookie token)
   - "CSRF token has incorrect length." (for non-cookie token)
3. **Reduced Unnecessary Work**: Avoids calling `_get_new_csrf_token()` and `_compare_masked_tokens()` for requests that will be rejected anyway
4. **Better Troubleshooting**: More specific error messages make it easier to diagnose CSRF issues
5. **Backward Compatibility**: 32-character tokens (unmasked secrets) still work correctly

## Test Results

- All 102 existing CSRF tests pass
- New functionality verified with comprehensive tests covering:
  - Invalid characters in cookie (64-char with dashes)
  - Incorrect length in cookie
  - Invalid characters in non-cookie token
  - Incorrect length in non-cookie token
  - GET requests with invalid cookies (generate new token)
  - Session-based CSRF (still works correctly)
  - Backward compatibility with 32-char tokens

## Code Flow

### For GET/HEAD requests with invalid cookie:
1. `process_request()` calls `_get_token()`
2. `_get_token()` raises `InvalidTokenFormat`
3. `process_request()` catches it, generates new token, sets `csrf_cookie_needs_reset = True`
4. Response middleware sets new cookie

### For POST requests with invalid cookie:
1. `process_request()` calls `_get_token()`
2. `_get_token()` raises `InvalidTokenFormat`
3. `process_request()` catches it, marks `csrf_cookie_invalid_format`, generates new token
4. `process_view()` checks `csrf_cookie_invalid_format` and rejects with specific message
5. Request is rejected early, avoiding unnecessary work

### For POST requests with valid cookie but invalid non-cookie token:
1. `process_request()` calls `_get_token()`, succeeds
2. `process_view()` validates non-cookie token
3. `_sanitize_token()` raises `InvalidTokenFormat` for non-cookie token
4. `process_view()` rejects with message: "CSRF token {reason}."
