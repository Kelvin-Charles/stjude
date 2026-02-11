from flask import Blueprint, request, jsonify
from models import (
  db,
  User,
  Project,
  ProjectProgress,
  UserRole,
  ProjectStep,
  ProjectStepQuestion,
  StudentStepAnswer,
  Resource,
  ProjectSubmission,
)
from auth import (
  generate_token,
  require_auth,
  require_student,
  require_mentor,
  require_manager,
  get_current_user,
)
from datetime import datetime
import os
import secrets
from werkzeug.utils import secure_filename
from flask import send_file


api = Blueprint("api", __name__)

@api.route("/students", methods=["GET"])
@require_mentor
def list_students(user):
  """List all active students (for mentors/managers)."""
  try:
    students = (
      User.query.filter(User.role == UserRole.STUDENT, User.is_active.is_(True))
      .order_by(User.full_name.asc())
      .all()
    )
    return jsonify({"success": True, "students": [s.to_dict() for s in students]}), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500

@api.route("/admin/students/<int:student_id>/reset-password", methods=["POST"])
@require_manager
def admin_reset_student_password(user, student_id):
  """
  Manager/admin can reset a student's password.

  Body:
    - password (optional): set to this value
    - generate (optional bool): if true, generate a temporary password
  """
  try:
    data = request.get_json() or {}
    new_password = data.get("password")
    generate = bool(data.get("generate")) if "generate" in data else False

    student = User.query.get_or_404(student_id)
    if student.role != UserRole.STUDENT:
      return jsonify({"success": False, "error": "Target user must be a student"}), 400

    if generate and not new_password:
      new_password = secrets.token_urlsafe(8)

    if not new_password or len(str(new_password)) < 4:
      return jsonify({"success": False, "error": "password must be at least 4 characters"}), 400

    student.set_password(str(new_password))
    db.session.commit()

    # Return the generated password only if we generated it server-side
    resp = {"success": True, "message": "Password reset", "student": student.to_dict()}
    if generate:
      resp["temporary_password"] = new_password
    return jsonify(resp), 200
  except Exception as e:
    db.session.rollback()
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/register", methods=["POST"])
def register():
  """Register a new user - students only"""
  try:
    data = request.get_json() or {}

    required_fields = ["username", "password", "full_name", "batch"]
    for field in required_fields:
      if not data.get(field):
        return jsonify({"success": False, "error": f"{field} is required"}), 400

    username = data["username"]
    email = data.get("email") or f"{username}@no-email.local"

    if User.query.filter_by(username=username).first():
      return jsonify({"success": False, "error": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
      return jsonify({"success": False, "error": "Email already exists"}), 400

    user = User(
      username=username,
      email=email,
      full_name=data["full_name"],
      gender=data.get("gender"),
      batch=data["batch"],
      role=UserRole.STUDENT,
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = generate_token(user)
    return (
      jsonify(
        {
          "success": True,
          "message": "User registered",
          "token": token,
          "user": user.to_dict(),
        }
      ),
      201,
    )
  except Exception as e:
    db.session.rollback()
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/login", methods=["POST"])
def login():
  try:
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
      return (
        jsonify(
          {"success": False, "error": "Username and password are required"}
        ),
        400,
      )

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
      return jsonify({"success": False, "error": "Invalid username or password"}), 401
    if not user.is_active:
      return jsonify({"success": False, "error": "Account is inactive"}), 403

    token = generate_token(user)
    return (
      jsonify(
        {
          "success": True,
          "message": "Login successful",
          "token": token,
          "user": user.to_dict(),
        }
      ),
      200,
    )
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/me", methods=["GET"])
@require_auth
def me(user):
  return jsonify({"success": True, "user": user.to_dict()}), 200


@api.route("/projects", methods=["GET"])
@require_auth
def list_projects(user):
  try:
    projects = Project.query.filter_by(is_active=True).all()
    out = []
    for p in projects:
      d = p.to_dict()
      if user.role == UserRole.STUDENT:
        prog = ProjectProgress.query.filter_by(
          student_id=user.id, project_id=p.id
        ).first()
        d["progress"] = prog.to_dict() if prog else None
      out.append(d)
    return jsonify({"success": True, "projects": out}), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/projects/<int:project_id>", methods=["GET"])
@require_auth
def get_project(user, project_id):
  try:
    project = Project.query.get_or_404(project_id)
    d = project.to_dict()
    if user.role == UserRole.STUDENT:
      prog = ProjectProgress.query.filter_by(
        student_id=user.id, project_id=project_id
      ).first()
      d["progress"] = prog.to_dict() if prog else None

    if project.project_path:
      project_dir = os.path.join(
        os.path.dirname(__file__), "projects", project.project_path
      )
      files = []
      if os.path.exists(project_dir):
        for name in os.listdir(project_dir):
          path = os.path.join(project_dir, name)
          if os.path.isfile(path):
            try:
              with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            except Exception:
              content = None
            files.append({"name": name, "content": content})
      d["files"] = files

    return jsonify({"success": True, "project": d}), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/projects/<int:project_id>/steps", methods=["GET"])
@require_student
def list_steps(user, project_id):
  try:
    steps = (
      ProjectStep.query.filter_by(project_id=project_id, is_released=True)
      .order_by(ProjectStep.order_index.asc())
      .all()
    )
    return jsonify(
      {"success": True, "steps": [s.to_dict(include_questions=True) for s in steps]}
    ), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/progress", methods=["GET"])
@require_student
def my_progress(user):
  try:
    items = ProjectProgress.query.filter_by(student_id=user.id).all()
    return jsonify(
      {"success": True, "progress": [p.to_dict() for p in items]}
    ), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/progress", methods=["POST"])
@require_student
def update_progress(user):
  try:
    data = request.get_json() or {}
    project_id = data.get("project_id")
    if not project_id:
      return jsonify({"success": False, "error": "project_id is required"}), 400

    project = Project.query.get_or_404(project_id)
    prog = ProjectProgress.query.filter_by(
      student_id=user.id, project_id=project.id
    ).first()
    if not prog:
      prog = ProjectProgress(student_id=user.id, project_id=project.id)
      db.session.add(prog)

    # Calculate progress based on actual step completions
    total_steps = ProjectStep.query.filter_by(
      project_id=project_id, is_released=True
    ).count()
    
    if total_steps > 0:
      # Count steps where student has answered at least one question
      completed_steps = 0
      steps = ProjectStep.query.filter_by(
        project_id=project_id, is_released=True
      ).order_by(ProjectStep.order_index.asc()).all()
      
      for step in steps:
        # Check if student has answered any question in this step
        has_answers = StudentStepAnswer.query.join(
          ProjectStepQuestion
        ).filter(
          StudentStepAnswer.student_id == user.id,
          ProjectStepQuestion.step_id == step.id
        ).first() is not None
        
        if has_answers:
          completed_steps += 1
      
      calculated_percentage = int((completed_steps / total_steps) * 100)
      
      # Use calculated percentage if not explicitly provided
      if "progress_percentage" in data:
        prog.progress_percentage = max(
          0, min(100, int(data["progress_percentage"]))
        )
      else:
        prog.progress_percentage = calculated_percentage
      
      # Update status based on progress
      if calculated_percentage == 100:
        prog.status = "completed"
        if not prog.completed_at:
          prog.completed_at = datetime.utcnow()
      elif calculated_percentage > 0:
        prog.status = "in_progress"
        if not prog.started_at:
          prog.started_at = datetime.utcnow()
      else:
        prog.status = "not_started"
    else:
      # Fallback to manual update if no steps
      if "status" in data:
        prog.status = data["status"]
      if "progress_percentage" in data:
        prog.progress_percentage = max(
          0, min(100, int(data["progress_percentage"]))
        )
    
    prog.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"success": True, "progress": prog.to_dict()}), 200
  except Exception as e:
    db.session.rollback()
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/projects/<int:project_id>/progress", methods=["GET"])
@require_student
def get_project_progress(user, project_id):
  """Get detailed progress for a specific project including step completion"""
  try:
    project = Project.query.get_or_404(project_id)
    
    # Get overall progress
    prog = ProjectProgress.query.filter_by(
      student_id=user.id, project_id=project_id
    ).first()
    
    if not prog:
      prog = ProjectProgress(student_id=user.id, project_id=project_id)
      db.session.add(prog)
      db.session.commit()
    
    # Get all steps and their completion status
    steps = ProjectStep.query.filter_by(
      project_id=project_id, is_released=True
    ).order_by(ProjectStep.order_index.asc()).all()
    
    step_progress = []
    for step in steps:
      # Check if student has answered questions for this step
      step_questions = ProjectStepQuestion.query.filter_by(step_id=step.id).all()
      answered_count = 0
      correct_count = 0
      total_points_earned = 0
      total_points_possible = sum(q.points for q in step_questions)
      
      for question in step_questions:
        answer = StudentStepAnswer.query.filter_by(
          student_id=user.id, question_id=question.id
        ).first()
        if answer:
          answered_count += 1
          if answer.is_correct:
            correct_count += 1
          total_points_earned += answer.points_awarded
      
      step_progress.append({
        "step_id": step.id,
        "step_order": step.order_index,
        "step_title": step.title,
        "is_completed": answered_count > 0,
        "questions_answered": answered_count,
        "questions_correct": correct_count,
        "total_questions": len(step_questions),
        "points_earned": total_points_earned,
        "points_possible": total_points_possible,
      })
    
    # Recalculate overall progress
    total_steps = len(steps)
    completed_steps = sum(1 for sp in step_progress if sp["is_completed"])
    calculated_percentage = int((completed_steps / total_steps) * 100) if total_steps > 0 else 0
    
    # Update progress record if needed
    if prog.progress_percentage != calculated_percentage:
      prog.progress_percentage = calculated_percentage
      if calculated_percentage == 100:
        prog.status = "completed"
        if not prog.completed_at:
          prog.completed_at = datetime.utcnow()
      elif calculated_percentage > 0:
        prog.status = "in_progress"
        if not prog.started_at:
          prog.started_at = datetime.utcnow()
      db.session.commit()
    
    return jsonify({
      "success": True,
      "progress": prog.to_dict(),
      "step_progress": step_progress,
      "overall_percentage": calculated_percentage,
      "completed_steps": completed_steps,
      "total_steps": total_steps,
    }), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/steps/<int:step_id>/answers", methods=["GET"])
@require_student
def get_step_answers(user, step_id):
  """Get student's previous answers for a step"""
  try:
    step = ProjectStep.query.get_or_404(step_id)
    answers = {}
    results = []
    total_points = 0
    max_points = 0
    
    for q in step.questions:
      max_points += q.points
      answer = StudentStepAnswer.query.filter_by(
        student_id=user.id, question_id=q.id
      ).first()
      if answer:
        answers[q.id] = answer.selected_option
        total_points += answer.points_awarded
        results.append({
          "question_id": q.id,
          "selected_option": answer.selected_option,
          "is_correct": answer.is_correct,
          "points_awarded": answer.points_awarded,
          "max_points": q.points,
        })
    
    all_correct = all(r["is_correct"] for r in results) if results else False
    
    return jsonify({
      "success": True,
      "answers": answers,
      "results": results,
      "total_points": total_points,
      "max_points": max_points,
      "all_correct": all_correct,
      "has_answers": len(answers) > 0,
    }), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/steps/<int:step_id>/answer", methods=["POST"])
@require_student
def answer_step(user, step_id):
  try:
    step = ProjectStep.query.get_or_404(step_id)
    data = request.get_json() or {}
    answers = data.get("answers", {})
    if not isinstance(answers, dict) or not answers:
      return jsonify({"success": False, "error": "answers object is required"}), 400

    total_points = 0
    max_points = 0
    results = []

    for q in step.questions:
      max_points += q.points
      selected = answers.get(str(q.id)) or answers.get(q.id)
      if not selected:
        continue
      selected = str(selected).upper()
      is_correct = selected == q.correct_option.upper()

      existing = StudentStepAnswer.query.filter_by(
        student_id=user.id, question_id=q.id
      ).first()
      is_retry = existing is not None

      if is_retry and not existing.is_correct:
        points_awarded = int(q.points * 0.5) if is_correct else 0
      elif is_retry and existing.is_correct:
        points_awarded = existing.points_awarded
      else:
        points_awarded = q.points if is_correct else 0

      if not existing:
        existing = StudentStepAnswer(student_id=user.id, question_id=q.id)
        db.session.add(existing)

      existing.selected_option = selected
      existing.is_correct = is_correct
      existing.points_awarded = points_awarded
      existing.answered_at = datetime.utcnow()

      total_points += existing.points_awarded

      results.append(
        {
          "question_id": q.id,
          "selected_option": selected,
          "is_correct": is_correct,
          "points_awarded": existing.points_awarded,
          "max_points": q.points,
          "is_retry": is_retry,
          "was_previously_correct": existing.is_correct if is_retry else None,
        }
      )

    db.session.commit()
    all_correct = all(r["is_correct"] for r in results) if results else False

    return jsonify(
      {
        "success": True,
        "results": results,
        "total_points": total_points,
        "max_points": max_points,
        "all_correct": all_correct,
      }
    ), 200
  except Exception as e:
    db.session.rollback()
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/leaderboard", methods=["GET"])
@require_auth
def leaderboard(user):
  from sqlalchemy import func

  try:
    rows = (
      db.session.query(
        User.id,
        User.username,
        User.full_name,
        func.coalesce(func.sum(StudentStepAnswer.points_awarded), 0).label("pts"),
      )
      .filter(User.role == UserRole.STUDENT, User.is_active.is_(True))
      .outerjoin(StudentStepAnswer, User.id == StudentStepAnswer.student_id)
      .group_by(User.id, User.username, User.full_name)
      .order_by(func.coalesce(func.sum(StudentStepAnswer.points_awarded), 0).desc())
      .all()
    )
    lb = []
    rank = 1
    current_rank = None
    current_points = None
    for r in rows:
      entry = {
        "rank": rank,
        "student_id": r.id,
        "username": r.username,
        "full_name": r.full_name,
        "total_points": int(r.pts) if r.pts is not None else 0,
      }
      lb.append(entry)
      if user.role == UserRole.STUDENT and r.id == user.id:
        current_rank = rank
        current_points = entry["total_points"]
      rank += 1
    return jsonify(
      {
        "success": True,
        "leaderboard": lb,
        "current_user_rank": current_rank,
        "current_user_points": current_points,
      }
    ), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/projects/<int:project_id>/run", methods=["POST"])
@require_student
def run_project(user, project_id):
  try:
    import subprocess

    project = Project.query.get_or_404(project_id)
    if not project.project_path:
      return jsonify({"success": False, "error": "Project path not found"}), 404
    project_dir = os.path.join(
      os.path.dirname(__file__), "projects", project.project_path
    )
    pyfile = os.path.join(project_dir, "index.py")
    if not os.path.exists(pyfile):
      return jsonify({"success": False, "error": "Python file not found"}), 404
    with open(pyfile, "r", encoding="utf-8") as f:
      code = f.read()
    try:
      result = subprocess.run(
        ["python3", pyfile],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=project_dir,
      )
      if result.returncode != 0:
        return (
          jsonify(
            {"success": False, "error": result.stderr, "output": result.stdout}
          ),
          400,
        )
      return jsonify(
        {"success": True, "output": result.stdout, "code": code}
      ), 200
    except subprocess.TimeoutExpired:
      return jsonify({"success": False, "error": "Code execution timed out"}), 400
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/resources", methods=["GET"])
@require_auth
def list_resources(user):
  try:
    # Scan uploads/books directory for PDF files and auto-create resources
    # routes.py is in backend/, so dirname(__file__) gives us backend/ directory
    # In container: /app, so books_dir will be /app/uploads/books
    backend_dir = os.path.dirname(__file__)
    books_dir = os.path.join(backend_dir, "uploads", "books")
    if os.path.exists(books_dir):
      # Get a default creator (first mentor/manager, or current user)
      default_creator = (
        User.query.filter(User.role.in_([UserRole.MENTOR, UserRole.MANAGER]))
        .first()
      ) or user
      
      # Get all existing resource file paths
      existing_paths = {
        r.content for r in Resource.query.all() 
        if r.content and r.content.startswith("/uploads/books/")
      }
      
      # Scan for PDF files
      for filename in os.listdir(books_dir):
        if filename.lower().endswith('.pdf'):
          file_path = os.path.join(books_dir, filename)
          if os.path.isfile(file_path):
            # Check if resource already exists for this file
            resource_path = f"/uploads/books/{filename}"
            if resource_path not in existing_paths:
              # Extract title from filename (remove extension and clean up)
              title = filename.rsplit('.', 1)[0]  # Remove .pdf extension
              # Clean up common filename patterns
              title = title.replace(' - libgen.li', '').replace('_', ' ').strip()
              
              # Create new resource entry
              new_resource = Resource(
                title=title,
                content=resource_path,
                description=f"PDF book: {title}",
                category="Books",
                created_by=default_creator.id,
                is_active=True
              )
              db.session.add(new_resource)
              print(f"Added new resource: {title} -> {resource_path}")
      
      # Commit any new resources
      db.session.commit()
      print(f"Scanned {books_dir}, found PDFs and committed resources")
    
    # Return all active resources
    resources = (
      Resource.query.filter_by(is_active=True)
      .order_by(Resource.created_at.desc())
      .all()
    )
    return jsonify(
      {"success": True, "resources": [r.to_dict() for r in resources]}
    ), 200
  except Exception as e:
    db.session.rollback()
    import traceback
    print(f"Error in list_resources: {str(e)}")
    print(traceback.format_exc())
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/resources", methods=["POST"])
@require_mentor
def create_resource(user):
  try:
    data = request.get_json() or {}
    if not data.get("title") or not data.get("content"):
      return jsonify({"success": False, "error": "title and content are required"}), 400
    res = Resource(
      title=data["title"],
      content=data["content"],
      description=data.get("description"),
      category=data.get("category", "General"),
      created_by=user.id,
    )
    db.session.add(res)
    db.session.commit()
    return jsonify({"success": True, "resource": res.to_dict()}), 201
  except Exception as e:
    db.session.rollback()
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/resources/<int:resource_id>", methods=["GET"])
@require_auth
def get_resource(user, resource_id):
  try:
    res = Resource.query.get_or_404(resource_id)
    if not res.is_active:
      return jsonify({"success": False, "error": "Resource not found"}), 404
    return jsonify({"success": True, "resource": res.to_dict()}), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


# Project Submission Endpoints
ALLOWED_EXTENSIONS = {'py', 'txt', 'pdf', 'doc', 'docx', 'zip', 'rar', '7z', 'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route("/projects/<int:project_id>/submit", methods=["POST"])
@require_student
def submit_project(user, project_id):
  """Student uploads a project file"""
  try:
    from werkzeug.utils import secure_filename
    from flask import send_file
    
    project = Project.query.get_or_404(project_id)
    
    if 'file' not in request.files:
      return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
      return jsonify({"success": False, "error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
      return jsonify({"success": False, "error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'submissions')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    safe_filename = secure_filename(file.filename)
    unique_filename = f"{user.id}_{project_id}_{timestamp}_{safe_filename}"
    file_path = os.path.join(uploads_dir, unique_filename)
    
    # Save file
    file.save(file_path)
    file_size = os.path.getsize(file_path)
    
    # Create submission record
    submission_type = request.form.get('submission_type', 'project')  # 'project' or 'final_test'
    submission = ProjectSubmission(
      student_id=user.id,
      project_id=project_id,
      filename=file.filename,
      file_path=file_path,
      file_size=file_size,
      mime_type=file.content_type or 'application/octet-stream',
      notes=request.form.get('notes', ''),
      status='submitted',
      submission_type=submission_type
    )
    db.session.add(submission)
    db.session.commit()
    
    return jsonify({
      "success": True,
      "message": "Project submitted successfully",
      "submission": submission.to_dict()
    }), 201
  except Exception as e:
    db.session.rollback()
    import traceback
    error_msg = str(e)
    traceback.print_exc()
    print(f"Error submitting project: {error_msg}")
    return jsonify({"success": False, "error": error_msg}), 500


@api.route("/projects/<int:project_id>/submissions", methods=["GET"])
@require_student
def my_project_submissions(user, project_id):
  """Get student's own submissions for a project"""
  try:
    submission_type = request.args.get('submission_type')
    query = ProjectSubmission.query.filter_by(
      student_id=user.id,
      project_id=project_id
    )
    if submission_type:
      query = query.filter_by(submission_type=submission_type)
    submissions = query.order_by(ProjectSubmission.submitted_at.desc()).all()
    
    return jsonify({
      "success": True,
      "submissions": [s.to_dict() for s in submissions]
    }), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/submissions", methods=["GET"])
@require_student
def my_submissions(user):
  """Get all of student's submissions"""
  try:
    submissions = ProjectSubmission.query.filter_by(
      student_id=user.id
    ).order_by(ProjectSubmission.submitted_at.desc()).all()
    
    return jsonify({
      "success": True,
      "submissions": [s.to_dict() for s in submissions]
    }), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/submissions/<int:submission_id>/content", methods=["GET"])
@require_auth
def get_submission_content(user, submission_id):
  """Get submission file content for viewing"""
  try:
    submission = ProjectSubmission.query.get_or_404(submission_id)
    
    # Students can only view their own, mentors/managers can view any
    if user.role == UserRole.STUDENT and submission.student_id != user.id:
      return jsonify({"success": False, "error": "Access denied"}), 403
    
    if not os.path.exists(submission.file_path):
      return jsonify({"success": False, "error": "File not found"}), 404
    
    # Read file content
    try:
      with open(submission.file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    except UnicodeDecodeError:
      # If UTF-8 fails, try reading as binary and return base64
      import base64
      with open(submission.file_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')
        return jsonify({
          "success": True,
          "content": content,
          "is_binary": True,
          "filename": submission.filename
        }), 200
    
    return jsonify({
      "success": True,
      "content": content,
      "is_binary": False,
      "filename": submission.filename,
      "mime_type": submission.mime_type
    }), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/submissions/<int:submission_id>/download", methods=["GET"])
@require_auth
def download_submission(user, submission_id):
  """Download a submission file"""
  try:
    from flask import send_file
    
    submission = ProjectSubmission.query.get_or_404(submission_id)
    
    # Students can only download their own, mentors/managers can download any
    if user.role == UserRole.STUDENT and submission.student_id != user.id:
      return jsonify({"success": False, "error": "Access denied"}), 403
    
    if not os.path.exists(submission.file_path):
      return jsonify({"success": False, "error": "File not found"}), 404
    
    return send_file(
      submission.file_path,
      as_attachment=True,
      download_name=submission.filename,
      mimetype=submission.mime_type or 'application/octet-stream'
    )
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/admin/submissions", methods=["GET"])
@require_mentor
def list_all_submissions(user):
  """List all submissions (for mentors/managers)"""
  try:
    project_id = request.args.get('project_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    query = ProjectSubmission.query
    
    if project_id:
      query = query.filter_by(project_id=project_id)
    if student_id:
      query = query.filter_by(student_id=student_id)
    
    submissions = query.order_by(ProjectSubmission.submitted_at.desc()).all()
    
    return jsonify({
      "success": True,
      "submissions": [s.to_dict() for s in submissions]
    }), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/submissions/<int:submission_id>/review", methods=["POST"])
@require_mentor
def review_submission(user, submission_id):
  """Add review notes and update status"""
  try:
    submission = ProjectSubmission.query.get_or_404(submission_id)
    data = request.get_json() or {}
    
    submission.review_notes = data.get('review_notes', '')
    submission.status = data.get('status', submission.status)
    submission.reviewed_by = user.id
    submission.reviewed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
      "success": True,
      "message": "Submission reviewed",
      "submission": submission.to_dict()
    }), 200
  except Exception as e:
    db.session.rollback()
    return jsonify({"success": False, "error": str(e)}), 500


@api.route("/final-project/submit", methods=["POST"])
@require_student
def submit_final_project(user):
  """Student uploads final project (not tied to any specific project)"""
  try:
    from werkzeug.utils import secure_filename
    from flask import send_file
    
    if 'file' not in request.files:
      return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
      return jsonify({"success": False, "error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
      return jsonify({"success": False, "error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'submissions')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    safe_filename = secure_filename(file.filename)
    unique_filename = f"{user.id}_final_{timestamp}_{safe_filename}"
    file_path = os.path.join(uploads_dir, unique_filename)
    
    # Save file
    file.save(file_path)
    file_size = os.path.getsize(file_path)
    
    # Create submission record (project_id is None for final project)
    submission = ProjectSubmission(
      student_id=user.id,
      project_id=None,  # Final project is not tied to any specific project
      filename=file.filename,
      file_path=file_path,
      file_size=file_size,
      mime_type=file.content_type or 'application/octet-stream',
      notes=request.form.get('notes', ''),
      status='submitted',
      submission_type='final_project'
    )
    db.session.add(submission)
    db.session.commit()
    
    return jsonify({
      "success": True,
      "message": "Final project submitted successfully",
      "submission": submission.to_dict()
    }), 201
  except Exception as e:
    db.session.rollback()
    import traceback
    error_msg = str(e)
    traceback.print_exc()
    print(f"Error submitting final project: {error_msg}")
    return jsonify({"success": False, "error": error_msg}), 500


@api.route("/final-project/submissions", methods=["GET"])
@require_student
def my_final_project_submissions(user):
  """Get student's final project submissions"""
  try:
    submissions = ProjectSubmission.query.filter_by(
      student_id=user.id,
      submission_type='final_project'
    ).order_by(ProjectSubmission.submitted_at.desc()).all()
    
    return jsonify({
      "success": True,
      "submissions": [s.to_dict() for s in submissions]
    }), 200
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500

