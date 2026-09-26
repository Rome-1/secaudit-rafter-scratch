import re, sys

files = {
    'redis': '/app/src/database/redis/sorted.js',
    'postgres': '/app/src/database/postgres/sorted.js',
    'mongo': '/app/src/database/mongo/sorted.js',
}

ok = True
for name, path in files.items():
    try:
        with open(path, 'r', encoding='utf-8') as f:
            s = f.read()
    except Exception as e:
        print(f'FAILED to open {name} at {path}: {e}')
        ok = False
        continue
    m = re.search(r"module\.sortedSetsCardSum\s*=\s*async function\s*\(([^)]*)\)", s)
    if not m:
        print(f'FAILED: {name} sortedSetsCardSum not found')
        ok = False
        continue
    params = [p.strip() for p in m.group(1).split(',')]
    if params != ['keys', 'min', 'max']:
        print(f'FAILED: {name} params were {params} (expected [keys, min, max])')
        ok = False
    body_start = m.end()
    next_anchor = s.find('module.sortedSetRank', body_start)
    if next_anchor == -1:
        next_anchor = len(s)
    body = s[body_start:next_anchor]
    if name == 'redis':
        if 'zcount' not in body:
            print('FAILED: redis implementation does not use zcount')
            ok = False
    elif name == 'postgres':
        if 'COUNT(*)' not in body or 'score' not in body:
            print('FAILED: postgres implementation missing COUNT/score filtering')
            ok = False
    elif name == 'mongo':
        if 'countDocuments' not in body or 'query.score' not in body:
            print('FAILED: mongo implementation missing countDocuments with score filter')
            ok = False
    print(f'PASS: {name} implementation looks good')

if not ok:
    sys.exit(1)
print('All adapters pass static checks.')
