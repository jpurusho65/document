from fastapi import FastAPI, WebSocket, Request, UploadFile, File
from fastapi.responses import HTMLResponse
import asyncio
import uvicorn

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/post-data/")
async def post_data(request: Request):
    data = await request.json()
    print(f"Received POST data: {data}")
    return {"Received": data}

@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        # Async update to WebSocket would go here
        file_object.write(file.file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # This will be used to send progress updates
        data = await websocket.receive_text()
        await asyncio.sleep(1)  # Simulate some processing delay
        await websocket.send_text(f"Processed: {data}")


def main():
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="info", reload=True)

# You can run this server using `uvicorn server:app --reload`
# Test this server file

if __name__ == '__main__':
    main()
