import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app # type: ignore
from flask_login import login_required, current_user # type: ignore
from werkzeug.utils import secure_filename # type: ignore
from app.models import IRMImage, db
from app.utils import role_required
from app.ml_model.predict import predict_irm
from app.models import Notification
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
patient_bp = Blueprint('patient', __name__)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@patient_bp.route('/patient/dashboard')
@login_required
@role_required('patient')
def patient_dashboard():
    irm_images = IRMImage.query.filter_by(patient_id=current_user.id).all()
    return render_template('patient/patient_dashboard.html', irm_images=irm_images)

@patient_bp.route('/patient/upload_irm', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def upload_irm():
    if request.method == 'POST':
        if 'irm_image' not in request.files:
            flash('Aucun fichier sélectionné.', 'danger')
            return redirect(request.url)

        file = request.files['irm_image']
        if file.filename == '':
            flash('Aucun fichier sélectionné.', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            filename = f"{timestamp}_{filename}"
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Prédiction avec le modèle IA
            predicted_class, confidence = predict_irm(file_path)

            # Sauvegarde en BDD
            new_irm = IRMImage(
                patient_id=current_user.id,
                filename=filename,
                prediction=predicted_class,
                confidence=confidence,
                confirmed_by_medecin=False
            )
            db.session.add(new_irm)
            db.session.commit()

            flash('Image IRM uploadée avec succès. Votre médecin confirmera bientôt la prédiction.', 'success')
            return redirect(url_for('patient.patient_dashboard'))
        else:
            flash('Format de fichier invalide. (png/jpg/jpeg)', 'danger')
            return redirect(request.url)

    return render_template('patient/upload_irm.html')

@patient_bp.route('/notifications')
@login_required
@role_required('patient')
def mes_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('patient/notifications.html', notifications=notifications)

@patient_bp.route('/patient/mes_irm')
@login_required
@role_required('patient')
def mes_irm():
    irm_images = IRMImage.query.filter_by(patient_id=current_user.id).order_by(IRMImage.uploaded_at.desc()).all()
    return render_template('patient/mes_irm.html', irm_images=irm_images)