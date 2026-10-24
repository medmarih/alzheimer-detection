
from flask_login import login_required, current_user # type: ignore
from app.models import User, IRMImage
from app.utils import role_required
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app # type: ignore
from app import db
from app.utils import send_notification
from app.utils import send_email 
from app.models import Notification
from sqlalchemy.orm import joinedload
from flask import render_template

medecin_bp = Blueprint('medecin', __name__)

@medecin_bp.route('/medecin/medecin_dashboard')
@login_required
@role_required('medecin')
def medecin_dashboard():
    # On récupère les IRM non confirmées
    irm_images = IRMImage.query.options(joinedload(IRMImage.patient)).all()
    irm_images = IRMImage.query.filter_by(confirmed_by_medecin=False).all()
    return render_template('medecin/medecin_dashboard.html', irm_images=irm_images)

@medecin_bp.route('/validation_irm')
@login_required
@role_required('medecin')
def validation_irm():
    irm_images = IRMImage.query.filter_by(validated_by_medecin=False).all()
    return render_template('medecin/validation_irm.html', irm_images=irm_images)

@medecin_bp.route('/confirmer/<int:irm_id>/<decision>')
@login_required
@role_required('medecin')
def confirmer_diagnostic(irm_id, decision):
    irm = IRMImage.query.get_or_404(irm_id)
    irm.confirmed_result = decision
    irm.confirmed_by_medecin = True
    db.session.commit()
    patient = irm.patient  # grâce à ForeignKey (relation avec User)
    subject = "Résultat de votre IRM confirmé"
    body = f"Bonjour {patient.username},\n\nVotre IRM a été confirmée par le médecin.\nRésultat : {decision}.\nMerci."
    print(f"[DEBUG] Envoi de mail à : {patient.email}")

    send_email(subject, [patient.email], body)


    message = f"Votre IRM {irm.filename} a été {decision.lower()} par le médecin."
    send_notification(irm.patient_id, message)
    return redirect(url_for('medecin.validation_irm'))

@medecin_bp.route('/historique_validations')
@login_required
@role_required('medecin')
def historique_validations():
    irm_images = IRMImage.query.filter_by(confirmed_by_medecin=True).all()
    return render_template('medecin/historique.html', irm_images=irm_images)

@medecin_bp.route('/patient/<int:patient_id>/historique')
@login_required
@role_required('medecin')
def historique_patient(patient_id):
    patient = User.query.get_or_404(patient_id)
    irm_images = IRMImage.query.filter_by(patient_id=patient.id).order_by(IRMImage.uploaded_at.desc()).all()
    return render_template('medecin/historique_patient.html', patient=patient, irm_images=irm_images)

@medecin_bp.route('/patient/<int:patient_id>/irm')
@login_required
@role_required('medecin')
def voir_patient_irm(patient_id):
    patient = User.query.get_or_404(patient_id)
    irm_images = IRMImage.query.filter_by(patient_id=patient_id).order_by(IRMImage.uploaded_at.desc()).all()
    return render_template('medecin/patient_irm.html', patient=patient, irm_images=irm_images)

@medecin_bp.route('/medecin/notifications')
@login_required
@role_required('medecin')
def medecin_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('medecin/notifications.html', notifications=notifications)

@medecin_bp.route('/medecin/statistiques')
@login_required
@role_required('medecin')
def statistiques():
    total_images = IRMImage.query.count()
    normales = IRMImage.query.filter_by(prediction='normal').count()
    suspectes = IRMImage.query.filter_by(prediction='suspect').count()
    
    return render_template('medecin/statistiques.html', total=total_images, normales=normales, suspectes=suspectes)

@medecin_bp.route('/medecin/confirmer_irm/<int:image_id>', methods=['GET', 'POST'])
@login_required
@role_required('medecin')
def confirmer_irm(image_id):
    irm_image = IRMImage.query.get_or_404(image_id)

    if request.method == 'POST':
        irm_image.confirmed_by_medecin = True
        irm_image.commentaire_medecin = request.form.get('commentaire')
        db.session.commit()
        patient = irm_image.patient  # grâce à ForeignKey (relation avec User)
        subject = "Résultat de votre IRM confirmé"
        body = f"Bonjour {patient.username},\n\nVotre IRM a été confirmée par le médecin.\nRésultat : {irm_image.commentaire_medecin}.\nMerci."
        print(f"[DEBUG] Envoi de mail à : {patient.email}")

        send_email(subject, [patient.email], body)

        # Envoyer une notification au patient
        from app.utils import send_notification
        message = f"Votre IRM du {irm_image.uploaded_at.strftime('%d/%m/%Y')} a été confirmée par le médecin."
        send_notification(user_id=irm_image.patient_id, message=message)

        flash('IRM confirmée et commentaire enregistré.', 'success')
        return redirect(url_for('medecin.medecin_dashboard'))

    return render_template('medecin/confirmer_irm.html', irm_image=irm_image)
@medecin_bp.route('/medecin/liste_patients')
@login_required
@role_required('medecin')
def liste_patients():
    patients = User.query.filter_by(role='patient').all()
    return render_template('medecin/liste_patients.html', patients=patients)
