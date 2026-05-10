# 🎬 도우인 쇼츠 자동화 파이프라인 (고도화 버전)

사용자 피드백을 반영하여 **자막 가림 방식과 AI 대본 생성 로직을 획기적으로 개선**한 버전을 구현 완료했습니다!

## ✨ 주요 업데이트 (고도화 포인트)

1. **EasyOCR 기반 동적 자막 블러링 (Step 3)**
   * 기존의 강제 크롭(자르기) 방식을 버리고, **파이썬 EasyOCR 라이브러리**를 도입했습니다.
   * 영상에서 중국어 자막이 있는 X, Y 좌표(Bounding Box)를 동적으로 찾아내고, 해당 위치에만 FFmpeg를 사용하여 블러(모자이크) 필터를 적용합니다. 
   * 이를 통해 영상의 중요한 장면을 전혀 자르지 않고 원본 비율을 그대로 유지할 수 있습니다.

2. **GPT-4o Vision API 도입 (Step 4)**
   * Whisper로 뽑아낸 오디오 텍스트만으로는 영상 내용을 알 수 없는 한계를 극복했습니다.
   * OpenCV를 사용하여 원본 영상에서 1초 단위로 핵심 프레임(이미지)들을 추출합니다.
   * **오디오 텍스트 + 여러 장의 영상 프레임**을 동시에 GPT-4o(비전 모델)에 던져서 "어떤 장면에서 무슨 말을 하는지" 문맥을 완벽히 파악한 후 한국어 대본을 짜도록 고도화했습니다.

3. **한국어 자막 자동 덧씌우기 (Step 6)**
   * 블러 처리된 중국어 자막을 덮어버리는 효과를 위해, GPT가 만들어준 한국어 대본을 영상 중앙 하단에 텍스트 자막(TextClip)으로 큼지막하게 렌더링하도록 기능을 추가했습니다.

## 🛠️ 폴더 구조
```text
douyin_shorts_maker/
├── .env.example        # 환경 변수 템플릿
├── requirements.txt    # [업데이트] easyocr, opencv-python 추가
├── main.py             # 전체 실행 (수정됨)
├── downloader.py       # 영상 다운로드 모듈 
├── ai_processor.py     # [업데이트] Vision API 프레임 추출 로직 추가
└── video_editor.py     # [업데이트] EasyOCR 블러 + 한국어 자막 추가 로직
```

## 🚀 실행 방법 가이드

### 1. 패키지 설치
터미널을 열고 아래 명령어를 실행하세요. EasyOCR 등 무거운 라이브러리가 추가되어 시간이 조금 걸릴 수 있습니다.
(Mac의 경우 MoviePy에서 자막 텍스트 렌더링을 위해 추가적으로 `brew install imagemagick` 설치가 필요할 수 있습니다.)

```bash
cd /Users/bbodek/.gemini/antigravity/scratch/douyin_shorts_maker
pip install -r requirements.txt
```

### 2. API 키 설정
`.env` 파일에 발급받은 OpenAI API 키를 넣어주세요.

### 3. 프로그램 실행
`main.py` 파일에 영상 링크를 인자로 넣어 실행합니다.
```bash
python main.py "도우인_또는_틱톡_영상_링크"
```

실행이 완료되면 `downloads` 폴더 안에 중간 과정 파일들과 최종 완성된 `4_final_shorts.mp4` 파일이 생성됩니다!
