from flask import Flask
from flask_mail import Mail, Message
from celery_setup import make_celery

app = Flask(__name__)
app.config.from_object('config')

celery = make_celery(app)

mail = Mail(app)

@celery.task
def send_contract_email(recipient, subject, body):
    with app.app_context():
        msg = Message(subject, recipients=[recipient], body=body)
        mail.send(msg)
