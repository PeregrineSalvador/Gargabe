from ultralytics import YOLO

# 1. 加载预训练模型
model = YOLO("yolov8n.pt")

# 2. 训练（参数和命令行一一对应）
model.train(
    data="/media/salvador/7415/GL_Gargabe_Task/datasets/trash_yolo/trash.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    project="runs/detect",
    name="trash_train",
    exist_ok=True
)

print("✅ 训练完成，最佳权重：", model.trainer.best)