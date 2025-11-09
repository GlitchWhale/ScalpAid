from database import SessionLocal, User, init_db
from werkzeug.security import generate_password_hash

def main():
    init_db()
    session = SessionLocal()

    try:
        # Insert a test user
        new_user = User(
            email="test@example.com",
            password_hash=generate_password_hash("secret123")
        )
        session.add(new_user)
        session.commit()

        # Query back
        users = session.query(User).all()
        print(" Database connection successful!")
        for u in users:
            print(f"User: {u.email}, Created: {u.created_at}")
    except Exception as e:
        print(" Database connection failed:", e)
    finally:
        session.close()

if __name__ == "__main__":
    main()
