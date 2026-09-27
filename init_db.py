#!/usr/bin/env python3
"""
Database initialization script for Streeling University Library
Creates initial users, sample books, and sets up database
"""

from app import create_app
from config.database import db
from models.models import User, Book, AuditLog
from datetime import datetime
import sys

def create_initial_users():
    """Create initial librarian and student users"""
    print("Creating initial users...")
    
    # Check if users already exist
    if User.query.count() > 0:
        print("Users already exist, skipping user creation")
        return None, None
    
    # Create librarian user
    librarian = User(
        username="librarian",
        email="librarian@streeling.edu",
        password="admin123",
        role="librarian"
    )
    
    # Create student user
    student = User(
        username="student",
        email="student@streeling.edu",
        password="student123",
        role="student"
    )
    
    # Insert users
    db.session.add(librarian)
    db.session.add(student)
    db.session.commit()
    
    print(f"✓ Created librarian user: {librarian.username}")
    print(f"✓ Created student user: {student.username}")
    
    return librarian.id, student.id

def create_sample_books(librarian_id):
    """Create sample books in the inventory"""
    print("Creating sample books...")
    
    # Check if books already exist
    if Book.query.count() > 0:
        print("Books already exist, skipping book creation")
        return
    
    sample_books = [
        {
            "title": "The Foundation",
            "author": "Isaac Asimov",
            "isbn": "978-0553293357",
            "category": "Science Fiction",
            "quantity": 5,
            "location": "A1-SF-001"
        },
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "isbn": "978-0441172719",
            "category": "Science Fiction",
            "quantity": 3,
            "location": "A1-SF-002"
        },
        {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "isbn": "978-0061120084",
            "category": "Fiction",
            "quantity": 4,
            "location": "B2-FIC-001"
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "isbn": "978-0452284234",
            "category": "Dystopian Fiction",
            "quantity": 6,
            "location": "B2-FIC-002"
        },
        {
            "title": "Introduction to Algorithms",
            "author": "Thomas H. Cormen",
            "isbn": "978-0262033848",
            "category": "Computer Science",
            "quantity": 2,
            "location": "C3-CS-001"
        },
        {
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "isbn": "978-0132350884",
            "category": "Computer Science",
            "quantity": 3,
            "location": "C3-CS-002"
        },
        {
            "title": "A Brief History of Time",
            "author": "Stephen Hawking",
            "isbn": "978-0553380163",
            "category": "Physics",
            "quantity": 4,
            "location": "D4-PHY-001"
        },
        {
            "title": "The Selfish Gene",
            "author": "Richard Dawkins",
            "isbn": "978-0199291151",
            "category": "Biology",
            "quantity": 2,
            "location": "D4-BIO-001"
        }
    ]
    
    books_inserted = []
    for book_data in sample_books:
        book = Book(
            title=book_data["title"],
            author=book_data["author"],
            isbn=book_data["isbn"],
            category=book_data["category"],
            quantity=book_data["quantity"],
            location=book_data["location"]
        )
        
        db.session.add(book)
        db.session.flush()  # Flush to get the book ID
        
        # Log the book creation
        audit_log = AuditLog(
            user_id=librarian_id,
            action='create',
            resource_type='book',
            resource_id=str(book.id),
            details={'title': book.title, 'isbn': book.isbn, 'initial_setup': True}
        )
        db.session.add(audit_log)
        
        books_inserted.append(book.id)
        print(f"✓ Created book: {book.title}")
    
    db.session.commit()
    return books_inserted

def main():
    """Main initialization function"""
    print("=== Streeling University Library Database Initialization ===")
    print()
    
    try:
        # Create Flask app to get application context
        app = create_app()
        
        with app.app_context():
            print("✓ Database connection successful")
            
            # Drop all tables and recreate them (use with caution)
            # Uncomment the next two lines if you want to reset the database
            # db.drop_all()
            # db.create_all()
            
            # Ensure all tables are created
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Create initial users
            librarian_id, student_id = create_initial_users()
            
            # Create sample books
            if librarian_id:
                create_sample_books(librarian_id)
            
            print()
            print("=== Database initialization completed successfully! ===")
            print()
            print("Default credentials:")
            print("Librarian - Username: librarian, Password: admin123")
            print("Student   - Username: student, Password: student123")
            print()
            print("You can now start the Flask server with: python app.py")
        
    except Exception as e:
        print(f" Database initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
