import sqlite3
import sqlalchemy.exc
import requests
import datetime as dt
import uuid
from models import Session, Users, Graphs, engine


def success_request(request: requests.Request) -> requests.models.Response:
    """
    Makes requests until it succeeds
    :param request:
    :return:
    """
    # Так как в Pixel Api 25% запросов не обрабатываются, если ты не подписчик на патреоне,
    # Поэтому мы повторяем запрос пока он не будет успешный
    success = False
    while not success:
        with requests.Session() as session:
            prepare_req = session.prepare_request(request)
            response = session.send(prepare_req)
            print(response.json())
            if 'Please retry this request.' not in response.json()['message']:
                success = True
    return response


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

            req = requests.Request(method="POST", url=self.PIXEL_ENDPOINT, json=new_user_params)
            success_request(req)
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
            req = requests.Request(method="DELETE", url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}", headers=headers)
            success_request(req)
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

            req = requests.Request(method="POST", url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs",
                                   json=new_graph_params,
                                   headers=self.HEADERS)
            success_request(req)
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

            req = requests.Request(method="DELETE",
                                   url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs/{self.GRAPH_NAME}",
                                   headers=self.HEADERS)
            success_request(req)
        else:
            raise AttributeError(f'Graph "{self.GRAPH_NAME}" do not exists')

    def change_progress(self, user_progress: int, user_date: str = dt.datetime.today().strftime('%Y%m%d')):
        """
        Changes the progress in the pixel graph by user date
        """
        new_score_params = {
            'date': user_date,
            'quantity': str(user_progress),
        }
        req = requests.Request(method="POST", url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs/{self.GRAPH_NAME}",
                               headers=self.HEADERS, json=new_score_params)
        success_request(req)

    def get_progress(self, user_date: str):
        """Returns the pixel value of the given day"""
        req = requests.Request(method="GET",
                               url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs/{self.GRAPH_NAME}/{user_date}",
                               headers=self.HEADERS)
        response = success_request(req)
        print(response.json())
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
        req = requests.Request(method="PUT",
                               url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs/{self.GRAPH_NAME}/{today}",
                               headers=self.HEADERS,
                               json=new_progress_param)
        success_request(req)
