import requests
import datetime as dt
import os

USERNAME = os.environ['PixelaUsername']
TOKEN = os.environ['PixelaToken']

PIXEL_ENDPOINT = f"https://pixe.la/v1/users/{USERNAME}/graphs/graph1"

HEADERS = {
    "X-USER-TOKEN": TOKEN,
}


# TODO 1: Возможность добавлять время в сегодняшний день в зависимости от ввода пользователя
def post_progress_pixel():
    today = dt.datetime.today().strftime('%Y%m%d')
    correct_input = False
    new_score = 0
    while not correct_input:
        try:
            new_score = float(input('Введите сколько вы сегодня поработали(в часах): '))
        except ValueError:
            print("Вы ввели некорректные данные. Попробуйте ещё раз.")
        else:
            correct_input = True

    new_score_params = {
        'date': today,
        'quantity': str(new_score),
    }
    response = requests.post(f'{PIXEL_ENDPOINT}', headers=HEADERS, json=new_score_params)
    print(response.text)


# TODO 2: Просмотр прогресса сегодняшнего дня
def get_progress_pixel():
    today = dt.datetime.today().strftime('%Y%m%d')

    response = requests.get(f'{PIXEL_ENDPOINT}/{today}', headers=HEADERS)
    print(response.json()['quantity'])


# TODO 3: Изменение прогресса на выбор: сегодня, вчера, позавчера
# TODO 4: Добавление прогресса в сегодняшний день
# TODO 5: Функция создания нового пользователя
# TODO 6: Функция создания нового графика Pixela

