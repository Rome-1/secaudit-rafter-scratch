# File Upload Directory Validation Fix

## Problem
The admin file upload endpoint (`/api/admin/upload/file`) was accepting file uploads to any specified folder path without verifying if the destination directory actually exists on the filesystem. This could lead to unexpected behavior where the system would automatically create directories that shouldn't exist.

## Solution
Added directory existence validation in the `uploadsController.uploadFile` function in `/app/src/controllers/admin/uploads.js`.

### Changes Made
In the `uploadFile` function (line 190-220), added validation before calling `file.saveFileToLocal`:

```javascript
// Validate that the target directory exists
const targetDir = path.join(nconf.get('upload_path'), params.folder || '');
if (!targetDir.startsWith(nconf.get('upload_path'))) {
    file.delete(uploadedFile.path);
    return next(new Error('[[error:invalid-path]]'));
}
const dirExists = await file.exists(targetDir);
if (!dirExists) {
    file.delete(uploadedFile.path);
    return next(new Error('[[error:invalid-path]]'));
}
```

### Validation Flow
1. **Path Construction**: Constructs the full target directory path using `path.join()`
2. **Path Traversal Check**: Ensures the target directory is within the upload path (prevents `../../` attacks)
3. **Existence Check**: Validates that the target directory exists using `file.exists()`
4. **Error Response**: Returns `[[error:invalid-path]]` if validation fails
5. **Cleanup**: Deletes the temporary uploaded file before returning error

### Key Features
- **Security**: Prevents path traversal attacks by checking if path starts with upload_path
- **Validation**: Rejects uploads to non-existent directories
- **Consistency**: Uses the same error message format as other path validation in the codebase
- **Cleanup**: Properly deletes temporary files on validation failure
- **Edge Cases**: Handles null/undefined/empty folder parameters gracefully

### Test Coverage
The implementation correctly handles:
- ✓ Uploads to existing directories (system, files, category)
- ✓ Uploads to root upload directory (empty string, null, undefined)
- ✓ Rejection of uploads to non-existent directories
- ✓ Rejection of path traversal attempts (../../, etc.)
- ✓ Consistent error messaging

### Compatibility
- No breaking changes to existing functionality
- Other upload functions (uploadLogo, uploadFavicon, etc.) are unaffected as they use hardcoded folder paths
- Follows existing code patterns used in `uploadsController.get` function
