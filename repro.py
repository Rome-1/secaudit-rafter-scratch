import os
print('- internal/config/storage.go exists:', os.path.exists('/app/internal/config/storage.go'))
print('- ui/src/app/meta/metaSlice.ts has selectConfig:', 'selectConfig' in open('/app/ui/src/app/meta/metaSlice.ts').read())
print('- ui/src/types/Meta.ts has OBJECT type:', 'OBJECT' in open('/app/ui/src/types/Meta.ts').read())
print('- invalid_readonly.yml exists:', os.path.exists('/app/internal/config/testdata/storage/invalid_readonly.yml'))
print('OK')
