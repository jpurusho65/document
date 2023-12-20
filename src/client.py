import asyncio
import websockets
import requests

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Start")
        for i in range(5):  # Simulating periodic updates
            response = await websocket.recv()
            print(response)
            await websocket.send(f"Update {i}")

def upload_file(url, file_path):
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file)}
        response = requests.post(url, files=files)
        return response

def main():
    server_url = "http://localhost:8000/upload-file/"
    file_to_upload = "sample.txt"

    response = upload_file(server_url, file_to_upload)
    print(f"Server response: {response.text}")


if __name__ == "__main__":
    # Test websocket connection
    asyncio.run(test_websocket())
    main()