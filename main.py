
import cv2

from common.hand_tracking import HandTracker
from common.gesture_detection import GestureDetector
from common.audio import AudioPlayer
from common.lighting import LightingCorrector

# 손 인식 및 손동작 인식 객체 생성
tracker = HandTracker()
gesture = GestureDetector()
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
        frame, hands = tracker.process(processed_frame)


        if hands:
            # 우선 첫 번째 손으로 동작 테스트
            state, play = gesture.update(hands[0])

            raw_state = gesture.classify(hands[0])
            print(f"실제 인식: {raw_state} / 화면 상태: {state}")

            cv2.putText(
                frame,
                f"Gesture: {state}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            if play:
                print("PLAY! - 손을 펼쳤습니다.")
                audio.play("test")

                cv2.putText(
                    frame,
                    "PLAY!",
                    (220, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0, 0, 255),
                    4
                )
        else:
            gesture.reset()

        
        
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

        # 웹캠 화면 하나만 출력
        cv2.imshow("JamJam", frame)



        
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


