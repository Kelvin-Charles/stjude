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


api = Blueprint("api", __name__)


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
    resources = (
      Resource.query.filter_by(is_active=True)
      .order_by(Resource.created_at.desc())
      .all()
    )
    return jsonify(
      {"success": True, "resources": [r.to_dict() for r in resources]}
    ), 200
  except Exception as e:
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

