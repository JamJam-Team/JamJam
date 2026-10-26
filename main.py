
import cv2

from common.hand_tracking import HandTracker
from common.gesture_detection import GestureDetector
from common.audio import AudioPlayer
from common.lighting import LightingCorrector

# 손 인식 및 손동작 인식 객체 생성
tracker = HandTracker()
# 왼손과 오른손의 손동작을 독립적으로 관리
gestures = {
    "Left": GestureDetector(),
    "Right": GestureDetector()
}
#소리 재생
audio = AudioPlayer()
audio.load_sound("test", "sounds/test.wav")
lighting = LightingCorrector()
lighting_enabled = True

# 웹캠 실행
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("웹캠 연결 실패!")
    tracker.close()
    raise SystemExit

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("영상 읽기 실패!")
            break

        
        frame = cv2.flip(frame, 1)

        
        # 조명 보정 ON/OFF
        if lighting_enabled:
            processed_frame = lighting.correct(frame)
        else:
            processed_frame = frame.copy()

        # 선택된 영상으로 손 인식
        
        frame, hands, handedness = tracker.process(processed_frame)



        
        if hands:
            detected_hands = set()

            for hand, hand_info in zip(hands, handedness):
                # 왼손 / 오른손 구분
                hand_label = hand_info[0].category_name
                # 실제 손과 표시가 반대이므로 좌우 교환
                if hand_label == "Left":
                    hand_label = "Right"
                else:
                    hand_label = "Left"

                detected_hands.add(hand_label)

                # 각 손의 동작을 독립적으로 인식
                state, play = gestures[hand_label].update(hand)

                # 화면에 손동작 상태 표시
                y_position = 40 if hand_label == "Left" else 120

                cv2.putText(
                    frame,
                    f"{hand_label}: {state}",
                    (20, y_position),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                if play:
                    print(f"{hand_label} PLAY!")
                    audio.play("test")

                    cv2.putText(
                        frame,
                        f"{hand_label} PLAY!",
                        (180, 240),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 0, 255),
                        3
                    )

            # 화면에서 사라진 손의 상태 초기화
            for hand_label in gestures:
                if hand_label not in detected_hands:
                    gestures[hand_label].reset()

        else:
            # 양손 모두 인식되지 않으면 초기화
            for gesture_detector in gestures.values():
                gesture_detector.reset()


        
        
        # 조명 보정 상태 표시
        lighting_status = (
            "CLAHE: ON" if lighting_enabled
            else "CLAHE: OFF"
        )

        cv2.putText(
            frame,
            lighting_status,
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        # 웹캠 화면을 크게 출력
        display_frame = cv2.resize(frame, (1280, 960))

        cv2.imshow("JamJam", display_frame)




        
        key = cv2.waitKey(1) & 0xFF

        # Q 키: 프로그램 종료
        if key == ord('q'):
            break

        # L 키: 조명 보정 ON/OFF
        elif key == ord('l'):
            lighting_enabled = not lighting_enabled
            print(f"조명 보정: {'ON' if lighting_enabled else 'OFF'}")


finally:
    cap.release()
    tracker.close()
    audio.close()
    cv2.destroyAllWindows()


