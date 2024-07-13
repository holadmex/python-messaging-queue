import os
import time
from flask import Flask, request, Response
from celery import Celery
from flask_mail import Mail, Message

app = Flask(__name__)

# Flask-Mail configuration for Gmail using SSL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  # Gmail SMTP SSL port
app.config['MAIL_USE_SSL'] = True  # Enable SSL encryption
app.config['MAIL_USERNAME'] = 'ojewumidimeji@gmail.com' # your email here
app.config['MAIL_PASSWORD'] = "ldbl lzvk hvdf sqcq" # your app password

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'pyamqp://guest@localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'

# Initialize Flask-Mail and Celery
mail = Mail(app)

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    celery.autodiscover_tasks(['app'])  # Ensure the app module is discovered
    return celery

celery = make_celery(app)

@celery.task(name='app.send_email')  # Register the task with a specific name
def send_email(to):
    msg = Message("Test Email", sender=app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = "This is a test email."

    try:
        with app.app_context():
            mail.send(msg)
        print(f"Sent email to {to}")
    except Exception as e:
        print(f"Error sending email: {e}")

    return True  # Optionally, return a value indicating success

@app.route("/")
def home():
    return "Welcome to the Messaging System!"

@app.route("/sendmail")
def sendmail():
    to = request.args.get('sendmail')
    if to:
        send_email.delay(to)
        return f'Sending email to {to}...'
    else:
        return 'Error: Missing "sendmail" parameter.'   

@app.route("/talktome")
def talktome():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f'Logged at {current_time}\n'
    log_file = 'logs/messaging_system.log'  # Adjusted to a relative path
    with open(log_file, 'a') as f:
        f.write(log_message)
    return 'Logging message...'

@app.route('/log')
def get_log():
    try:
        with open('logs/messaging_system.log', 'r') as f:
            log_content = f.read()
        return Response(log_content, mimetype='text/plain')
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(debug=True)






