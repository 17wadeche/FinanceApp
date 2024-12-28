import bcrypt

def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode(), bcrypt.gensalt()).decode()

# Example usage:
hashed_pwd = hash_password("your_password_here")
print(hashed_pwd)