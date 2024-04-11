import requests

LLM_URL = f"http://localhost:8888/message"

x = requests.post(LLM_URL, json={"user_id": '12345', 'user_info': 'I am user.', 'message': 'Hello World!'})

res = x.json()

if res['status'] == 200:
    print(res['response'])