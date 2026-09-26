import glob
import subprocess


def line_count(filename):
    """Return the number of lines in `filename` (glob patterns allowed)."""
    total = 0
    for name in sorted(glob.glob(filename)) or [filename]:
        out = subprocess.run(["wc", "-l", name], capture_output=True, text=True, check=True)
        total += int(out.stdout.split()[0])
    return total
