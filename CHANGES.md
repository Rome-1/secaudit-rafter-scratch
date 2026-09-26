# Upvoter List Access Control Implementation

## Overview
Fixed security vulnerability where `SocketPosts.getUpvoters` exposed upvoter information without checking read permissions.

## Changes Made

### 1. Backend: `/app/src/socket.io/posts/votes.js`

Modified `SocketPosts.getUpvoters` method (lines 38-87):

**Added Access Control:**
- Check if user is administrator (bypasses permission checks)
- For non-admins: validate `topics:read` permission on all categories
- Throw `[[error:no-privileges]]` if any category is not readable

**Added Performance Improvements:**
- Deduplicate UIDs before username resolution
- Use `Promise.all()` for parallel permission checks

**Added Cutoff Value:**
- Return `cutoff: 6` in response
- Show cutoff-1 (5) usernames when total > cutoff
- Put remaining count in `otherCount`

### 2. Frontend: `/app/public/src/client/topic/votes.js`

Modified `createTooltip` function (lines 48-73):

**Added:**
- `html: true` for tooltip HTML content support
- Dynamic cutoff from server response with fallback to 6

## Requirements Met

✅ Access control for non-administrators  
✅ Exact error message `[[error:no-privileges]]`  
✅ Administrator bypass  
✅ Permission check across all post IDs  
✅ UID deduplication  
✅ Cutoff value in response  
✅ Frontend uses server cutoff  
✅ HTML tooltip support  
✅ Uses `posts.getCidsByPids`  
✅ Bulk category validation  
✅ Username ordering preserved  

## Security Impact

**Before:** Any user could access upvoter data for any post  
**After:** Users must have `topics:read` permission on all associated categories

## Backwards Compatibility

✅ Response structure maintains all existing fields  
✅ Added `cutoff` field (non-breaking)  
✅ Frontend has fallback for old servers  
✅ Existing tests remain compatible  
