# Summary of Changes to Password Lookup Plugin

## Issue
The password lookup plugin was ignoring key=value parameters such as `seed`, resulting in non-deterministic output even when a fixed seed was provided.

## Root Cause
The `_parse_parameters` function was a global function that didn't integrate with Ansible's plugin option system. Parameters passed as kwargs were not being properly retrieved when parsing terms.

## Changes Made

### 1. Converted `_parse_parameters` to Instance Method
- **Location**: `lib/ansible/plugins/lookup/password.py` - class `LookupModule`
- **What**: Moved `_parse_parameters` from a global function to an instance method of `LookupModule`
- **Why**: To allow access to plugin options via `self.get_option()` and `self.set_options()`

### 2. Added `set_options()` Call in `run()` Method
- **Location**: `lib/ansible/plugins/lookup/password.py` - `LookupModule.run()`
- **What**: Added `self.set_options(var_options=variables, direct=kwargs)` at the start of `run()`
- **Why**: To properly initialize plugin options from variables and kwargs

### 3. Enhanced Parameter Resolution
- **Location**: `lib/ansible/plugins/lookup/password.py` - `LookupModule._parse_parameters()`
- **What**: Created `_get_option_safe()` helper function to safely retrieve options
- **Why**: To handle cases where options might not be defined in config but are passed via kwargs

### 4. Added Direct kwargs to _options
- **Location**: `lib/ansible/plugins/lookup/password.py` - `LookupModule.run()`
- **What**: Added code to store VALID_PARAMS from kwargs directly in `_options`
- **Why**: To ensure kwargs like `seed`, `chars`, etc. are available even if not in config

### 5. Enhanced `chars` Parameter Handling
- **Location**: `lib/ansible/plugins/lookup/password.py` - `LookupModule._parse_parameters()`
- **What**: Added type checking to handle both list and string formats for `chars`
- **Why**: To support both `chars=['ascii_letters', 'digits']` and `chars='ascii_letters,digits'`

### 6. Backward Compatibility Wrapper
- **Location**: `lib/ansible/plugins/lookup/password.py` - global `_parse_parameters()` function
- **What**: Created a wrapper function that delegates to the instance method
- **Why**: To maintain compatibility with tests and code that call `_parse_parameters()` as a module function

### 7. Handle Missing `_load_name`
- **Location**: `lib/ansible/plugins/lookup/password.py` - `LookupModule.run()`
- **What**: Added check to set `_load_name` if not already set
- **Why**: To support testing scenarios where plugin is not loaded via plugin loader

## Requirements Met

✅ **1. `chars` option supports both list and comma-separated string**
   - List: `chars=['ascii_letters', 'digits']` works
   - String: `chars='ascii_letters,digits'` works
   - Literal comma: `chars='a,b,c,,'` includes comma character

✅ **2. `_parse_parameters` is an instance method**
   - Moved from global function to `LookupModule._parse_parameters()`

✅ **3. Only accept expected keys**
   - Validates against `VALID_PARAMS = frozenset(('length', 'encrypt', 'chars', 'ident', 'seed'))`
   - Raises `AnsibleError` for invalid parameters

✅ **4. Term values take precedence over plugin options**
   - Parameters in term string are checked first via `params.get('key', ...)`
   - Plugin options via `get_option()` are used as defaults

✅ **5. `length` defaults to 20 if unspecified**
   - Uses `DEFAULT_LENGTH = 20` constant

✅ **6. `seed` ensures deterministic behavior**
   - Same seed produces identical passwords across multiple runs
   - Different seeds produce different passwords

✅ **7. Handle `_raw_params` during parsing**
   - Reconstructs file path when spaces are present
   - Validates full term string starts with reconstructed path

✅ **8. `run()` calls `set_options()`**
   - Calls `self.set_options(var_options=variables, direct=kwargs)` before parsing

✅ **9. Defaults sourced via `get_option()`**
   - Uses `_get_option_safe()` helper to safely retrieve options
   - Falls back to defaults when option not available

✅ **10. `run()` delegates to `self._parse_parameters()`**
   - Changed from `_parse_parameters(term, kwargs)` to `self._parse_parameters(term)`

✅ **11. Password candidates from `chars` list**
   - Uses existing `_gen_candidate_chars()` function
   - Evaluates string module attributes like `ascii_letters`, `digits`

## Testing

All 29 existing unit tests pass:
- `TestParseParameters` - 3 tests
- `TestReadPasswordFile` - 2 tests  
- `TestGenCandidateChars` - 1 test
- `TestRandomPassword` - 7 tests
- `TestParseContent` - 3 tests
- `TestFormatContent` - 4 tests
- `TestWritePasswordFile` - 1 test
- `TestLookupModuleWithoutPasslib` - 5 tests
- `TestLookupModuleWithPasslib` - 2 tests
- `TestLookupModuleWithPasslibWrappedAlgo` - 1 test

Additional verification:
- Seed parameter in term format produces deterministic output
- Seed parameter in kwargs format produces deterministic output
- Different seeds produce different passwords
- Term parameters take precedence over kwargs
- Chars as list works correctly
- Chars as comma-separated string works correctly
- Chars with literal comma (,,) works correctly
- Length parameter works in both term and kwargs
- Default length is 20 when not specified
- Multiple parameters in term work together correctly
