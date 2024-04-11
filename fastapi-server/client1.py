import requests

LLM_URL = f'http://localhost:8888/message'

while True:
    input_text = input("Enter your message: ")
    if input_text == "-1":
        break
    x = requests.post(LLM_URL, json={"user_id": '12345', 'user_info': '', 'message': input_text})
    res = x.json()
    if res['status'] == 200:
        print(res['response'])