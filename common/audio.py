
import pygame
from pathlib import Path


class AudioPlayer:
    def __init__(self):
        # 소리 재생 기능 초기화
        pygame.mixer.init()

        # 불러온 음원 저장
        self.sounds = {}

    def load_sound(self, name, file_path):
        # 음원 파일 경로 확인
        path = Path(file_path)

        if not path.is_file():
            print(f"음원 파일을 찾을 수 없습니다: {path}")
            return False

        # 음원 불러오기
        self.sounds[name] = pygame.mixer.Sound(str(path))
        return True

    def play(self, name):
        # 해당 이름의 음원 재생
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"등록되지 않은 음원: {name}")

    def stop_all(self):
        # 재생 중인 모든 소리 정지
        pygame.mixer.stop()

    def close(self):
        # 소리 재생 기능 종료
        pygame.mixer.quit()
