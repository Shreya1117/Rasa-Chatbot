import asyncio
from fastapi import FastAPI, Request
from hypercorn.asyncio import serve
from hypercorn.config import Config
from starlette.responses import JSONResponse, FileResponse
import aiohttp

RASA_STATUS_URL = 'http://localhost:5005/webhooks/rest/'
RASA_URL = 'http://localhost:5005/webhooks/rest/webhook/'

users = dict()

config = Config()
config.bind = ["localhost:7777"]
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/home")
async def root():
    print("WELCOME, USER!!!")
    return FileResponse("templates/test.html")

@app.post("/predict")
async def root(request: Request):
    print()
    data = await request.json()
    user_id = data["user_id"]
    if user_id not in users.keys():
        users[user_id] = {'query': 0}
    users[user_id]['query'] += 1      # Query number

    user_message = data['user_message']
    print('Successfully sent message --->', user_message)

    async with aiohttp.ClientSession() as session:
        async with session.post(RASA_URL, json={'sender': '12345', 'message': user_message}) as response:
            res: list[dict[str, str]] = await response.json()
            code = response.status

    if code == 200:
        print('Successfully got response from llm --->', res[0]['text'])

    return JSONResponse(content=res[0])

asyncio.run(serve(app, config))