"""파이프라인 오케스트레이션 진입점"""
import asyncio
import os
import sys
from pathlib import Path
from loguru import logger
from src.config import settings

# 임시 경로 추가 (모듈 import용)
sys.path.insert(0, str(Path(__file__).parent))

async def run_pipeline(video_url: str, script_text: str = "") -> str:
    logger.info("🚀 Shorts 파이프라인 시작")
    
    # 1. 원본 추출
    logger.info("1️⃣ Douyin 원본 추출 중...")
    from src.extractor.douyin_dl import download_douyin
    raw_path = await download_douyin(video_url, output_dir=settings.output_dir)
    
    # 2. 음성 분리 (BGM 제거/목소리 추출)
    logger.info("2️⃣ BGM 제거 및 음성 클린업 중...")
    from src.audio_processor.isolate import isolate_voice
    clean_audio_path = await isolate_voice(raw_path, mode=settings.audio_isolation_mode)
    
    # 3. TTS + 자막 생성
    logger.info("3️⃣ 한국어 TTS 및 자막 생성 중...")
    from src.tts_sub.korean_tts import generate_tts
    from src.tts_sub.subtitle_gen import generate_subtitles
    tts_path = await generate_tts(script_text or "자동 생성된 내레이션", voice=settings.tts_voice)
    srt_path = await generate_subtitles(tts_path, output_dir=settings.output_dir)
    
    # 4. 영상 합성 (자막 번닝 + 오디오 교체)
    logger.info("4️⃣ 영상 합성 및 인코딩 중...")
    from src.video_composer.compose import compose_shorts
    final_video_path = await compose_shorts(
        video=raw_path,
        audio=tts_path,
        subtitles=srt_path,
        output_dir=settings.output_dir
    )
    
    # 5. YouTube Shorts 업로드
    logger.info("5️⃣ YouTube Shorts 업로드 중...")
    from src.uploader.youtube_shorts import upload_to_youtube
    upload_status = await upload_to_youtube(
        video_path=final_video_path,
        title="자동 생성 쇼츠",
        description="파이프라인 자동 업로드",
        category_id=settings.yt_category_id,
        client_secret_path=settings.yt_client_secret_path,
        token_path=settings.yt_oauth_token_path
    )
    
    logger.success(f"✅ 완료: {final_video_path} | 업로드 상태: {upload_status}")
    return final_video_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Douyin → Shorts 자동화 파이프라인")
    parser.add_argument("--url", required=True, help="Douyin 영상 URL")
    parser.add_argument("--script", default="", help="내레이션 대본 (비워두면 자동 TTS)")
    args = parser.parse_args()
    
    asyncio.run(run_pipeline(video_url=args.url, script_text=args.script))