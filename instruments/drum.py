
import cv2
import time


class Drum:
    def __init__(self):
        self.grid_count = 7

        # 드럼 격자별 악기 이름
        self.drum_names = [
            "CRASH",
            "HIGH TOM",
            "FLOOR TOM",
            "RIDE",
            "HI-HAT",
            "KICK",
            "SNARE"
        ]

        # 드럼 격자별 음원 이름
        self.sound_names = [
            "crash",
            "high_tom",
            "floor_tom",
            "ride",
            "hihat",
            "kick",
            "snare"
        ]

        # 악기별 색상 (OpenCV는 BGR 순서)
        self.colors = [
            (0, 215, 255),    # CRASH - 노란색
            (255, 160, 180),  # HIGH TOM - 보라색
            (255, 120, 100),  # FLOOR TOM - 파란색
            (255, 220, 80),   # RIDE - 하늘색
            (120, 220, 80),   # HI-HAT - 초록색
            (60, 160, 255),   # KICK - 주황색
            (150, 100, 255)   # SNARE - 분홍색
        ]

        # 마지막으로 타격한 격자와 시간
        self.hit_times = {}

        # 타격 효과 유지 시간 (초)
        self.flash_duration = 0.3

    # =====================================
    # 격자 위치 계산
    # =====================================

    def get_grid_rect(self, grid_number, width, height):
        half_height = height // 2

        # 위쪽 4칸
        if grid_number <= 4:
            index = grid_number - 1

            x1 = index * width // 4
            x2 = (index + 1) * width // 4

            y1, y2 = 0, half_height

        # 아래쪽 3칸
        else:
            index = grid_number - 5

            x1 = index * width // 3
            x2 = (index + 1) * width // 3

            y1, y2 = half_height, height

        return x1, y1, x2, y2

    # =====================================
    # 드럼 격자 UI 표시
    # =====================================

    def draw_grid(self, frame):
        height, width = frame.shape[:2]

        for i in range(self.grid_count):
            grid_number = i + 1

            x1, y1, x2, y2 = self.get_grid_rect(
                grid_number, width, height
            )

            color = self.colors[i]

            # 반투명 색상 배경
            overlay = frame.copy()

            cv2.rectangle(
                overlay,
                (x1, y1),
                (x2 - 1, y2 - 1),
                color,
                -1
            )

            cv2.addWeighted(
                overlay, 0.12,
                frame, 0.88,
                0, frame
            )

            # 악기별 색상 테두리
            cv2.rectangle(
                frame,
                (x1 + 3, y1 + 3),
                (x2 - 4, y2 - 4),
                color,
                2
            )

            # 악기 이름 표시
            cv2.putText(
                frame,
                self.drum_names[i],
                (x1 + 10, y2 - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 255, 255),
                2
            )

        return frame

    # =====================================
    # 손바닥 위치에 따른 격자 번호 계산
    # =====================================

    def get_grid(self, x, y):
        # x, y는 0~1 사이의 정규화 좌표

        # 위쪽 4칸
        if y < 0.5:
            grid = int(x * 4) + 1
            return min(grid, 4)

        # 아래쪽 3칸
        else:
            grid = int(x * 3) + 5
            return min(grid, 7)

    # =====================================
    # 드럼 타격 기록
    # =====================================

    def register_hit(self, grid_number):
        # 해당 격자가 타격된 시간 저장
        self.hit_times[grid_number] = time.monotonic()

    # =====================================
    # 드럼 타격 시 하얀색 반짝임 효과
    # =====================================

    def draw_hit_effect(self, frame):
        current_time = time.monotonic()
        height, width = frame.shape[:2]

        for grid_number, hit_time in list(self.hit_times.items()):

            # 0.3초가 지난 타격 효과 제거
            if current_time - hit_time > self.flash_duration:
                del self.hit_times[grid_number]
                continue

            # 타격된 격자의 위치 계산
            x1, y1, x2, y2 = self.get_grid_rect(
                grid_number, width, height
            )

            # 반투명 하얀색 타격 효과
            overlay = frame.copy()

            cv2.rectangle(
                overlay,
                (x1, y1),
                (x2 - 1, y2 - 1),
                (255, 255, 255),
                -1
            )

            cv2.addWeighted(
                overlay, 0.3,
                frame, 0.7,
                0, frame
            )

        return frame

    # =====================================
    # 드럼 음원 불러오기
    # =====================================

    def load_sounds(self, audio):
        audio.load_sound("crash", "sounds/drum/crash.wav")
        audio.load_sound("high_tom", "sounds/drum/high_tom.wav")
        audio.load_sound("floor_tom", "sounds/drum/floor_tom.wav")
        audio.load_sound("ride", "sounds/drum/ride.wav")
        audio.load_sound("hihat", "sounds/drum/hihat.wav")
        audio.load_sound("kick", "sounds/drum/kick.wav")
        audio.load_sound("snare", "sounds/drum/snare.wav")

        # 하이햇 볼륨 0.7 유지
        audio.sounds["hihat"].set_volume(0.7)

    # =====================================
    # 드럼 음원 재생
    # =====================================

    def play_sound(self, audio, grid_number):
        if 1 <= grid_number <= self.grid_count:
            sound_name = self.sound_names[grid_number - 1]
            audio.play(sound_name)
