import re, sys, pathlib

root = pathlib.Path('/app')

ok = True
messages = []

def check_file(path, pattern, desc, flags=0):
    global ok
    text = path.read_text()
    if re.search(pattern, text, flags):
        messages.append(f"PASS: {desc}")
        return True
    else:
        messages.append(f"FAIL: {desc}")
        ok = False
        return False

# 1. AuthenticationMethodInfo has RequiresDatabase bool
p = root / 'internal' / 'config' / 'authentication.go'
check_file(p, r"type\s+AuthenticationMethodInfo\s*struct\s*{[\s\S]*?RequiresDatabase\s+bool", "AuthenticationMethodInfo includes RequiresDatabase bool")

# 2. JWT info has RequiresDatabase: false
check_file(p, r"AuthenticationMethodJWTConfig\) info\(\)\s*AuthenticationMethodInfo\s*{[\s\S]*?RequiresDatabase:\s*false,", "JWT info requires DB = false", flags=re.MULTILINE)

# 3. Token, OIDC, Github, Kubernetes info has RequiresDatabase: true
check_file(p, r"AuthenticationMethodTokenConfig\) info\(\)[\s\S]*?RequiresDatabase:\s*true,", "Token info requires DB = true", flags=re.MULTILINE)
check_file(p, r"AuthenticationMethodOIDCConfig\) info\(\)[\s\S]*?RequiresDatabase:\s*true,", "OIDC info requires DB = true", flags=re.MULTILINE)
check_file(p, r"AuthenticationMethodGithubConfig\) info\(\)[\s\S]*?RequiresDatabase:\s*true,", "Github info requires DB = true", flags=re.MULTILINE)
check_file(p, r"AuthenticationMethodKubernetesConfig\) info\(\)[\s\S]*?RequiresDatabase:\s*true,", "Kubernetes info requires DB = true", flags=re.MULTILINE)

# 4. AuthenticationConfig.RequiresDatabase method exists and checks enabled && RequiresDatabase
check_file(p, r"func \(c AuthenticationConfig\) RequiresDatabase\(\) bool\s*{[\s\S]*?info.Enabled && info.RequiresDatabase[\s\S]*?}", "AuthenticationConfig.RequiresDatabase implemented correctly", flags=re.MULTILINE)

# 5. ShouldRunCleanup considers RequiresDatabase
check_file(p, r"ShouldRunCleanup\) \(shouldCleanup bool\)\s*{[\s\S]*?info.Enabled && info.RequiresDatabase && info.Cleanup != nil", "ShouldRunCleanup considers RequiresDatabase", flags=re.MULTILINE)

# 6. Cleanup.Run skips methods where RequiresDatabase is false
cp = root / 'internal' / 'cleanup' / 'cleanup.go'
check_file(cp, r"if !info\.RequiresDatabase \{[\s\S]*?skipping\)", "Cleanup.Run skips non-DB methods", flags=re.MULTILINE)

# 7. authenticationGRPC uses RequiresDatabase to avoid DB when storage != database
ap = root / 'internal' / 'cmd' / 'authn.go'
check_file(ap, r"cfg\.Storage\.Type != config\.DatabaseStorageType && !authCfg\.RequiresDatabase\(\)", "authenticationGRPC checks RequiresDatabase for DB connection")

# 8. authenticationGRPC connects to DB only in else branch (by presence of getDB call after that check)
text = ap.read_text()
first_check_idx = text.find('cfg.Storage.Type != config.DatabaseStorageType && !authCfg.RequiresDatabase()')
getdb_idx = text.find('getDB(ctx, logger, cfg, forceMigrate)')
if first_check_idx != -1 and getdb_idx != -1 and getdb_idx > first_check_idx:
    messages.append("PASS: getDB called after RequiresDatabase check")
else:
    messages.append("FAIL: getDB not properly guarded by RequiresDatabase check")
    ok = False

print("\n".join(messages))
if not ok:
    sys.exit(1)
