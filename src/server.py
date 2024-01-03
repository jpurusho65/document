"""
FastAPI application module.

This module provides HTTP endpoints and websockets endpoints to handle GET, POST requests,
file uploads, and WebSocket connections.
"""
from fastapi import FastAPI, WebSocket, Request, UploadFile, File
from fastapi.responses import HTMLResponse
import asyncio
import uvicorn

# Initialize an instance of FastAPI
app = FastAPI()

@app.get("/")
async def read_root():
    """
    Handles GET request at the root ("/") URL.
    
    A method that returns a dictionary with a simple greeting message. 

    Returns:
        dict: A dictionary object consisting of a greeting message.
    """
    return {"Hello": "World"}

@app.post("/post-data/")
async def post_data(request: Request):
    """
    Handles POST request at the "/post-data/" URL.
    
    A method that reads JSON data from the request, prints the data to the console,
    and then returns an acknowledgment back to the client. 
  
    Args:
        request (Request): The incoming request object.
        
    Returns:
        dict: A dictionary object that acknowledges the data received.
    """
    data = await request.json()
    print(f"POST data: {data}")
    return {data}

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles file upload at the "/upload-file/" URL.
    
    A method that handles a file upload, saving this file to the disk, 
    and then returns the path of the saved file in the response. 

    Args:
        file (UploadFile, optional): The file to be uploaded and saved to the disk.
        
    Returns:
        dict: A dictionary object with information about the saved file.
    """
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles WebSocket connections at the "/ws" URL.
    
    This method continuously receives data through the WebSocket, simulates processing the data,
    and then sends a response back through the WebSocket.

    Args:
        websocket (WebSocket): The WebSocket connection object.
    """
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await asyncio.sleep(1)  # Simulate some processing delay
        await websocket.send_text(f"Processed: {data}")

def main():
    """
    Starts the FastAPI application.
    
    This is the entry point of our application. It is not meant to be called directly. 
    Instead, it is run when this Python module is executed as a standalone script.
    """
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="info", reload=True)

if __name__ == '__main__':
    main()