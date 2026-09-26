import subprocess, sys

# Run only the relevant tests for QR feature
cmd = ["yarn", "test", "--silent", "--", "-i", 
       "test/components/views/settings/tabs/user/SessionManagerTab-test.tsx",
       "test/components/views/settings/tabs/user/SecurityUserSettingsTab-test.tsx",
       "test/components/views/settings/devices/LoginWithQRSection-test.tsx",
]
print("Running:", " ".join(cmd))
try:
    res = subprocess.run(cmd, cwd="/app", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(res.stdout)
    sys.exit(res.returncode)
except FileNotFoundError as e:
    print("Failed to run yarn/jest:", e)
    sys.exit(1)
