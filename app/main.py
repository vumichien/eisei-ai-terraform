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
import time

ml_models = {}

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["torque_wrench_model"] = YOLO(
        "models/torque-wrench-type-5.onnx", task="detect"
    )
    ml_models["straight_model"] = YOLO("models/straight-check-7.onnx", task="classify")
    ml_models["value_model"] = YOLO("models/value-detect-8.onnx", task="classify")
    # ml_models["torque_wrench_model"] = YOLO("models/torque-wrench-type-5.pt")
    # ml_models["straight_model"] = YOLO("models/straight-check-7.pt")
    # ml_models["value_model"] = YOLO("models/value-detect-8.pt")

    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


def detect_torque_wrench(image):
    start_time = time.time()
    predictions = ml_models["torque_wrench_model"](image, imgsz=1024)[0]
    detections = sv.Detections.from_ultralytics(predictions)
    parsed_detections = parse_detection(detections)
    logger.info(f"Time taken for torque wrench detection: {time.time() - start_time}")
    return parsed_detections


def check_straight(image_file_name):
    start_time = time.time()
    names = ["NG", "OK"]
    image_folder = "data/tmp/straight_box"
    image_full_path = f"{image_folder}/{image_file_name}"
    predictions = ml_models["straight_model"](image_full_path, imgsz=224)[0]
    prediction_label = predictions.probs.top1
    prediction_conf = predictions.probs.top1conf
    logger.info(f"Time taken for straight prediction: {time.time() - start_time}")
    return names[prediction_label], prediction_conf.item()


def predict_value(image_file_name):
    start_time = time.time()
    names = ["60_cNm_Bronz_18", "60_cNm_Bronz_20", "NG"]
    image_folder = "data/tmp/value_box"
    image_full_path = f"{image_folder}/{image_file_name}"
    predictions = ml_models["value_model"](image_full_path, imgsz=224)[0]
    prediction_label = predictions.probs.top1
    prediction_conf = predictions.probs.top1conf
    logger.info(f"Time taken for value prediction: {time.time() - start_time}")
    return names[prediction_label], prediction_conf.item()


def detect_torque_wrench_value(image, image_file_name="temp.jpg"):
    parsed_results = detect_torque_wrench(image)
    logger.info(f"Parsed results: {parsed_results}")
    if parsed_results is not None:
        for obj in parsed_results:
            logger.info(f"Detect 60_cNm_Bronz with confidence={obj['confidence']}")
            if obj["class_id"] == 0 and obj["confidence"] >= 0.8:
                box = (
                    obj["x"],
                    obj["y"],
                    obj["x"] + obj["width"],
                    obj["y"] + obj["height"],
                )
                crop_images(image, output_directory="data/tmp/", box=box)
                straight_label, straight_conf = check_straight(image_file_name)
                logger.info(
                    f"Straight label={straight_label}, Straight confidence={straight_conf}"
                )
                value_label, value_conf = predict_value(image_file_name)
                logger.info(f"Value label={value_label}, Value confidence={value_conf}")
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
                    "object": {
                        "class": "60_cNm_Bronz",
                        "confidence": obj["confidence"],
                    }
                }

    else:
        return None


def infer(image):
    image_arr = np.frombuffer(image, np.uint8)
    image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (1024, 1024))
    start_time = time.time()
    result = detect_torque_wrench_value(image)
    logger.info(f"Time taken for inference: {time.time() - start_time}")
    return result


@app.post("/api/detect/")
async def process_image(image: UploadFile = File(...)):
    filename = image.filename
    logger.info(f"Received process-image request for file: {filename}")
    image_data = await image.read()
    results = infer(image_data)
    logger.info("Returning JSON results")
    if results is None:
        return JSONResponse(content={})
    return JSONResponse(content=results)


@app.get("/")
def hello_world():
    return "Hello World from Detomo AI!"


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
