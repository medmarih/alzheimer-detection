# app/routes/auth_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request  # type: ignore
from app import db, bcrypt
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user  # type: ignore

auth_bp = Blueprint('auth', __name__)

# Vérifie si c'est un patient qui s'inscrit (on ne veut pas que médecin/admin s'inscrivent seuls)
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Nom d’utilisateur ou email déjà utilisé.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password, role='patient')
        db.session.add(new_user)
        db.session.commit()

        flash('Compte patient créé avec succès. Vous pouvez vous connecter.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Rediriger l'utilisateur vers son dashboard en fonction de son rôle
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.role == 'medecin':
            return redirect(url_for('medecin.medecin_dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient.patient_dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user:
            print(f"Utilisateur trouvé : {user.email}")
        else:
            print(f"Aucun utilisateur trouvé avec l'email : {email}")

        # Bypass temporaire pour admin
        if user and user.role == 'admin' and user.email == 'admin@gmail.com':
            login_user(user)
            
            return redirect(url_for('admin.admin_dashboard'))

        # Vérification normale du mot de passe
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Connexion réussie.', 'success')

            # Rediriger vers le dashboard en fonction du rôle de l'utilisateur
            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role == 'medecin':
                return redirect(url_for('medecin.medecin_dashboard'))
            elif user.role == 'patient':
                return redirect(url_for('patient.patient_dashboard'))
        else:
            flash('Email ou mot de passe invalide.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))


# Redirige vers le bon dashboard selon le rôle
@auth_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif current_user.role == 'medecin':
        return redirect(url_for('medecin.medecin_dashboard'))
    elif current_user.role == 'patient':
        return redirect(url_for('patient.patient_dashboard'))
    else:
        flash('Rôle inconnu.', 'danger')
        return redirect(url_for('auth.logout'))


@auth_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    else:
        return redirect(url_for('auth.login'))
