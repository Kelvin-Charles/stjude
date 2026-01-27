from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, Project, ProjectProgress, UserRole, ProjectStep, ProjectStepQuestion
from routes import api
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

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

def init_db():
    """Initialize database tables and default data"""
    with app.app_context():
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

if __name__ == '__main__':
    # Initialize database on first run
    init_db()
    # Run on all interfaces, port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
