import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Start")
        for i in range(5):  # Simulating periodic updates
            response = await websocket.recv()
            print(response)
            await websocket.send(f"Update {i}")

# Run test client
asyncio.run(test_websocket())
