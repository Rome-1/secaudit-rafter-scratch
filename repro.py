import os, subprocess
os.chdir('/app')
print('go test ./...')
proc = subprocess.run(['bash','-lc','go test ./...'], text=True)
print(proc.returncode)
