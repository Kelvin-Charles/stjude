from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum


db = SQLAlchemy()


class UserRole(enum.Enum):
  STUDENT = "student"
  MENTOR = "mentor"
  MANAGER = "manager"


class User(db.Model):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False, index=True)
  email = db.Column(db.String(120), unique=True, nullable=False, index=True)
  password_hash = db.Column(db.String(255), nullable=False)
  full_name = db.Column(db.String(200), nullable=False)
  gender = db.Column(db.String(10))  # 'girl' or 'boy'
  batch = db.Column(db.String(50))  # V1, V2, V3
  role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  is_active = db.Column(db.Boolean, default=True)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def to_dict(self):
    return {
      "id": self.id,
      "username": self.username,
      "email": self.email,
      "full_name": self.full_name,
      "gender": self.gender,
      "batch": self.batch,
      "role": self.role.value,
      "created_at": self.created_at.isoformat() if self.created_at else None,
      "is_active": self.is_active,
    }


class Project(db.Model):
  __tablename__ = "projects"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(200), nullable=False, unique=True)
  description = db.Column(db.Text)
  project_path = db.Column(db.String(500))
  difficulty_level = db.Column(db.String(50))
  estimated_time = db.Column(db.Integer)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  is_active = db.Column(db.Boolean, default=True)

  progress_records = db.relationship("ProjectProgress", backref="project", lazy=True, cascade="all, delete-orphan")
  steps = db.relationship("ProjectStep", backref="project", lazy=True, cascade="all, delete-orphan")

  def to_dict(self):
    return {
      "id": self.id,
      "name": self.name,
      "description": self.description,
      "project_path": self.project_path,
      "difficulty_level": self.difficulty_level,
      "estimated_time": self.estimated_time,
      "created_at": self.created_at.isoformat() if self.created_at else None,
      "is_active": self.is_active,
    }


class ProjectProgress(db.Model):
  __tablename__ = "project_progress"

  id = db.Column(db.Integer, primary_key=True)
  student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
  status = db.Column(db.String(50), default="not_started")
  progress_percentage = db.Column(db.Integer, default=0)
  started_at = db.Column(db.DateTime)
  completed_at = db.Column(db.DateTime)
  notes = db.Column(db.Text)
  mentor_feedback = db.Column(db.Text)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  __table_args__ = (db.UniqueConstraint("student_id", "project_id", name="unique_student_project"),)

  def to_dict(self):
    return {
      "id": self.id,
      "student_id": self.student_id,
      "project_id": self.project_id,
      "status": self.status,
      "progress_percentage": self.progress_percentage,
      "started_at": self.started_at.isoformat() if self.started_at else None,
      "completed_at": self.completed_at.isoformat() if self.completed_at else None,
      "notes": self.notes,
      "mentor_feedback": self.mentor_feedback,
      "updated_at": self.updated_at.isoformat() if self.updated_at else None,
    }


