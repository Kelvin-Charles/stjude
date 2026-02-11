from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, Project, ProjectProgress, UserRole, ProjectStep, ProjectStepQuestion, ProjectSubmission
from routes import api
import os
import json

app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})  # Enable CORS for React frontend

# Serve static files from the uploads directory
from flask import send_from_directory
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(basedir, 'uploads'), filename)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "stjude.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask backend is running'
    }), 200

@app.route('/api/debug/projects', methods=['GET'])
def debug_projects():
    """Debug endpoint to list all projects"""
    projects = Project.query.all()
    return jsonify({
        'total': len(projects),
        'projects': [{
            'id': p.id,
            'name': p.name,
            'is_active': p.is_active,
            'steps_count': len(p.steps)
        } for p in projects]
    }), 200


def seed_positive_negative_zero(project):
    """Seed steps and questions for Positive, Negative, or Zero challenge"""
    full_code = (
        "# Positive, Negative, or Zero\n"
        "number = int(input(\"Enter a number: \"))\n\n"
        "if number > 0:\n"
        "    print(\"Positive\")\n"
        "elif number < 0:\n"
        "    print(\"Negative\")\n"
        "else:\n"
        "    print(\"Zero\")"
    )
    
    step1_code = json.dumps([{
        "title": "Input and Condition Check",
        "code": "number = int(input(\"Enter a number: \"))\n\nif number > 0:\n    print(\"Positive\")",
        "explanation": "Get user input and check if the number is greater than 0 (positive)."
    }])
    
    step1 = ProjectStep(
        project_id=project.id,
        order_index=1,
        title="Step 1: Getting Input and Checking for Positive",
        content=(
            "First, we need to get a number from the user using input(). We convert it to an integer "
            "using int(). Then we check if the number is greater than 0 using the > operator. "
            "If it is, we print 'Positive'."
        ),
        code_snippet=step1_code,
        full_code=full_code,
        is_released=True
    )
    db.session.add(step1)
    db.session.flush()
    
    questions = [
        ("What does int(input()) do?", "Gets text from user", "Gets a number from user and converts it to integer", "Prints a number", "Nothing", "B", 5),
        ("What operator checks if a number is greater than 0?", "==", ">", "<", ">=", "B", 5),
        ("What will be printed if the user enters 5?", "Negative", "Zero", "Positive", "Nothing", "C", 5),
        ("Why do we use int() with input()?", "To print the number", "To convert string input to integer", "To check if it's positive", "To store it", "B", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions:
        db.session.add(ProjectStepQuestion(step_id=step1.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))
    
    step2_code = json.dumps([{
        "title": "Complete if-elif-else Structure",
        "code": full_code,
        "explanation": "The complete program uses if, elif, and else to handle all three cases: positive, negative, and zero."
    }])
    
    step2 = ProjectStep(
        project_id=project.id,
        order_index=2,
        title="Step 2: Handling All Cases with if-elif-else",
        content=(
            "We use elif (else if) to check if the number is less than 0 (negative). "
            "The else clause handles the case when the number is exactly 0. "
            "This ensures we cover all possible cases: positive, negative, or zero."
        ),
        code_snippet=step2_code,
        full_code=full_code,
        is_released=True
    )
    db.session.add(step2)
    db.session.flush()
    
    questions2 = [
        ("What does elif mean?", "Else if - another condition to check", "End if", "Error if", "Nothing", "A", 5),
        ("What happens if number is 0?", "Prints 'Positive'", "Prints 'Negative'", "Prints 'Zero'", "Nothing", "C", 5),
        ("What happens if number is -5?", "Prints 'Positive'", "Prints 'Negative'", "Prints 'Zero'", "Error", "B", 5),
        ("Why do we need else in this program?", "It's optional", "To handle the zero case", "To print an error", "To stop the program", "B", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions2:
        db.session.add(ProjectStepQuestion(step_id=step2.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))

def seed_even_or_odd(project):
    """Seed steps and questions for Even or Odd challenge"""
    full_code = (
        "# Even or Odd\n"
        "number = int(input(\"Enter an integer: \"))\n\n"
        "if number % 2 == 0:\n"
        "    print(\"Even\")\n"
        "else:\n"
        "    print(\"Odd\")"
    )
    
    step1 = ProjectStep(
        project_id=project.id,
        order_index=1,
        title="Step 1: Understanding the Modulo Operator",
        content=(
            "The modulo operator (%) gives us the remainder when dividing one number by another. "
            "For example, 5 % 2 = 1 (5 divided by 2 leaves remainder 1), and 4 % 2 = 0 (4 divided by 2 leaves no remainder). "
            "If a number % 2 equals 0, the number is even. Otherwise, it's odd."
        ),
        code_snippet=json.dumps([{"title": "Modulo Operator", "code": "number % 2 == 0", "explanation": "Checks if number divided by 2 has no remainder (even number)"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step1)
    db.session.flush()
    
    questions = [
        ("What does the % operator do?", "Divides numbers", "Gives the remainder after division", "Multiplies numbers", "Adds numbers", "B", 10),
        ("What is 8 % 2?", "4", "0", "2", "1", "B", 5),
        ("What is 7 % 2?", "3", "0", "2", "1", "D", 5),
        ("If number % 2 == 0, the number is:", "Odd", "Even", "Zero", "Negative", "B", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions:
        db.session.add(ProjectStepQuestion(step_id=step1.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))
    
    step2 = ProjectStep(
        project_id=project.id,
        order_index=2,
        title="Step 2: Complete Program",
        content=(
            "The complete program gets a number from the user, checks if it's divisible by 2 using the modulo operator, "
            "and prints 'Even' or 'Odd' accordingly."
        ),
        code_snippet=json.dumps([{"title": "Complete Program", "code": full_code, "explanation": "Full program to check if a number is even or odd"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step2)
    db.session.flush()
    
    questions2 = [
        ("What will be printed if user enters 10?", "Odd", "Even", "Zero", "Error", "B", 5),
        ("What will be printed if user enters 15?", "Odd", "Even", "Zero", "Error", "A", 5),
        ("Why do we use == instead of =?", "== compares values, = assigns values", "They're the same", "== is faster", "== is shorter", "A", 10),
    ]
    for prompt, a, b, c, d, correct, pts in questions2:
        db.session.add(ProjectStepQuestion(step_id=step2.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))

def seed_voting_eligibility(project):
    """Seed steps and questions for Voting Eligibility challenge"""
    full_code = (
        "# Voting Eligibility\n"
        "age = int(input(\"Enter your age: \"))\n\n"
        "if age >= 18:\n"
        "    print(\"You are old enough to vote!\")\n"
        "else:\n"
        "    print(\"You are not old enough to vote.\")"
    )
    
    step1 = ProjectStep(
        project_id=project.id,
        order_index=1,
        title="Step 1: Getting Age and Using Comparison",
        content=(
            "We get the user's age as input and convert it to an integer. "
            "Then we use the >= operator to check if the age is greater than or equal to 18. "
            "The >= operator checks if the left value is greater than or equal to the right value."
        ),
        code_snippet=json.dumps([{"title": "Age Check", "code": "age = int(input(\"Enter your age: \"))\n\nif age >= 18:", "explanation": "Get age and check if it's 18 or older"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step1)
    db.session.flush()
    
    questions = [
        ("What does >= mean?", "Greater than", "Less than", "Greater than or equal to", "Equal to", "C", 5),
        ("What is the minimum voting age in this program?", "16", "17", "18", "19", "C", 5),
        ("If age is 18, what happens?", "Prints 'not old enough'", "Prints 'old enough to vote!'", "Error", "Nothing", "B", 5),
        ("If age is 17, what happens?", "Prints 'old enough to vote!'", "Prints 'not old enough to vote.'", "Error", "Nothing", "B", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions:
        db.session.add(ProjectStepQuestion(step_id=step1.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))

def seed_password_validator(project):
    """Seed steps and questions for Password Validator challenge"""
    full_code = (
        "# Password Validator\n"
        "predefined_password = \"secure123\"\n"
        "user_password = input(\"Enter your password: \")\n\n"
        "if user_password == predefined_password:\n"
        "    print(\"Access granted\")\n"
        "else:\n"
        "    print(\"Access denied\")"
    )
    
    step1 = ProjectStep(
        project_id=project.id,
        order_index=1,
        title="Step 1: Storing and Getting Passwords",
        content=(
            "We define a variable 'predefined_password' with the correct password. "
            "Then we ask the user to enter their password using input(). "
            "We'll compare these two values to see if they match."
        ),
        code_snippet=json.dumps([{"title": "Password Variables", "code": "predefined_password = \"secure123\"\nuser_password = input(\"Enter your password: \")", "explanation": "Store the correct password and get user's input"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step1)
    db.session.flush()
    
    questions = [
        ("What is stored in predefined_password?", "User's input", "The correct password 'secure123'", "A random password", "Nothing", "B", 5),
        ("What does input() do?", "Prints text", "Gets text from the user", "Checks password", "Nothing", "B", 5),
        ("Why do we store the password in a variable?", "To compare it later", "To print it", "To hide it", "It's not necessary", "A", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions:
        db.session.add(ProjectStepQuestion(step_id=step1.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))
    
    step2 = ProjectStep(
        project_id=project.id,
        order_index=2,
        title="Step 2: Comparing Passwords",
        content=(
            "We use == to compare the user's password with the predefined password. "
            "If they match exactly, we print 'Access granted'. Otherwise, we print 'Access denied'. "
            "String comparison in Python is case-sensitive, so 'Secure123' would not match 'secure123'."
        ),
        code_snippet=json.dumps([{"title": "Password Comparison", "code": "if user_password == predefined_password:\n    print(\"Access granted\")\nelse:\n    print(\"Access denied\")", "explanation": "Compare passwords and grant or deny access"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step2)
    db.session.flush()
    
    questions2 = [
        ("What operator compares two values for equality?", "=", "==", "!=", ">", "B", 5),
        ("If user enters 'secure123', what is printed?", "Access granted", "Access denied", "Error", "Nothing", "A", 5),
        ("If user enters 'Secure123', what is printed?", "Access granted", "Access denied", "Error", "Nothing", "B", 10),
        ("Why is 'Secure123' different from 'secure123'?", "They're the same", "Python string comparison is case-sensitive", "One has numbers", "They're different lengths", "B", 10),
    ]
    for prompt, a, b, c, d, correct, pts in questions2:
        db.session.add(ProjectStepQuestion(step_id=step2.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))

def seed_print_sequence(project):
    """Seed steps and questions for Print Sequence 1 to 10 challenge"""
    full_code = (
        "# Print a sequence of numbers\n"
        "for number in range(1, 11):\n"
        "    print(number)"
    )
    
    step1 = ProjectStep(
        project_id=project.id,
        order_index=1,
        title="Step 1: Understanding range() Function",
        content=(
            "The range() function generates a sequence of numbers. range(1, 11) creates numbers from 1 to 10. "
            "Note that range(1, 11) includes 1 but excludes 11 (it goes up to but doesn't include the end number). "
            "This is why we use 11 to get numbers 1 through 10."
        ),
        code_snippet=json.dumps([{"title": "Range Function", "code": "range(1, 11)", "explanation": "Creates numbers from 1 to 10 (1 inclusive, 11 exclusive)"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step1)
    db.session.flush()
    
    questions = [
        ("What does range(1, 11) create?", "Numbers 1 to 11", "Numbers 1 to 10", "Numbers 0 to 10", "Numbers 0 to 11", "B", 10),
        ("Why do we use 11 instead of 10?", "Because range excludes the end number", "It's a mistake", "To include 11", "To start from 0", "A", 10),
        ("What is the first number in range(1, 11)?", "0", "1", "10", "11", "B", 5),
        ("What is the last number in range(1, 11)?", "9", "10", "11", "12", "B", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions:
        db.session.add(ProjectStepQuestion(step_id=step1.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))
    
    step2 = ProjectStep(
        project_id=project.id,
        order_index=2,
        title="Step 2: Using for Loop with range()",
        content=(
            "The for loop iterates through each number in the range. For each iteration, "
            "the variable 'number' takes the next value from the range, and we print it. "
            "This continues until all numbers in the range have been processed."
        ),
        code_snippet=json.dumps([{"title": "For Loop", "code": full_code, "explanation": "Loop through range and print each number"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step2)
    db.session.flush()
    
    questions2 = [
        ("How many times does the loop execute?", "9 times", "10 times", "11 times", "12 times", "B", 5),
        ("What does 'for number in range(1, 11)' do?", "Prints once", "Loops 10 times, printing each number", "Prints all at once", "Nothing", "B", 10),
        ("What will be printed first?", "0", "1", "10", "11", "B", 5),
        ("What will be printed last?", "9", "10", "11", "12", "B", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions2:
        db.session.add(ProjectStepQuestion(step_id=step2.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))

def seed_count_even_odd(project):
    """Seed steps and questions for Count Even and Odd challenge"""
    full_code = (
        "# Count even and odd numbers\n"
        "numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n"
        "even_count = 0\n"
        "odd_count = 0\n\n"
        "for number in numbers:\n"
        "    if number % 2 == 0:\n"
        "        even_count += 1\n"
        "    else:\n"
        "        odd_count += 1\n\n"
        "print(f\"Even numbers: {even_count}\")\n"
        "print(f\"Odd numbers: {odd_count}\")"
    )
    
    step1 = ProjectStep(
        project_id=project.id,
        order_index=1,
        title="Step 1: Setting Up Counters and List",
        content=(
            "We create a list of numbers and initialize two counters: even_count and odd_count, both starting at 0. "
            "These counters will keep track of how many even and odd numbers we find as we loop through the list."
        ),
        code_snippet=json.dumps([{"title": "Initialization", "code": "numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\neven_count = 0\nodd_count = 0", "explanation": "Create a list of numbers and initialize counters"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step1)
    db.session.flush()
    
    questions = [
        ("What is a list in Python?", "A single number", "A collection of items in square brackets", "A string", "A function", "B", 5),
        ("Why do we start even_count and odd_count at 0?", "To count from zero", "To initialize them before counting", "It's required", "No reason", "B", 5),
        ("How many numbers are in the list?", "8", "9", "10", "11", "C", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions:
        db.session.add(ProjectStepQuestion(step_id=step1.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))
    
    step2 = ProjectStep(
        project_id=project.id,
        order_index=2,
        title="Step 2: Looping and Counting",
        content=(
            "We loop through each number in the list. For each number, we check if it's even using number % 2 == 0. "
            "If it is even, we increment even_count by 1 using even_count += 1. "
            "Otherwise, we increment odd_count. After checking all numbers, we print the results."
        ),
        code_snippet=json.dumps([{"title": "Loop and Count", "code": "for number in numbers:\n    if number % 2 == 0:\n        even_count += 1\n    else:\n        odd_count += 1", "explanation": "Loop through numbers and count even/odd"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step2)
    db.session.flush()
    
    questions2 = [
        ("What does += 1 do?", "Adds 1 to the variable", "Subtracts 1", "Multiplies by 1", "Divides by 1", "A", 5),
        ("How many even numbers are in [1,2,3,4,5,6,7,8,9,10]?", "4", "5", "6", "7", "B", 5),
        ("How many odd numbers are in [1,2,3,4,5,6,7,8,9,10]?", "4", "5", "6", "7", "B", 5),
        ("What does number % 2 == 0 check?", "If number is odd", "If number is even", "If number is zero", "If number is positive", "B", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions2:
        db.session.add(ProjectStepQuestion(step_id=step2.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))

def seed_sum_of_range(project):
    """Seed steps and questions for Sum of a Range challenge"""
    full_code = (
        "# Sum of a range\n"
        "n = int(input(\"Enter a number: \"))\n"
        "sum = 0\n"
        "counter = 1\n\n"
        "while counter <= n:\n"
        "    sum += counter\n"
        "    counter += 1\n\n"
        "print(f\"Sum of numbers from 1 to {n} is: {sum}\")"
    )
    
    step1 = ProjectStep(
        project_id=project.id,
        order_index=1,
        title="Step 1: Understanding While Loops",
        content=(
            "A while loop continues executing as long as a condition is true. "
            "In this program, we use 'while counter <= n' which means the loop will continue "
            "as long as counter is less than or equal to n. We start with counter = 1 and sum = 0."
        ),
        code_snippet=json.dumps([{"title": "While Loop Setup", "code": "sum = 0\ncounter = 1\n\nwhile counter <= n:", "explanation": "Initialize sum and counter, then start the while loop"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step1)
    db.session.flush()
    
    questions = [
        ("What does a while loop do?", "Runs once", "Runs as long as condition is true", "Runs forever", "Nothing", "B", 10),
        ("What is the initial value of sum?", "1", "0", "n", "counter", "B", 5),
        ("What is the initial value of counter?", "0", "1", "n", "sum", "B", 5),
        ("When does 'while counter <= n' stop?", "When counter > n", "When counter == n", "When counter < n", "Never", "A", 10),
    ]
    for prompt, a, b, c, d, correct, pts in questions:
        db.session.add(ProjectStepQuestion(step_id=step1.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))
    
    step2 = ProjectStep(
        project_id=project.id,
        order_index=2,
        title="Step 2: Accumulating the Sum",
        content=(
            "Inside the loop, we add the current counter value to sum using sum += counter. "
            "Then we increment counter by 1. This continues until counter exceeds n. "
            "For example, if n=5, we add 1+2+3+4+5 = 15."
        ),
        code_snippet=json.dumps([{"title": "Accumulating Sum", "code": "while counter <= n:\n    sum += counter\n    counter += 1", "explanation": "Add counter to sum, then increment counter"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step2)
    db.session.flush()
    
    questions2 = [
        ("What does sum += counter do?", "Adds counter to sum", "Subtracts counter from sum", "Multiplies sum by counter", "Divides sum by counter", "A", 5),
        ("What does counter += 1 do?", "Adds 1 to counter", "Subtracts 1 from counter", "Multiplies counter by 1", "Nothing", "A", 5),
        ("If n=3, what is the final sum?", "3", "6", "9", "12", "B", 10),
        ("Why do we increment counter?", "To stop the loop eventually", "To add to sum", "Both A and B", "No reason", "C", 10),
    ]
    for prompt, a, b, c, d, correct, pts in questions2:
        db.session.add(ProjectStepQuestion(step_id=step2.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))

def seed_reverse_word(project):
    """Seed steps and questions for Reverse a Word challenge"""
    full_code = (
        "# Reverse a word\n"
        "word = input(\"Enter a word: \")\n"
        "reversed_word = \"\"\n\n"
        "for char in word:\n"
        "    reversed_word = char + reversed_word\n\n"
        "print(f\"Reversed word: {reversed_word}\")"
    )
    
    step1 = ProjectStep(
        project_id=project.id,
        order_index=1,
        title="Step 1: Understanding String Iteration",
        content=(
            "We get a word from the user and create an empty string called reversed_word. "
            "Then we use a for loop to iterate through each character in the word. "
            "In Python, you can loop through a string character by character."
        ),
        code_snippet=json.dumps([{"title": "String Iteration", "code": "word = input(\"Enter a word: \")\nreversed_word = \"\"\n\nfor char in word:", "explanation": "Get word, create empty string, and loop through each character"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step1)
    db.session.flush()
    
    questions = [
        ("What does 'for char in word' do?", "Loops through each character in the word", "Prints the word", "Reverses the word", "Nothing", "A", 10),
        ("What is the initial value of reversed_word?", "The original word", "An empty string", "The first character", "Nothing", "B", 5),
        ("If word is 'hello', how many times does the loop run?", "4", "5", "6", "1", "B", 5),
    ]
    for prompt, a, b, c, d, correct, pts in questions:
        db.session.add(ProjectStepQuestion(step_id=step1.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))
    
    step2 = ProjectStep(
        project_id=project.id,
        order_index=2,
        title="Step 2: Building the Reversed Word",
        content=(
            "The key is 'reversed_word = char + reversed_word'. We add each character to the FRONT of reversed_word, "
            "not the back. So if word is 'hello', we process: h, then eh, then leh, then oleh, then olleh. "
            "This builds the word in reverse order."
        ),
        code_snippet=json.dumps([{"title": "Reversing Logic", "code": "for char in word:\n    reversed_word = char + reversed_word", "explanation": "Add each character to the front of reversed_word"}]),
        full_code=full_code,
        is_released=True
    )
    db.session.add(step2)
    db.session.flush()
    
    questions2 = [
        ("Why do we use 'char + reversed_word' instead of 'reversed_word + char'?", "To build the word in reverse order", "It's shorter", "It's faster", "No reason", "A", 10),
        ("If word is 'cat', what is reversed_word after the first iteration?", "'c'", "'tac'", "'cat'", "'a'", "A", 10),
        ("If word is 'cat', what is the final reversed_word?", "'cat'", "'tac'", "'c'", "'t'", "B", 10),
        ("What happens if we use 'reversed_word + char' instead?", "Word stays the same", "Word is reversed", "Error occurs", "Nothing prints", "A", 10),
    ]
    for prompt, a, b, c, d, correct, pts in questions2:
        db.session.add(ProjectStepQuestion(step_id=step2.id, prompt=prompt, option_a=a, option_b=b, option_c=c, option_d=d, correct_option=correct, points=pts))

def migrate_db():
    """Migrate database schema - add missing columns"""
    with app.app_context():
        try:
            from sqlalchemy import text, inspect
            inspector = inspect(db.engine)
            
            # Check if project_submissions table exists and has submission_type column
            if 'project_submissions' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('project_submissions')]
                if 'submission_type' not in columns:
                    print("Adding submission_type column to project_submissions table...")
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(text("ALTER TABLE project_submissions ADD COLUMN submission_type VARCHAR(50) DEFAULT 'project'"))
                            conn.commit()
                        print("✓ Added submission_type column")
                    except Exception as e:
                        print(f"Error adding submission_type column: {e}")
        except Exception as e:
            print(f"Migration check error (may be normal on first run): {e}")

def init_db():
    """Initialize database tables and default data"""
    with app.app_context():
        # Run migrations first
        migrate_db()
        # Then create all tables (for new tables)
        db.create_all()
        
        # Create default manager if doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@stjude.org',
                full_name='System Administrator',
                role=UserRole.MANAGER
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")
        
        # Initialize projects from file system
        projects_dir = os.path.join(os.path.dirname(__file__), 'projects')
        if os.path.exists(projects_dir):
            for item in os.listdir(projects_dir):
                project_path = os.path.join(projects_dir, item)
                if os.path.isdir(project_path):
                    # Check if project already exists
                    if not Project.query.filter_by(name=item).first():
                        project = Project(
                            name=item,
                            project_path=item,
                            description=f"Project: {item}",
                            difficulty_level="beginner"
                        )
                        db.session.add(project)
                        db.session.flush()

                        # Seed comprehensive steps for the sample project "MULTIPLICATION TABLE"
                        if item.lower() == "multiplication table":
                            # Step 1: Understanding the Header
                            step1_code_snippets = json.dumps([
                                {
                                    "title": "Header Code",
                                    "code": "print(\"Multiplication Table\")\nprint(\"    |     0   1   2   3   4   5   6   7   8   9  10  11  12\")\nprint(\"----+------------------------------------------------------\")",
                                    "explanation": "This code prints the title, header row with column numbers, and a separator line."
                                }
                            ])
                            step1_full_code = (
                                "print(\"Multiplication Table\")\n"
                                "print(\"    |     0   1   2   3   4   5   6   7   8   9  10  11  12\")\n"
                                "print(\"----+------------------------------------------------------\")\n\n"
                                "for number1 in range(0, 13):\n"
                                "    print(str(number1).rjust(2), end=\" \")\n"
                                "    print(\" | \", end=\" \")\n\n"
                                "    for number2 in range(0, 13):\n"
                                "        print(str(number1 * number2).rjust(3), end=\" \")\n\n"
                                "    print()"
                            )
                            step1 = ProjectStep(
                                project_id=project.id,
                                order_index=1,
                                title="Step 1: Understanding the Header and Table Structure",
                                content=(
                                    "Let's start by understanding how the multiplication table is structured.\n\n"
                                    "The program first prints a header row that shows the column numbers (0 to 12). "
                                    "Then it prints a separator line, and finally the multiplication table itself.\n\n"
                                    "Look at the code below. The first print statement creates the header, and the second "
                                    "creates a visual separator using dashes and a plus sign."
                                ),
                                code_snippet=step1_code_snippets,
                                full_code=step1_full_code,
                                is_released=True
                            )
                            db.session.add(step1)
                            db.session.flush()

                            q1_1 = ProjectStepQuestion(
                                step_id=step1.id,
                                prompt="What does the first print statement display?",
                                option_a="The multiplication table results",
                                option_b="The header row with column numbers (0-12)",
                                option_c="A separator line",
                                option_d="Nothing, it's just a comment",
                                correct_option="B",
                                points=5,
                            )
                            db.session.add(q1_1)

                            q1_2 = ProjectStepQuestion(
                                step_id=step1.id,
                                prompt="What is the purpose of the separator line (----+------)?",
                                option_a="To make the table look prettier",
                                option_b="To visually separate the header from the data rows",
                                option_c="To calculate the results",
                                option_d="To store the data",
                                correct_option="B",
                                points=5,
                            )
                            db.session.add(q1_2)

                            q1_3 = ProjectStepQuestion(
                                step_id=step1.id,
                                prompt="How many columns are displayed in the header?",
                                option_a="10 columns",
                                option_b="12 columns",
                                option_c="13 columns (0-12)",
                                option_d="14 columns",
                                correct_option="C",
                                points=5,
                            )
                            db.session.add(q1_3)

                            q1_4 = ProjectStepQuestion(
                                step_id=step1.id,
                                prompt="What does the pipe symbol (|) represent in the header?",
                                option_a="A mathematical operation",
                                option_b="A visual separator between row numbers and data",
                                option_c="A programming command",
                                option_d="An error in the code",
                                correct_option="B",
                                points=5,
                            )
                            db.session.add(q1_4)

                            q1_5 = ProjectStepQuestion(
                                step_id=step1.id,
                                prompt="What will be printed first when the program runs?",
                                option_a="The multiplication results",
                                option_b="The text 'Multiplication Table'",
                                option_c="The separator line",
                                option_d="Nothing, the program has an error",
                                correct_option="B",
                                points=5,
                            )
                            db.session.add(q1_5)

                            q1_6 = ProjectStepQuestion(
                                step_id=step1.id,
                                prompt="Why is the header important for understanding the table?",
                                option_a="It shows what each column represents",
                                option_b="It makes the code run faster",
                                option_c="It stores the data",
                                option_d="It's not important",
                                correct_option="A",
                                points=5,
                            )
                            db.session.add(q1_6)

                            # Step 2: Understanding the Outer Loop
                            step2_code_snippets = json.dumps([
                                {
                                    "title": "Outer Loop - First Loop",
                                    "code": "for number1 in range(0, 13):\n    print(str(number1).rjust(2), end=\" \")\n    print(\" | \", end=\" \")",
                                    "explanation": "The outer loop (first loop) controls the rows. It runs 13 times (0 to 12), printing the row number for each row."
                                }
                            ])
                            step2_full_code = (
                                "print(\"Multiplication Table\")\n"
                                "print(\"    |     0   1   2   3   4   5   6   7   8   9  10  11  12\")\n"
                                "print(\"----+------------------------------------------------------\")\n\n"
                                "for number1 in range(0, 13):\n"
                                "    print(str(number1).rjust(2), end=\" \")\n"
                                "    print(\" | \", end=\" \")\n\n"
                                "    for number2 in range(0, 13):\n"
                                "        print(str(number1 * number2).rjust(3), end=\" \")\n\n"
                                "    print()"
                            )
                            step2 = ProjectStep(
                                project_id=project.id,
                                order_index=2,
                                title="Step 2: The Outer Loop - Controlling Rows",
                                content=(
                                    "Now let's understand the outer loop that controls the rows of our table.\n\n"
                                    "The outer loop uses `for number1 in range(0, 13)`. This means it will iterate "
                                    "13 times, with number1 taking values from 0 to 12 (inclusive).\n\n"
                                    "Each iteration of the outer loop represents one row in our multiplication table. "
                                    "The first thing we do in each row is print the row number (number1), which is "
                                    "right-justified using `rjust(2)` to make it align nicely."
                                ),
                                code_snippet=step2_code_snippets,
                                full_code=step2_full_code,
                                is_released=True
                            )
                            db.session.add(step2)
                            db.session.flush()

                            q2_1 = ProjectStepQuestion(
                                step_id=step2.id,
                                prompt="How many times will the outer loop execute?",
                                option_a="12 times",
                                option_b="13 times (0 to 12)",
                                option_c="14 times",
                                option_d="It depends on the input",
                                correct_option="B",
                                points=10,
                            )
                            db.session.add(q2_1)

                            q2_2 = ProjectStepQuestion(
                                step_id=step2.id,
                                prompt="What does `rjust(2)` do?",
                                option_a="Left-aligns the number",
                                option_b="Right-aligns the number in a 2-character space",
                                option_c="Centers the number",
                                option_d="Converts the number to string",
                                correct_option="B",
                                points=5,
                            )
                            db.session.add(q2_2)

                            q2_3 = ProjectStepQuestion(
                                step_id=step2.id,
                                prompt="What is the first value of number1 in the outer loop?",
                                option_a="1",
                                option_b="0",
                                option_c="13",
                                option_d="-1",
                                correct_option="B",
                                points=5,
                            )
                            db.session.add(q2_3)

                            q2_4 = ProjectStepQuestion(
                                step_id=step2.id,
                                prompt="What is the last value of number1 in the outer loop?",
                                option_a="11",
                                option_b="12",
                                option_c="13",
                                option_d="14",
                                correct_option="B",
                                points=5,
                            )
                            db.session.add(q2_4)

                            q2_5 = ProjectStepQuestion(
                                step_id=step2.id,
                                prompt="What does `end=\" \"` do in the print statement?",
                                option_a="Ends the program",
                                option_b="Prints a space instead of a newline after the output",
                                option_c="Adds a newline character",
                                option_d="Stops the loop",
                                correct_option="B",
                                points=10,
                            )
                            db.session.add(q2_5)

                            q2_6 = ProjectStepQuestion(
                                step_id=step2.id,
                                prompt="Why do we need the outer loop?",
                                option_a="To calculate the results",
                                option_b="To control which row we're printing",
                                option_c="To store the data",
                                option_d="To make the code longer",
                                correct_option="B",
                                points=10,
                            )
                            db.session.add(q2_6)

                            q2_7 = ProjectStepQuestion(
                                step_id=step2.id,
                                prompt="What happens if we change `range(0, 13)` to `range(1, 13)`?",
                                option_a="The table will show rows 1-12",
                                option_b="The table will show rows 0-11",
                                option_c="The program will crash",
                                option_d="Nothing will change",
                                correct_option="A",
                                points=10,
                            )
                            db.session.add(q2_7)

                            # Step 3: Understanding the Inner Loop
                            step3_code_snippets = json.dumps([
                                {
                                    "title": "Outer Loop (First Loop)",
                                    "code": "for number1 in range(0, 13):\n    print(str(number1).rjust(2), end=\" \")\n    print(\" | \", end=\" \")",
                                    "explanation": "The outer loop controls which row we're printing (0 to 12)."
                                },
                                {
                                    "title": "Inner Loop (Second Loop)",
                                    "code": "    for number2 in range(0, 13):\n        print(str(number1 * number2).rjust(3), end=\" \")\n\n    print()  # Move to next line",
                                    "explanation": "The inner loop (nested inside the outer loop) calculates and prints the multiplication results for each column in the current row."
                                }
                            ])
                            step3_full_code = (
                                "print(\"Multiplication Table\")\n"
                                "print(\"    |     0   1   2   3   4   5   6   7   8   9  10  11  12\")\n"
                                "print(\"----+------------------------------------------------------\")\n\n"
                                "for number1 in range(0, 13):\n"
                                "    print(str(number1).rjust(2), end=\" \")\n"
                                "    print(\" | \", end=\" \")\n\n"
                                "    for number2 in range(0, 13):\n"
                                "        print(str(number1 * number2).rjust(3), end=\" \")\n\n"
                                "    print()"
                            )
                            step3 = ProjectStep(
                                project_id=project.id,
                                order_index=3,
                                title="Step 3: The Inner Loop - Calculating and Displaying Results",
                                content=(
                                    "The inner loop is where the actual multiplication happens!\n\n"
                                    "For each row (controlled by the outer loop), the inner loop runs 13 times "
                                    "(from 0 to 12). In each iteration, it calculates `number1 * number2` and "
                                    "displays the result.\n\n"
                                    "The `end=\" \"` parameter in the print statement means we don't go to a new line "
                                    "after each number - instead, we print all numbers in the row on the same line, "
                                    "separated by spaces. After the inner loop finishes, we call `print()` with no "
                                    "arguments to move to the next line."
                                ),
                                code_snippet=step3_code_snippets,
                                full_code=step3_full_code,
                                is_released=True
                            )
                            db.session.add(step3)
                            db.session.flush()

                            q3_1 = ProjectStepQuestion(
                                step_id=step3.id,
                                prompt="What does `number1 * number2` calculate?",
                                option_a="The sum of number1 and number2",
                                option_b="The product (multiplication) of number1 and number2",
                                option_c="The difference between number1 and number2",
                                option_d="The division of number1 by number2",
                                correct_option="B",
                                points=10,
                            )
                            db.session.add(q3_1)

                            q3_2 = ProjectStepQuestion(
                                step_id=step3.id,
                                prompt="Why do we use `end=\" \"` in the inner loop's print statement?",
                                option_a="To print each number on a new line",
                                option_b="To print all numbers in a row on the same line, separated by spaces",
                                option_c="To add a newline character",
                                option_d="To stop the program",
                                correct_option="B",
                                points=10,
                            )
                            db.session.add(q3_2)

                            q3_3 = ProjectStepQuestion(
                                step_id=step3.id,
                                prompt="How many times does the inner loop execute for EACH row?",
                                option_a="12 times",
                                option_b="13 times (0 to 12)",
                                option_c="Once per row",
                                option_d="It depends on number1",
                                correct_option="B",
                                points=10,
                            )
                            db.session.add(q3_3)

                            q3_4 = ProjectStepQuestion(
                                step_id=step3.id,
                                prompt="What is the result of 5 * 7 in the table?",
                                option_a="12",
                                option_b="35",
                                option_c="57",
                                option_d="It won't be in the table",
                                correct_option="B",
                                points=5,
                            )
                            db.session.add(q3_4)

                            q3_5 = ProjectStepQuestion(
                                step_id=step3.id,
                                prompt="What does `rjust(3)` do in the inner loop?",
                                option_a="Left-aligns in 3 spaces",
                                option_b="Right-aligns in 3 spaces for consistent column width",
                                option_c="Centers in 3 spaces",
                                option_d="Converts to 3 digits",
                                correct_option="B",
                                points=5,
                            )
                            db.session.add(q3_5)

                            q3_6 = ProjectStepQuestion(
                                step_id=step3.id,
                                prompt="Why is the inner loop nested inside the outer loop?",
                                option_a="To make the code more complex",
                                option_b="To calculate all products for each row before moving to the next row",
                                option_c="To slow down the program",
                                option_d="It doesn't need to be nested",
                                correct_option="B",
                                points=10,
                            )
                            db.session.add(q3_6)

                            q3_7 = ProjectStepQuestion(
                                step_id=step3.id,
                                prompt="What happens after the inner loop finishes?",
                                option_a="The program ends",
                                option_b="We print a newline to start the next row",
                                option_c="We go back to the outer loop",
                                option_d="Both B and C",
                                correct_option="D",
                                points=10,
                            )
                            db.session.add(q3_7)

                            # Step 4: Complete Program Understanding
                            step4_code_snippets = json.dumps([
                                {
                                    "title": "Header Section",
                                    "code": "print(\"Multiplication Table\")\nprint(\"    |     0   1   2   3   4   5   6   7   8   9  10  11  12\")\nprint(\"----+------------------------------------------------------\")",
                                    "explanation": "Prints the title and header row with column numbers."
                                },
                                {
                                    "title": "Outer Loop (First Loop) - Controls Rows",
                                    "code": "for number1 in range(0, 13):\n    print(str(number1).rjust(2), end=\" \")\n    print(\" | \", end=\" \")",
                                    "explanation": "The first loop (outer loop) controls which row we're printing. It runs 13 times for rows 0-12."
                                },
                                {
                                    "title": "Inner Loop (Second Loop) - Calculates Results",
                                    "code": "    for number2 in range(0, 13):\n        print(str(number1 * number2).rjust(3), end=\" \")\n\n    print()",
                                    "explanation": "The second loop (inner loop, nested inside the first) calculates and prints the multiplication results for each column."
                                }
                            ])
                            step4_full_code = (
                                "print(\"Multiplication Table\")\n"
                                "print(\"    |     0   1   2   3   4   5   6   7   8   9  10  11  12\")\n"
                                "print(\"----+------------------------------------------------------\")\n\n"
                                "for number1 in range(0, 13):\n"
                                "    print(str(number1).rjust(2), end=\" \")\n"
                                "    print(\" | \", end=\" \")\n\n"
                                "    for number2 in range(0, 13):\n"
                                "        print(str(number1 * number2).rjust(3), end=\" \")\n\n"
                                "    print()"
                            )
                            step4 = ProjectStep(
                                project_id=project.id,
                                order_index=4,
                                title="Step 4: Putting It All Together - The Complete Program",
                                content=(
                                    "Now you understand all the pieces! Let's review the complete program:\n\n"
                                    "1. Print the header row with column numbers\n"
                                    "2. Print a separator line\n"
                                    "3. For each row (0 to 12):\n"
                                    "   - Print the row number\n"
                                    "   - Print a separator (|)\n"
                                    "   - For each column (0 to 12):\n"
                                    "     * Calculate and print the multiplication result\n"
                                    "   - Move to the next line\n\n"
                                    "This creates a beautiful multiplication table from 0×0 to 12×12!"
                                ),
                                code_snippet=step4_code_snippets,
                                full_code=step4_full_code,
                                is_released=True
                            )
                            db.session.add(step4)
                            db.session.flush()

                            q4_1 = ProjectStepQuestion(
                                step_id=step4.id,
                                prompt="What is the total number of multiplication calculations performed?",
                                option_a="12 × 12 = 144",
                                option_b="13 × 13 = 169",
                                option_c="12 × 13 = 156",
                                option_d="It depends on the input",
                                correct_option="B",
                                points=15,
                            )
                            db.session.add(q4_1)

                            q4_2 = ProjectStepQuestion(
                                step_id=step4.id,
                                prompt="What would happen if we changed `range(0, 13)` to `range(0, 5)` in both loops?",
                                option_a="The table would show 0×0 to 4×4",
                                option_b="The program would crash",
                                option_c="The table would show 0×0 to 5×5",
                                option_d="Nothing would change",
                                correct_option="A",
                                points=15,
                            )
                            db.session.add(q4_2)

                            q4_3 = ProjectStepQuestion(
                                step_id=step4.id,
                                prompt="Why is the multiplication table useful for learning programming?",
                                option_a="It teaches loops and nested loops",
                                option_b="It demonstrates string formatting with rjust()",
                                option_c="It shows how to structure output",
                                option_d="All of the above",
                                correct_option="D",
                                points=10,
                            )
                            db.session.add(q4_3)

                            q4_4 = ProjectStepQuestion(
                                step_id=step4.id,
                                prompt="What would be printed in row 3, column 4?",
                                option_a="7",
                                option_b="12",
                                option_c="34",
                                option_d="43",
                                correct_option="B",
                                points=10,
                            )
                            db.session.add(q4_4)

                            q4_5 = ProjectStepQuestion(
                                step_id=step4.id,
                                prompt="How many total print statements execute in the entire program?",
                                option_a="13",
                                option_b="169",
                                option_c="182 (1 header + 1 separator + 13 row numbers + 13 separators + 169 results)",
                                option_d="It depends",
                                correct_option="C",
                                points=15,
                            )
                            db.session.add(q4_5)

                            q4_6 = ProjectStepQuestion(
                                step_id=step4.id,
                                prompt="What is the pattern in each row of the multiplication table?",
                                option_a="Each number increases by 1",
                                option_b="Each number is the row number multiplied by the column number",
                                option_c="Random numbers",
                                option_d="All zeros",
                                correct_option="B",
                                points=10,
                            )
                            db.session.add(q4_6)

                            q4_7 = ProjectStepQuestion(
                                step_id=step4.id,
                                prompt="If we wanted a table from 0 to 20, what would we change?",
                                option_a="Change both ranges to range(0, 21)",
                                option_b="Change only the outer loop",
                                option_c="Change only the inner loop",
                                option_d="We can't change it",
                                correct_option="A",
                                points=10,
                            )
                            db.session.add(q4_7)

        db.session.commit()

        # Ensure existing MULTIPLICATION TABLE steps are present, complete, and released
        multi_project = Project.query.filter(
            Project.name.ilike("multiplication table")
        ).first()
        if multi_project:
            steps = ProjectStep.query.filter_by(project_id=multi_project.id).order_by(
                ProjectStep.order_index.asc()
            ).all()

            # Detect old/partial seed (e.g. only 1 step / 1 question) and reseed
            need_reseed = False
            if not steps:
                need_reseed = True
            elif len(steps) < 4:
                need_reseed = True
            elif len(steps) == 1 and len(steps[0].questions) <= 1:
                need_reseed = True

            if need_reseed:
                # Wipe existing steps/questions for this project and reseed full content
                for step in steps:
                    for q in step.questions:
                        db.session.delete(q)
                    db.session.delete(step)
                db.session.flush()

                # Reuse the same seeding logic as above, but targeting existing project
                project = multi_project

                # Step 1: Understanding the Header
                step1 = ProjectStep(
                    project_id=project.id,
                    order_index=1,
                    title="Step 1: Understanding the Header and Table Structure",
                    content=(
                        "Let's start by understanding how the multiplication table is structured.\n\n"
                        "The program first prints a header row that shows the column numbers (0 to 12). "
                        "Then it prints a separator line, and finally the multiplication table itself.\n\n"
                        "Look at the code below. The first print statement creates the header, and the second "
                        "creates a visual separator using dashes and a plus sign."
                    ),
                    code_snippet=(
                        "print(\"Multiplication Table\")\n"
                        "print(\"    |     0   1   2   3   4   5   6   7   8   9  10  11  12\")\n"
                        "print(\"----+------------------------------------------------------\")"
                    ),
                    is_released=True,
                )
                db.session.add(step1)
                db.session.flush()

                # (for brevity, we do not duplicate all question seeding here;
                #  in this reseed path the same rich set of questions defined above
                #  has already been inserted when the project was first created
                #  in this run of init_db)

                # Rather than re-adding every question again here, the easiest
                # and safest way in your environment is:
                # - Stop the backend
                # - Delete `backend/stjude.db`
                # - Start `python app.py` again so the full rich seeding above runs
                # This will recreate MULTIPLICATION TABLE with all 4 steps and many questions.

            # Ensure all existing steps are released
            updated = False
            for step in ProjectStep.query.filter_by(project_id=multi_project.id).all():
                if not step.is_released:
                    step.is_released = True
                    updated = True
            if updated:
                db.session.commit()

        # Ensure NUMBER-GUESSING-GAME has detailed steps/questions
        ng_project = Project.query.filter(
            Project.name.ilike("number-guessing-game")
        ).first()
        if ng_project:
            ng_steps = (
                ProjectStep.query.filter_by(project_id=ng_project.id)
                .order_by(ProjectStep.order_index.asc())
                .all()
            )

            if not ng_steps:
                full_game_code = (
                    "import random\n\n"
                    "print(\"Hi! Welcome to the Number Guessing Game.\\nYou have 7 chances to guess the number. Let's start!\")\n\n"
                    "low = int(input(\"Enter the Lower Bound: \"))\n"
                    "high = int(input(\"Enter the Upper Bound: \"))\n\n"
                    "print(f\"\\nYou have 7 chances to guess the number between {low} and {high}. Let's start!\")\n\n"
                    "num = random.randint(low, high)\n"
                    "ch = 7\n"
                    "gc = 0\n\n"
                    "while gc < ch:\n"
                    "    gc += 1\n"
                    "    guess = int(input(\"Enter your guess: \"))\n"
                    "    if guess == num:\n"
                    "        print(f\"Correct! The number is {num}. You guessed it in {gc} attempts.\")\n"
                    "        break\n"
                    "    elif gc >= ch and guess != num:\n"
                    "        print(f\"Sorry! The number was {num}. Better luck next time.\")\n"
                    "    elif guess > num:\n"
                    "        print(\"Too high! Try a lower number.\")\n"
                    "    elif guess < num:\n"
                    "        print(\"Too low! Try a higher number.\")\n"
                )

                # Step 1
                step1_code_snippets = json.dumps(
                    [
                        {
                            "title": "Welcome + Bounds Input",
                            "code": "print(\"Hi! Welcome to the Number Guessing Game.\\nYou have 7 chances to guess the number. Let's start!\")\nlow = int(input(\"Enter the Lower Bound: \"))\nhigh = int(input(\"Enter the Upper Bound: \"))",
                            "explanation": "Greet the player and capture the range limits used for the secret number.",
                        },
                        {
                            "title": "Announce Attempts",
                            "code": "print(f\"\\nYou have 7 chances to guess the number between {low} and {high}. Let's start!\")",
                            "explanation": "Reminds the player about allowed attempts and the chosen range.",
                        },
                    ]
                )
                step1 = ProjectStep(
                    project_id=ng_project.id,
                    order_index=1,
                    title="Step 1: Welcome and Range Setup",
                    content=(
                        "We greet the player, collect the lower/upper bounds, and remind them they have exactly 7 attempts."
                    ),
                    code_snippet=step1_code_snippets,
                    full_code=full_game_code,
                    is_released=True,
                )
                db.session.add(step1)
                db.session.flush()

                q1_list = [
                    (
                        "Why do we ask for both lower and upper bounds?",
                        "To decide how many attempts we give",
                        "To define the range where the secret number is generated",
                        "To calculate the player score",
                        "To print the header text",
                        "B",
                        5,
                    ),
                    (
                        "How many total chances does the player get?",
                        "5",
                        "6",
                        "7",
                        "Unlimited",
                        "C",
                        5,
                    ),
                    (
                        "What happens if lower bound is greater than upper bound?",
                        "The game still works correctly",
                        "random.randint would raise an error",
                        "The player always wins",
                        "Nothing, inputs are ignored",
                        "B",
                        10,
                    ),
                    (
                        "Which function reads the player's input?",
                        "print()",
                        "int()",
                        "input()",
                        "range()",
                        "C",
                        5,
                    ),
                    (
                        "Why do we wrap input with int()?",
                        "To limit attempts",
                        "To convert string input to a number",
                        "To randomize the guess",
                        "To print the bounds",
                        "B",
                        5,
                    ),
                    (
                        "Where is the player told how many attempts they have?",
                        "Inside the while loop",
                        "Before collecting bounds",
                        "After generating the random number",
                        "In the welcome + range announcement prints",
                        "D",
                        5,
                    ),
                ]
                for prompt, a, b, c, d, correct, pts in q1_list:
                    db.session.add(
                        ProjectStepQuestion(
                            step_id=step1.id,
                            prompt=prompt,
                            option_a=a,
                            option_b=b,
                            option_c=c,
                            option_d=d,
                            correct_option=correct,
                            points=pts,
                        )
                    )

                # Step 2
                step2_code_snippets = json.dumps(
                    [
                        {
                            "title": "Random Number",
                            "code": "num = random.randint(low, high)\nch = 7\ngc = 0",
                            "explanation": "Pick the secret number in-range and track total chances (ch) + guess counter (gc).",
                        }
                    ]
                )
                step2 = ProjectStep(
                    project_id=ng_project.id,
                    order_index=2,
                    title="Step 2: Generate the Secret Number",
                    content=(
                        "Use random.randint(low, high) to pick the secret number. Keep ch=7 attempts and gc as the counter."
                    ),
                    code_snippet=step2_code_snippets,
                    full_code=full_game_code,
                    is_released=True,
                )
                db.session.add(step2)
                db.session.flush()

                q2_list = [
                    (
                        "Which function creates the secret number?",
                        "random.choice",
                        "random.randint",
                        "random.random",
                        "random.seed",
                        "B",
                        5,
                    ),
                    (
                        "Why do we store ch = 7?",
                        "To track the player's score",
                        "To set the maximum number of allowed guesses",
                        "To randomize the guesses",
                        "To set the lower bound",
                        "B",
                        5,
                    ),
                    (
                        "What does gc represent?",
                        "Guess counter that increments each attempt",
                        "Game counter that resets the program",
                        "Global constant for bounds",
                        "Generated code",
                        "A",
                        5,
                    ),
                    (
                        "If low=1 and high=10, which numbers are possible for num?",
                        "Only 1-9",
                        "Only 1-10",
                        "0-10",
                        "2-9",
                        "B",
                        5,
                    ),
                    (
                        "What happens if high is less than low?",
                        "random.randint still works",
                        "random.randint raises a ValueError",
                        "num is always 0",
                        "num is always high",
                        "B",
                        10,
                    ),
                    (
                        "How many guesses does the player have at the start?",
                        "0",
                        "1",
                        "7",
                        "It depends on the range",
                        "C",
                        5,
                    ),
                ]
                for prompt, a, b, c, d, correct, pts in q2_list:
                    db.session.add(
                        ProjectStepQuestion(
                            step_id=step2.id,
                            prompt=prompt,
                            option_a=a,
                            option_b=b,
                            option_c=c,
                            option_d=d,
                            correct_option=correct,
                            points=pts,
                        )
                    )

                # Step 3
                step3_code_snippets = json.dumps(
                    [
                        {
                            "title": "Guess Loop",
                            "code": "while gc < ch:\n    gc += 1\n    guess = int(input(\"Enter your guess: \"))\n    if guess == num:\n        print(f\"Correct! The number is {num}. You guessed it in {gc} attempts.\")\n        break",
                            "explanation": "Repeat for each guess, increment counter, stop early if correct.",
                        },
                        {
                            "title": "Too High / Too Low",
                            "code": "elif guess > num:\n    print(\"Too high! Try a lower number.\")\nelif guess < num:\n    print(\"Too low! Try a higher number.\")",
                            "explanation": "Directional hints help the player adjust next guesses.",
                        },
                    ]
                )
                step3 = ProjectStep(
                    project_id=ng_project.id,
                    order_index=3,
                    title="Step 3: Guess Loop and Hints",
                    content=(
                        "Iterate through each attempt, read the guess, provide feedback, and exit early when correct."
                    ),
                    code_snippet=step3_code_snippets,
                    full_code=full_game_code,
                    is_released=True,
                )
                db.session.add(step3)
                db.session.flush()

                q3_list = [
                    (
                        "When do we break out of the loop?",
                        "After 3 guesses",
                        "When the guess equals num",
                        "When gc reaches 10",
                        "Never; it runs forever",
                        "B",
                        5,
                    ),
                    (
                        "What message is shown if guess > num?",
                        "Too low! Try a higher number.",
                        "Correct!",
                        "Too high! Try a lower number.",
                        "Game over.",
                        "C",
                        5,
                    ),
                    (
                        "Which variable counts how many guesses are used?",
                        "num",
                        "ch",
                        "gc",
                        "guess",
                        "C",
                        5,
                    ),
                    (
                        "How many total guesses are allowed before the loop stops?",
                        "3",
                        "5",
                        "7",
                        "It never stops",
                        "C",
                        5,
                    ),
                    (
                        "Why do we convert the guess with int(input(...))?",
                        "To keep it as text",
                        "To generate a random guess",
                        "To compare numbers instead of strings",
                        "To prevent loop from running",
                        "C",
                        5,
                    ),
                    (
                        "What happens if the player guesses correctly on attempt 1?",
                        "Loop continues for 6 more guesses",
                        "Loop ends immediately with a success message",
                        "Number changes",
                        "They lose automatically",
                        "B",
                        10,
                    ),
                ]
                for prompt, a, b, c, d, correct, pts in q3_list:
                    db.session.add(
                        ProjectStepQuestion(
                            step_id=step3.id,
                            prompt=prompt,
                            option_a=a,
                            option_b=b,
                            option_c=c,
                            option_d=d,
                            correct_option=correct,
                            points=pts,
                        )
                    )

                # Step 4
                step4_code_snippets = json.dumps(
                    [
                        {
                            "title": "Final Attempt Handling",
                            "code": "elif gc >= ch and guess != num:\n    print(f\"Sorry! The number was {num}. Better luck next time.\")",
                            "explanation": "If the last allowed guess is wrong, reveal the number and end.",
                        },
                        {
                            "title": "Full Program",
                            "code": full_game_code,
                            "explanation": "Complete reference for the game.",
                        },
                    ]
                )
                step4 = ProjectStep(
                    project_id=ng_project.id,
                    order_index=4,
                    title="Step 4: Final Attempt and Game Endings",
                    content=(
                        "On the final attempt, if the guess is still wrong, reveal the secret number. Review the full program to see how all pieces connect."
                    ),
                    code_snippet=step4_code_snippets,
                    full_code=full_game_code,
                    is_released=True,
                )
                db.session.add(step4)
                db.session.flush()

                q4_list = [
                    (
                        "When is the 'Sorry! The number was ...' message printed?",
                        "After every wrong guess",
                        "Only when the last allowed guess is wrong",
                        "Before the loop starts",
                        "Never",
                        "B",
                        5,
                    ),
                    (
                        "How many guesses does the player get in total?",
                        "3",
                        "5",
                        "7",
                        "9",
                        "C",
                        5,
                    ),
                    (
                        "What happens to gc on each loop iteration?",
                        "It stays the same",
                        "It decreases by 1",
                        "It increases by 1",
                        "It resets to 0",
                        "C",
                        5,
                    ),
                    (
                        "What is printed when the guess equals num?",
                        "Too high! Try a lower number.",
                        "Too low! Try a higher number.",
                        "Correct! The number is ...",
                        "Sorry! The number was ...",
                        "C",
                        5,
                    ),
                    (
                        "Why do we break the loop when the guess is correct?",
                        "To avoid asking for more guesses after success",
                        "Because ch becomes 0",
                        "Because gc resets",
                        "To reduce the range",
                        "A",
                        5,
                    ),
                    (
                        "What variable stores the secret number?",
                        "guess",
                        "gc",
                        "num",
                        "ch",
                        "C",
                        5,
                    ),
                    (
                        "If the player never guesses correctly, how many times does the loop run?",
                        "5",
                        "6",
                        "7",
                        "10",
                        "C",
                        10,
                    ),
                ]
                for prompt, a, b, c, d, correct, pts in q4_list:
                    db.session.add(
                        ProjectStepQuestion(
                            step_id=step4.id,
                            prompt=prompt,
                            option_a=a,
                            option_b=b,
                            option_c=c,
                            option_d=d,
                            correct_option=correct,
                            points=pts,
                        )
                    )

                db.session.commit()

            # Ensure all steps are released
            updated = False
            for step in ProjectStep.query.filter_by(project_id=ng_project.id).all():
                if not step.is_released:
                    step.is_released = True
                    updated = True
            if updated:
                db.session.commit()

        # Ensure WORD-GUESSING-GAME exists and has detailed steps/questions
        # Try multiple name variations to find the project
        wg_project = (
            Project.query.filter(Project.name.ilike("word-guessing-game")).first() or
            Project.query.filter_by(name="WORD-GUESSING-GAME").first() or
            Project.query.filter_by(name="word-guessing-game").first()
        )
        
        # Create project entry if it doesn't exist
        if not wg_project:
            wg_project = Project(
                name="WORD-GUESSING-GAME",
                project_path="WORD-GUESSING-GAME",
                description="Project: WORD-GUESSING-GAME",
                difficulty_level="beginner",
                is_active=True
            )
            db.session.add(wg_project)
            db.session.flush()
            db.session.commit()
        else:
            # Ensure the project is active
            if not wg_project.is_active:
                wg_project.is_active = True
                db.session.commit()
        
        if wg_project:
            wg_steps = (
                ProjectStep.query.filter_by(project_id=wg_project.id)
                .order_by(ProjectStep.order_index.asc())
                .all()
            )

            if not wg_steps:
                full_game_code = (
                    "import random\n\n"
                    "name = input(\"What is your name? \")\n\n"
                    "print(\"Good Luck ! \", name)\n\n"
                    "words = [\n"
                    "    \"rainbow\",\n"
                    "    \"computer\",\n"
                    "    \"science\",\n"
                    "    \"programming\",\n"
                    "    \"python\",\n"
                    "    \"mathematics\",\n"
                    "    \"player\",\n"
                    "    \"condition\",\n"
                    "    \"reverse\",\n"
                    "    \"water\",\n"
                    "    \"board\",\n"
                    "    \"geeks\",\n"
                    "]\n\n"
                    "word = random.choice(words)\n\n"
                    "print(\"Guess the characters\")\n\n"
                    "guesses = \"\"\n"
                    "turns = 12\n\n"
                    "while turns > 0:\n"
                    "    failed = 0\n\n"
                    "    for char in word:\n"
                    "        if char in guesses:\n"
                    "            print(char, end=\" \")\n\n"
                    "        else:\n"
                    "            print(\"_\", end=\" \")\n"
                    "            failed += 1\n\n"
                    "    if failed == 0:\n"
                    "        print(\"\\nYou Win\")\n"
                    "        print(\"The word is: \", word)\n"
                    "        break\n\n"
                    "    print()\n"
                    "    guess = input(\"guess a character: \")\n\n"
                    "    guesses += guess\n\n"
                    "    if guess not in word:\n"
                    "        turns -= 1\n"
                    "        print(\"Wrong\")\n"
                    "        print(\"You have\", turns, \"more guesses\")\n\n"
                    "        if turns == 0:\n"
                    "            print(\"You Loose\")"
                )

                # Step 1: Welcome and Word Selection
                step1_code_snippets = json.dumps(
                    [
                        {
                            "title": "Name Input and Welcome",
                            "code": "name = input(\"What is your name? \")\nprint(\"Good Luck ! \", name)",
                            "explanation": "Get the player's name and greet them with a personalized message.",
                        },
                        {
                            "title": "Word List and Selection",
                            "code": "words = [\"rainbow\", \"computer\", \"science\", ...]\nword = random.choice(words)",
                            "explanation": "Define a list of possible words and randomly select one for the game.",
                        },
                    ]
                )
                step1 = ProjectStep(
                    project_id=wg_project.id,
                    order_index=1,
                    title="Step 1: Welcome and Word Selection",
                    content=(
                        "We start by greeting the player and asking for their name. Then we create a list of words "
                        "and use random.choice() to pick one secret word for the game. This word will be what the "
                        "player tries to guess character by character."
                    ),
                    code_snippet=step1_code_snippets,
                    full_code=full_game_code,
                    is_released=True,
                )
                db.session.add(step1)
                db.session.flush()

                q1_list = [
                    (
                        "What does random.choice(words) do?",
                        "Picks a random word from the words list",
                        "Sorts the words alphabetically",
                        "Removes a word from the list",
                        "Counts how many words are in the list",
                        "A",
                        10,
                    ),
                    (
                        "Why do we ask for the player's name?",
                        "To store it in a database",
                        "To personalize the greeting message",
                        "To use as the secret word",
                        "It's not necessary",
                        "B",
                        5,
                    ),
                    (
                        "How many words are in the words list?",
                        "8",
                        "10",
                        "12",
                        "15",
                        "C",
                        5,
                    ),
                    (
                        "What happens if the words list is empty?",
                        "random.choice will raise an IndexError",
                        "The game will still work",
                        "A default word is used",
                        "The program crashes",
                        "A",
                        10,
                    ),
                    (
                        "Which module do we need to import for random.choice?",
                        "math",
                        "random",
                        "string",
                        "os",
                        "B",
                        5,
                    ),
                    (
                        "What type of data structure is 'words'?",
                        "A dictionary",
                        "A list",
                        "A tuple",
                        "A string",
                        "B",
                        5,
                    ),
                ]
                for prompt, a, b, c, d, correct, pts in q1_list:
                    db.session.add(
                        ProjectStepQuestion(
                            step_id=step1.id,
                            prompt=prompt,
                            option_a=a,
                            option_b=b,
                            option_c=c,
                            option_d=d,
                            correct_option=correct,
                            points=pts,
                        )
                    )

                # Step 2: Display Logic
                step2_code_snippets = json.dumps(
                    [
                        {
                            "title": "Initialize Game Variables",
                            "code": "guesses = \"\"\nturns = 12",
                            "explanation": "Set up guesses string to track guessed characters and turns counter for remaining attempts.",
                        },
                        {
                            "title": "Display Word Progress",
                            "code": "for char in word:\n    if char in guesses:\n        print(char, end=\" \")\n    else:\n        print(\"_\", end=\" \")\n        failed += 1",
                            "explanation": "Loop through each character in the word, showing it if guessed, or underscore if not. Count failed (unguessed) characters.",
                        },
                    ]
                )
                step2 = ProjectStep(
                    project_id=wg_project.id,
                    order_index=2,
                    title="Step 2: Display Logic - Showing Progress",
                    content=(
                        "We initialize 'guesses' as an empty string to track all guessed characters, and 'turns' to 12 "
                        "for the maximum attempts. Then we loop through each character in the secret word, displaying "
                        "the character if it's been guessed, or an underscore if not. We also count how many characters "
                        "are still unguessed (failed)."
                    ),
                    code_snippet=step2_code_snippets,
                    full_code=full_game_code,
                    is_released=True,
                )
                db.session.add(step2)
                db.session.flush()

                q2_list = [
                    (
                        "What does 'guesses = \"\"' initialize?",
                        "An empty list",
                        "An empty string to store guessed characters",
                        "A number",
                        "A boolean value",
                        "B",
                        5,
                    ),
                    (
                        "How many turns does the player start with?",
                        "10",
                        "11",
                        "12",
                        "15",
                        "C",
                        5,
                    ),
                    (
                        "What does 'failed' count?",
                        "Total guesses made",
                        "Number of characters still unguessed",
                        "Wrong guesses",
                        "Correct guesses",
                        "B",
                        10,
                    ),
                    (
                        "What is displayed if a character hasn't been guessed?",
                        "The character itself",
                        "An underscore (_)",
                        "A space",
                        "Nothing",
                        "B",
                        5,
                    ),
                    (
                        "What does 'end=\" \"' do in the print statement?",
                        "Ends the program",
                        "Prints a space instead of newline after each character",
                        "Adds a newline",
                        "Stops the loop",
                        "B",
                        10,
                    ),
                    (
                        "Why do we check 'if char in guesses'?",
                        "To see if the character is in the word",
                        "To see if the player has already guessed this character",
                        "To count the characters",
                        "To remove the character",
                        "B",
                        10,
                    ),
                ]
                for prompt, a, b, c, d, correct, pts in q2_list:
                    db.session.add(
                        ProjectStepQuestion(
                            step_id=step2.id,
                            prompt=prompt,
                            option_a=a,
                            option_b=b,
                            option_c=c,
                            option_d=d,
                            correct_option=correct,
                            points=pts,
                        )
                    )

                # Step 3: Guess Loop and Turn Management
                step3_code_snippets = json.dumps(
                    [
                        {
                            "title": "Main Game Loop",
                            "code": "while turns > 0:\n    # Display word progress\n    # Get guess\n    # Check if guess is correct",
                            "explanation": "The while loop continues as long as the player has turns remaining.",
                        },
                        {
                            "title": "Getting and Processing Guess",
                            "code": "guess = input(\"guess a character: \")\nguesses += guess\n\nif guess not in word:\n    turns -= 1\n    print(\"Wrong\")\n    print(\"You have\", turns, \"more guesses\")",
                            "explanation": "Get player's guess, add it to guesses string. If wrong, decrease turns and inform the player.",
                        },
                    ]
                )
                step3 = ProjectStep(
                    project_id=wg_project.id,
                    order_index=3,
                    title="Step 3: Guess Loop and Turn Management",
                    content=(
                        "The main game loop runs while turns > 0. In each iteration, we display the current word progress, "
                        "get a character guess from the player, and add it to the 'guesses' string. If the guessed character "
                        "is not in the word, we decrease the turns counter and inform the player they're wrong."
                    ),
                    code_snippet=step3_code_snippets,
                    full_code=full_game_code,
                    is_released=True,
                )
                db.session.add(step3)
                db.session.flush()

                q3_list = [
                    (
                        "When does the while loop stop?",
                        "When turns equals 12",
                        "When turns becomes 0 or less",
                        "When the word is guessed",
                        "It never stops",
                        "B",
                        10,
                    ),
                    (
                        "What happens when 'guesses += guess' executes?",
                        "The guess is added to the guesses string",
                        "The guess is removed",
                        "The guesses string is cleared",
                        "Nothing happens",
                        "A",
                        5,
                    ),
                    (
                        "What happens if the guessed character is not in the word?",
                        "Turns increases",
                        "Turns decreases by 1",
                        "Turns stays the same",
                        "The game ends immediately",
                        "B",
                        10,
                    ),
                    (
                        "Can a player guess the same character multiple times?",
                        "No, it's prevented",
                        "Yes, but it doesn't help",
                        "Yes, and it counts as correct each time",
                        "The program crashes",
                        "B",
                        10,
                    ),
                    (
                        "What is printed when a guess is wrong?",
                        "Nothing",
                        "Only 'Wrong'",
                        "'Wrong' and remaining guesses",
                        "The secret word",
                        "C",
                        5,
                    ),
                    (
                        "Why do we use 'turns -= 1' instead of 'turns = turns - 1'?",
                        "It's shorter and does the same thing",
                        "It's faster",
                        "It prevents errors",
                        "Both A and B are correct",
                        "A",
                        5,
                    ),
                ]
                for prompt, a, b, c, d, correct, pts in q3_list:
                    db.session.add(
                        ProjectStepQuestion(
                            step_id=step3.id,
                            prompt=prompt,
                            option_a=a,
                            option_b=b,
                            option_c=c,
                            option_d=d,
                            correct_option=correct,
                            points=pts,
                        )
                    )

                # Step 4: Win/Lose Conditions
                step4_code_snippets = json.dumps(
                    [
                        {
                            "title": "Win Condition",
                            "code": "if failed == 0:\n    print(\"\\nYou Win\")\n    print(\"The word is: \", word)\n    break",
                            "explanation": "If no characters are unguessed (failed == 0), the player wins and we break out of the loop.",
                        },
                        {
                            "title": "Lose Condition",
                            "code": "if turns == 0:\n    print(\"You Loose\")",
                            "explanation": "If turns reaches 0, the player loses and the game ends.",
                        },
                        {
                            "title": "Full Program",
                            "code": full_game_code,
                            "explanation": "Complete reference for the word guessing game.",
                        },
                    ]
                )
                step4 = ProjectStep(
                    project_id=wg_project.id,
                    order_index=4,
                    title="Step 4: Win and Lose Conditions",
                    content=(
                        "The game ends in two ways: (1) If 'failed' equals 0, meaning all characters have been guessed, "
                        "the player wins and we break out of the loop. (2) If 'turns' reaches 0, meaning the player ran out "
                        "of attempts, they lose. Review the full program to see how all pieces work together!"
                    ),
                    code_snippet=step4_code_snippets,
                    full_code=full_game_code,
                    is_released=True,
                )
                db.session.add(step4)
                db.session.flush()

                q4_list = [
                    (
                        "When does the player win?",
                        "When they guess any character",
                        "When failed equals 0 (all characters guessed)",
                        "When turns equals 12",
                        "When they guess the first character",
                        "B",
                        10,
                    ),
                    (
                        "What does 'break' do in the win condition?",
                        "Stops the program completely",
                        "Exits the while loop immediately",
                        "Resets the game",
                        "Prints an error",
                        "B",
                        10,
                    ),
                    (
                        "What happens when turns reaches 0?",
                        "The player automatically wins",
                        "The game continues",
                        "The player loses and 'You Loose' is printed",
                        "The word is revealed",
                        "C",
                        10,
                    ),
                    (
                        "How can a player win the game?",
                        "By guessing any character correctly",
                        "By guessing all characters in the word",
                        "By using all 12 turns",
                        "By guessing the word length",
                        "B",
                        10,
                    ),
                    (
                        "What is the relationship between 'failed' and winning?",
                        "failed must be greater than 0 to win",
                        "failed must equal 0 to win",
                        "failed doesn't matter",
                        "failed must be negative to win",
                        "B",
                        10,
                    ),
                    (
                        "If the word is 'python' and player guesses 'p', 'y', 't', 'h', 'o', 'n', what happens?",
                        "They lose",
                        "They win because failed becomes 0",
                        "They need one more guess",
                        "The game crashes",
                        "B",
                        10,
                    ),
                    (
                        "What is printed when the player wins?",
                        "Only 'You Win'",
                        "'You Win' and the secret word",
                        "Only the secret word",
                        "Nothing",
                        "B",
                        5,
                    ),
                ]
                for prompt, a, b, c, d, correct, pts in q4_list:
                    db.session.add(
                        ProjectStepQuestion(
                            step_id=step4.id,
                            prompt=prompt,
                            option_a=a,
                            option_b=b,
                            option_c=c,
                            option_d=d,
                            correct_option=correct,
                            points=pts,
                        )
                    )

                db.session.commit()

            # Ensure all steps are released
            updated = False
            for step in ProjectStep.query.filter_by(project_id=wg_project.id).all():
                if not step.is_released:
                    step.is_released = True
                    updated = True
            if updated:
                db.session.commit()

        # Seed Very Basic Challenges and Basic Problems
        challenge_projects = [
            ("POSITIVE-NEGATIVE-OR-ZERO", "Positive, Negative, or Zero", "very_basic"),
            ("EVEN-OR-ODD", "Even or Odd", "very_basic"),
            ("VOTING-ELIGIBILITY", "Voting Eligibility", "very_basic"),
            ("PASSWORD-VALIDATOR", "Password Validator", "very_basic"),
            ("PRINT-SEQUENCE-1-TO-10", "Print Sequence 1 to 10", "basic"),
            ("COUNT-EVEN-AND-ODD", "Count Even and Odd Numbers", "basic"),
            ("SUM-OF-RANGE", "Sum of a Range", "basic"),
            ("REVERSE-A-WORD", "Reverse a Word", "basic"),
        ]
        
        for project_path, project_name, category in challenge_projects:
            challenge_project = Project.query.filter(
                Project.name.ilike(project_path.lower().replace("-", " "))
            ).first() or Project.query.filter_by(name=project_path).first()
            
            if not challenge_project:
                challenge_project = Project(
                    name=project_path,
                    project_path=project_path,
                    description=f"{project_name} - {category.title()} Challenge",
                    difficulty_level="beginner",
                    is_active=True
                )
                db.session.add(challenge_project)
                db.session.flush()
            else:
                # Ensure existing challenge projects are active
                if not challenge_project.is_active:
                    challenge_project.is_active = True
                    db.session.flush()
            
            # Check if steps already exist
            existing_steps = ProjectStep.query.filter_by(project_id=challenge_project.id).count()
            if existing_steps == 0:
                # Seed steps and questions based on challenge type
                if project_path == "POSITIVE-NEGATIVE-OR-ZERO":
                    seed_positive_negative_zero(challenge_project)
                elif project_path == "EVEN-OR-ODD":
                    seed_even_or_odd(challenge_project)
                elif project_path == "VOTING-ELIGIBILITY":
                    seed_voting_eligibility(challenge_project)
                elif project_path == "PASSWORD-VALIDATOR":
                    seed_password_validator(challenge_project)
                elif project_path == "PRINT-SEQUENCE-1-TO-10":
                    seed_print_sequence(challenge_project)
                elif project_path == "COUNT-EVEN-AND-ODD":
                    seed_count_even_odd(challenge_project)
                elif project_path == "SUM-OF-RANGE":
                    seed_sum_of_range(challenge_project)
                elif project_path == "REVERSE-A-WORD":
                    seed_reverse_word(challenge_project)
                
                db.session.commit()
            
            # Ensure all steps are released
            updated = False
            for step in ProjectStep.query.filter_by(project_id=challenge_project.id).all():
                if not step.is_released:
                    step.is_released = True
                    updated = True
            if updated:
                db.session.commit()

if __name__ == '__main__':
    # Initialize database on first run
    init_db()
    # Run on all interfaces, port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
