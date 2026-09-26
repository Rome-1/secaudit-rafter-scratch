import subprocess, sys, textwrap, os

# This script verifies that Plugins.toggleActive rejects invalid plugin identifiers

node_js = textwrap.dedent(r'''
const path = require('path');
const nconf = require('nconf');

// Set minimal configuration required by modules that are imported transitively
nconf.set('base_dir', __dirname);
nconf.set('database', 'redis');

(async () => {
  try {
    // Import only the install module to attach methods onto a bare Plugins object
    const Plugins = {};
    require('./src/plugins/install')(Plugins);

    // Expect immediate validation failure before any state queries/changes are attempted
    await Plugins.toggleActive('not-a-plugin');
    console.log('UNEXPECTED: no error thrown');
  } catch (err) {
    console.log('ERROR_MESSAGE:' + (err && err.message));
  }
})();
''')

# Run the Node.js snippet via stdin
proc = subprocess.run(['node', '-e', node_js], capture_output=True, text=True)
print(proc.stdout)
print(proc.stderr, file=sys.stderr)

# Simple assertion-like exit code for usage in CI
if 'ERROR_MESSAGE:[[error:invalid-plugin-id]]' in proc.stdout:
    sys.exit(0)
else:
    sys.exit(1)
