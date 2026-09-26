import subprocess, sys, os

pkgs = [
  './lib/auth/native',
  './lib/reversetunnel',
  './lib/auth',
  './lib/service',
]

def run(cmd):
    print('Running:', ' '.join(cmd), flush=True)
    p = subprocess.run(cmd, cwd='/app')
    if p.returncode != 0:
        sys.exit(p.returncode)

for pkg in pkgs:
    run(['go', 'build', pkg])

print('OK build of target packages')
