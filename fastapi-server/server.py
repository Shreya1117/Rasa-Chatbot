import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from hypercorn.asyncio import serve
from hypercorn.config import Config
from starlette.responses import JSONResponse, FileResponse
import aiohttp
from random import randint

RASA_STATUS_URL = 'http://localhost:5005/webhooks/rest/'
RASA_URL = 'http://localhost:5005/webhooks/rest/webhook/'

users = dict()

config = Config()
config.bind = ["localhost:7777"]
app = FastAPI()


def generate_random_n_digit_number(n: int):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return str(randint(range_start, range_end))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/users/fetch_id")
async def root():
    while True:
        user_id = generate_random_n_digit_number(5)
        if user_id not in users.keys():
            break
    users[user_id] = {'query': 0}
    print('Generated USER_ID --->', user_id)
    return JSONResponse(content={'user_id': user_id})

@app.get("/home")
async def root():
    print("WELCOME, USER!!!")
    resp = FileResponse("templates/home.html")
    return resp

@app.post("/predict")
async def root(request: Request):
    print()
    data = await request.json()
    user_id = data["user_id"]
    if user_id not in users.keys():
        print('Invalid User-ID, Session Expired.')
        return JSONResponse(content={}, status_code=500)
    users[user_id]['query'] += 1      # Query number

    user_message = data['user_message']
    print('Successfully sent message --->', user_message)

    async with aiohttp.ClientSession() as session:
        async with session.post(RASA_URL, json={'sender': user_id, 'message': user_message}) as response:
            res: list[dict[str, str]] = await response.json()
            code = response.status

    response = {'text': ''}
    if code == 200:
        print('Successfully got response from llm --->', res)
        for dict_val in res:
            response['text'] += dict_val['text']
            # response['user_id'] = dict_val['receiver_id']
            # later, move this functionality to the client, maybe
    if response['text'].strip() == '':
        response['text'] = 'Continue talking.'
    return JSONResponse(content=response)

app.mount("/res/Images", StaticFiles(directory="./res/Images"))

asyncio.run(serve(app, config))