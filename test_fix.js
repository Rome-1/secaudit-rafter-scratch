// Test script to verify the fixed implementation

// Mock localStorage for Node.js environment
const localStorage = {
  _data: {},
  setItem: function(key, value) {
    this._data[key] = value;
  },
  getItem: function(key) {
    return this._data[key] || null;
  },
  removeItem: function(key) {
    delete this._data[key];
  },
  clear: function() {
    this._data = {};
  },
  get length() {
    return Object.keys(this._data).length;
  }
};

// Mock global localStorage with proper indexing
global.localStorage = new Proxy(localStorage, {
  get(target, prop) {
    if (typeof prop === 'string' && prop in target._data) {
      return target._data[prop];
    }
    return target[prop];
  }
});

// Mock Object.keys to work with localStorage
const originalObjectKeys = Object.keys;
Object.keys = function(obj) {
  if (obj === localStorage) {
    return Object.keys(localStorage._data);
  }
  return originalObjectKeys(obj);
};

// Constants from the original code
const STORAGE_PREFIX = 'ps-';
const LAST_ACTIVE_PING = 'drive-last-active';

// Mock error reporting
const sendErrorReport = (error) => {
  console.log('Error reported:', error.message || error);
};

// Mock EnrichedError
class EnrichedError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.extra = options.extra;
  }
}

// Helper function (unchanged)
function getLastActiveUserId() {
  const storageKeys = Object.keys(localStorage);
  let lastActiveUserId = '';
  let lastAccess = 0;

  for (const k of storageKeys) {
    if (k.startsWith(LAST_ACTIVE_PING)) {
      try {
        const data = JSON.parse(localStorage[k]);
        const lastPing = Number(data.value);
        if (lastAccess < lastPing) {
          lastAccess = lastPing;
          lastActiveUserId = k.substring(k.indexOf(LAST_ACTIVE_PING) + LAST_ACTIVE_PING.length + 1);
        }
      } catch (e) {
        // Handle parsing errors
      }
    }
  }
  return lastActiveUserId || null;
}

// NEW IMPLEMENTATION - Fixed according to requirements
function getLastPersistedLocalID() {
  try {
    const storageKeys = Object.keys(localStorage);
    
    // Return null if localStorage is empty
    if (storageKeys.length === 0) {
      return null;
    }
    
    // Get localID from last active session
    // This support multi tabs and multi accounts
    const lastActiveUserId = getLastActiveUserId();
    if (lastActiveUserId) {
      for (const k of storageKeys) {
        if (k.startsWith(STORAGE_PREFIX)) {
          try {
            const suffix = k.substring(STORAGE_PREFIX.length);
            
            // Check if suffix is numeric
            if (!/^\d+$/.test(suffix)) {
              continue; // Skip non-numeric suffixes
            }
            
            const data = JSON.parse(localStorage[k]);
            if (data.UserID === lastActiveUserId && data.UID) {
              return Number(suffix);
            }
          } catch (e) {
            // Skip keys with invalid JSON
            continue;
          }
        }
      }
    }

    // Fallback: rely on last storage prefix
    // This does not support multi tabs
    let lastLocalID = null;
    for (const k of storageKeys) {
      if (k.startsWith(STORAGE_PREFIX)) {
        try {
          const suffix = k.substring(STORAGE_PREFIX.length);
          
          // Check if suffix is numeric
          if (!/^\d+$/.test(suffix)) {
            continue; // Skip non-numeric suffixes
          }
          
          const data = JSON.parse(localStorage[k]);
          if (lastLocalID === null || data.persistedAt > lastLocalID.persistedAt) {
            lastLocalID = {
              persistedAt: data.persistedAt,
              ID: Number(suffix),
            };
          }
        } catch (e) {
          // Skip keys with invalid JSON
          continue;
        }
      }
    }

    return lastLocalID?.ID ?? null;
  } catch (e) {
    sendErrorReport(
      new EnrichedError('Failed to parse JSON from localStorage', {
        extra: {
          e,
        },
      })
    );
    return null;
  }
}

// Test scenarios
console.log('=== TESTING FIXED IMPLEMENTATION ===');

// Test 1: Empty localStorage - Should return null
console.log('\n1. Empty localStorage:');
localStorage.clear();
const result1 = getLastPersistedLocalID();
console.log('Result:', result1);
console.log('✓ Expected: null, Got:', result1, '- PASS:', result1 === null);

