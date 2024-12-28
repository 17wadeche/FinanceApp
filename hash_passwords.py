# hash_passwords.py

import bcrypt

def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode(), bcrypt.gensalt()).decode()

# Example usage:
if __name__ == "__main__":
    users = {
        "johndoe": "password123",
        "janedoe": "securepassword"
    }
    
    for username, password in users.items():
        hashed = hash_password(password)
        print(f"{username}: {hashed}")
