from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


task_user = db.Table(
    "task_user",
    db.Column("task_id", db.Integer, db.ForeignKey("task.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
)

recurring_user = db.Table(
    "recurring_user",
    db.Column("recurring_id", db.Integer, db.ForeignKey("recurring_task.id"), primary_key=True),
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

    recurring_id = db.Column(db.Integer, db.ForeignKey('recurring_task.id'), nullable=True)

    #def is_due_soon(self):
    #    now = datetime.utcnow()
    #    return (self.deadline - now).days <= 3 and not self.completed


class RecurringTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255))
    description = db.Column(db.Text)

    interval_months = db.Column(db.Integer, nullable=False)
    next_run = db.Column(db.DateTime, nullable=False)

    #active = db.Column(db.Boolean, default=True)

    # связь с обычными задачами
    tasks = db.relationship('Task', backref='recurring', lazy=True)

    users = db.relationship(
        "User",
        secondary=recurring_user,
        backref="recurring_tasks"
    )


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


