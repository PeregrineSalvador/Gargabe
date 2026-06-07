import cv2
import mediapipe as mp

class GestureDetector:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process_frame(self, frame):
        """
        处理单帧图像，识别手势
        返回: gesture_name (str), hand_landmarks
        """
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture = "NONE"
        current_landmarks = None

        if results.multi_hand_landmarks:
            current_landmarks = results.multi_hand_landmarks[0]
            landmarks_dict = {id: (int(lm.x * w), int(lm.y * h)) for id, lm in enumerate(current_landmarks.landmark)}

            # 1. 计算手指伸直状态
            index_up  = landmarks_dict[8][1] < landmarks_dict[6][1]
            middle_up = landmarks_dict[12][1] < landmarks_dict[10][1]
            ring_up   = landmarks_dict[16][1] < landmarks_dict[14][1]
            pinky_up  = landmarks_dict[20][1] < landmarks_dict[18][1]
            thumb_up  = abs(landmarks_dict[4][0] - landmarks_dict[17][0]) > 60

            # 2. 手势状态决策
            if index_up and middle_up and ring_up and pinky_up and thumb_up:
                gesture = "FIVE"
            elif not index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
                gesture = "FIST"
            elif (not index_up) and middle_up and ring_up and pinky_up:
                gesture = "OK"
            elif index_up and middle_up and ring_up and pinky_up and (not thumb_up):
                gesture = "FOUR"
            elif index_up and not middle_up and not ring_up and not pinky_up:
                gesture = "ONE"
            elif index_up and middle_up and not ring_up and not pinky_up:
                gesture = "TWO"
            elif index_up and middle_up and ring_up and not pinky_up:
                gesture = "THREE"
                
        return gesture, current_landmarks

    def draw(self, frame, landmarks):
        if landmarks:
            self.mp_drawing.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)

    def close(self):
        self.hands.close()