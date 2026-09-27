from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from config.database import db
from models.models import Book, AuditLog
from datetime import datetime
from sqlalchemy import or_

inventory_bp = Blueprint('inventory', __name__)

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

@inventory_bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    try:
        # Get query parameters for filtering
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        # Build query
        query = Book.query
        
        if search:
            query = query.filter(
                or_(
                    Book.title.ilike(f'%{search}%'),
                    Book.author.ilike(f'%{search}%'),
                    Book.isbn.ilike(f'%{search}%')
                )
            )
        
        if category:
            query = query.filter_by(category=category)
        
        # Get total count
        total = query.count()
        
        # Get books with pagination
        books_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        books = [book.to_dict() for book in books_paginated.items]
        
        # Log the read action
        user_id = int(get_jwt_identity())
        audit_log = AuditLog(
            user_id=user_id,
            action='read',
            resource_type='book',
            details={'search': search, 'category': category, 'page': page}
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'books': books,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/books', methods=['POST'])
@jwt_required()
@require_librarian()
def add_book():
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['title', 'author', 'isbn', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if book with same ISBN already exists
        existing_book = Book.query.filter_by(isbn=data['isbn']).first()
        if existing_book:
            return jsonify({'error': 'Book with this ISBN already exists'}), 409
        
        # Create new book
        book = Book(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            category=data['category'],
            quantity=data.get('quantity', 1),
            location=data.get('location', '')
        )
        
        db.session.add(book)
        db.session.commit()
        
        # Log the creation
        user_id = int(get_jwt_identity())
        audit_log = AuditLog(
            user_id=user_id,
            action='create',
            resource_type='book',
            resource_id=str(book.id),
            details={'title': book.title, 'isbn': book.isbn}
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': 'Book added successfully',
            'book_id': book.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
@require_librarian()
def update_book(book_id):
    try:
        data = request.get_json()
        
        # Check if book exists
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Prepare update data
        allowed_fields = ['title', 'author', 'isbn', 'category', 'quantity', 'location']
        updated_fields = []
        
        for field in allowed_fields:
            if field in data:
                updated_fields.append(field)
                setattr(book, field, data[field])
        
        if not updated_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        book.updated_at = datetime.utcnow()
        
        # Update available quantity if total quantity changed
        if 'quantity' in data:
            old_quantity = book.quantity
            new_quantity = data['quantity']
            available_quantity = book.available_quantity
            
            # Adjust available quantity proportionally
            if old_quantity > 0:
                book.available_quantity = max(0, available_quantity + (new_quantity - old_quantity))
            else:
                book.available_quantity = new_quantity
        
        db.session.commit()
        
        # Log the update
        user_id = int(get_jwt_identity())
        audit_log = AuditLog(
            user_id=user_id,
            action='update',
            resource_type='book',
            resource_id=str(book_id),
            details={'updated_fields': updated_fields, 'title': book.title}
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'message': 'Book updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
@require_librarian()
def delete_book(book_id):
    try:
        # Check if book exists
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Store book details before deletion
        book_title = book.title
        book_isbn = book.isbn
        
        # Delete book
        db.session.delete(book)
        db.session.commit()
        
        # Log the deletion
        user_id = int(get_jwt_identity())
        audit_log = AuditLog(
            user_id=user_id,
            action='delete',
            resource_type='book',
            resource_id=str(book_id),
            details={'title': book_title, 'isbn': book_isbn}
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({'message': 'Book deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    try:
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        return jsonify({'book': book.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    try:
        # Get distinct categories from books
        categories = db.session.query(Book.category).distinct().all()
        categories = [cat[0] for cat in categories]
        
        return jsonify({'categories': categories}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500