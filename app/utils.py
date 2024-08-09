import os
from PIL import Image


def parse_detection(detections):
    parsed_rows = []
    for i in range(len(detections.xyxy)):
        x_min = float(detections.xyxy[i][0])
        y_min = float(detections.xyxy[i][1])
        x_max = float(detections.xyxy[i][2])
        y_max = float(detections.xyxy[i][3])

        width = int(x_max - x_min)
        height = int(y_max - y_min)

        row = {
            "x": int(x_min),
            "y": int(y_min),
            "width": width,
            "height": height,
            "class_id": (
                "" if detections.class_id is None else int(detections.class_id[i])
            ),
            "confidence": (
                "" if detections.confidence is None else float(detections.confidence[i])
            ),
            "tracker_id": (
                "" if detections.tracker_id is None else int(detections.tracker_id[i])
            ),
        }

        if hasattr(detections, "data"):
            for key, value in detections.data.items():
                if key == "class_name":
                    key = "class"
                row[key] = (
                    str(value[i])
                    if hasattr(value, "__getitem__") and value.ndim != 0
                    else str(value)
                )
        parsed_rows.append(row)
    return parsed_rows


def crop_images(image, output_directory, box):
    image_file_name = "temp.jpg"
    image = Image.fromarray(image)
    cropped_img = image.crop(box)
    resized_img = cropped_img.resize((640, 1024))
    straight_box_img = resized_img.crop(((320 - 32), 468, (320 + 32), 756)).resize(
        (224, 224)
    )
    value_box_img = resized_img.crop(((320 - 256), 468, (320 + 256), 884)).resize(
        (224, 224)
    )

    # Create directories if they do not exist
    cropped_img_dir = os.path.join(output_directory, "cropped")
    straight_box_img_dir = os.path.join(output_directory, "straight_box")
    value_box_img_dir = os.path.join(output_directory, "value_box")

    os.makedirs(cropped_img_dir, exist_ok=True)
    os.makedirs(straight_box_img_dir, exist_ok=True)
    os.makedirs(value_box_img_dir, exist_ok=True)

    cropped_output_img_path = os.path.join(cropped_img_dir, image_file_name)
    cropped_img.save(cropped_output_img_path)

    straight_box_img_path = os.path.join(straight_box_img_dir, image_file_name)
    straight_box_img.save(straight_box_img_path)

    value_box_img_path = os.path.join(value_box_img_dir, image_file_name)
    value_box_img.save(value_box_img_path)
