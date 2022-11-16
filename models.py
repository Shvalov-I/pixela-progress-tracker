from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'Pixela_User'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    token = Column(String(50), unique=True)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}"