// Test 2: No valid STORAGE_PREFIX keys - Should return null
console.log('\n2. No valid STORAGE_PREFIX keys:');
localStorage.clear();
localStorage.setItem('other-key', 'value');
localStorage.setItem('random-key', JSON.stringify({data: 'test'}));
const result2 = getLastPersistedLocalID();
console.log('Result:', result2);
console.log('✓ Expected: null, Got:', result2, '- PASS:', result2 === null);

// Test 3: Keys with STORAGE_PREFIX but non-numeric suffix - Should return null
console.log('\n3. Keys with STORAGE_PREFIX but non-numeric suffix:');
localStorage.clear();
localStorage.setItem(`${STORAGE_PREFIX}abc`, JSON.stringify({persistedAt: Date.now()}));
localStorage.setItem(`${STORAGE_PREFIX}xyz`, JSON.stringify({persistedAt: Date.now()}));
const result3 = getLastPersistedLocalID();
console.log('Result:', result3);
console.log('✓ Expected: null, Got:', result3, '- PASS:', result3 === null);

// Test 4: Valid numeric keys - Should return the one with highest persistedAt
console.log('\n4. Valid numeric keys:');
localStorage.clear();
localStorage.setItem(`${STORAGE_PREFIX}123`, JSON.stringify({persistedAt: Date.now() - 1000}));
localStorage.setItem(`${STORAGE_PREFIX}456`, JSON.stringify({persistedAt: Date.now()}));
localStorage.setItem(`${STORAGE_PREFIX}789`, JSON.stringify({persistedAt: Date.now() - 2000}));
const result4 = getLastPersistedLocalID();
console.log('Result:', result4);
console.log('✓ Expected: 456, Got:', result4, '- PASS:', result4 === 456);

// Test 5: JSON parsing errors - Should return null
console.log('\n5. JSON parsing errors:');
localStorage.clear();
localStorage.setItem(`${STORAGE_PREFIX}123`, 'invalid json');
const result5 = getLastPersistedLocalID();
console.log('Result:', result5);
console.log('✓ Expected: null, Got:', result5, '- PASS:', result5 === null);

// Test 6: Mixed valid and invalid keys - Should return valid one
console.log('\n6. Mixed valid and invalid keys:');
localStorage.clear();
localStorage.setItem(`${STORAGE_PREFIX}abc`, JSON.stringify({persistedAt: Date.now()})); // Invalid suffix
localStorage.setItem(`${STORAGE_PREFIX}123`, JSON.stringify({persistedAt: Date.now() - 500})); // Valid
localStorage.setItem(`${STORAGE_PREFIX}456`, 'invalid json'); // Invalid JSON
localStorage.setItem(`${STORAGE_PREFIX}789`, JSON.stringify({persistedAt: Date.now()})); // Valid - most recent
const result6 = getLastPersistedLocalID();
console.log('Result:', result6);
console.log('✓ Expected: 789, Got:', result6, '- PASS:', result6 === 789);

// Test 7: With last active ping - Should prioritize active session
console.log('\n7. With last active ping:');
localStorage.clear();
localStorage.setItem(`${LAST_ACTIVE_PING}-user123`, JSON.stringify({ value: Date.now() }));
localStorage.setItem(`${STORAGE_PREFIX}999`, JSON.stringify({ UserID: 'user123', UID: 'session-123' }));
localStorage.setItem(`${STORAGE_PREFIX}888`, JSON.stringify({ persistedAt: Date.now() + 1000 })); // Higher persistedAt but not active
const result7 = getLastPersistedLocalID();
console.log('Result:', result7);
console.log('✓ Expected: 999, Got:', result7, '- PASS:', result7 === 999);

// Test 8: Edge case - numeric suffix "0" should be valid
console.log('\n8. Edge case - numeric suffix "0":');
localStorage.clear();
localStorage.setItem(`${STORAGE_PREFIX}0`, JSON.stringify({persistedAt: Date.now()}));
const result8 = getLastPersistedLocalID();
console.log('Result:', result8);
console.log('✓ Expected: 0, Got:', result8, '- PASS:', result8 === 0);

console.log('\n=== SOLUTION SUMMARY ===');
console.log('✅ Fixed implementation now returns null for ambiguous cases instead of 0');
console.log('✅ Session restoration logic can now distinguish between:');
console.log('   - Valid session with ID 0 (returns number 0)');
console.log('   - No valid session found (returns null)');
console.log('✅ Only evaluates keys with STORAGE_PREFIX and numeric suffixes');
console.log('✅ Handles JSON parsing errors gracefully');
console.log('✅ Never falls back to returning 0 for error cases');