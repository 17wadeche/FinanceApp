import secrets

def generate_cookie_key(length=32):
    """
    Generates a secure random hexadecimal string.

    Args:
        length (int): The number of bytes to generate. The final string will be twice this length
                     because each byte is represented by two hexadecimal characters.

    Returns:
        str: A secure random hexadecimal string.
    """
    return secrets.token_hex(length)

if __name__ == "__main__":
    print("Your secure COOKIE_KEY is:")
    print(generate_cookie_key())
