from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager # type: ignore
from datetime import datetime
from app import db






class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'medecin', 'patient'

    dossier = db.relationship('DossierPatient', backref='patient', uselist=False)
    irm_images = db.relationship('IRMImage', backref='patient', cascade="all, delete", lazy=True)
    notifications = db.relationship('Notification', backref='user', cascade="all, delete", lazy=True)


class IRMImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prediction = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    confirmed_by_medecin = db.Column(db.Boolean, default=False)
    valid_image = db.Column(db.Boolean, default=True)
    commentaire_medecin = db.Column(db.Text, nullable=True)
    confirmed_result = db.Column(db.String(100), nullable=True)
    




class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)


class DossierPatient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    notes = db.Column(db.Text)
