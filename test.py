from app import app
from app.models import *
from werkzeug.security import generate_password_hash

if __name__ == "__main__":
    db.create_all()

    role = Role(
        name="super",
        auths=""
    )
    db.session.add(role)
    db.session.commit()

    admin = Admin(
        name="imoocmovie",
        pwd=generate_password_hash("imoocmovie"),
        is_super=0,
        role_id=1
    )
    db.session.add(admin)
    db.session.commit()
