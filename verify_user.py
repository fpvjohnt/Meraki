from src.web import create_app, db
from src.web.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    if user:
        print(f"User found: Username: {user.username}, Email: {user.email}")
    else:
        print("Test user not found in the database.")