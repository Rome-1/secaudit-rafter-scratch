import subprocess, sys, os

def run(cmd):
    print("$", cmd)
    p = subprocess.Popen(cmd, shell=True)
    p.communicate()
    return p.returncode

if __name__ == "__main__":
    # run go tests for the repository
    # Using ./... to cover all packages
    code = run("go test ./...")
    sys.exit(code)
