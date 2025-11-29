from ultralytics import YOLO

def main():
    # Load YOLO base model
    model = YOLO("yolov8n.pt")

    model.train(
        data=r"C:\Users\AbdulBashar\Downloads\weapon detection.v1i.yolov8\data.yaml",  
        epochs=100,
        resume=False,
        device=0,        # GPU ✔
        workers=8,
        imgsz=416,
        batch=16,
        name="weapon_detection4",
        project="YOLOv8"
    )

if __name__ == "__main__":
    main()
