import cv2
import time


class Piano:
    def __init__(self):
        self.grid_count = 5
        # 위쪽 2칸: C, G / 아래쪽 3칸: Am, F, Em
        self.piano_names = ["C", "G", "Am", "F", "Em"]
        self.sound_names = ["piano_C", "piano_G", "piano_Am", "piano_F", "piano_Em"]
        # OpenCV BGR 색상
        self.colors = [
            (250, 220, 160), (180, 230, 160), (170, 210, 255),
            (235, 180, 210), (210, 180, 250)
        ]
        self.hit_times = {}
        self.flash_duration = 0.3

    def get_grid_rect(self, grid_number, width, height):
        if not 1 <= grid_number <= self.grid_count:
            raise ValueError("피아노 격자 번호는 1~5여야 합니다.")
        half_height = height // 2
        if grid_number <= 2:
            index = grid_number - 1
            x1 = index * width // 2
            x2 = (index + 1) * width // 2
            y1, y2 = 0, half_height
        else:
            index = grid_number - 3
            x1 = index * width // 3
            x2 = (index + 1) * width // 3
            y1, y2 = half_height, height
        return x1, y1, x2, y2

    def draw_grid(self, frame):
        height, width = frame.shape[:2]
        for i in range(self.grid_count):
            x1, y1, x2, y2 = self.get_grid_rect(i + 1, width, height)
            color = self.colors[i]
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2 - 1, y2 - 1), color, -1)
            cv2.addWeighted(overlay, 0.12, frame, 0.88, 0, frame)
            cv2.rectangle(frame, (x1 + 3, y1 + 3), (x2 - 4, y2 - 4), color, 2)
            cv2.putText(frame, self.piano_names[i], (x1 + 15, y2 - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
        return frame

    def get_grid(self, x, y):
        if not (0 <= x <= 1 and 0 <= y <= 1):
            return None
        if y < 0.5:
            return min(int(x * 2) + 1, 2)
        return min(int(x * 3) + 3, 5)

    def register_hit(self, grid_number):
        if 1 <= grid_number <= self.grid_count:
            self.hit_times[grid_number] = time.monotonic()

    def draw_hit_effect(self, frame):
        current_time = time.monotonic()
        height, width = frame.shape[:2]
        for grid_number, hit_time in list(self.hit_times.items()):
            if current_time - hit_time > self.flash_duration:
                del self.hit_times[grid_number]
                continue
            x1, y1, x2, y2 = self.get_grid_rect(grid_number, width, height)
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2 - 1, y2 - 1),
                          (255, 255, 255), -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        return frame

    def load_sounds(self, audio):
        for sound_name in self.sound_names:
            audio.load_sound(sound_name, f"sounds/piano/{sound_name}.wav")

    def play_sound(self, audio, grid_number):
        if grid_number is not None and 1 <= grid_number <= self.grid_count:
            audio.play(self.sound_names[grid_number - 1])
