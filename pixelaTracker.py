import requests
import datetime as dt
import os

class PixelaUser:
    pass

class PixelaGraph:
    USERNAME = os.environ['PIXELA_USERNAME']
    TOKEN = os.environ['PIXELA_TOKEN']

    PIXEL_ENDPOINT = f"https://pixe.la/v1/users/{USERNAME}/graphs/graph1"

    HEADERS = {
        "X-USER-TOKEN": TOKEN,
    }

    def __init__(self, username: str, token: str, graph_name: str):
        self.USERNAME = username
        self.TOKEN = token
        self.GRAPH_NAME = graph_name
        self.HEADERS = {"X-USER-TOKEN": self.TOKEN}
        self.PIXEL_ENDPOINT = f"https://pixe.la/v1/users/{self.USERNAME}/graphs/{self.GRAPH_NAME}"