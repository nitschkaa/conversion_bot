import requests

response = requests.get('https://v6.exchangerate-api.com/v6/3be3a092e3659483327c5f86/latest/USD')
print(response.text)
