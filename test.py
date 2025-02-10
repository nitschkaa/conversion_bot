import requests

response = requests.get('https://v6.exchangerate-api.com/v6/''/latest/USD')
print(response.text)
