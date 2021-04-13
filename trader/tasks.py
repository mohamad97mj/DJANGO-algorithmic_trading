from celery import shared_task
from celery.decorators import periodic_task
from binance.client import Client
from pprint import pprint
import time

api_key = 'm6IcuuOFD4r1OiS5Mw87UjNjiKPav14CviOOyxz6CvG17AY1QBIxuPF7v6scDuqg'
api_secret = 'B0CdJ9l95FOdtsZPdZ4oNRhnqj2mor7EniB99icmrxUW8bt5eoRZhk8CVCRfQau5'
client = Client(api_key, api_secret)


@shared_task
def get_open_orders():
    orders = client.get_open_orders()
    pprint(orders)
