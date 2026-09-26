import re, sys, pathlib

root = pathlib.Path(__file__).parent
server = root / 'src' / 'socket.io' / 'posts' / 'votes.js'
client = root / 'public' / 'src' / 'client' / 'topic' / 'votes.js'

errors = []

# Server checks
s = server.read_text(encoding='utf-8')

# 1) Access control: must use posts.getCidsByPids and privileges.categories.isUserAllowedTo with topics:read
if 'getCidsByPids' not in s:
    errors.append('Server: missing posts.getCidsByPids usage')
if "categories.isUserAllowedTo('topics:read'" not in s and 'categories.isUserAllowedTo("topics:read"' not in s:
    errors.append('Server: missing privileges check for topics:read')
if '[[error:no-privileges]]' not in s:
    errors.append('Server: missing no-privileges error throw')
# 2) Deduplicate before resolving usernames: look for a single call to getUsernamesByUids over a union
calls = len(re.findall(r'getUsernamesByUids\(', s))
if calls != 1:
    errors.append(f'Server: expected 1 call to user.getUsernamesByUids, found {calls}')
# 3) Cutoff presence
if 'cutoff' not in s:
    errors.append('Server: missing cutoff in response')

# Client checks
c = client.read_text(encoding='utf-8')

# 4) Use cutoff from server response, not hardcoded 6
if re.search(r">\s*6\)\s*\{", c):
    errors.append('Client: still using hardcoded 6 in comparison')
if 'data.cutoff' not in c and 'd.cutoff' not in c:
    errors.append('Client: not reading cutoff from server response')
# 5) Tooltip html: true
if 'new bootstrap.Tooltip' in c and 'html: true' not in c:
    errors.append('Client: tooltip not configured with html: true')

if errors:
    print('FAIL')
    for e in errors:
        print('-', e)
    sys.exit(1)
else:
    print('PASS')
    sys.exit(0)
