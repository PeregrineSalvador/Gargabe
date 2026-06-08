import cv2
import time
import numpy as np
import threading
from flask import Flask, render_template, Response, jsonify, redirect
from gesture_detector import GestureDetector


app = Flask(__name__)

# 全局状态
detector = None
cap = None
system_state = "STANDBY"
garbage_result = "None"
current_gesture = "NONE"
last_state_change = time.time()
logs = []
use_fallback = False
lock = threading.Lock()


def init_system():
    global detector, cap, use_fallback
    detector = GestureDetector()
    
    # 使用与 garbage_control_system.py 相同的方式初始化摄像头
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        use_fallback = False
        add_log("✅ 摄像头初始化成功")
    else:
        cap.release()
        cap = None
        use_fallback = True
        add_log("⚠️ 摄像头不可用，使用模拟视频流")


def add_log(message):
    with lock:
        timestamp = time.strftime("%H:%M:%S")
        logs.append({"time": timestamp, "msg": message})
        if len(logs) > 100:
            logs.pop(0)


def can_switch_state(delay=1.5):
    global last_state_change
    if time.time() - last_state_change > delay:
        last_state_change = time.time()
        return True
    return False


def call_yolo_model(frame):
    time.sleep(0.2)
    return "可回收物 - 塑料瓶"


def update_state_machine(gesture, frame):
    global system_state, garbage_result, last_state_change
    
    if gesture == "FIST":
        system_state = "STANDBY"
        garbage_result = "None"
        add_log("✊ 握拳复位系统")
        last_state_change = time.time()
        return
    
    if system_state == "STANDBY":
        if gesture == "FIVE" and can_switch_state():
            system_state = "DETECTING"
            add_log("🖐️ 检测到手势5，开始识别...")
    
    elif system_state == "DETECTING":
        add_log("🔍 正在调用算法识别物品...")
        garbage_result = call_yolo_model(frame)
        add_log(f"✅ 识别结果: {garbage_result}")
        system_state = "WAITING_AUDIT"
        last_state_change = time.time()
    
    elif system_state == "WAITING_AUDIT":
        if gesture == "OK" and can_switch_state():
            add_log(f"👍 审核通过！【{garbage_result}】闸门已开")
            add_log("⏳ 等待2秒冷却...")
            system_state = "COOLDOWN"
            last_state_change = time.time()
        elif gesture == "ILY" and can_switch_state():
            add_log("❌ 审核错误！进入纠错模式...")
            system_state = "ERROR_CORRECT"
            last_state_change = time.time()
    
    elif system_state == "COOLDOWN":
        if time.time() - last_state_change > 2.0:
            add_log("🔄 自动进入下一轮识别...")
            system_state = "DETECTING"
    
    elif system_state == "ERROR_CORRECT":
        GARBAGE_TYPES = {
            "ONE": "可回收物",
            "TWO": "厨余垃圾",
            "THREE": "有害垃圾",
            "FOUR": "其他垃圾"
        }
        if gesture in GARBAGE_TYPES and can_switch_state():
            real_category = GARBAGE_TYPES[gesture]
            add_log(f"✏️ 修正为: {real_category}")
            
            original_category = garbage_result.split(' - ')[0] if garbage_result != "None" else ""
            if original_category == real_category:
                add_log(f"✅ 识别正确！无需纠错")
            else:
                add_log(f"❌ 识别错误！算法: [{garbage_result}] → 修正: [{real_category}]")
            
            add_log("⏳ 等待2秒冷却...")
            system_state = "COOLDOWN"
            garbage_result = "None"
            last_state_change = time.time()


def draw_ui(frame, gesture):
    STATE_COLORS = {
        "STANDBY": (0, 165, 255),
        "DETECTING": (0, 255, 0),
        "WAITING_AUDIT": (0, 255, 255),
        "COOLDOWN": (128, 128, 128),
        "ERROR_CORRECT": (0, 0, 255)
    }
    curr_color = STATE_COLORS.get(system_state, (0, 255, 0))
    
    cv2.putText(frame, f"STATE: {system_state}", (30, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, curr_color, 2)
    cv2.putText(frame, f"GESTURE: {gesture}", (30, 120), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    if system_state in ["WAITING_AUDIT", "ERROR_CORRECT"]:
        cv2.putText(frame, f"RESULT: {garbage_result}", (30, 160), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    if system_state == "ERROR_CORRECT":
        cv2.putText(frame, "1:Recycle 2:Kitchen 3:Harmful 4:Other", 
                    (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


def generate_fallback_frame():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, "Camera Not Available", (150, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    cv2.putText(frame, "Using fallback mode", (180, 280), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)
    return frame


def detect_ily_gesture(frame, landmarks):
    if landmarks is None:
        return False
    
    h, w, _ = frame.shape
    landmarks_dict = {id: (int(lm.x * w), int(lm.y * h)) for id, lm in enumerate(landmarks.landmark)}
    
    index_up = landmarks_dict[8][1] < landmarks_dict[6][1]
    middle_up = landmarks_dict[12][1] < landmarks_dict[10][1]
    ring_up = landmarks_dict[16][1] < landmarks_dict[14][1]
    pinky_up = landmarks_dict[20][1] < landmarks_dict[18][1]
    thumb_up = abs(landmarks_dict[4][0] - landmarks_dict[17][0]) > 60
    
    return thumb_up and index_up and not middle_up and not ring_up and pinky_up


def generate_frames():
    global current_gesture
    
    while True:
        if use_fallback:
            frame = generate_fallback_frame()
        else:
            success, frame = cap.read()
            if not success:
                frame = generate_fallback_frame()
            else:
                frame = cv2.flip(frame, 1)
        
        gesture, landmarks = detector.process_frame(frame)
        
        if gesture == "NONE" and landmarks is not None:
            if detect_ily_gesture(frame, landmarks):
                gesture = "ILY"
        
        with lock:
            current_gesture = gesture
        detector.draw(frame, landmarks)
        
        update_state_machine(gesture, frame)
        draw_ui(frame, gesture)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/status')
def status():
    with lock:
        return jsonify({
            "state": system_state,
            "gesture": current_gesture,
            "result": garbage_result,
            "image_url": "/garbage_image" if garbage_result != "None" else None
        })


@app.route('/garbage_image')
def garbage_image():
    garbage_images = {
        "可回收物": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=recyclable%20plastic%20bottle%20on%20white%20background&image_size=square",
        "厨余垃圾": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=food%20waste%20leftovers%20on%20white%20background&image_size=square",
        "有害垃圾": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=hazardous%20battery%20chemical%20waste%20on%20white%20background&image_size=square",
        "其他垃圾": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=other%20trash%20miscellaneous%20rubbish%20on%20white%20background&image_size=square"
    }
    
    category = garbage_result.split(' - ')[0] if garbage_result != "None" else "其他垃圾"
    image_url = garbage_images.get(category, garbage_images["其他垃圾"])
    
    return redirect(image_url)


@app.route('/logs')
def logs_endpoint():
    with lock:
        return jsonify(list(logs))


if __name__ == '__main__':
    init_system()
    port = 8080
    print(f"Web服务启动中... 访问 http://localhost:{port}")
    try:
        app.run(host='0.0.0.0', port=port, threaded=True)
    finally:
        if cap is not None:
            cap.release()
        if detector is not None:
            detector.close()