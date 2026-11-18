import cv2
import time
import os

class Bass:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

        # 좌우 분할 기준선 (왼쪽 240px: 왼손 프렛 / 오른쪽 400px: 오른손 주법)
        self.split_x = 240

        # 왼손 프렛 (세로 3등분)
        self.fret_names = ["Fret 1", "Fret 3", "Fret 5"]
        self.fret_h = self.height // 3

        # 오른손 주법 (세로 5등분)
        self.tech_names = ["Rhythm 1", "Rhythm 2", "Rhythm 3", "Rhythm 4", "Rhythm 5"]
        self.tech_h = self.height // 5

        # 상태 관리
        self.current_fret = 0       # 0: Fret 1, 1: Fret 3, 2: Fret 5
        self.active_tech = None     # 현재 오른손이 올라가 있는 주법 인덱스
        self.last_hit_tech = None   # 최근 타격된 주법
        self.last_hit_time = 0      # 타격 이펙트 타이머

    def load_sounds(self, audio):
        """베이스 음원 로드 (음원이 아직 없으면 test.wav로 자동 대체)"""
        base_dir = "sounds/bass"
        fallback_sound = "sounds/test.wav"

        frets = ["fret1", "fret3", "fret5"]
        techs = ["rhythm1", "rhythm2", "rhythm3", "rhythm4", "rhythm5"]

        for f in frets:
            for t in techs:
                sound_key = f"{f}_{t}"
                sound_path = f"{base_dir}/{sound_key}.wav"

                # 전용 사운드가 있으면 해당 파일, 없으면 test.wav 로드
                if os.path.exists(sound_path):
                    audio.load_sound(sound_key, sound_path)
                elif os.path.exists(fallback_sound):
                    audio.load_sound(sound_key, fallback_sound)

    def update_fret(self, y_norm):
        """왼손 손바닥 Y좌표(0~1)를 받아 프렛(0, 1, 2) 선택"""
        py = int(y_norm * self.height)
        self.current_fret = min(max(py // self.fret_h, 0), 2)
        return self.current_fret

    def get_tech_grid(self, y_norm):
        """오른손 손바닥 Y좌표(0~1)를 받아 주법(0~4) 반환"""
        py = int(y_norm * self.height)
        self.active_tech = min(max(py // self.tech_h, 0), 4)
        return self.active_tech

    def register_hit(self, tech_idx):
        """오른손 주법 타격 등록"""
        self.last_hit_tech = tech_idx
        self.last_hit_time = time.time()

    def play_sound(self, audio, tech_idx):
        """선택된 왼손 프렛과 오른손 주법 조합으로 재생"""
        frets = ["fret1", "fret3", "fret5"]
        techs = ["rhythm1", "rhythm2", "rhythm3", "rhythm4", "rhythm5"]

        sound_key = f"{frets[self.current_fret]}_{techs[tech_idx]}"
        audio.play(sound_key)

    def draw_grid(self, frame):
        """베이스 화면 격자 렌더링"""
        overlay = frame.copy()

        # 1. 왼손 프렛 3칸
        for i in range(3):
            y1 = i * self.fret_h
            y2 = y1 + self.fret_h

            # 선택된 프렛 칸 하이라이트 (파란색 반투명)
            if i == self.current_fret:
                cv2.rectangle(overlay, (0, y1), (self.split_x, y2), (255, 120, 0), -1)

            cv2.line(frame, (0, y2), (self.split_x, y2), (200, 200, 200), 2)
            cv2.putText(frame, self.fret_names[i], (20, y1 + (self.fret_h // 2) + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        # 2. 오른손 주법 5칸
        for j in range(5):
            y1 = j * self.tech_h
            y2 = y1 + self.tech_h

            # 오른손이 위치한 칸 하이라이트 (노란색 반투명)
            if j == self.active_tech:
                cv2.rectangle(overlay, (self.split_x, y1), (self.width, y2), (0, 200, 200), -1)

            cv2.line(frame, (self.split_x, y2), (self.width, y2), (200, 200, 200), 1)
            cv2.putText(frame, f"{j+1}. {self.tech_names[j]}", (self.split_x + 30, y1 + (self.tech_h // 2) + 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        # 투명도 합성
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

        # 중앙 경계선
        cv2.line(frame, (self.split_x, 0), (self.split_x, self.height), (0, 255, 255), 3)

        # 라벨 표시
        cv2.putText(frame, "[LEFT: FRET]", (30, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 200, 0), 2)
        cv2.putText(frame, "[RIGHT: TECHNIQUE]", (self.split_x + 60, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 200), 2)

        return frame

    def draw_hit_effect(self, frame):
        """타격 시 0.25초 동안 초록색 타격 이펙트 표시"""
        if self.last_hit_tech is not None:
            if time.time() - self.last_hit_time < 0.25:
                overlay = frame.copy()
                y1 = self.last_hit_tech * self.tech_h
                y2 = y1 + self.tech_h
                cv2.rectangle(overlay, (self.split_x, y1), (self.width, y2), (0, 255, 0), -1)
                frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
            else:
                self.last_hit_tech = None
        return frame