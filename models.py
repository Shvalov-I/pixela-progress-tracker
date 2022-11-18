from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, MetaData
from sqlalchemy.orm import declarative_base, relationship, Session, sessionmaker

engine = create_engine('sqlite:///pixela_tracker_data.db')
Base = declarative_base()


class Users(Base):
    __tablename__ = 'pixela_users'
    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    token = Column(String(50))
    graphs = relationship("Graphs")

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}"


class Graphs(Base):
    __tablename__ = 'pixela_users_graphs'
    id = Column(Integer, primary_key=True)
    graph_name = Column(String(30))
    user_id = Column(Integer, ForeignKey('pixela_users.id'))


Base.metadata.create_all(engine)

# with Session(engine) as session:
#     session.begin()
#     user_1 = Users(username="CJoker", token="sdfasdf")
#     graph_1 = Graphs(graph_name='graph1', user_id=1)
#     graph_2 = Graphs(graph_name='graph2', user_id=2)
#     session.add(user_1)
#     session.add(graph_1)
#     session.add(graph_2)
#     session.commit()

