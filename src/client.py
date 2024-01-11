"""
This script contains a class MyWebsocketAndUploadProgram that provides methods for interacting with websockets and HTTP servers. 
It includes methods for sending and receiving messages over a websocket connection and for uploading a file to a server via HTTP POST request.

The script is executed if it is run as the main module. It first tests the websocket connection by sending and receiving messages. 
Then it uploads a file to a server and prints the server's response.
"""

import asyncio
import websockets
import requests

class MyWebsocketAndUploadProgram:
    """
    A class that provides methods for interacting with websockets and HTTP servers.

    ...

    Methods
    -------
    test_websocket():
        Sends and receives messages over a websocket connection.
    upload_file(url: str, file_path: str) -> requests.Response:
        Uploads a file to a server via HTTP POST request and returns the server's response.
    main():
        Executes the script, uploads a file to a server and prints the server's response.
    """

    @staticmethod
    async def test_websocket():
        """
        Sends and receives messages over a websocket connection.

        This method is an asynchronous operation that opens a websocket connection to a server at a specified URL. 
        It sends an initial message to the server and then sends and receives a series of messages, simulating a real-world process of sending and receiving updates.
        """
        uri = "ws://localhost:8000/ws"  # Websocket URL
        async with websockets.connect(uri) as websocket:  # Create a connection to the websocket server
            await websocket.send("Start")  # Send initial message
            for i in range(5):  # Loop to simulate periodic updates
                response = await websocket.recv()  # Receive response from server
                print(f"Response: {response}")  # Print the received response
                await websocket.send(f"Update {i}")


    @staticmethod
    def upload_file(url: str, file_path: str) -> requests.Response:
        """
        Uploads a file to a server via HTTP POST request and returns the server's response.

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
        Executes the script, uploads a file to a server and prints the server's response.

        This method sets the URL of the server and the path of the file to be uploaded. 
        It then calls the upload_file method to upload the file and prints the server's response.
        """
        server_url = "http://localhost:8000/upload-file/"  # Server url
        file_to_upload = "sample2.txt"  # File to be uploaded

        response = MyWebsocketAndUploadProgram.upload_file(server_url, file_to_upload)  # Upload file and get server response
        print(f"Server response: {response.text}")  # Print server response


if __name__ == "__main__":
    """
    Executes the script if it is run as the main module.

    It first tests the websocket connection by sending and receiving messages. 
    Then it uploads a file to a server and prints the server's response.
    """
    asyncio.run(MyWebsocketAndUploadProgram.test_websocket())  # Run websocket test
    MyWebsocketAndUploadProgram.main()  # Run main method
