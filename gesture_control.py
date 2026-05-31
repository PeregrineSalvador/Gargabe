import cv2
import mediapipe as mp

# 1. 初始化 MediaPipe（版本对了，这里绝对不会再报错！）
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)
print("系统已启动，按下 'q' 键退出程序。")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            h, w, c = frame.shape
            landmarks_dict = {}
            for id, lm in enumerate(hand_landmarks.landmark):
                landmarks_dict[id] = (int(lm.x * w), int(lm.y * h))

            # 判断手指是否伸直
            index_finger_up = landmarks_dict[8][1] < landmarks_dict[6][1]
            middle_finger_up = landmarks_dict[12][1] < landmarks_dict[10][1]
            ring_finger_up = landmarks_dict[16][1] < landmarks_dict[14][1]
            pinky_finger_up = landmarks_dict[20][1] < landmarks_dict[18][1]

            # 【手势 1】：数字 1
            if index_finger_up and not middle_finger_up and not ring_finger_up and not pinky_finger_up:
                cv2.putText(frame, "Gesture: 1", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # 👇 补充你的控制代码 👇
                pass

            # 【手势 2】：数字 2 / 剪刀
            elif index_finger_up and middle_finger_up and not ring_finger_up and not pinky_finger_up:
                cv2.putText(frame, "Gesture: 2", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                # 👇 补充你的控制代码 👇
                pass

    cv2.imshow('Gesture Control System', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()