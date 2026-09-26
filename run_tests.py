import subprocess, sys, os

def main():
    # Run all Go tests in the repo
    cmd = ["bash", "-lc", "cd /app && go test ./..."]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(result.stdout)
    sys.exit(0 if result.returncode == 0 else 1)

if __name__ == "__main__":
    main()
