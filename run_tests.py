import subprocess, sys, os

def main():
    # Ensure we're in /app
    os.chdir(os.path.dirname(__file__))
    cmd = ["go", "test", "./..."]
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(res.stdout)
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
