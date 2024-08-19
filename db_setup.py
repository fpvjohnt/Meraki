from src.web import create_app, db
from src.web.models import User  # Import your models here

app = create_app()

print("Application created")

with app.app_context():
    print("Entered app context")
    print("Starting db.create_all()")
    db.create_all()
    print("Finished db.create_all()")

print("Script completed")