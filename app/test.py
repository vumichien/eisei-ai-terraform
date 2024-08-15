from ultralytics import YOLO
import supervision as sv
from utils import parse_detection, crop_images
import onnxruntime as ort
import torch

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

source = "data"
torque_wrench_model = YOLO("models/torque-wrench-type-5.pt")
straight_model = YOLO("models/straight-check-7.pt")
value_model = YOLO("models/value-detect-8.pt")

torque_wrench_model.export(format="onnx", imgsz=1024, int8=True, simplify=True)
straight_model.export(format="onnx", imgsz=224, int8=True, simplify=True)
value_model.export(format="onnx", imgsz=224, int8=True, simplify=True)


# def detect_torque_wrench(image_path):
#     predictions = torque_wrench_model(image_path)[0]
#     detections = sv.Detections.from_ultralytics(predictions)
#     parsed_detections = parse_detection(detections)
#     return parsed_detections
#
#
# def check_straight(image_file_name):
#     names = ['ng', 'ok']
#     image_folder = 'data/tmp/straight_box'
#     image_full_path = f"{image_folder}/{image_file_name}"
#     predictions = straight_model(image_full_path)[0]
#     prediction_label = predictions.probs.top1
#     prediction_conf = predictions.probs.top1conf
#     return prediction_label, prediction_conf
#
#
# def predict_value(image_file_name):
#     names = ['60_cNm_Bronz_18', '60_cNm_Bronz_20', 'NG']
#     image_folder = 'data/tmp/value_box'
#     image_full_path = f"{image_folder}/{image_file_name}"
#     predictions = value_model(image_full_path)[0]
#     prediction_label = predictions.probs.top1
#     prediction_conf = predictions.probs.top1conf
#     return prediction_label, prediction_conf
#
#
# def detect_torque_wrench_value(image_file_name):
#     parsed_results = detect_torque_wrench(image_file_name)
#     print(parsed_results)
#     if parsed_results is not None:
#         for obj in parsed_results:
#             if obj['class_id'] == 0 and obj['confidence'] >= 0.8:
#                 print("detect 60_cNm_Bronz with confidence=", obj['confidence'])
#                 box = (obj['x'], obj['y'], obj['x'] + obj['width'], obj['y'] + obj['height'])
#                 crop_images(image_file_name, output_directory="data/tmp/", box=box)
#                 prediction_label, prediction_conf = check_straight(image_file_name)
#                 print("check_straight", prediction_label, prediction_conf)
#
#                 prediction_label, prediction_conf = predict_value(image_file_name)
#                 print("check_straight", prediction_label, prediction_conf)
#             elif obj['class_id'] == 0 and obj['confidence'] < 0.8:
#                 print("detect 60_cNm_Bronz with confidence=", obj['confidence'])


# results = model(source, imgsz=640)
# for result in results:
#     label = result.names
#     print(label[result.probs.top1])
# detect_torque_wrench_value("data/IMG_0078_jpeg.rf.1d964747be89eeac64299cfbf3625497.jpg")
