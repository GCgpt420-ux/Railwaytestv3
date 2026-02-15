from sqlalchemy import select
from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models import User

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

def main():
    db = SessionLocal()
    try:
        demo_email = settings.DEMO_EMAIL
        u = db.scalar(select(User).where(User.email == demo_email))
        if not u:
            u = User(
                name="Demo User",
                email=demo_email,
                phone="123456789",
                is_active=True,
                is_admin=True,
            )
            db.add(u)
            db.commit()
            print(f"✅ Usuario demo creado (id={u.id}, email={demo_email}, is_admin={u.is_admin})")
        else:
            if not getattr(u, "is_admin", False):
                u.is_admin = True
                db.add(u)
                db.commit()
            print(f"✅ Usuario demo ya existe (id={u.id}, email={demo_email}, is_admin={u.is_admin})")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()