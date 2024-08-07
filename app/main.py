import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import logging
from ultralytics import YOLO

app = FastAPI()
model = YOLO("models/straight-check-v4.pt")


def infer(image):
    image_arr = np.frombuffer(image, np.uint8)
    image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (640, 640))
    result = model(image, imgsz=640)[0]
    label = result.names
    width, height = result.orig_shape[1], result.orig_shape[0]
    print(result.speed)
    parsed_result = {'predictions': label[result.probs.top1], 'image': {'width': width, 'height': height}}
    return parsed_result


@app.post("/process-image/")
async def process_image(image: UploadFile = File(...)):
    filename = image.filename
    logging.info(f"Received process-image request for file: {filename}")
    image_data = await image.read()
    results = infer(image_data)
    logging.info("Returning JSON results")
    return JSONResponse(content=results)


@app.get("/")
def hello_world():
    return 'Hello World from Detomo AI!'


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
