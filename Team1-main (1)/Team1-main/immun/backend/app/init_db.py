from app import create_app, db
from app.models import User

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'  # updated to use role instead of is_admin
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin account created!")
        else:
            print("Admin account already exists!")

if __name__ == '__main__':
    init_db()
