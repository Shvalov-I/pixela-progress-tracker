import sqlite3
import sqlalchemy.exc
import requests
import datetime as dt
import uuid
from models import Session, Users, Graphs, engine


class PixelaUser:
    """An object describing the work with the user"""
    PIXEL_ENDPOINT = f"https://pixe.la/v1/users"

    def __init__(self, username: str):
        self.USERNAME = username
        self.TOKEN = None

    def is_exists(self):
        with Session(engine) as session, session.begin():
            # Проверка есть ли пользователь с таким именем в базе данных
            if session.query(Users).filter(Users.username == self.USERNAME).first():
                return True
            else:
                return False

    def get_token(self):
        if self.is_exists():
            with Session(engine) as session, session.begin():
                user = session.query(Users).filter(Users.username == self.USERNAME).first()
                return user.token
        else:
            raise AttributeError(f'User "{self.USERNAME}" do not exists')

    def create_user(self, username: str):
        self.USERNAME = username
        if self.is_exists():
            self.TOKEN = str(uuid.uuid4())
            with Session(engine) as session, session.begin():
                new_user = Users(username=self.USERNAME, token=self.TOKEN)
                session.add(new_user)
                session.commit()
        else:
            raise AttributeError(f'User "{self.USERNAME}" already exists')




# class PixelaGraph:
#     USERNAME = os.environ['PIXELA_USERNAME']
#     TOKEN = os.environ['PIXELA_TOKEN']
#
#     PIXEL_ENDPOINT = f"https://pixe.la/v1/users/{USERNAME}/graphs/graph1"
#
#     HEADERS = {
#         "X-USER-TOKEN": TOKEN,
#     }
#
#     def __init__(self, username: str, token: str, graph_name: str):
#         self.USERNAME = username
#         self.TOKEN = token
#         self.GRAPH_NAME = graph_name
#         self.HEADERS = {"X-USER-TOKEN": self.TOKEN}
#         self.PIXEL_ENDPOINT = f"https://pixe.la/v1/users/{self.USERNAME}/graphs/{self.GRAPH_NAME}"
#
#     def post_progress_pixel(user_date: str = dt.datetime.today().strftime('%Y%m%d')):
#         """Asks the value of the user and changes the progress by user date"""
#         correct_input = False
#         new_score = 0
#         while not correct_input:
#             try:
#                 new_score = float(input('Введите на какое значение вы хотите изменить(в часах): '))
#             except ValueError:
#                 print("Вы ввели некорректные данные. Попробуйте ещё раз.")
#             else:
#                 correct_input = True
#
#         new_score_params = {
#             'date': user_date,
#             'quantity': str(new_score),
#         }
#         response = requests.post(f'{PIXEL_ENDPOINT}', headers=HEADERS, json=new_score_params)
#
#     def get_progress_pixel(user_date: str):
#         """Returns the pixel value of the given day"""
#         response = requests.get(f'{PIXEL_ENDPOINT}/{user_date}', headers=HEADERS)
#         return response.json()['quantity']
#
#     def change_progress_pixel():
#
#         today = dt.datetime.today().strftime('%Y%m%d')
#
#         yesterday = dt.datetime.today() - dt.timedelta(days=1)
#         yesterday = yesterday.strftime('%Y%m%d')
#
#         day_before_yesterday = dt.datetime.today() - dt.timedelta(days=1)
#         day_before_yesterday = day_before_yesterday.strftime('%Y%m%d')
#
#         user_date_id = None
#
#         correct_input = False
#         while not correct_input:
#             try:
#                 user_date_id = int(input('Введите код дня, который вы хотите изменить '
#                                          '(Сегодня - 0, Вчера - 1, Позавчера - 2): '))
#                 if user_date_id in (0, 1, 2):
#                     correct_input = True
#                 else:
#                     print('Вы ввели неправильный индекс дня. Попробуйте ещё раз.')
#             except ValueError:
#                 print('Некорректный ввод. Попробуйте ещё раз.')
#
#         if user_date_id == 0:
#             print(f'Ваш прогресс сегодня составляет {get_progress_pixel(today)}')
#             post_progress_pixel(today)
#         elif user_date_id == 1:
#             print(f'Ваш прогресс вчера составляет {get_progress_pixel(yesterday)}')
#             post_progress_pixel(yesterday)
#         elif user_date_id == 2:
#             print(f'Ваш прогресс позавчера составляет {get_progress_pixel(day_before_yesterday)}')
#             post_progress_pixel(day_before_yesterday)
#
#     change_progress_pixel()
