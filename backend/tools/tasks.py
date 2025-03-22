from tools.workers import celery
from celery.schedules import crontab
from datetime import timedelta, datetime
from models import *
from tools.mailer import send_email
from flask import render_template

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(10.0, mul.s(21, 2), name='multiply every 10 seconds')
    # sender.add_periodic_task(crontab(hour=10, minute=00), send_daily_reminder.s(), name='Daily Reminder at 10:00')
    # sender.add_periodic_task(30.0, send_daily_reminder.s(), name='Daily Reminder at 10:00')
    sender.add_periodic_task(30.0, send_monthly_report.s(), name='Monthly report every 30 seconds')
    # sender.add_periodic_task(crontab(day=1, hour=0, minute=0), send_monthly_report.s(), name='Monthly report every month')


@celery.task
def add(x, y):
    return x + y

@celery.task
def mul(x, y):
    return x * y


@celery.task
#send daily reminders to users who haven't logged in since past 24 hours
def send_daily_reminder():
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    inactive_users = User.query.filter(User.lastLoggedIn < twenty_four_hours_ago).filter(User.role == 'user').all()

    count = 0
    for user in inactive_users:
        formatted_last_logged_in = user.lastLoggedIn.strftime('%Y-%m-%d %H:%M:%S')
        message = f'You are receiving this mail as you haven\'t logged in for past 24 hours. An your last loggedin time was {formatted_last_logged_in}. Please keep shopping in our app!'
        html = render_template('daily_reminder.html', user=user, message=message)
        send_email(user.email, "Daily Reminder", html)
        count += 1
    return f'Reminder sent to {count} users'

@celery.task
def send_monthly_report():
    users = User.query.filter(User.role == 'user').all()
    one_month_ago = datetime.now() - timedelta(days=30)
    
    for user in users:
        user_orders = Order.query.filter_by(user_id = user.id).filter(Order.order_date > one_month_ago).all()
        order_details = []
        total_amount_spent = 0
        if not user_orders:
            continue
        for order in user_orders:
            order_details.append({
                'order_date': order.order_date,
                'product_names': [item.product.name for item in order.order_items],
                'total_order_value': order.total_amount
            })
            total_amount_spent += order.total_amount

        html = render_template('monthly_report.html', user=user, order_details=order_details, total_amount_spent=total_amount_spent)
        send_email(user.email, "Monthly Report", html)

    return 'Report sent to users'