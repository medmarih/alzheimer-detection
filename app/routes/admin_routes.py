from flask import Blueprint, render_template, request, redirect, url_for, flash # type: ignore
from flask_login import login_required # type: ignore
from app.models import User
from app import db, bcrypt
from app.utils import role_required
from sqlalchemy import or_

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    medecins = User.query.filter_by(role='medecin').all()
    patients = User.query.filter_by(role='patient').all()
    return render_template('admin/admin_dashboard.html', medecins=medecins, patients=patients)

@admin_bp.route('/admin/create_medecin', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_medecin():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter(or_(User.username == username, User.email == email)).first()
        if existing_user:
            flash('Nom d’utilisateur ou email déjà utilisé.', 'danger')
            return redirect(url_for('admin.create_medecin'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_medecin = User(username=username, email=email, password=hashed_password, role='medecin')
        db.session.add(new_medecin)
        db.session.commit()

        flash('Médecin créé avec succès.', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/create_medecin.html')
@admin_bp.route('/admin/create_patient', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_patient():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Nom d’utilisateur ou email déjà utilisé.', 'danger')
            return redirect(url_for('admin.create_patient'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_patient = User(username=username, email=email, password=hashed_password, role='patient')
        db.session.add(new_patient)
        db.session.commit()

        flash('Patient créé avec succès.', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/create_patient.html')
@admin_bp.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        role = request.form['role']
        if role in ['patient', 'medecin', 'admin']:
            user.role = role
        db.session.commit()

        flash('Utilisateur mis à jour avec succès.', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/edit_user.html', user=user)
@admin_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé avec succès.', 'success')
    return redirect(url_for('admin.admin_dashboard'))
@admin_bp.route('/admin/view_user/<int:user_id>')
@login_required
@role_required('admin')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/view_user.html', user=user)


