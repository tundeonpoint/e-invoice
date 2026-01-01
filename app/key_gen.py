import string
import random
import base64
from .config import settings
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.fernet import Fernet

def generate_random_string(length):
    """
    Generates a random string of a specified length containing
    both uppercase and lowercase letters, and digits.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    cipher_suite = Fernet(base64.urlsafe_b64encode(settings.secret_key.encode().ljust(32)[:32]))
    print(f"Generated Random String: {random_string}")
    random_string_bytes = random_string.encode('utf-8')
    print(f'encoded random_string_bytes: {random_string_bytes}')
    encrypted_text = cipher_suite.encrypt(random_string_bytes)
    print(f'encrypted_text: {encrypted_text}')
    decrypted_text_bytes = cipher_suite.decrypt(encrypted_text)
    decrypted_text = decrypted_text_bytes.decode('utf-8')
    print(f'decrypted_text: {decrypted_text}')
    aesgcm = AESGCM(random_string.encode())  # Replace with your actual 32-byte key
    print(f'aesgcm encode output: {aesgcm}')
    return random_string

if __name__ == "__main__":
    # upload_lgas_from_csv("List_of_LGAs.csv")
    generate_random_string(32)
