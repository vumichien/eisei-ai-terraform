from ultralytics import YOLO

source = "data"
model = YOLO("models/straight-check-v4.pt")

results = model(source, imgsz=640)
for result in results:
    label = result.names
    print(label[result.probs.top1])
