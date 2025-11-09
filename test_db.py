from database import SessionLocal, User, init_db

def main():
    # Make sure tables exist
    init_db()

    # Open a session
    session = SessionLocal()

    try:
        # Run a simple query
        users = session.query(User).all()
        print("Database connection successful!")
        print(f"Found {len(users)} users in the table.")
    except Exception as e:
        print("Database connection failed:", e)
    finally:
        session.close()

if __name__ == "__main__":
    main()
