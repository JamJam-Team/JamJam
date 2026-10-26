# JamJam

웹캠과 손동작을 활용한 가상 밴드 연주 시스템

## 프로젝트 소개

**JamJam**은 노트북 웹캠을 통해 사용자의 손 위치와 움직임을 인식하여  
실제 악기 없이 **드럼, 피아노, 기타, 베이스를 연주할 수 있는 가상 밴드 프로젝트**입니다.

손의 2D 위치뿐만 아니라 **제스처 변화을 감지**합니다.

최종 연주 곡은 **아이유 - 너의 의미**이며, 악기별 특성에 맞는 연주 인터페이스를 구현하는 것을 목표로 합니다.

## 주요 기능

- 웹캠을 이용한 실시간 영상 입력
- 손 및 손가락 위치 인식
- 저조도 환경을 위한 조명 보정
- 손동작에 따른 악기 음원 재생
- 주먹을 쥐고 이동한 뒤 손을 펴서 연주
- 드럼 · 피아노 · 기타 · 베이스 연주


## 기술 스택

| 구분 | 기술 |
| --- | --- |
| Language | Python |
| Computer Vision | OpenCV |
| Hand Tracking | MediaPipe |
| Data Processing | NumPy |
| Audio | pygame.mixer |
| Collaboration | Git / GitHub |


## 📂 프로젝트 구조

공통적으로 사용하는 기능과 악기별 기능을 분리하여 개발합니다.

```text
JamJam/
├── common/
│   ├── __init__.py
│   ├── hand_tracking.py
│   ├── gesture_detection.py
│   ├── audio.py
│   └── lighting.py
├── instruments/        # 악기별 기능
│   ├── bass.py
│   ├── drum.py
│   ├── piano.py
│   └── guitar.py
├── models/
│   └── hand_landmarker.task
├── sounds/             # 악기별 음원
│   ├── bass/
│   ├── drum/
│   ├── piano/
│   └── guitar/
├── main.py
└── .gitignore
```

### 공통 기능

웹캠, 손 인식, 조명 보정, 음원 재생과 같이  
모든 악기에서 사용하는 기능은 `common/`에서 관리합니다.

### 악기별 기능

악기마다 다른 **격자 배치, 연주 방식, 음원 매핑**은  
`instruments/`에서 각각 구현합니다.


## 악기 구성

| 악기 | 구성 | 담당 |
| --- | --- | --- |
| 🥁 드럼 | 7칸 리듬 패턴 | 장호정 |
| 🎹 피아노 | 5칸 베이스 반주 | 고은빈 |
| 🎸 베이스 | 8칸 양손 연주 | 김지은 |
| 🎸 기타 | 8칸 양손 연주 | 장서윤 |


## 프로젝트 실행

### 1. Clone Repository

```bash
git clone <repository-url>
cd JamJam
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

#### Windows PowerShell

```powershell
& .\.venv\Scripts\Activate.ps1
```

정상적으로 활성화되면 다음과 같이 표시됩니다.

```text
(.venv) PS C:\...\JamJam>
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
python -m pip install mediapipe opencv-python pygame numpy
```

### 5. Run

```bash
python main.py
```