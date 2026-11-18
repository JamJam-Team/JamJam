
import cv2
import time


class Guitar:
    def __init__(self):
        # 왼손: 코드 선택
        self.chord_names = ["D", "A", "G", "Bm7"]

        # 오른손: 연주 방법 및 예외
        self.method_names = [
            "METHOD 1",
            "METHOD 2",
            "METHOD 3",
            "EXCEPTION"
        ]

        # 구역별 색상 (OpenCV BGR)
        self.chord_colors = [
            (250, 220, 160),
            (180, 230, 160),
            (170, 210, 255),
            (235, 180, 210)
        ]

        self.method_colors = [
            (255, 180, 100),
            (180, 230, 180),
            (210, 180, 250),
            (100, 180, 255)
        ]

        # 선택 효과
        self.hit_times = {}
        self.flash_duration = 0.3

    # =====================================
    # 구역 위치 계산
    # =====================================

    def get_grid_rect(self, side, grid_number, width, height):
        if not 1 <= grid_number <= 4:
            raise ValueError("구역 번호는 1~4여야 합니다.")

        half_width = width // 2

        if side == "LEFT":
            x1 = 0
            x2 = half_width
        else:
            x1 = half_width
            x2 = width

        y1 = (grid_number - 1) * height // 4
        y2 = grid_number * height // 4

        return x1, y1, x2, y2

    # =====================================
    # 기타 화면 표시
    # =====================================

    def draw_grid(self, frame):
        height, width = frame.shape[:2]

        for i in range(4):
            # 왼쪽: 코드 구역
            x1, y1, x2, y2 = self.get_grid_rect(
                "LEFT", i + 1, width, height
            )

            color = self.chord_colors[i]
            overlay = frame.copy()

            cv2.rectangle(
                overlay, (x1, y1), (x2 - 1, y2 - 1),
                color, -1
            )
            cv2.addWeighted(overlay, 0.12, frame, 0.88, 0, frame)

            cv2.rectangle(
                frame, (x1 + 3, y1 + 3), (x2 - 4, y2 - 4),
                color, 2
            )

            cv2.putText(
                frame, self.chord_names[i],
                (x1 + 15, y1 + 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (255, 255, 255), 2
            )

            # 오른쪽: 연주 방법 및 예외 구역
            x1, y1, x2, y2 = self.get_grid_rect(
                "RIGHT", i + 1, width, height
            )

            color = self.method_colors[i]
            overlay = frame.copy()

            cv2.rectangle(
                overlay, (x1, y1), (x2 - 1, y2 - 1),
                color, -1
            )
            cv2.addWeighted(overlay, 0.12, frame, 0.88, 0, frame)

            cv2.rectangle(
                frame, (x1 + 3, y1 + 3), (x2 - 4, y2 - 4),
                color, 2
            )

            cv2.putText(
                frame, self.method_names[i],
                (x1 + 15, y1 + 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2
            )

        cv2.putText(
            frame, "LEFT HAND: CHORD",
            (10, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45, (255, 255, 255), 1
        )

        cv2.putText(
            frame, "RIGHT HAND: METHOD",
            (width // 2 + 10, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45, (255, 255, 255), 1
        )

        return frame

    # =====================================
    # 왼손 코드 판별
    # =====================================

    def get_chord(self, x, y):
        if not (0 <= x < 0.5 and 0 <= y <= 1):
            return None

        grid = min(int(y * 4), 3)
        return self.chord_names[grid]

    # =====================================
    # 오른손 연주 방법 판별
    # =====================================

    def get_method(self, x, y):
        if not (0.5 <= x <= 1 and 0 <= y <= 1):
            return None

        grid = min(int(y * 4), 3)
        return self.method_names[grid]

    # =====================================
    # 선택 효과 기록
    # =====================================

    def register_hit(self, side, grid_number):
        self.hit_times[(side, grid_number)] = time.monotonic()

    # =====================================
    # 선택 효과 표시
    # =====================================

    def draw_hit_effect(self, frame):
        current_time = time.monotonic()
        height, width = frame.shape[:2]

        for (side, grid_number), hit_time in list(self.hit_times.items()):
            if current_time - hit_time > self.flash_duration:
                del self.hit_times[(side, grid_number)]
                continue

            x1, y1, x2, y2 = self.get_grid_rect(
                side, grid_number, width, height
            )

            overlay = frame.copy()
            cv2.rectangle(
                overlay, (x1, y1), (x2 - 1, y2 - 1),
                (255, 255, 255), -1
            )

            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        return frame



    # =====================================
    # 기타 음원 불러오기
    # =====================================

    def load_sounds(self, audio):

        # 방법 1
        audio.load_sound("D_method1", "sounds/guitar/D_method1.wav")
        audio.load_sound("A_method1", "sounds/guitar/A_method1.wav")
        audio.load_sound("G_method1", "sounds/guitar/G_method1.wav")
        audio.load_sound("Bm7_method1", "sounds/guitar/Bm7_method1.wav")

        # 방법 2
        audio.load_sound("A_method2", "sounds/guitar/A_method2.wav")
        audio.load_sound("G_method2", "sounds/guitar/G_method2.wav")

        # 방법 3
        audio.load_sound("D_method3", "sounds/guitar/D_method3.wav")
        audio.load_sound("A_method3", "sounds/guitar/A_method3.wav")
        audio.load_sound("G_method3", "sounds/guitar/G_method3.wav")
        audio.load_sound("Bm7_method3", "sounds/guitar/Bm7_method3.wav")

        # 예외
        audio.load_sound("EXCEPTION", "sounds/guitar/EXCEPTION.wav")


    # =====================================
    # 기타 음원 재생
    # =====================================

    def play_sound(self, audio, chord, method):

        method_numbers = {
            "METHOD 1": "1",
            "METHOD 2": "2",
            "METHOD 3": "3"
        }

        method_number = method_numbers.get(method)

        if method_number is None:
            return

        sound_name = f"{chord}_method{method_number}"

        audio.play(sound_name)


    def play_exception(self, audio):

        audio.play("EXCEPTION")