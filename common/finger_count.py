
import math


class FingerCounter:
    def angle(self, a, b, c):
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

    def count(self, hand):
        count = 0

        # 검지, 중지, 약지, 소지
        fingers = [
            (5, 6, 8),
            (9, 10, 12),
            (13, 14, 16),
            (17, 18, 20)
        ]

        for mcp, pip, tip in fingers:
            finger_angle = self.angle(
                hand[mcp],
                hand[pip],
                hand[tip]
            )

            if finger_angle > 150:
                count += 1

        # 엄지손가락
        # 엄지 관절 각도와 손바닥에서 떨어진 정도 확인
        thumb_angle = self.angle(
            hand[2],
            hand[3],
            hand[4]
        )

        thumb_tip_distance = math.hypot(
            hand[4].x - hand[5].x,
            hand[4].y - hand[5].y
        )

        thumb_base_distance = math.hypot(
            hand[2].x - hand[5].x,
            hand[2].y - hand[5].y
        )

        if (
            thumb_angle > 150
            and thumb_tip_distance > thumb_base_distance 
        ):
            count += 1

        return count
