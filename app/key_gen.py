import string
import random

def generate_random_string(length):
    """
    Generates a random string of a specified length containing
    both uppercase and lowercase letters, and digits.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    print(random_string)
    return random_string

if __name__ == "__main__":
    # upload_lgas_from_csv("List_of_LGAs.csv")
    generate_random_string(60)
