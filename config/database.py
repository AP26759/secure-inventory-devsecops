from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app"""
    # Get database path from environment or use default
    db_path = os.getenv('DATABASE_PATH', 'library.db')
    
    # Use absolute path to place database in backend root directory
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), db_path)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the app with the database
    db.init_app(app)
    
    # Create all tables
    with app.app_context():
        db.create_all()
    
    return db