class ProjectStep(db.Model):
  __tablename__ = "project_steps"

  id = db.Column(db.Integer, primary_key=True)
  project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
  order_index = db.Column(db.Integer, nullable=False)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=False)
  code_snippet = db.Column(db.Text)  # JSON string with multiple code examples
  full_code = db.Column(db.Text)  # Complete program code (hidden by default)
  is_released = db.Column(db.Boolean, default=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

  questions = db.relationship("ProjectStepQuestion", backref="step", lazy=True, cascade="all, delete-orphan")

  __table_args__ = (db.UniqueConstraint("project_id", "order_index", name="unique_step_order_per_project"),)

  def to_dict(self, include_questions=False):
    data = {
      "id": self.id,
      "project_id": self.project_id,
      "order_index": self.order_index,
      "title": self.title,
      "content": self.content,
      "code_snippet": self.code_snippet,
      "full_code": self.full_code,
      "is_released": self.is_released,
      "created_at": self.created_at.isoformat() if self.created_at else None,
    }
    if include_questions:
      data["questions"] = [q.to_dict() for q in self.questions]
    return data


class ProjectStepQuestion(db.Model):
  __tablename__ = "project_step_questions"

  id = db.Column(db.Integer, primary_key=True)
  step_id = db.Column(db.Integer, db.ForeignKey("project_steps.id"), nullable=False, index=True)
  prompt = db.Column(db.Text, nullable=False)
  option_a = db.Column(db.String(255), nullable=False)
  option_b = db.Column(db.String(255), nullable=False)
  option_c = db.Column(db.String(255))
  option_d = db.Column(db.String(255))
  correct_option = db.Column(db.String(1), nullable=False)
  points = db.Column(db.Integer, default=1)

  answers = db.relationship("StudentStepAnswer", backref="question", lazy=True, cascade="all, delete-orphan")

  def to_dict(self):
    return {
      "id": self.id,
      "step_id": self.step_id,
      "prompt": self.prompt,
      "options": {
        "A": self.option_a,
        "B": self.option_b,
        "C": self.option_c,
        "D": self.option_d,
      },
      "points": self.points,
    }


class StudentStepAnswer(db.Model):
  __tablename__ = "student_step_answers"

  id = db.Column(db.Integer, primary_key=True)
  student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
  question_id = db.Column(db.Integer, db.ForeignKey("project_step_questions.id"), nullable=False, index=True)
  selected_option = db.Column(db.String(1), nullable=False)
  is_correct = db.Column(db.Boolean, default=False)
  points_awarded = db.Column(db.Integer, default=0)
  answered_at = db.Column(db.DateTime, default=datetime.utcnow)

  __table_args__ = (db.UniqueConstraint("student_id", "question_id", name="unique_answer_per_question"),)

  def to_dict(self):
    return {
      "id": self.id,
      "student_id": self.student_id,
      "question_id": self.question_id,
      "selected_option": self.selected_option,
      "is_correct": self.is_correct,
      "points_awarded": self.points_awarded,
      "answered_at": self.answered_at.isoformat() if self.answered_at else None,
    }


class Resource(db.Model):
  __tablename__ = "resources"

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=False)
  description = db.Column(db.Text)
  category = db.Column(db.String(100))
  created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  is_active = db.Column(db.Boolean, default=True)

  creator = db.relationship("User", backref="created_resources")

  def to_dict(self):
    return {
      "id": self.id,
      "title": self.title,
      "content": self.content,
      "description": self.description,
      "category": self.category,
      "created_by": self.created_by,
      "creator_name": self.creator.full_name if self.creator else None,
      "created_at": self.created_at.isoformat() if self.created_at else None,
      "updated_at": self.updated_at.isoformat() if self.updated_at else None,
      "is_active": self.is_active,
    }


class ProjectSubmission(db.Model):
  __tablename__ = "project_submissions"

  id = db.Column(db.Integer, primary_key=True)
  student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
  project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True, index=True)  # Nullable for final project submissions
  filename = db.Column(db.String(500), nullable=False)
  file_path = db.Column(db.String(1000), nullable=False)
  file_size = db.Column(db.Integer)  # Size in bytes
  mime_type = db.Column(db.String(100))
  notes = db.Column(db.Text)
  submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
  reviewed_at = db.Column(db.DateTime)
  reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"))
  review_notes = db.Column(db.Text)
  status = db.Column(db.String(50), default="submitted")  # submitted, reviewed, approved, needs_revision
  submission_type = db.Column(db.String(50), default="project")  # project, final_test

  student = db.relationship("User", foreign_keys=[student_id], backref="submissions")
  project = db.relationship("Project", backref="submissions")
  reviewer = db.relationship("User", foreign_keys=[reviewed_by])

  def to_dict(self):
    return {
      "id": self.id,
      "student_id": self.student_id,
      "student_name": self.student.full_name if self.student else None,
      "project_id": self.project_id,
      "project_name": self.project.name if self.project else None,
      "filename": self.filename,
      "file_path": self.file_path,
      "file_size": self.file_size,
      "mime_type": self.mime_type,
      "notes": self.notes,
      "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
      "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
      "reviewed_by": self.reviewed_by,
      "reviewer_name": self.reviewer.full_name if self.reviewer else None,
      "review_notes": self.review_notes,
      "status": self.status,
      "submission_type": self.submission_type,
    }

