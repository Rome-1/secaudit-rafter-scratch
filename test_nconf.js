const nconf = require('nconf');
const path = require('path');
nconf.use('memory');
nconf.set('upload_path', path.join(__dirname, 'public', 'uploads'));
console.log('get upload_path=', nconf.get('upload_path'));