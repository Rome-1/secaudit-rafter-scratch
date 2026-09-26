// Reproduction script to test the current behavior of getLastPersistedLocalID
// Simulating the issue described in the PR

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

// Mock global localStorage
global.localStorage = localStorage;

// Constants from the original code
const STORAGE_PREFIX = 'ps-';
const LAST_ACTIVE_PING = 'drive-last-active';

// Mock error reporting
const sendErrorReport = (error) => {
  console.log('Error reported:', error.message || error);
};

// Current implementation
function getLastActiveUserId() {
  const storageKeys = Object.keys(localStorage._data);
  let lastActiveUserId = '';
  let lastAccess = 0;

  for (const k of storageKeys) {
    if (k.startsWith(LAST_ACTIVE_PING)) {
      try {
        const data = JSON.parse(localStorage.getItem(k));
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

// Current implementation of getLastPersistedLocalID (returns 0 for edge cases)
function getLastPersistedLocalID() {
  try {
    const storageKeys = Object.keys(localStorage._data);
    
    const lastActiveUserId = getLastActiveUserId();
    if (lastActiveUserId) {
      for (const k of storageKeys) {
        if (k.startsWith(STORAGE_PREFIX)) {
          try {
            const data = JSON.parse(localStorage.getItem(k));
            if (data.UserID === lastActiveUserId && data.UID) {
              return Number(k.substring(STORAGE_PREFIX.length));
            }
          } catch (e) {
            // Handle parsing errors
          }
        }
      }
    }

    // Fallback: rely on last storage prefix
    let lastLocalID = null;
    for (const k of storageKeys) {
      if (k.startsWith(STORAGE_PREFIX)) {
        try {
          const data = JSON.parse(localStorage.getItem(k));
          if (lastLocalID === null || data.persistedAt > lastLocalID.persistedAt) {
            lastLocalID = {
              persistedAt: data.persistedAt,
              ID: Number(k.substring(STORAGE_PREFIX.length)),
            };
          }
        } catch (e) {
          // Handle parsing errors
        }
      }
    }

    return lastLocalID?.ID || 0;
  } catch (e) {
    sendErrorReport(new Error('Failed to parse JSON from localStorage: ' + e.message));
    return 0;
  }
}

// Test scenarios
console.log('=== TESTING CURRENT IMPLEMENTATION ===');

// Test 1: Empty localStorage
console.log('\n1. Empty localStorage:');
localStorage.clear();
console.log('Result:', getLastPersistedLocalID()); // Expected: 0 (current), Should be: null

// Test 2: No valid STORAGE_PREFIX keys
console.log('\n2. No valid STORAGE_PREFIX keys:');
localStorage.clear();
localStorage.setItem('other-key', 'value');
localStorage.setItem('random-key', JSON.stringify({data: 'test'}));
console.log('Result:', getLastPersistedLocalID()); // Expected: 0 (current), Should be: null

// Test 3: Keys with STORAGE_PREFIX but non-numeric suffix
console.log('\n3. Keys with STORAGE_PREFIX but non-numeric suffix:');
localStorage.clear();
localStorage.setItem(`${STORAGE_PREFIX}abc`, JSON.stringify({persistedAt: Date.now()}));
localStorage.setItem(`${STORAGE_PREFIX}xyz`, JSON.stringify({persistedAt: Date.now()}));
console.log('Result:', getLastPersistedLocalID()); // Should be: null for invalid numeric IDs

// Test 4: Valid numeric keys
console.log('\n4. Valid numeric keys:');
localStorage.clear();
localStorage.setItem(`${STORAGE_PREFIX}123`, JSON.stringify({persistedAt: Date.now() - 1000}));
localStorage.setItem(`${STORAGE_PREFIX}456`, JSON.stringify({persistedAt: Date.now()}));
console.log('Result:', getLastPersistedLocalID()); // Should return 456

// Test 5: JSON parsing errors
console.log('\n5. JSON parsing errors:');
localStorage.clear();
localStorage.setItem(`${STORAGE_PREFIX}123`, 'invalid json');
console.log('Result:', getLastPersistedLocalID()); // Expected: 0 (current), Should be: null

console.log('\n=== DEMONSTRATION OF THE ISSUE ===');
console.log('The current implementation returns 0 for all error/empty cases.');
console.log('This causes ambiguity in session restoration logic because:');
console.log('- localID 0 could be a valid session ID');
console.log('- localID 0 could mean "no valid session found"');
console.log('The restoration logic cannot distinguish between these cases.');