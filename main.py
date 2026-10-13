import cv2

# 1. 웹캠 연결
cap = cv2.VideoCapture(0)

# 2. 웹캠 해상도 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 웹캠 연결 확인
if not cap.isOpened():
    print("웹캠 연결 실패!")
    exit()

while True:
    # 3. 웹캠 영상 읽기
    ret, frame = cap.read()

    if not ret:
        print("영상 읽기 실패!")
        break

    # 4. 좌우 반전 (거울처럼 표시)
    frame = cv2.flip(frame, 1)

    # 5. 웹캠 화면 출력
    cv2.imshow("JamJam - Webcam Test", frame)

    # 6. q 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 7. 웹캠 종료
cap.release()
cv2.destroyAllWindows()