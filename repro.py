import json, re, sys
from pathlib import Path
root = Path('/app')

ok = True
messages = []

# 1. defaults.json must include groupsExemptFromMaintenanceMode with default admins + Global Moderators
try:
    defaults = json.loads((root / 'install' / 'data' / 'defaults.json').read_text())
    val = defaults.get('groupsExemptFromMaintenanceMode')
    assert isinstance(val, list), 'groupsExemptFromMaintenanceMode must be a list in defaults.json'
    assert 'administrators' in val and 'Global Moderators' in val, 'defaults must contain administrators and Global Moderators'
    messages.append('defaults.json: groupsExemptFromMaintenanceMode present with expected defaults')
except Exception as e:
    ok = False
    messages.append(f'defaults.json check failed: {e}')

# 2. maintenance.js must check groups in maintenance mode
try:
    m = (root / 'src' / 'middleware' / 'maintenance.js').read_text()
    assert 'groupsExemptFromMaintenanceMode' in m, 'maintenance.js must reference groupsExemptFromMaintenanceMode'
    assert 'groups.isMemberOfAny' in m, 'maintenance.js must check membership via groups.isMemberOfAny'
    messages.append('maintenance.js: exemption logic found')
except Exception as e:
    ok = False
    messages.append(f'maintenance.js check failed: {e}')

# 3. settings controller: advanced
try:
    ctrl = (root / 'src' / 'controllers' / 'admin' / 'settings.js').read_text()
    assert re.search(r"settingsController\.advanced\s*=\s*async", ctrl), 'settingsController.advanced function missing'
    messages.append('settings controller: advanced endpoint present')
except Exception as e:
    ok = False
    messages.append(f'settings controller check failed: {e}')

# 4. Admin routes: explicit advanced route
try:
    routes = (root / 'src' / 'routes' / 'admin.js').read_text()
    assert "/settings/advanced" in routes and 'controllers.admin.settings.advanced' in routes, 'explicit /settings/advanced route missing'
    messages.append('admin routes: explicit /settings/advanced route present')
except Exception as e:
    ok = False
    messages.append(f'admin routes check failed: {e}')

# 5. View template has multi-select for groupsExemptFromMaintenanceMode
try:
    tpl = (root / 'src' / 'views' / 'admin' / 'settings' / 'advanced.tpl').read_text()
    assert 'data-field="groupsExemptFromMaintenanceMode"' in tpl, 'advanced.tpl missing multi-select for groupsExemptFromMaintenanceMode'
    messages.append('advanced.tpl: multi-select present')
except Exception as e:
    ok = False
    messages.append(f'advanced.tpl check failed: {e}')

print('\n'.join(messages))
if not ok:
    sys.exit(1)
