from src.web import create_app, db
from src.web.models import User

app = create_app()

with app.app_context():
    # Check if the user already exists
    test_user = User.query.filter_by(username='testuser').first()
    if test_user is None:
        # Create a new test user
        new_user = User(username='testuser', email='testuser@example.com')
        db.session.add(new_user)
        db.session.commit()
        print("Test user created successfully.")
    else:
        print("Test user already exists.")

    # Verify the user was added
    users = User.query.all()
    print(f"Total number of users: {len(users)}")