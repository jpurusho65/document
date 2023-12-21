import asyncio
import websockets
import requests

class MyWebsocketAndUploadProgram:
    """
    The MyWebsocketAndUploadProgram class contains methods for interacting with both 
    websockets and HTTP servers, using both GET and POST requests.
    """

    @staticmethod
    async def test_websocket():
        """
        The static method test_websocket is an asynchronous operation that opens a websocket 
        connection and sends and receives a series of messages, simulating a real-world 
        process of sending and receiving updates.
        
        """
        uri = "ws://localhost:8000/ws"  # Websocket URL
        async with websockets.connect(uri) as websocket:  # Create a connection to the websocket server
            await websocket.send("Start")  # Send initial message
            for i in range(10):  # Loop to simulate periodic updates
                response = await websocket.recv()  # Receive response from server
                print(response)  # Print the received response
                await websocket.send(f"Update {i}")  # Send update to the server


    @staticmethod
    def upload_file(url: str, file_path: str) -> requests.Response:
        """
        The upload_file static method reads a file from the path `file_path` 
        and uploads it to `url` via HTTP POST, returns the server response.

        Parameters:
        url (str): The URL to which the file will be uploaded.
        file_path (str): The path of the file that will be uploaded.

        Returns:
        requests.Response: The server response to the upload.
        """
        with open(file_path, 'rb') as file:  # Open the file
            files = {'file': (file_path, file)}  # Create a dictionary with file data
            response = requests.post(url, files=files)  # Post the file to the given url
            return response  # Return the server response

    @staticmethod
    def main():
        """
        The main static method of MyWebsocketAndUploadProgram where the script execution begins. 
        It sets the url and file_path parameters and then calls the upload_file method, 
        afterwards it prints the server response.
        """
        server_url = "http://localhost:8000/upload-file/"  # Server url
        file_to_upload = "sample.txt"  # File to be uploaded

        response = MyWebsocketAndUploadProgram.upload_file(server_url, file_to_upload)  # Upload file and get server response
        print(f"Server response: {response.text}")  # Print server response


if __name__ == "__main__":
    # Test websocket connection
    asyncio.run(MyWebsocketAndUploadProgram.test_websocket())  # Run websocket test
    MyWebsocketAndUploadProgram.main()  # Run main method
```
