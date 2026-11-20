import cv2

from common.hand_tracking import HandTracker
from common.gesture_detection import GestureDetector
from common.audio import AudioPlayer
from common.lighting import LightingCorrector
from common.finger_count import FingerCounter
from common.instrument_selector import InstrumentSelector
from instruments.drum import Drum
from instruments.piano import Piano
from instruments.bass import Bass
from instruments.guitar import Guitar

# =====================================
# 1. 공통 기능 및 악기 객체 생성
# =====================================

tracker = HandTracker()

gestures = {
    "Left": GestureDetector(),
    "Right": GestureDetector()
}

finger_counter = FingerCounter()
selector = InstrumentSelector()
lighting = LightingCorrector()
lighting_enabled = True

audio = AudioPlayer()

# 드럼 객체 생성 및 음원 등록
drum = Drum()
drum.load_sounds(audio)

# 피아노 객체 생성 및 음원 등록
piano = Piano()
piano.load_sounds(audio)

# 베이스 객체 생성 및 음원 등록
bass = Bass()
bass.load_sounds(audio)

# 기타 객체 생성 및 음원 등록
guitar = Guitar()
guitar.load_sounds(audio)

# 선택된 악기가 없으면 악기 선택 화면 표시
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

        # CLAHE 조명 보정 적용 여부 확인
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
                (20, 35),
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
            ]

            for i, text in enumerate(menu):
                cv2.putText(
                    frame,
                    text,
                    (25, 110 + i * 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

            # 키보드 조작 안내
            key_guide = [
                "KEYBOARD GUIDE",
                "Q : Quit",
                "L : CLAHE ON/OFF",
                "ESC : Back to Menu"
            ]

            for i, text in enumerate(key_guide):
                cv2.putText(
                    frame,
                    text,
                    (480, 30 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )

            # 첫 번째 인식된 손의 손가락 개수로 악기 선택
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

            # ---------------------------------
            # 화면 상단에 현재 선택된 악기 표시
            # ---------------------------------

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
            # 5-1. 드럼
            # ---------------------------------

            if selected_instrument == "DRUM":

                # 드럼 연주 영역을 위쪽 4칸, 아래쪽 3칸으로 표시
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

                    # 주먹을 쥐었다 펴면 해당 격자 타격 처리
                    if play:
                        # 타격한 격자와 시간 기록
                        drum.register_hit(grid_number)

                        # 해당 격자의 드럼 음원 재생
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
            # 5-2. 피아노
            # ---------------------------------
            elif selected_instrument == "PIANO":

                # 피아노 연주 영역 표시
                frame = piano.draw_grid(frame)

                detected_hands = set()

                for hand, hand_info in zip(hands, handedness):

                    # 좌우 반전 보정
                    hand_label = hand_info[0].category_name
                    hand_label = (
                        "Right" if hand_label == "Left"
                        else "Left"
                    )
                    detected_hands.add(hand_label)

                    # 손바닥 중심으로 격자 계산
                    x, y = tracker.get_palm_center(hand)
                    grid_number = piano.get_grid(x, y)

                    # 주먹을 쥐었다 펴는 동작 감지
                    state, play = gestures[hand_label].update(hand)

                    height, width = frame.shape[:2]
                    center_x = int(x * width)
                    center_y = int(y * height)

                    cv2.circle(
                        frame, (center_x, center_y),
                        12, (0, 0, 255), -1
                    )

                    cv2.putText(
                        frame,
                        f"GRID {grid_number} {state}",
                        (center_x + 15, center_y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 255), 2
                    )

                    if play and grid_number is not None:
                        piano.register_hit(grid_number)
                        piano.play_sound(audio, grid_number)

                        print(
                            f"{hand_label} PIANO "
                            f"{piano.piano_names[grid_number - 1]} PLAY!"
                        )

                # 화면에서 사라진 손 상태 초기화
                for hand_label in gestures:
                    if hand_label not in detected_hands:
                        gestures[hand_label].reset()

                # 연주 효과 표시
                frame = piano.draw_hit_effect(frame)

            
            # ---------------------------------
            # 5-3. 베이스 (왼손 프렛 3칸 + 오른손 주법 5칸)
            # ---------------------------------
            elif selected_instrument == "BASS":

                # 베이스 연주 영역 표시
                frame = bass.draw_grid(frame)

                detected_hands = set()

                for hand, hand_info in zip(hands, handedness):

                    # 좌우 반전 보정
                    hand_label = hand_info[0].category_name
                    hand_label = "Right" if hand_label == "Left" else "Left"
                    detected_hands.add(hand_label)

                    # 손바닥 중심 좌표 (0~1)
                    x, y = tracker.get_palm_center(hand)
                    height, width = frame.shape[:2]
                    center_x = int(x * width)
                    center_y = int(y * height)

                    # 주먹을 쥐었다 펴는 동작 감지
                    state, play = gestures[hand_label].update(hand)

                    # 왼손 위치에 따라 프렛(Fret 1, 3, 5) 선택
                    if hand_label == "Left":
                        fret_idx = bass.update_fret(y)

                        # 왼손 위치와 선택한 프렛 표시
                        cv2.circle(frame, (center_x, center_y), 12, (255, 0, 0), -1)
                        cv2.putText(
                            frame,
                            f"{bass.fret_names[fret_idx]}",
                            (center_x + 15, center_y - 15),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255, 200, 0),
                            2
                        )

                    # 오른손 위치에 따라 주법(Finger, Slap, Pop, Pick, Mute) 선택
                    elif hand_label == "Right":
                        tech_idx = bass.get_tech_grid(y)

                        # 오른손 위치와 선택한 주법 표시
                        cv2.circle(frame, (center_x, center_y), 12, (0, 0, 255), -1)
                        cv2.putText(
                            frame,
                            f"{bass.tech_names[tech_idx]} {state}",
                            (center_x + 15, center_y - 15),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 255),
                            2
                        )

                        # 오른손을 쥐었다 펴면 선택한 주법의 음원 재생
                        if play:
                            bass.register_hit(tech_idx)
                            bass.play_sound(audio, tech_idx)
                            print(
                                f"[BASS] {bass.fret_names[bass.current_fret]} + "
                                f"{bass.tech_names[tech_idx]} PLAY!"
                            )

                # 화면에서 사라진 손 상태 초기화
                for hand_label in gestures:
                    if hand_label not in detected_hands:
                        gestures[hand_label].reset()

                # 연주 시각 효과 표시
                frame = bass.draw_hit_effect(frame)
            

            # ---------------------------------
            # 5-4. 기타
            # ---------------------------------
            elif selected_instrument == "GUITAR":

                # 기타 연주 영역 표시
                frame = guitar.draw_grid(frame)

                detected_hands = set()

                # 현재 선택된 코드와 연주 방법
                selected_chord = None
                selected_method = None

                # 손동작으로 연주 신호가 발생했는지 기록
                play_requested = False

                for hand, hand_info in zip(hands, handedness):

                    # 왼손 / 오른손 구분
                    hand_label = hand_info[0].category_name

                    if hand_label == "Left":
                        hand_label = "Right"
                    else:
                        hand_label = "Left"

                    detected_hands.add(hand_label)

                    # 손바닥 중심 좌표
                    x, y = tracker.get_palm_center(hand)

                    # 주먹 / 손 펴기 판별
                    state, play = gestures[hand_label].update(hand)

                    # 손 위치에 따라 코드 또는 연주 방법 선택
                    if hand_label == "Left":
                        selected_chord = guitar.get_chord(x, y)
                    else:
                        selected_method = guitar.get_method(x, y)

                    # 손바닥 위치 표시
                    height, width = frame.shape[:2]
                    center_x = int(x * width)
                    center_y = int(y * height)

                    cv2.circle(
                        frame,
                        (center_x, center_y),
                        12,
                        (0, 0, 255),
                        -1
                    )

                    # 손 위치에 따라 선택된 코드 또는 주법 정보 표시
                    selected_text = (
                        selected_chord
                        if hand_label == "Left"
                        else selected_method
                    )

                    cv2.putText(
                        frame,
                        f"{hand_label}: {selected_text} {state}",
                        (center_x + 15, center_y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 255),
                        2
                    )

                    # 손동작이 감지되면 연주 요청 기록
                    if play:
                        play_requested = True

                # 화면에서 사라진 손 초기화
                for hand_label in gestures:
                    if hand_label not in detected_hands:
                        gestures[hand_label].reset()

                if play_requested:

                    # 예외 주법이 선택된 경우 별도 음원 재생
                    if selected_method == "EXCEPTION":

                        guitar.play_exception(audio)

                        print("GUITAR EXCEPTION PLAY!")

                    # 코드와 주법이 모두 선택된 경우 음원 재생
                    elif (
                        selected_chord is not None
                        and selected_method is not None
                    ):

                        guitar.play_sound(
                            audio,
                            selected_chord,
                            selected_method
                        )

                        print(
                            f"GUITAR PLAY: "
                            f"{selected_chord} + {selected_method}"
                        )

                # 기타 연주 시각 효과 표시
                frame = guitar.draw_hit_effect(frame)   
            
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
            (960, 720)
        )

        cv2.imshow("JamJam", display_frame)


        # =====================================
        # 8. 키보드 입력
        # =====================================

        key = cv2.waitKey(1) & 0xFF

        # Q: 프로그램 종료
        if key == ord("q"):
            break

        # L: CLAHE 조명 보정 켜기/끄기
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
