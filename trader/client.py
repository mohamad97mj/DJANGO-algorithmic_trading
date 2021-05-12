from binance.client import Client

api_key = 'knBxiPJqJhGwpADVP4sqvH8RXLnc8vBPIB1iTKDONQ07q2VD9Ik7KCmqxCw1rrMT'  # test
# api_key = 'm6IcuuOFD4r1OiS5Mw87UjNjiKPav14CviOOyxz6CvG17AY1QBIxuPF7v6scDuqg' #main
api_secret = '4Pf1cmFJ7qi5aefurLjQSIvb3iGCDcEnkgPi4qvlDSulcFQlbQZgIGTgHcUJgvDG'  # test
# api_secret = 'B0CdJ9l95FOdtsZPdZ4oNRhnqj2mor7EniB99icmrxUW8bt5eoRZhk8CVCRfQau5' #main
client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binance.vision/api'

