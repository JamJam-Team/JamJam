
import cv2


class LightingCorrector:
    def __init__(self):
        # CLAHE 객체 생성
        self.clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )

    def correct(self, frame):
        # BGR 영상을 LAB 색 공간으로 변환
        lab = cv2.cvtColor(
            frame, cv2.COLOR_BGR2LAB
        )

        # 밝기 채널과 색상 채널 분리
        l, a, b = cv2.split(lab)

        # 밝기 채널에 CLAHE 적용
        corrected_l = self.clahe.apply(l)

        # 보정된 밝기 채널과 색상 채널 결합
        corrected_lab = cv2.merge(
            (corrected_l, a, b)
        )

        # 다시 BGR 컬러 영상으로 변환
        corrected_frame = cv2.cvtColor(
            corrected_lab, cv2.COLOR_LAB2BGR
        )

        return corrected_frame
