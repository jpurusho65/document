from fastapi import FastAPI, WebSocket, Request, UploadFile, File
from fastapi.responses import HTMLResponse
import asyncio
import uvicorn

# Initialize an instance of FastAPI
app = FastAPI()

@app.get("/")
# Defines a route for get requests to the root ("/") url.
# Returns a simple hello world response.
async def read_root():
    return {"Hello": "World"}

@app.post("/post-data/")
# This function, decorated as a POST route, is used to read incoming JSON data from the request
# and print the data to the console.
# It takes in the request (of type Request) object as a parameter.
# It eventually returns an acknowledgment in the form of a dictionary back to the client.
async def post_data(request: Request):
    data = await request.json()
    print(f"Received POST data: {data}")
    return {"Received": data}

@app.post("/upload-file/")
# This function, decorated as a POST route, is used to upload a file.
# It takes in a file (of type UploadFile) as a parameter, which is being read from the request.
# It saves the file to the disk and returns the path of the saved file in the response.
async def upload_file(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.websocket("/ws")
# This function is used to handle WebSocket connections.
# It takes as an argument a WebSocket connection object.
# It continuously receives data through the WebSocket, simulates processing the data by sleeping,
# and then sends a response back through the WebSocket.
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await asyncio.sleep(1)  # Simulate some processing delay
        await websocket.send_text(f"Processed: {data}")

# main function to start the FastAPI application.
def main():
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="info", reload=True)

if __name__ == '__main__':
    main()
```
