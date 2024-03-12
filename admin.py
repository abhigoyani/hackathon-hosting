import sys
from models import User
from database import SessionLocal

db = SessionLocal()


def handle_args(args):
    if len(args) != 3:
        print("Error: Invalid number of arguments.")
        return

    action = args[1]
    user_id = args[2]

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        print(f"Error: No user found with id {user_id}.")
        return

    if action == 'add':
        user.admin = True
    elif action == 'remove':
        user.admin = False
    else:
        print("Error: Invalid action. Please use 'add' or 'remove'.")
        return

    db.commit()


if __name__ == "__main__":
    handle_args(sys.argv)
