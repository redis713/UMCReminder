from zoneinfo import ZoneInfo
from flask import Flask, render_template, request, redirect, url_for
from models import db, Task, User, RecurringTask
from config import Config
from config_client import ConfigClient
from flask_migrate import Migrate
from flask import jsonify
from datetime import datetime, timedelta, date
from scheduler import generate_tasks, write_month
from sqlalchemy import desc

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
        db.session.add(task)

        for uid in user_ids:
            user = User.query.get(int(uid))
            if user:
                task.users.append(user)

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

@app.route('/recurring_list')
def recurring_list():
    recurring_tasks = RecurringTask.query.all()
    return render_template("recurring_list.html", recurring_tasks=recurring_tasks)

def edit_recurring(rt_id):
    rt = RecurringTask.query.get(rt_id)

    if request.method == 'POST':
        rt.title = request.form['title']
        rt.description = request.form['description']
        rt.interval_months = request.form['interval_months']
        rt.next_run = datetime.strptime(request.form['next_run'], "%Y-%m-%dT%H:%M")




@app.route('/add_recurring', methods=['GET', 'POST'])
def add_recurring():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        interval = int(request.form['interval'])
        #start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d").date()
        start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%dT%H:%M")
        start_date = start_date.replace(tzinfo=ZoneInfo("Asia/Irkutsk")) # чтобы потом сравнивать с текущим временем нормально
        user_ids = request.form.getlist('user_ids')  # список id из формы

        month = start_date.month


        rtask = RecurringTask(
            title=title,
            description=description,
            interval_months=interval,
            next_run=start_date
        )

        db.session.add(rtask)
        db.session.flush()

        task = Task(
            title=title + write_month(month),
            description=description,
            deadline=start_date,
            recurring_id=rtask.id
        )

        db.session.add(task)

        for uid in user_ids:
            user = User.query.get(int(uid))
            if user:
                rtask.users.append(user)
                task.users.append(user)

        db.session.commit()

        return redirect('recurring_list')

    users = User.query.all()
    return render_template('add_recurring.html', users=users)


@app.route('/delete_recurring/<int:rt_id>')
def delete_recurring(rt_id):
    rt = RecurringTask.query.get(rt_id)
    db.session.delete(rt)
    db.session.commit()
    return redirect(url_for('recurring_list'))


@app.route('/api/get_client_info')
def get_client_info():
    return jsonify({
        "check_interval": ConfigClient.CHECK_INTERVAL,
        "width": ConfigClient.WIDTH,
        "height": ConfigClient.HEIGHT,
        "title": ConfigClient.TITLE
    })


@app.route('/api/tasks')
def api_tasks():
    #now = datetime.utcnow()
    now = datetime.now(ZoneInfo('Asia/Irkutsk'))
    future = now + timedelta(days=7)

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


@app.route('/alert_window')
def alert_window():
    #now = datetime.now(ZoneInfo('Asia/Irkutsk'))
    now = datetime.now(ZoneInfo('Asia/Irkutsk')).replace(tzinfo=None)
    future = now + timedelta(days=7)

    tasks = Task.query.filter(
        Task.completed == False,
        Task.deadline <= future
    ).order_by(Task.deadline).all()

    prepared_tasks = []

    for task in tasks:

        delta = task.deadline - now
        days_left = delta.total_seconds() / 86400

        if days_left < 0:
            priority = "overdue"
        elif days_left <= 1:
            priority = "danger"
        elif days_left <= 3:
            priority = "warning"
        else:
            priority = "safe"

        prepared_tasks.append({
            "task": task,
            "priority": priority
        })

    print(prepared_tasks)


    return render_template('alert_window.html', tasks=prepared_tasks)




@app.before_request
def run_scheduler():
    generate_tasks()
    #print('every time')

if __name__ == '__main__':
    #with app.app_context():
    #    db.create_all()
    #init_scheduler(app)
    app.run(debug=True)
