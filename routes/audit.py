from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from config.database import db
from models.models import AuditLog, User
from datetime import datetime, timedelta
from sqlalchemy import func

audit_bp = Blueprint('audit', __name__)

def require_librarian():
    """Decorator to check if user has librarian role"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != 'librarian':
                return jsonify({'error': 'Librarian access required'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@audit_bp.route('/logs', methods=['GET'])
@jwt_required()
@require_librarian()
def get_audit_logs():
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        user_id = request.args.get('user_id', '')
        action = request.args.get('action', '')
        resource_type = request.args.get('resource_type', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Build query
        query = AuditLog.query
        
        if user_id:
            query = query.filter_by(user_id=int(user_id))
        
        if action:
            query = query.filter_by(action=action)
        
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        # Date range filter
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.timestamp >= start)
        
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.timestamp <= end)
        
        # Get total count
        total = query.count()
        
        # Get logs with pagination, sorted by timestamp (newest first)
        logs_paginated = query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logs = []
        for log in logs_paginated.items:
            log_dict = log.to_dict()
            
            # Get username for user_id
            if log.user_id:
                user = User.query.get(log.user_id)
                log_dict['username'] = user.username if user else 'Unknown'
            else:
                log_dict['username'] = 'Unknown'
            
            logs.append(log_dict)
        
        # Log this audit view action
        current_user_id = int(get_jwt_identity())
        audit_log = AuditLog(
            user_id=current_user_id,
            action='read',
            resource_type='audit_log',
            details={'page': page, 'filters': {k: v for k, v in request.args.items()}}
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'logs': logs,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@audit_bp.route('/logs/summary', methods=['GET'])
@jwt_required()
@require_librarian()
def get_audit_summary():
    try:
        # Get statistics for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Total actions in last 30 days
        total_actions = AuditLog.query.filter(
            AuditLog.timestamp >= thirty_days_ago
        ).count()
        
        # Actions by type
        actions_by_type = db.session.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= thirty_days_ago
        ).group_by(AuditLog.action).order_by(func.count(AuditLog.id).desc()).all()
        
        actions_by_type = [{'_id': action, 'count': count} for action, count in actions_by_type]
        
        # Resource types accessed
        resources_by_type = db.session.query(
            AuditLog.resource_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= thirty_days_ago
        ).group_by(AuditLog.resource_type).order_by(func.count(AuditLog.id).desc()).all()
        
        resources_by_type = [{'_id': resource, 'count': count} for resource, count in resources_by_type]
        
        # Most active users
        active_users = db.session.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= thirty_days_ago
        ).group_by(AuditLog.user_id).order_by(func.count(AuditLog.id).desc()).limit(10).all()
        
        # Enrich user data with usernames
        active_users_list = []
        for user_id, count in active_users:
            user = User.query.get(user_id)
            active_users_list.append({
                '_id': user_id,
                'count': count,
                'username': user.username if user else 'Unknown'
            })
        
        return jsonify({
            'total_actions': total_actions,
            'actions_by_type': actions_by_type,
            'resources_by_type': resources_by_type,
            'most_active_users': active_users_list,
            'period': '30 days'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@audit_bp.route('/logs/export', methods=['GET'])
@jwt_required()
@require_librarian()
def export_audit_logs():
    try:
        # Get query parameters for filtering (same as get_audit_logs)
        user_id = request.args.get('user_id', '')
        action = request.args.get('action', '')
        resource_type = request.args.get('resource_type', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Build query
        query = AuditLog.query
        
        if user_id:
            query = query.filter_by(user_id=int(user_id))
        
        if action:
            query = query.filter_by(action=action)
        
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        # Date range filter
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.timestamp >= start)
        
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.timestamp <= end)
        
        # Get all matching logs (limit to 10000 for performance)
        logs_query = query.order_by(AuditLog.timestamp.desc()).limit(10000).all()
        
        logs = []
        for log in logs_query:
            log_dict = log.to_dict()
            
            # Get username for user_id
            if log.user_id:
                user = User.query.get(log.user_id)
                log_dict['username'] = user.username if user else 'Unknown'
            else:
                log_dict['username'] = 'Unknown'
            
            logs.append(log_dict)
        
        # Log the export action
        current_user_id = int(get_jwt_identity())
        audit_log = AuditLog(
            user_id=current_user_id,
            action='export',
            resource_type='audit_log',
            details={'exported_count': len(logs), 'filters': {k: v for k, v in request.args.items()}}
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'logs': logs,
            'exported_count': len(logs),
            'export_timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500