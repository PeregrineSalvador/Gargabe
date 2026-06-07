import cv2
import time
from gesture_detector import GestureDetector


class GarbageControlSystem:
    """垃圾分类控制系统 - 封装状态管理和业务逻辑"""
    
    GARBAGE_TYPES = {
        "ONE": "可回收物",
        "TWO": "厨余垃圾",
        "THREE": "有害垃圾",
        "FOUR": "其他垃圾"
    }
    
    STATE_COLORS = {
        "STANDBY": (0, 165, 255),       # 橙色
        "WAITING_AUDIT": (0, 255, 255), # 黄色
        "ERROR_CORRECT": (0, 0, 255)    # 红色
    }
    
    def __init__(self):
        self.detector = GestureDetector()
        self.cap = cv2.VideoCapture(0)
        self.system_state = "STANDBY"
        self.garbage_result = "None"
        self.last_state_change = time.time()
    
    def can_switch_state(self, delay=1.5):
        """状态切换防抖"""
        if time.time() - self.last_state_change > delay:
            self.last_state_change = time.time()
            return True
        return False
    
    def call_yolo_model(self, image_frame):
        """预留的YOLOv8识别接口"""
        time.sleep(0.2)  # 模拟推理延迟
        return "可回收物 - 塑料瓶"
    
    def log_correction_result(self, detected_res, real_res):
        """预留的日志/数据集收集接口"""
        print(f"[数据埋点/记录] ❌ 识别错误！算法结果: [{detected_res}] --> 人工修正为: [{real_res}]")
    
    def process_standby(self, gesture):
        """待机状态处理"""
        if gesture == "FIVE" and self.can_switch_state():
            self.system_state = "DETECTING"
    
    def process_detecting(self, frame):
        """检测状态处理"""
        print("正在调用算法识别物品...")
        self.garbage_result = self.call_yolo_model(frame)
        print(f"算法识别结果为: {self.garbage_result}。请人工审核...")
        self.system_state = "WAITING_AUDIT"
    
    def process_waiting_audit(self, gesture):
        """等待审核状态处理"""
        if gesture == "OK" and self.can_switch_state():
            print(f"审核通过！【{self.garbage_result}】投放闸门已打开。")
            self.system_state = "STANDBY"
        elif gesture == "FOUR" and self.can_switch_state():
            print("审核结果：错误！系统进入人工纠错模式，请伸出数字手势...")
            self.system_state = "ERROR_CORRECT"
    
    def process_error_correct(self, gesture):
        """纠错状态处理"""
        if gesture in self.GARBAGE_TYPES and self.can_switch_state():
            real_category = self.GARBAGE_TYPES[gesture]
            print(f"人工修正成功，实际归类为: {real_category}")
            self.log_correction_result(self.garbage_result, real_category)
            self.system_state = "STANDBY"
            self.garbage_result = "None"
    
    def update_state_machine(self, gesture, frame):
        """状态机主入口"""
        if gesture == "FIST":
            self.system_state = "STANDBY"
            self.garbage_result = "None"
            return
        
        state_handlers = {
            "STANDBY": lambda: self.process_standby(gesture),
            "DETECTING": lambda: self.process_detecting(frame),
            "WAITING_AUDIT": lambda: self.process_waiting_audit(gesture),
            "ERROR_CORRECT": lambda: self.process_error_correct(gesture)
        }
        
        handler = state_handlers.get(self.system_state)
        if handler:
            handler()
    
    def draw_ui(self, frame, gesture):
        """绘制UI看板"""
        curr_color = self.STATE_COLORS.get(self.system_state, (0, 255, 0))
        
        cv2.putText(frame, f"SYS_STATE: {self.system_state}", (30, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, curr_color, 2)
        cv2.putText(frame, f"CURR_GESTURE: {gesture}", (30, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if self.system_state in ["WAITING_AUDIT", "ERROR_CORRECT"]:
            cv2.putText(frame, f"YOLO_RES: {self.garbage_result}", (30, 120), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        if self.system_state == "ERROR_CORRECT":
            cv2.putText(frame, "FIX: Show 1(Recycle) 2(Kitchen) 3(Harmful) 4(Other)", 
                        (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    def run(self):
        """系统主循环"""
        print("系统已启动。标准流程：[手势5]开始识别 -> [手势OK]确认通过 / [手势4]进入纠错 -> 纠错模式下用[手势1~4]手动分类。")
        
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            gesture, landmarks = self.detector.process_frame(frame)
            self.detector.draw(frame, landmarks)
            
            self.update_state_machine(gesture, frame)
            self.draw_ui(frame, gesture)
            
            cv2.imshow('Garbage Control System', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        self.detector.close()