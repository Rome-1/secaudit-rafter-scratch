import subprocess


def line_count(filename):
    """Return the number of lines in `filename`."""
    out = subprocess.run(["wc", "-l", filename], capture_output=True, text=True, check=True)
    return int(out.stdout.split()[0])
