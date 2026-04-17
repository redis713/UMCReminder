from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


task_user = db.Table(
    "task_user",
    db.Column("task_id", db.Integer, db.ForeignKey("task.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    users = db.relationship(
        "User",
        secondary=task_user,
        back_populates="tasks"
    )

    def is_due_soon(self):
        now = datetime.utcnow()
        return (self.deadline - now).days <= 3 and not self.completed


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    #telegramid = db.Column(db.String(50), nullable=True)  # id чата для напоминаний
    email = db.Column(db.String(120), nullable=True)       # вдруг захочешь email тоже

    tasks = db.relationship(
        "Task",
        secondary=task_user,
        back_populates="users"
    )


