# 🎬 Douyin → YouTube Shorts 자동화 파이프라인 설계서

## 1. 데이터 흐름 (Data Flow)
```
Douyin URL → [Extractor] → raw_video.mp4
     ↓
[Audio Isolation] → clean_voice.m4a + mute_video.mp4
     ↓
[TTS + Subtitle] → tts_audio.mp3 + captions.srt
     ↓
[Composer] → final_shorts.mp4 (자막 번닝, 9:16crop, 1080x1920)
     ↓
[YouTube API] → Unlisted → Publish → Shorts Feed
```

## 2. 모듈별 핵심 구현 가이드

### 🔹 `extractor/douyin_dl.py`
- `yt-dlp --extractor-args "tiktok:api_hostname=api22-normal-c-useast2a.tiktokv.com"` 등 Douyin 전용 옵션 적용
- 메타데이터(`-metadata`, `--remux-video`, `--no-playlist`)로 불필요 정보 제거
- 실패 시 `--cookies-from-browser` 또는 `--extractor-retries` 폴백

### 🔹 `audio_processor/isolate.py`
- **Native (기본)**: `ffmpeg -af "highpass=60,lowpass=3000,afftdn=nf=-25" -vn -c:a aac`
  - 음성 대역(60-3kHz) 필터링 + `afftdn` 노이즈 감소
- **Demucs (고품질)**: `demucs -s vocal -s other input.mp4` → `vocals.wav` 추출
  - GPU 권장. CPU 시 `--two-stems vocals`로 메모리 절감

### 🔹 `tts_sub/korean_tts.py` & `subtitle_gen.py`
- `edge-tts --voice {voice} --text "{text}" --write-media {out}`
- `faster-whisper`로 `tts_audio.mp3` → `captions.srt` 자동 생성 (포맷: `SRT 2.1`)
- 자막 스타일: `ffmpeg -vf "subtitles=subs.srt:force_style='{settings.subtitle_style}'"`

### 🔹 `video_composer/compose.py`
- `ffmpeg -i mute_video.mp4 -i tts_audio.mp3 -vf "subtitles=captions.srt" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -shortest final.mp4`
- Shorts 기준: `9:16` 비율 강제 (`-vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"`), 길이 `≤60s`

### 🔹 `uploader/youtube_shorts.py`
- OAuth2 `https://www.googleapis.com/auth/youtube.upload` 스코프
- `media.upload` API 호출 시 `category`, `privacyStatus=unlisted`, `notifySubscribers=true`
- 업로드 후 `youtube.videos().update(status={privacyStatus: "public"})`로 공개 전환
- 실패 시 `retry=3` + `exponential_backoff` 적용

## 3. 보안 및 운영 원칙
- 모든 시크릿은 `.env` 또는 `google_credentials/` 디렉토리 관리
- YouTube OAuth 토큰은 `~/.cache/yt_shorts_token.json`에 자동 저장
- FFmpeg/Demucs는 별도 시스템 설치 필요: `brew install ffmpeg` / `pip install demucs torchaudio`
- 로깅은 `loguru`로 파일(`logs/pipeline_%Y%m%d.log`) + 콘솔 동시 출력