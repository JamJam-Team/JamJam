
import wave
import math
import struct
from pathlib import Path

# 테스트 음원 저장 폴더
sound_dir = Path("sounds")
sound_dir.mkdir(exist_ok=True)

file_path = sound_dir / "test.wav"

sample_rate = 44100
duration = 0.25
frequency = 440

with wave.open(str(file_path), "w") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate

        # 끝으로 갈수록 소리가 작아지도록 설정
        volume = 0.3 * (1 - t / duration)

        sample = int(
            32767 * volume *
            math.sin(2 * math.pi * frequency * t)
        )

        wav.writeframes(struct.pack("<h", sample))

print("테스트 음원 생성 완료!")
print(file_path)
