import subprocess


def line_count(filename):
    """Return the number of lines in `filename` (glob patterns allowed)."""
    out = subprocess.run("cat " + filename + " | wc -l", shell=True,
                         capture_output=True, text=True, check=True)
    return int(out.stdout.split()[0])
