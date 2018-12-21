import asyncio
import websockets
from slacker import Slacker

token = "xoxb-502213453520-507384248019-BsMUDahN9t0xkAgG9nUKIkB9"
slack = Slacker(token)

res = slack.rtm.connect()
endpoint = res.body['url']

async def get_answer():
    ws = await websockets.connect(endpoint)
    while True:
        msg = await ws.recv()
        print(msg)
        return msg
    ws.close()

loop = asyncio.get_event_loop()
abc = loop.run_until_complete(get_answer())
loop.close()

print(abc)