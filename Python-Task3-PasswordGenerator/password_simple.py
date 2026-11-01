# Random Password Generator
import random
import string

def get_length():
    while True:
        try:
            length = int(input("Enter password length (minimum 8): "))
            if length < 8:
                print("Length must be at least 8.")
            else:
                return length
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def ask_yes_no(question):
    while True:
        answer = input(question + " (y/n): ").lower()
        if answer in ("y", "n"):
            return answer == "y"
        print("Please type y or n.")
        
def get_character_types():
    while True:
        chars = ""
        count = 0
        if ask_yes_no("Include uppercase letters?"):
            chars += string.ascii_uppercase
            count += 1
        if ask_yes_no("Include lowercase letters?"):
            chars += string.ascii_lowercase
            count += 1
        if ask_yes_no("Include numbers?"):
            chars += string.digits
            count += 1
        if ask_yes_no("Include symbols?"):
            chars += string.punctuation
            count += 1
        if count >= 2:
            return chars
        print("Please select at least 2 character types.\n")

def generate_password(length, chars):
    password = ""
    for _ in range(length):
        password += random.choice(chars)
    return password


print("=== Random Password Generator ===")
while True:
    length = get_length()
    chars = get_character_types()
    print("Your password:", generate_password(length, chars))
    if not ask_yes_no("Generate another password?"):
        print("Goodbye!")
        break