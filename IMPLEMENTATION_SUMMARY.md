# Maintenance Mode Exemption Implementation Summary

## Overview
Successfully implemented the ability to allow non-admin forum access while in maintenance mode, as requested in the PR description.

## Changes Made

### 1. Core Middleware Logic (`src/middleware/maintenance.js`)
- Added `groups` module requirement
- Implemented `getGroupsExemptFromMaintenanceMode()` function with robust fallback handling
- Implemented `checkUserExemptFromMaintenance()` function for user exemption checking
- Added group exemption logic that runs after admin check but before blocking users
- Handles JSON configuration parsing with error handling
- Supports guest exemptions for unauthenticated users
- Maintains default exemptions for 'administrators' and 'Global Moderators'

### 2. Admin Settings Controller (`src/controllers/admin/settings.js`)
- Added `settingsController.advanced` method as specified in the interface requirements
- Fetches non-privileged groups using `groups.getNonPrivilegeGroups()`
- Renders `admin/settings/advanced` template with group data
- Follows NodeBB controller patterns and async/await best practices

### 3. Admin UI Template (`src/views/admin/settings/advanced.tpl`)
- Added multi-select control for group exemption configuration
- Proper data field binding (`data-field="groupsExemptFromMaintenanceMode"`)
- Template loops for displaying available groups
- Integrated with existing advanced settings page structure

### 4. Admin Routes (`src/routes/admin.js`)
- Added dedicated route for `/admin/settings/advanced`
- Positioned before generic settings route to ensure proper routing
- Uses standard NodeBB route setup pattern

### 5. Default Configuration (`install/data/defaults.json`)
- Added `groupsExemptFromMaintenanceMode` with default value `["administrators", "Global Moderators"]`
- Ensures system has sensible defaults even without explicit configuration

## Requirements Compliance

### ✅ Configurable Exemption List
- `groupsExemptFromMaintenanceMode` configuration key implemented
- Defaults include administrators and Global Moderators
- Supports array format for multiple groups

### ✅ Maintenance Bypass Logic  
- Non-admin users in exempt groups can access forum during maintenance
- Preserves existing admin access behavior
- Login URLs remain accessible as before

### ✅ Guest Handling
- Unauthenticated visitors treated as 'guests' group
- Can be exempted by including 'guests' in configuration
- Proper fallback for uid <= 0 scenarios

### ✅ Admin UI
- Multi-select control for non-privileged groups
- Persists to `groupsExemptFromMaintenanceMode` config key
- Dedicated admin route `/admin/settings/advanced`

### ✅ Error Handling & Fallbacks
- Invalid JSON configuration handled gracefully
- Missing/empty config falls back to defaults
- Array type validation with proper error handling

### ✅ No Breaking Changes
- Maintenance mode disabled = no behavior change
- Existing admin/login behavior preserved
- All original functionality maintained

## Technical Implementation Details

### Configuration Handling
```javascript
// Supports multiple formats:
// - JSON string: '["group1", "group2"]' 
// - Array: ["group1", "group2"]
// - Invalid/missing: falls back to defaults
```

### User Access Logic
```javascript
// Priority order:
// 1. Maintenance mode disabled → allow all
// 2. Login URLs → always allow
// 3. Administrator check → allow (existing behavior)
// 4. Group exemption check → allow if in exempt group  
// 5. Default → show maintenance page
```

### Group Membership Check
- Uses `groups.isMemberOfGroups(uid, exemptGroups)` API
- Handles both authenticated and unauthenticated users
- Efficient single API call for multiple group checks

## Testing Readiness

The implementation is ready for:
- **Unit Testing**: Various user types, group memberships, configuration scenarios
- **Integration Testing**: Admin UI functionality, configuration persistence  
- **End-to-End Testing**: Complete maintenance mode scenarios
- **Edge Case Testing**: Invalid configs, mixed user types, guest scenarios

## Files Modified

1. `src/middleware/maintenance.js` - Core exemption logic
2. `src/controllers/admin/settings.js` - Admin controller method
3. `src/views/admin/settings/advanced.tpl` - UI template
4. `src/routes/admin.js` - Route configuration  
5. `install/data/defaults.json` - Default configuration

## Zero Breaking Changes

- ✅ Existing admin access preserved
- ✅ Login functionality unchanged  
- ✅ Maintenance mode disabled behavior unchanged
- ✅ All original features work as before
- ✅ Backward compatible configuration

The implementation successfully meets all requirements from the PR description while maintaining full backward compatibility and robust error handling.