import sqlite3
import sqlalchemy.exc
import requests
import datetime as dt
import uuid
from models import Session, Users, Graphs, engine


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

    def create_graph(self, unit:str, type_of_graph: str = 'int', color: str = 'shibafu', time_zone: str = 'Asia/Novosibirsk'):
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
                response = requests.post(url=f"{self.PIXEL_ENDPOINT}/{self.USERNAME}/graphs",
                                         json=new_graph_params,
                                         headers=self.HEADERS)
                print(response.json())
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
        else:
            raise AttributeError(f'Graph "{self.GRAPH_NAME}" do not exists')

    # def post_progress_pixel(user_date: str = dt.datetime.today().strftime('%Y%m%d')):
    #     """Asks the value of the user and changes the progress by user date"""
    #     correct_input = False
    #     new_score = 0
    #     while not correct_input:
    #         try:
    #             new_score = float(input('Введите на какое значение вы хотите изменить(в часах): '))
    #         except ValueError:
    #             print("Вы ввели некорректные данные. Попробуйте ещё раз.")
    #         else:
    #             correct_input = True
    #
    #     new_score_params = {
    #         'date': user_date,
    #         'quantity': str(new_score),
    #     }
    #     response = requests.post(f'{PIXEL_ENDPOINT}', headers=HEADERS, json=new_score_params)
    #
    # def get_progress_pixel(user_date: str):
    #     """Returns the pixel value of the given day"""
    #     response = requests.get(f'{PIXEL_ENDPOINT}/{user_date}', headers=HEADERS)
    #     return response.json()['quantity']
    #
    # def change_progress_pixel():
    #
    #     today = dt.datetime.today().strftime('%Y%m%d')
    #
    #     yesterday = dt.datetime.today() - dt.timedelta(days=1)
    #     yesterday = yesterday.strftime('%Y%m%d')
    #
    #     day_before_yesterday = dt.datetime.today() - dt.timedelta(days=1)
    #     day_before_yesterday = day_before_yesterday.strftime('%Y%m%d')
    #
    #     user_date_id = None
    #
    #     correct_input = False
    #     while not correct_input:
    #         try:
    #             user_date_id = int(input('Введите код дня, который вы хотите изменить '
    #                                      '(Сегодня - 0, Вчера - 1, Позавчера - 2): '))
    #             if user_date_id in (0, 1, 2):
    #                 correct_input = True
    #             else:
    #                 print('Вы ввели неправильный индекс дня. Попробуйте ещё раз.')
    #         except ValueError:
    #             print('Некорректный ввод. Попробуйте ещё раз.')
    #
    #     if user_date_id == 0:
    #         print(f'Ваш прогресс сегодня составляет {get_progress_pixel(today)}')
    #         post_progress_pixel(today)
    #     elif user_date_id == 1:
    #         print(f'Ваш прогресс вчера составляет {get_progress_pixel(yesterday)}')
    #         post_progress_pixel(yesterday)
    #     elif user_date_id == 2:
    #         print(f'Ваш прогресс позавчера составляет {get_progress_pixel(day_before_yesterday)}')
    #         post_progress_pixel(day_before_yesterday)
    #
    # change_progress_pixel()
