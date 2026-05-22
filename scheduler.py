from datetime import date, datetime
import calendar

from models import db, RecurringTask, Task


def write_month(month):
    months_words = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    return ' (' + months_words[month] + ')'


'''
# без сохранения времени, поменяет на 00:00
def add_months(d, months):
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day)
'''


#с сохранением времени
def add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])

    return dt.replace(year=year, month=month, day=day)


def generate_tasks():
    today = datetime.combine(date.today(), datetime.min.time())

    recurring_list = RecurringTask.query.filter(
        RecurringTask.next_run <= today
    ).all()

    for r in recurring_list:
        # цикл на случай если система долго стояла мертвой. насоздает задач за все время без активности
        while r.next_run <= today:
            r.next_run = add_months(r.next_run, r.interval_months) # сначала прибавляем интервал и уже потом на новую дату создаем задачу

            month = r.next_run.month

            task = Task(
                title=r.title + write_month(month),
                description=r.description,
                deadline=r.next_run,
                recurring_id=r.id
            )

            task.users = r.users  # если у тебя есть связь
            db.session.add(task)

        #r.next_run = add_months(r.next_run, r.interval_months)

    db.session.commit()