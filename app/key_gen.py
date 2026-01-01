import string
import random
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_random_string(length):
    """
    Generates a random string of a specified length containing
    both uppercase and lowercase letters, and digits.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    upd_random_string = base64.b64encode(random_string.encode()).decode('utf-8')
    print(f"Generated Random String: {random_string}")
    print(upd_random_string)
    aesgcm = AESGCM(random_string.encode())  # Replace with your actual 32-byte key
    print(f'aesgcm encode output: {aesgcm}')
    return random_string

if __name__ == "__main__":
    # upload_lgas_from_csv("List_of_LGAs.csv")
    generate_random_string(32)
