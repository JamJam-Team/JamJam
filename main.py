
import cv2

from common.hand_tracking import HandTracker
from common.gesture_detection import GestureDetector
from common.audio import AudioPlayer
from common.lighting import LightingCorrector
from common.finger_count import FingerCounter
from common.instrument_selector import InstrumentSelector
from instruments.drum import Drum


# =====================================
# 1. 공통 기능 객체 생성
# =====================================

tracker = HandTracker()

gestures = {
    "Left": GestureDetector(),
    "Right": GestureDetector()
}

finger_counter = FingerCounter()
selector = InstrumentSelector()
drum = Drum()
audio = AudioPlayer()
audio.load_sound("test", "sounds/test.wav")
drum.load_sounds(audio)


lighting = LightingCorrector()
lighting_enabled = True

# None이면 악기 선택 화면
selected_instrument = None


# =====================================
# 2. 웹캠 설정
# =====================================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("웹캠 연결 실패!")
    cap.release()
    tracker.close()
    audio.close()
    raise SystemExit


# =====================================
# 3. 프로그램 실행
# =====================================

try:
    while True:

        ret, frame = cap.read()

        if not ret:
            print("영상 읽기 실패!")
            break

        # 좌우 반전
        frame = cv2.flip(frame, 1)

        # CLAHE 조명 보정
        if lighting_enabled:
            processed_frame = lighting.correct(frame)
        else:
            processed_frame = frame.copy()

        # MediaPipe 손 인식
        frame, hands, handedness = tracker.process(processed_frame)


        # =====================================
        # 4. 악기 선택 화면
        # =====================================

        if selected_instrument is None:

            cv2.putText(
                frame,
                "SELECT INSTRUMENT",
                (120, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2
            )

            menu = [
                "1 - DRUM",
                "2 - PIANO",
                "3 - GUITAR",
                "4 - BASS",
                "5 - COMMON DEMO"
            ]

            for i, text in enumerate(menu):
                cv2.putText(
                    frame,
                    text,
                    (160, 110 + i * 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 255, 255),
                    2
                )

            # 첫 번째 손으로 악기 선택
            if hands:

                finger_count = finger_counter.count(hands[0])
                selected = selector.update(finger_count)

                cv2.putText(
                    frame,
                    f"Fingers: {finger_count}",
                    (170, 385),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                if selected is not None:

                    selected_instrument = selected

                    print(f"선택된 모드: {selected}")

                    # 이전 손동작 상태 초기화
                    for detector in gestures.values():
                        detector.reset()

            else:
                selector.reset()


        # =====================================
        # 5. 악기 연주 화면
        # =====================================

        else:

            cv2.putText(
                frame,
                selected_instrument,
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                1
            )

            # ---------------------------------
            # 5-1. 공통 기능 시연 모드
            # ---------------------------------

            if selected_instrument == "COMMON DEMO":

                detected_hands = set()

                for hand, hand_info in zip(hands, handedness):

                    # 왼손 / 오른손 구분
                    hand_label = hand_info[0].category_name

                    # 좌우 반전 보정
                    if hand_label == "Left":
                        hand_label = "Right"
                    else:
                        hand_label = "Left"

                    detected_hands.add(hand_label)

                    # 손동작 인식
                    state, play = gestures[hand_label].update(hand)

                    # 펼친 손가락 개수
                    finger_count = finger_counter.count(hand)

                    # 손가락 개수 표시
                    text_y = 110 if hand_label == "Left" else 150

                    cv2.putText(
                        frame,
                        f"{hand_label} Fingers: {finger_count}",
                        (20, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )

                    # 손동작 상태 표시
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

                    # FIST -> OPEN이면 테스트 소리 재생
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

                # 화면에서 사라진 손 상태 초기화
                for hand_label in gestures:
                    if hand_label not in detected_hands:
                        gestures[hand_label].reset()


            # ---------------------------------
            # 5-2. 드럼
            # ---------------------------------

            elif selected_instrument == "DRUM":

                # 위쪽 4칸, 아래쪽 3칸 표시
                frame = drum.draw_grid(frame)

                detected_hands = set()

                for hand, hand_info in zip(hands, handedness):

                    # 왼손 / 오른손 구분
                    hand_label = hand_info[0].category_name

                    # 좌우 반전 보정
                    if hand_label == "Left":
                        hand_label = "Right"
                    else:
                        hand_label = "Left"

                    detected_hands.add(hand_label)

                    # 손바닥 중심 좌표 (0~1)
                    x, y = tracker.get_palm_center(hand)

                    # 현재 손이 위치한 격자 번호
                    grid_number = drum.get_grid(x, y)

                    # 주먹 / 펼친 손 인식
                    state, play = gestures[hand_label].update(hand)

                    # 손바닥 중심 픽셀 좌표
                    height, width = frame.shape[:2]
                    center_x = int(x * width)
                    center_y = int(y * height)

                    # 손바닥 중심에 빨간 원 표시
                    cv2.circle(
                        frame,
                        (center_x, center_y),
                        12,
                        (0, 0, 255),
                        -1
                    )

                    # 격자 번호와 손동작 상태 표시
                    cv2.putText(
                        frame,
                        f"GRID {grid_number} {state}",
                        (center_x + 15, center_y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )

                    # FIST -> OPEN이면 해당 격자 타격
                    if play:
                        # 타격한 격자와 시간 기록
                        drum.register_hit(grid_number)

                        # 드럼 클래스에 소리 재생 요청
                        drum.play_sound(audio, grid_number)

                        print(
                            f"{hand_label} DRUM "
                            f"{grid_number} HIT!"
                        )


                # 화면에서 사라진 손 상태 초기화
                for hand_label in gestures:
                    if hand_label not in detected_hands:
                        gestures[hand_label].reset()

                # 타격한 격자를 0.3초 동안 초록색으로 표시
                frame = drum.draw_hit_effect(frame)


            # ---------------------------------
            # 5-3. 다른 악기 (추후 구현)
            # ---------------------------------

            else:

                cv2.putText(
                    frame,
                    "Instrument screen - Coming soon",
                    (80, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )


        # =====================================
        # 6. CLAHE 상태 표시
        # =====================================

        lighting_status = (
            "CLAHE: ON" if lighting_enabled
            else "CLAHE: OFF"
        )

        cv2.putText(
            frame,
            lighting_status,
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )


        # =====================================
        # 7. 화면 출력
        # =====================================

        display_frame = cv2.resize(
            frame,
            (1280, 960)
        )

        cv2.imshow("JamJam", display_frame)


        # =====================================
        # 8. 키보드 입력
        # =====================================

        key = cv2.waitKey(1) & 0xFF

        # Q: 프로그램 종료
        if key == ord("q"):
            break

        # L: CLAHE ON/OFF
        elif key == ord("l"):

            lighting_enabled = not lighting_enabled

            print(
                f"조명 보정: "
                f"{'ON' if lighting_enabled else 'OFF'}"
            )

        # ESC: 악기 선택 화면으로 돌아가기
        elif key == 27:

            selected_instrument = None

            selector.reset()

            for detector in gestures.values():
                detector.reset()

            audio.stop_all()

            print("악기 선택 화면으로 돌아갑니다.")


# =====================================
# 9. 프로그램 종료
# =====================================

finally:

    cap.release()
    tracker.close()
    audio.close()
    cv2.destroyAllWindows()
