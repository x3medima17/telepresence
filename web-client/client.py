#!/usr/bin/env python

import asyncio
import websockets
import json
import time

async def hello():
	async with websockets.connect('ws://localhost:8888/ws') as websocket:
		with open('log.txt','r') as f:
			data = f.read()
			data = json.loads(data)
			for item in data:
				frame = json.dumps(item)
				await websocket.send(frame)
				time.sleep(0.05)


asyncio.get_event_loop().run_until_complete(hello())