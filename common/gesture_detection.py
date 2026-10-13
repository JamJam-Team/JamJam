
import math


class GestureDetector:
    def __init__(self):
        self.previous_state = "UNKNOWN"
        self.candidate_state = "UNKNOWN"
        self.stable_count = 0
        self.required_frames = 3

    def get_distance(self, p1, p2):
        return math.hypot(
            p1.x - p2.x,
            p1.y - p2.y
        )

    
    
    def classify(self, hand):
        def angle(a, b, c):
            # 세 관절이 이루는 각도 계산
            ax, ay = a.x - b.x, a.y - b.y
            cx, cy = c.x - b.x, c.y - b.y

            dot = ax * cx + ay * cy
            length1 = math.hypot(ax, ay)
            length2 = math.hypot(cx, cy)

            if length1 * length2 == 0:
                return 0

            cos_value = dot / (length1 * length2)
            cos_value = max(-1, min(1, cos_value))

            return math.degrees(math.acos(cos_value))

        # 검지, 중지, 약지, 소지
        fingers = [
            (5, 6, 8),
            (9, 10, 12),
            (13, 14, 16),
            (17, 18, 20)
        ]

        extended = 0
        folded = 0

        for mcp, pip, tip in fingers:
            finger_angle = angle(
                hand[mcp],
                hand[pip],
                hand[tip]
            )

            if finger_angle > 150:
                extended += 1

            elif finger_angle < 120:
                folded += 1

        if extended >= 4:
            return "OPEN"

        if folded >= 3:
            return "FIST"

        return "UNKNOWN"


    
    def update(self, hand):
        state = self.classify(hand)

        # 같은 손동작이 연속으로 감지되는지 확인
        if state == self.candidate_state:
            self.stable_count += 1
        else:
            self.candidate_state = state
            self.stable_count = 1

        play = False

        if self.stable_count >= self.required_frames:
            if state == "FIST":
                # 주먹을 쥐면 다음 연주 준비
                self.previous_state = "FIST"

            elif state == "OPEN":
                # 주먹을 쥔 상태에서 손을 펼 때만 재생
                if self.previous_state == "FIST":
                    play = True

                self.previous_state = "OPEN"

            # UNKNOWN일 때는 이전 상태 유지

        return self.previous_state, play


    def reset(self):
        self.previous_state = "UNKNOWN"
        self.candidate_state = "UNKNOWN"
        self.stable_count = 0
