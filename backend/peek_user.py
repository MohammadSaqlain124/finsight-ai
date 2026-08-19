from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == "sam@example.com").first()
print("Email stored as:  ", user.email)
print("Password stored as:", user.hashed_password)
db.close()