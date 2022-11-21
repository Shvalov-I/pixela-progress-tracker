import sqlite3
import sqlalchemy.exc
import requests
import datetime as dt
import uuid
from models import Session, Users, Graphs, engine


def success_request(request):
    """
    Makes requests until it succeeds
    :param request:
    :return:
    """
    # Так как в Pixel Api 25% запросов не обрабатываются, если ты не подписчик на патреоне,
    # Поэтому мы повторяем запрос пока он не будет успешный
    success = False
    while not success:
        with requests.Session() as s:
            prepare_req = s.prepare_request(request)
            response = s.send(prepare_req)
            print(response.json())
            success = response.json()['isSuccess']

class PixelaUser:
    """Object for working with the user"""
    PIXEL_ENDPOINT = f"https://pixe.la/v1/users"

    def __init__(self, username: str):
        self.USERNAME = username
        if self.is_exists():
            self.TOKEN = self.get_token()
        else:
            self.TOKEN = None

    def is_exists(self):
        """
        Checking if the user exists
        :return:
        """
        with Session(engine) as session, session.begin():
            # Проверка есть ли пользователь с таким именем в базе данных
            if session.query(Users).filter(Users.username == self.USERNAME).first():
                return True
            else:
                return False

    def get_token(self):
        """
        Returns the user's token or throws an error if the user does not exist.
        :return:
        """
        if self.is_exists():
            with Session(engine) as session, session.begin():
                user = session.query(Users).filter(Users.username == self.USERNAME).first()
                return user.token
        else:
            raise AttributeError(f'User "{self.USERNAME}" do not exists')

    def create_user(self):
        """
        Creates a new user or throws an error if such a user already exists
        :return:
        """
        if not self.is_exists():
            self.TOKEN = str(uuid.uuid4())
            with Session(engine) as session, session.begin():
                new_user = Users(username=self.USERNAME, token=self.TOKEN)
                session.add(new_user)
                session.commit()

            new_user_params = {
                "token": self.TOKEN,
                "username": self.USERNAME,
                "agreeTermsOfService": "yes",
                "notMinor": "yes",
            }

            response = requests.post(url=self.PIXEL_ENDPOINT, json=new_user_params)
            print(response.json())
        else:
            raise AttributeError(f'User "{self.USERNAME}" already exists')

    def delete_user(self):
        """
        Deletes the user or throws an error if the user does not exist
        :return:
        """
        if self.is_exists():
            with Session(engine) as session, session.begin():
                deleted_user = session.query(Users).filter(Users.username == self.USERNAME).first()
                session.delete(deleted_user)

            headers = {
                "X-USER-TOKEN": self.TOKEN,
            }
            # Так как в Pixel Api 25% запросов не обрабатываются, если ты не подписчик на патреоне,
            # Поэтому мы повторяем запрос пока он не будет успешный
            success = False
            while not success:
                response = requests.delete(url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}", headers=headers)
                print(response.json())
                success = response.json()['isSuccess']
        else:
            raise AttributeError(f'User "{self.USERNAME}" do not exists')


class PixelaGraph:
    """Object for working with graphs"""
    PIXEL_ENDPOINT = f"https://pixe.la/v1/users"

    def __init__(self, username: str, token: str, graph_name: str):
        self.USERNAME = username
        self.TOKEN = token
        self.GRAPH_NAME = graph_name
        self.HEADERS = {
            "X-USER-TOKEN": self.TOKEN,
        }

    def is_exists(self):
        """
        Checking if the graph exists
        :return:
        """
        with Session(engine) as session, session.begin():
            # Проверка есть ли у заданного пользователя график с таким именем в базе данных
            user = session.query(Users).filter(Users.username == self.USERNAME).first()
            if self.GRAPH_NAME in [graph.graph_name for graph in user.graphs]:
                return True
            else:
                return False

    def create_graph(self, unit: str, type_of_graph: str = 'int', color: str = 'shibafu',
                     time_zone: str = 'Asia/Novosibirsk'):
        """Create new Pixela graph
        :param unit:
        It is a unit of the quantity recorded in the pixelation graph.
        Ex. commit, kilogram, calory.;
        :param type_of_graph:
        It is the type of quantity to be handled in the graph.
        Only int or float are supported.;
        :param color:
        Defines the display color of the pixel in the pixelation graph.
        shibafu (green), momiji (red), sora (blue), ichou (yellow),
        ajisai (purple) and kuro (black) are supported as color kind.;
        :param time_zone:
        Specify the time zone for this graph as TZ database name (not Time zone abbreviation).
        If not specified, it is treated as UTC.
        """
        if not self.is_exists():
            with Session(engine) as session, session.begin():
                user = session.query(Users).filter(Users.username == self.USERNAME).first()
                new_graph = Graphs(graph_name=self.GRAPH_NAME, user_id=user.id)
                session.add(new_graph)
                session.commit()

            new_graph_params = {
                "id": self.GRAPH_NAME,
                "name": self.GRAPH_NAME,
                "unit": unit,
                "type": type_of_graph,
                "color": color,
                "timezone": time_zone,
            }

            # Так как в Pixel Api 25% запросов не обрабатываются, если ты не подписчик на патреоне,
            # Поэтому мы повторяем запрос пока он не будет успешный
            success = False
            while not success:
                response = requests.post(url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs",
                                         json=new_graph_params,
                                         headers=self.HEADERS)
                print(response.json())
                success = response.json()['isSuccess']
        else:
            raise AttributeError(f'Graph "{self.GRAPH_NAME}" already exists')

    def delete_graph(self):
        """
        Deletes the graph or throws an error if the user does not exist
        :return:
        """
        if self.is_exists():
            with Session(engine) as session, session.begin():
                user = session.query(Users).filter(Users.username == self.USERNAME).first()
                deleted_graph = Graphs(graph_name=self.GRAPH_NAME, user_id=user.id)
                session.delete(deleted_graph)
                session.commit()

            # Так как в Pixel Api 25% запросов не обрабатываются, если ты не подписчик на патреоне,
            # Поэтому мы повторяем запрос пока он не будет успешный
            success = False
            while not success:
                response = requests.delete(url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs/{self.GRAPH_NAME}",
                                           headers=self.HEADERS)
                print(response.json())
                success = response.json()['isSuccess']
        else:
            raise AttributeError(f'Graph "{self.GRAPH_NAME}" do not exists')

    def change_progress(self, user_progress: float, user_date: str = dt.datetime.today().strftime('%Y%m%d')):
        """
        Changes the progress in the pixel graph by user date
        """
        new_score_params = {
            'date': user_date,
            'quantity': user_progress,
        }
        response = requests.post(url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs/{self.GRAPH_NAME}",
                                 headers=self.HEADERS, json=new_score_params)
        print(response.json())

    def get_progress(self, user_date: str):
        """Returns the pixel value of the given day"""
        response = requests.get(url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs/{self.GRAPH_NAME}/{user_date}",
                                headers=self.HEADERS)
        user_progress = None
        try:
            user_progress = response.json()['quantity']
        except KeyError:
            user_progress = 0
        return user_progress

    def update_today_progress(self, user_progress: float):
        today = dt.datetime.today().strftime('%Y%m%d')
        today_progress = float(self.get_progress(today))
        today_progress += user_progress
        new_progress_param = {
            'quantity': str(today_progress),
        }
        response = requests.put(url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs/{self.GRAPH_NAME}/{today}",
                                headers=self.HEADERS,
                                json=new_progress_param)
        print(response.json())
