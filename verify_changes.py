import re, os, sys
root = '/app'

ok = True

def check_file(path, contains=None, not_contains=None):
    global ok
    p = os.path.join(root, path)
    try:
        with open(p, 'r', encoding='utf-8') as f:
            s = f.read()
    except Exception as e:
        print('ERROR reading', path, e)
        ok = False
        return ''
    if contains:
        for c in contains:
            if re.search(c, s, re.M|re.S) is None:
                print('MISSING in', path, ':', c)
                ok = False
    if not_contains:
        for c in not_contains:
            if re.search(c, s, re.M|re.S):
                print('SHOULD NOT CONTAIN in', path, ':', c)
                ok = False
    return s

# 1. config: prometheusOptions has Password and defaults include PrometheusDefaultPath
check_file('conf/configuration.go', contains=[r'type\s+prometheusOptions\s+struct\s*{[\s\S]*Password\s+string[\s\S]*}', r'viper\.SetDefault\(prometheus.metricspath,\s*consts\.PrometheusDefaultPath\)', r'viper\.SetDefault\(prometheus.password'],)

# 2. consts: PrometheusDefaultPath and PrometheusAuthUser
check_file('consts/consts.go', contains=[r'PrometheusDefaultPath\s*=\s*/metrics', r'PrometheusAuthUser\s*=\s*prometheus'])

# 3. metrics interface & implementation
check_file('core/metrics/prometheus.go', contains=[r'type\s+Metrics\s+interface', r'WriteInitialMetrics\(ctx\s+context\.Context\)', r'WriteAfterScanMetrics\(ctx\s+context\.Context,\s*success\s+bool\)', r'GetHandler\(\)\s+http\.Handler', r'NewPrometheusInstance\(', r'type\s+metrics\s+struct\s*{[\s\S]*ds\s+model\.DataStore[\s\S]*}', r'middleware\.BasicAuth', r'promhttp\.Handler\(\)'])

# 4. remove authHeaderMapper from middlewares and use jwtVerifier
check_file('server/server.go', not_contains=[r'authHeaderMapper,'], contains=[r'jwtVerifier,'])

# 5. jwtVerifier uses tokenFromHeader
check_file('server/auth.go', contains=[r'func\s+tokenFromHeader\(r\s+\*http\.Request\)\s+string', r'jwtauth\.Verify\(auth\.TokenAuth,\s*[^\)]*tokenFromCustom'])

# 6. scanner uses metrics interface
check_file('scanner/scanner.go', contains=[r's\.m\.WriteAfterScanMetrics\(', r'metrics\.NewPrometheusInstance\('], not_contains=[r'metrics\.WriteAfterScanMetrics\('])

# 7. metrics initial write at startup via server.MountPrometheus
check_file('server/server.go', contains=[r'func\s*\(s \*Server\)\s*MountPrometheus\(', r's\.metrics\.WriteInitialMetrics\(', r'PrometheusDefaultPath'])

if ok:
    print('All checks passed (static verification).')
else:
    print('Some checks failed.')
    sys.exit(1)
