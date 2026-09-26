import hashlib

# Simulate old Go validateCredentials behavior (before fix)
def old_validate_credentials(user_password: str, plain_pass: str, token: str, salt: str, jwt: str) -> bool:
    valid = False
    if jwt:
        # Simulate failure to verify jwt; in old code, if jwt invalid, valid stays False
        valid = False
    elif plain_pass:
        if plain_pass.startswith("enc:"):
            try:
                plain_pass = bytes.fromhex(plain_pass[4:]).decode()
            except Exception:
                pass
        valid = (plain_pass == user_password)
    elif token:
        # BUG: if salt is missing, this still uses md5(password + "")
        t = hashlib.md5((user_password + (salt or "")).encode()).hexdigest()
        valid = (t == token)
    return valid

# Simulate new Go validateCredentials behavior (after fix)
def new_validate_credentials(user_password: str, plain_pass: str, token: str, salt: str, jwt: str) -> bool:
    # user must exist (simulated by ensuring user_password is not None)
    if user_password is None:
        return False
    valid = False
    if jwt:
        valid = False
    elif plain_pass:
        if plain_pass.startswith("enc:"):
            try:
                plain_pass = bytes.fromhex(plain_pass[4:]).decode()
            except Exception:
                pass
        valid = (plain_pass == user_password)
    elif token:
        # FIX: require non-empty salt for token-based auth
        if not salt:
            valid = False
        else:
            t = hashlib.md5((user_password + salt).encode()).hexdigest()
            valid = (t == token)
    return valid


def demo():
    user_password = "wordpass"
    salt = "retnlmjetrymazgkt"
    token_with_salt = hashlib.md5((user_password + salt).encode()).hexdigest()
    token_without_salt = hashlib.md5((user_password).encode()).hexdigest()

    print("Valid token with salt:")
    print("old:", old_validate_credentials(user_password, "", token_with_salt, salt, ""))
    print("new:", new_validate_credentials(user_password, "", token_with_salt, salt, ""))

    print("\nBypass attempt: provide token md5(password) but omit salt:")
    print("old (BUG):", old_validate_credentials(user_password, "", token_without_salt, "", ""))
    print("new (FIXED):", new_validate_credentials(user_password, "", token_without_salt, "", ""))


if __name__ == "__main__":
    demo()
