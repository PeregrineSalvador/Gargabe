import os

SRC = "trashnet/data"
DST_IMG = "datasets/trash_yolo/images/train"
DST_LBL = "datasets/trash_yolo/labels/train"

classes = ["glass", "paper", "cardboard", "plastic", "metal", "trash"]
class_id = {c:i for i,c in enumerate(classes)}

for c in classes:
    img_dir = os.path.join(SRC, c)
    for img in os.listdir(img_dir):
        if not img.endswith(".jpg"):
            continue
        os.system(f"cp {img_dir}/{img} {DST_IMG}")

        # YOLO 格式：[class_id x_center y_center w h]
        label = f"{class_id[c]} 0.5 0.5 1.0 1.0\n"
        with open(os.path.join(DST_LBL, img.replace(".jpg", ".txt")), "w") as f:
            f.write(label)