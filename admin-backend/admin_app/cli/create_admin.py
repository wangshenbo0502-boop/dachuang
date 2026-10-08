import argparse
from admin_app.db import Base, engine, SessionLocal
from admin_app.models import AdminAccount
from admin_app.security import hash_password

parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("password")
parser.add_argument("--role", default="super_admin", choices=["super_admin", "operator", "auditor"])
args = parser.parse_args()
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    db.add(AdminAccount(username=args.username, password_hash=hash_password(args.password), role=args.role))
    db.commit()
    print(f"created administrator: {args.username}")
finally:
    db.close()
