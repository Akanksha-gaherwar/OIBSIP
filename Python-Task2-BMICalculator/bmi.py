# BMI Calculator

def get_number(message):
    while True:
        try:
            value = float(input(message))
            if value <= 0:
                print("Please enter a positive number.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

weight = get_number("Enter your weight in kg: ")
height = get_number("Enter your height in meters: ")

bmi = weight / (height ** 2)
print(f"Your BMI is {bmi:.2f}")
print(f"Category: {get_category(bmi)}")