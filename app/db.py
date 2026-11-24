from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase
from app.config import settings
url=settings.database_url or 'sqlite:///./careerintel.db'
engine=create_engine(url,connect_args={'check_same_thread':False} if url.startswith('sqlite') else {},pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
class Base(DeclarativeBase):pass
def get_db():
 db=SessionLocal()
 try:yield db
 finally:db.close()
