from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, ImmunizationRecord, db
import os
from werkzeug.utils import secure_filename

records_bp = Blueprint('records', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@records_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_record():
    current_user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, f"{current_user_id}_{filename}")
    file.save(file_path)
    
    data = request.form
    record = ImmunizationRecord(
        user_id=current_user_id,
        vaccine_name=data['vaccine_name'],
        date_administered=data['date_administered'],
        next_due_date=data.get('next_due_date'),
        provider=data.get('provider'),
        document_path=file_path
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'message': 'Record uploaded successfully'}), 201

@records_bp.route('/my-records', methods=['GET'])
@jwt_required()
def get_user_records():
    current_user_id = get_jwt_identity()
    records = ImmunizationRecord.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([{
        'id': record.id,
        'vaccine_name': record.vaccine_name,
        'date_administered': record.date_administered.isoformat(),
        'next_due_date': record.next_due_date.isoformat() if record.next_due_date else None,
        'provider': record.provider,
        'document_path': record.document_path,
        'created_at': record.created_at.isoformat()
    } for record in records]), 200

@records_bp.route('/all-records', methods=['GET'])
@jwt_required()
def get_all_records():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
        
    records = ImmunizationRecord.query.all()
    
    return jsonify([{
        'id': record.id,
        'user_id': record.user_id,
        'vaccine_name': record.vaccine_name,
        'date_administered': record.date_administered.isoformat(),
        'next_due_date': record.next_due_date.isoformat() if record.next_due_date else None,
        'provider': record.provider,
        'document_path': record.document_path,
        'created_at': record.created_at.isoformat()
    } for record in records]), 200

@records_bp.route('/document/<int:record_id>', methods=['GET'])
@jwt_required()
def get_document(record_id):
    current_user_id = get_jwt_identity()
    record = ImmunizationRecord.query.get_or_404(record_id)
    
    if not record.user_id == current_user_id:
        user = User.query.get(current_user_id)
        if not user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
    
    return send_file(record.document_path) 