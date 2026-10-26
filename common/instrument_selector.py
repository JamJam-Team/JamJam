import time


class InstrumentSelector:
    def __init__(self):
        self.instruments = {
            1: "DRUM",
            2: "PIANO",
            3: "GUITAR",
            4: "BASS",
            5: "COMMON DEMO"
        }

        self.candidate = None
        self.start_time = None
        self.hold_seconds = 1.0

    def update(self, finger_count):
        # 1~5개가 아니면 선택 초기화
        if finger_count not in self.instruments:
            self.reset()
            return None

        # 손가락 개수가 바뀌면 시간 다시 측정
        if finger_count != self.candidate:
            self.candidate = finger_count
            self.start_time = time.monotonic()
            return None

        # 같은 개수를 1초 유지하면 선택
        elapsed = time.monotonic() - self.start_time

        if elapsed >= self.hold_seconds:
            selected = self.instruments[finger_count]
            self.reset()
            return selected

        return None

    def reset(self):
        self.candidate = None
        self.start_time = None
