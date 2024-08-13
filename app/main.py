import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import logging
from ultralytics import YOLO
from contextlib import asynccontextmanager
from utils import parse_detection, crop_images
import supervision as sv

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["torque_wrench_model"] = YOLO("models/torque-wrench-type-5.pt")
    ml_models["straight_model"] = YOLO("models/straight-check-7.pt")
    ml_models["value_model"] = YOLO("models/value-detect-8.pt")
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


def detect_torque_wrench(image):
    predictions = ml_models["torque_wrench_model"](image)[0]
    detections = sv.Detections.from_ultralytics(predictions)
    parsed_detections = parse_detection(detections)
    return parsed_detections


def check_straight(image_file_name):
    names = ["NG", "OK"]
    image_folder = "data/tmp/straight_box"
    image_full_path = f"{image_folder}/{image_file_name}"
    predictions = ml_models["straight_model"](image_full_path)[0]
    prediction_label = predictions.probs.top1
    prediction_conf = predictions.probs.top1conf
    return names[prediction_label], prediction_conf.item()


def predict_value(image_file_name):
    names = ["60_cNm_Bronz_18", "60_cNm_Bronz_20", "NG"]
    image_folder = "data/tmp/value_box"
    image_full_path = f"{image_folder}/{image_file_name}"
    predictions = ml_models["value_model"](image_full_path)[0]
    prediction_label = predictions.probs.top1
    prediction_conf = predictions.probs.top1conf
    return names[prediction_label], prediction_conf.item()


def detect_torque_wrench_value(image, image_file_name="temp.jpg"):
    parsed_results = detect_torque_wrench(image)
    print(parsed_results)
    if parsed_results is not None:
        for obj in parsed_results:
            print("detect 60_cNm_Bronz with confidence=", obj["confidence"])
            if obj["class_id"] == 0 and obj["confidence"] >= 0.8:
                box = (
                    obj["x"],
                    obj["y"],
                    obj["x"] + obj["width"],
                    obj["y"] + obj["height"],
                )
                crop_images(image, output_directory="data/tmp/", box=box)
                straight_label, straight_conf = check_straight(image_file_name)
                print(
                    "straight_label=", straight_label, "straight_conf=", straight_conf
                )
                value_label, value_conf = predict_value(image_file_name)
                print("value_label=", value_label, "value_conf=", value_conf)
                return {
                    "object": {
                        "class": "60_cNm_Bronz",
                        "confidence": obj["confidence"],
                    },
                    "straight": {"class": straight_label, "confidence": straight_conf},
                    "value": {"class": value_label, "confidence": value_conf},
                }
            elif obj["class_id"] == 0 and obj["confidence"] < 0.8:
                return {
                    {
                        "object": {
                            "class": "60_cNm_Bronz",
                            "confidence": obj["confidence"],
                        }
                    }
                }

    else:
        return None


def infer(image):
    image_arr = np.frombuffer(image, np.uint8)
    image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (1024, 1024))
    result = detect_torque_wrench_value(image)
    return result


@app.post("/api/detect/")
async def process_image(image: UploadFile = File(...)):
    filename = image.filename
    logging.info(f"Received process-image request for file: {filename}")
    image_data = await image.read()
    results = infer(image_data)
    logging.info("Returning JSON results")
    if results is None:
        return JSONResponse(content={})
    return JSONResponse(content=results)


@app.get("/")
def hello_world():
    return "Hello World from Detomo AI!"


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
