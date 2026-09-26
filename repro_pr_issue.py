import re, sys, pathlib

ROOT = pathlib.Path('/app')

os_go = ROOT / 'config' / 'os.go'
ubuntu_go = ROOT / 'gost' / 'ubuntu.go'

errors = []

# Check config/os.go Ubuntu mapping
text = os_go.read_text()

# Extract Ubuntu case block
m = re.search(r'case constant\.Ubuntu:\s*//[^\n]*\n\s*eol, found = map\[string\]EOL\{(.+?)\}\[release\]', text, re.S)
if not m:
    errors.append('Could not locate Ubuntu EOL map in config/os.go')
else:
    ub_map = m.group(1)
    # 20.04 extended support 2030-04-01
    m2004 = re.search(r'"20\.04"\s*:\s*\{([^}]*)\},?', ub_map)
    if not m2004:
        errors.append('Ubuntu 20.04 entry missing in config/os.go')
    else:
        body = m2004.group(1)
        # ExtendedSupportUntil present 2030, month 4, day 1
        if 'ExtendedSupportUntil' not in body:
            errors.append('Ubuntu 20.04 missing ExtendedSupportUntil in config/os.go')
        else:
            if not re.search(r'ExtendedSupportUntil:\s*time\.Date\(2030,\s*4,\s*1,\s*23,\s*59,\s*59,\s*0,\s*time\.UTC\)', body):
                errors.append('Ubuntu 20.04 ExtendedSupportUntil not set to 2030-04-01 23:59:59 UTC')
    # 22.04 standard support 2027-04-01 and extended 2032-04-01
    m2204 = re.search(r'"22\.04"\s*:\s*\{([^}]*)\},?', ub_map)
    if not m2204:
        errors.append('Ubuntu 22.04 entry missing in config/os.go')
    else:
        body = m2204.group(1)
        if not re.search(r'StandardSupportUntil:\s*time\.Date\(2027,\s*4,\s*1,\s*23,\s*59,\s*59,\s*0,\s*time\.UTC\)', body):
            errors.append('Ubuntu 22.04 StandardSupportUntil not set to 2027-04-01 23:59:59 UTC')
        if not re.search(r'ExtendedSupportUntil:\s*time\.Date\(2032,\s*4,\s*1,\s*23,\s*59,\s*59,\s*0,\s*time\.UTC\)', body):
            errors.append('Ubuntu 22.04 ExtendedSupportUntil not set to 2032-04-01 23:59:59 UTC')

# Check gost/ubuntu.go supported map includes 2204->jammy
utext = ubuntu_go.read_text()
msup = re.search(r'func \(ubu Ubuntu\) supported\(version string\) bool \{\s*_, ok := map\[string\]string\{(.+?)\}\[version\]', utext, re.S)
if not msup:
    errors.append('Could not locate supported() map in gost/ubuntu.go')
else:
    body = msup.group(1)
    if not re.search(r'"2204"\s*:\s*"jammy"', body):
        errors.append('gost/ubuntu.go supported() missing 2204:"jammy" entry')

if errors:
    print('Reproduction script detected the following issues:')
    for e in errors:
        print('-', e)
    sys.exit(1)
else:
    print('All checks passed: Ubuntu 20.04 extended support and Ubuntu 22.04 support are correctly configured.')
