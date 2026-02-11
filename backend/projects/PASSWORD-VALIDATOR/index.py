# Password Validator
# Define a variable with a predefined password (e.g., "secure123"). 
# Ask the user to input a password. Print "Access granted" if the input matches 
# the predefined password, otherwise print "Access denied".

predefined_password = "secure123"
user_password = input("Enter your password: ")

if user_password == predefined_password:
    print("Access granted")
else:
    print("Access denied")
