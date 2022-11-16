from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = 'pixela_users'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    token = Column(String(50), unique=True)
    graphs = relationship("Graphs", back_populates='user')
    def __repr__(self):
        return f"User(id={self.id}, username={self.username}"


class Graphs(Base):
    __tablename__ = 'pixela_users_graphs'
    id = Column(Integer, primary_key=True)
    graph_name = Column(String(30))
    user = relationship("Users", back_populates='graphs')
    user_id = Column(Integer, ForeignKey('pixela_users.id'))
