from functools import wraps
from flask import abort # type: ignore
from flask_login import current_user # type: ignore
from app.models import Notification, db

from flask import current_app
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def send_notification(user_id, message):
    notif = Notification(user_id=user_id, message=message)
    db.session.add(notif)
    db.session.commit()
def send_email(subject, recipients, body):
    from app import mail
    from flask_mail import Message
    msg = Message(subject, recipients=recipients, body=body)
    mail.send(msg)