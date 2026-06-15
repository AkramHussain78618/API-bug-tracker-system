from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)


class Bug(db.Model):
    __tablename__ = "bug"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(50))

    bug_source = db.Column(db.String(100))
    status = db.Column(db.String(50), default="Open")

    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    assigned_to_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )
    assigned_to = db.relationship(
    "User",
    foreign_keys=[assigned_to_id]
)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    comments = db.relationship(
        "Comment",
        backref="bug",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)

    comment = db.Column(db.Text, nullable=False)

    bug_id = db.Column(
        db.Integer,
        db.ForeignKey("bug.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )