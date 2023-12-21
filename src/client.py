import asyncio
import websockets
import requests

# Below method is used to test websocket connection. 
# It connects to the given uri, sends an initial message, receives and prints responses, 
# and sends updates until there's none left.
async def test_websocket():
    uri = "ws://localhost:8000/ws"  # Websocket URL
    async with websockets.connect(uri) as websocket:  # Create a connection to the websocket server
        await websocket.send("Start")  # Send initial message
        for i in range(10):  # Loop to simulate periodic updates
            response = await websocket.recv()  # Receive response from server
            print(response)  # Print the received response
            await websocket.send(f"Update {i}")  # Send update to the server

# Below method takes URL and File Path as input, uploads the file to that URL and 
# returns the response received from the server.
# Parameters: url (str), file_path (str)
# Returns: Response from server
def upload_file(url: str, file_path: str):
    with open(file_path, 'rb') as file:  # Open the file
        files = {'file': (file_path, file)}  # Create a dictionary with file data
        response = requests.post(url, files=files)  # Post the file to the given url
        return response  # Return the server response

# Below is the main method which uploads a sample file to the server url,
# and gets and prints the server response.
def main():
    server_url = "http://localhost:8000/upload-file/"  # Server url
    file_to_upload = "sample.txt"  # File to be uploaded

    response = upload_file(server_url, file_to_upload)  # Upload file and get server response
    print(f"Server response: {response.text}")  # Print server response


if __name__ == "__main__":
    # Test websocket connection
    asyncio.run(test_websocket())  # Run websocket test
    main()  # Run main method