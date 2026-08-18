from http import HTTPStatus

from fastapi import FastAPI
from starlette.types import Message

app = FastAPI()



app.get('/')
def read_root():
    return {'messaage': 'Ta funcionando!'}
