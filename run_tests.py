import os, subprocess, sys

def run(cmd):
    print('Running:', cmd)
    p = subprocess.Popen(cmd, shell=True)
    p.communicate()
    return p.returncode

# Set up env for tests
os.chdir('/app')
code = run('go test ./...')
sys.exit(code)
