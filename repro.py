import os, re, sys

ROOT = '/app'
chunk_path = os.path.join(ROOT, 'packages', 'util', 'chunk.ts')

errors = []

# 1) Verify the new file exists
if not os.path.isfile(chunk_path):
    errors.append(f"Missing file: {chunk_path}")
else:
    with open(chunk_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 2) Verify it has a default export named chunk
    if 'export default chunk' not in content:
        errors.append('chunk.ts does not have a default export named chunk')
    # 3) Verify signature defaults list to [] and size to 1
    if not re.search(r"chunk\s*=\s*<[^>]*>\(list:\s*[^)]*\[\]\s*=\s*\[\],\s*size\s*=\s*1\)", content):
        errors.append('chunk.ts does not declare default parameters list = [] and size = 1')

# 4) Find any imports of chunk from @proton/util/array (informational)
imports = []
for root, dirs, files in os.walk(ROOT):
    # Skip node_modules and hidden directories
    parts = set(root.split(os.sep))
    if 'node_modules' in parts or any(p.startswith('.') for p in parts):
        continue
    for name in files:
        if not name.endswith(('.ts', '.tsx', '.js', '.jsx', '.mjs')):
            continue
        p = os.path.join(root, name)
        try:
            s = open(p, 'r', encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        # Look specifically for chunk imported from @proton/util/array
        if re.search(r"import\s+\{[^}]*\bchunk\b[^}]*\}\s+from\s+'@proton/util/array'", s):
            imports.append(p)

print('New chunk file exists:', os.path.isfile(chunk_path))
print('Potential affected modules importing chunk from @proton/util/array (first 20 shown):')
for p in imports[:20]:
    print(' -', os.path.relpath(p, ROOT))
print('TOTAL_AFFECTED', len(imports))

if errors:
    print('ERRORS:')
    for e in errors:
        print(' -', e)
    sys.exit(1)
else:
    print('OK: chunk.ts present and signature looks correct.')
