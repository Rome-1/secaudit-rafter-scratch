# Reproduce and verify behavior of oval.major for empty input
# This script simulates the previous and current logic of oval.major


def major_old(version: str) -> str:
    ss = version.split(":", 1)
    if len(ss) == 1:
        ver = ss[0]
    else:
        ver = ss[1]
    # Old behavior slices up to the first '.' without checks
    idx = ver.index(".")  # ValueError if '.' not present; would panic in Go
    return ver[:idx]


def major_new(version: str) -> str:
    if version == "":
        return ""
    ss = version.split(":", 1)
    ver = ss[0] if len(ss) == 1 else ss[1]
    if ver == "":
        return ""
    idx = ver.find(".")
    return ver[:idx] if idx >= 0 else ver


def try_old():
    try:
        print("major_old(\"\") ->", major_old(""))
        return False
    except Exception as e:
        print("Reproduced error in old behavior: calling major(\"\") raises:", type(e).__name__, str(e))
        return True


def verify_new():
    cases = [
        ("", ""),
        ("4.1", "4"),
        ("0:4.1", "4"),
        ("0:", ""),
    ]
    ok = True
    for s, exp in cases:
        got = major_new(s)
        print(f"major_new({s!r}) -> {got!r}")
        if got != exp:
            print("Mismatch:", s, "expected", exp, "got", got)
            ok = False
    return ok


if __name__ == "__main__":
    print("[1] Reproducing the old bug (should raise):")
    old_err = try_old()
    print("\n[2] Verifying the fixed behavior (should pass):")
    new_ok = verify_new()
    if old_err and new_ok:
        print("\nResult: Reproduction succeeded and fix verified.")
    else:
        raise SystemExit(1)
