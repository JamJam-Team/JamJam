
import cv2
import mediapipe as mp
from pathlib import Path


class HandTracker:
    def __init__(self):
        # 손 인식 모델 파일 경로
        model_path = (
            Path(__file__).resolve().parent.parent
            / "models"
            / "hand_landmarker.task"
        )

        # MediaPipe 손 인식 설정
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_buffer=model_path.read_bytes()
            ),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_hands=2
        )

        # 손 인식 모델 생성
        self.detector = (
            mp.tasks.vision.HandLandmarker.create_from_options(options)
        )

    def process(self, frame):
        # OpenCV BGR -> RGB 변환
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe 이미지 변환
        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        # 손 인식 실행
        result = self.detector.detect(image)

        height, width = frame.shape[:2]

        # 인식된 손의 관절 표시
        for hand in result.hand_landmarks:
            for landmark in hand:
                x = int(landmark.x * width)
                y = int(landmark.y * height)

                # 관절 위치: 초록색 점
                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)
                

            
            # 손바닥 중심 좌표 가져오기
            palm_x, palm_y = self.get_palm_center(hand)

            # 영상 좌표로 변환
            x = int(palm_x * width)
            y = int(palm_y * height)

            # 손바닥 중심: 빨간색 점
            cv2.circle(frame, (x, y), 10, (0, 0, 255), -1)

            
        return frame, result.hand_landmarks, result.handedness



    
    def get_palm_center(self, hand):
        # 손바닥 중심 계산에 사용할 관절 번호
        palm_points = [0, 5, 9, 13, 17]

        # 정규화된 손바닥 중심 좌표 계산
        palm_x = sum(hand[i].x for i in palm_points) / len(palm_points)
        palm_y = sum(hand[i].y for i in palm_points) / len(palm_points)

        return palm_x, palm_y


    def close(self):
        self.detector.close()
