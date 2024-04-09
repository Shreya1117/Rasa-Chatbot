import requests

status_url = 'http://localhost:5005/webhooks/rest/'
url = 'http://localhost:5005/webhooks/rest/webhook/'

rasa_status = requests.get(status_url)

print(rasa_status.text)

while True:
    text = input("Enter your message for rasa: ")
    if text == '-1':
        print('Exiting...')
        break
    x = requests.post(url, json={'sender': 'someone', 'message': 'hello world'})
    print(x.text)