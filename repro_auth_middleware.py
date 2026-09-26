import re
from pathlib import Path

p = Path('/app/internal/server/auth/middleware.go')
code = p.read_text()

checks = {
    'has InterceptorOptions struct': re.search(r'type\s+InterceptorOptions\s+struct\s*{', code) is not None,
    'has WithServerSkipsAuthentication': 'WithServerSkipsAuthentication' in code and 'containers.Option[InterceptorOptions]' in code,
    'has clientTokenFromAuthorization helper': re.search(r'func\s+clientTokenFromAuthorization\s*\(', code) is not None,
    'has clientTokenFromMetadata helper': re.search(r'func\s+clientTokenFromMetadata\s*\(', code) is not None,
    'has cookieFromMetadata helper': re.search(r'func\s+cookieFromMetadata\s*\(', code) is not None,
    'uses grpcgateway-cookie header': 'grpcgateway-cookie' in code,
    'uses flipt_client_token cookie name': 'flipt_client_token' in code,
    'UnaryInterceptor supports options': re.search(r'func\s+UnaryInterceptor\([^)]*\.\.\.containers\.Option\[InterceptorOptions\][^)]*\)\s*grpc\.UnaryServerInterceptor', code) is not None,
}

failed = [name for name, ok in checks.items() if not ok]

if failed:
    print('Reproduction script: FAIL')
    print('Missing or incorrect implementations:')
    for name in failed:
        print('-', name)
    raise SystemExit(1)
else:
    print('Reproduction script: PASS')
    for name in checks:
        print('-', name)
    print('\nAll required symbols and logic appear to be present in middleware.go')
