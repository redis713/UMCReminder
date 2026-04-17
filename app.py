from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Task, User
from config import Config
from flask_migrate import Migrate
#from scheduler import init_scheduler
from flask import jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def index():
    tasks = Task.query.order_by(Task.deadline).all()
    users = User.query.all()
    return render_template("index.html", tasks=tasks, users=users)


@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        #telegramid = request.form['telegramid']
        email = request.form['email']

        #user = User(name=name, telegramid=telegramid, email=email)
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_user.html')


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get(user_id)

    if request.method == 'POST':
        user.name = request.form['name']
        #user.telegramid = request.form['telegramid']
        user.email = request.form['email']

        db.session.commit()
        return redirect(url_for('users_list'))

    return render_template('edit_user.html', user=user)


@app.route('/users_list')
def users_list():
    users = User.query.all()
    return render_template('users_list.html', users=users)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('users_list'))



@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%dT%H:%M')
        user_ids = request.form.getlist('user_ids')  # список id из формы

        task = Task(title=title, description=description, deadline=deadline)
        for uid in user_ids:
            user = User.query.get(int(uid))
            if user:
                task.users.append(user)

        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('add_task.html', users=users)


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get(task_id)
    users = User.query.all()

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%dT%H:%M')
        user_ids = request.form.getlist('user_ids')

        task.users = User.query.filter(User.id.in_(user_ids)).all()

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_task.html', task=task, users=users)


@app.route('/done/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/api/tasks')
def api_tasks():
    now = datetime.utcnow()
    future = now + timedelta(days=3)

    tasks = Task.query.filter(
        Task.completed == False,
        Task.deadline <= future
    ).all()

    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "deadline": t.deadline.isoformat(),
            "users": [u.name for u in t.users]
        }
        for t in tasks
    ])


if __name__ == '__main__':
    #with app.app_context():
    #    db.create_all()
    #init_scheduler(app)
    app.run(debug=True)
