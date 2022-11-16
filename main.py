import requests
import datetime as dt
import os

USERNAME = os.environ['PIXELA_USERNAME']
TOKEN = os.environ['PIXELA_TOKEN']

PIXEL_ENDPOINT = f"https://pixe.la/v1/users/{USERNAME}/graphs/graph1"

HEADERS = {
    "X-USER-TOKEN": TOKEN,
}



