
import cv2
import time
import pygame


class Drum:
    def __init__(self):
        self.grid_count = 7

        # 드럼 격자별 패턴 이름
        self.drum_names = [
            "PATTERN 1",
            "PATTERN 2",
            "PATTERN 3",
            "PATTERN 4",
            "PATTERN 5",
            "PATTERN 6",
            "PATTERN 7"
        ]

        # 격자별 음원 이름
        self.sound_names = [
            "pattern1",
            "pattern2",
            "pattern3",
            "pattern4",
            "pattern5",
            "pattern6",
            "pattern7"
        ]

        # 격자별 색상 (OpenCV BGR)
        self.colors = [
            (68, 68, 239),    
            (246, 130, 59),  
            (247, 85, 168),  
            (22, 115, 249),  
            (94, 197, 34),   
            (53, 230, 163),   
            (21, 204, 250)    
        ]

        # 타격 효과
        self.hit_times = {}
        self.flash_duration = 0.3

        # 현재 재생 중인 드럼 패턴 채널
        self.pattern_channel = None

    # =====================================
    # 격자 위치 계산
    # =====================================

    def get_grid_rect(self, grid_number, width, height):
        half_height = height // 2

        if grid_number <= 4:
            index = grid_number - 1

            x1 = index * width // 4
            x2 = (index + 1) * width // 4

            y1, y2 = 0, half_height

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

            # 반투명 배경
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

            # 격자 테두리
            cv2.rectangle(
                frame,
                (x1 + 3, y1 + 3),
                (x2 - 4, y2 - 4),
                color,
                2
            )

            # 패턴 이름
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
        if y < 0.5:
            grid = int(x * 4) + 1
            return min(max(grid, 1), 4)

        else:
            grid = int(x * 3) + 5
            return min(max(grid, 5), 7)

    # =====================================
    # 드럼 타격 기록
    # =====================================

    def register_hit(self, grid_number):
        self.hit_times[grid_number] = time.monotonic()

    # =====================================
    # 드럼 타격 시 하얀색 반짝임 효과
    # =====================================

    def draw_hit_effect(self, frame):
        current_time = time.monotonic()
        height, width = frame.shape[:2]

        for grid_number, hit_time in list(self.hit_times.items()):

            if current_time - hit_time > self.flash_duration:
                del self.hit_times[grid_number]
                continue

            x1, y1, x2, y2 = self.get_grid_rect(
                grid_number, width, height
            )

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
    # 드럼 패턴 음원 불러오기
    # =====================================

    def load_sounds(self, audio):
        for i in range(self.grid_count):
            sound_name = self.sound_names[i]
            sound_path = f"sounds/drum/{sound_name}.wav"

            audio.load_sound(sound_name, sound_path)

        # 드럼 패턴 전용 채널
        self.pattern_channel = pygame.mixer.Channel(1)

    # =====================================
    # 드럼 패턴 재생
    # =====================================

    def play_sound(self, audio, grid_number):
        if not 1 <= grid_number <= self.grid_count:
            return

        sound_name = self.sound_names[grid_number - 1]

        # 이전 패턴 중단
        self.pattern_channel.stop()

        # 새로운 패턴 재생
        self.pattern_channel.play(
            audio.sounds[sound_name]
        )
