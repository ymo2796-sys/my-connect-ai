"""환경변수 기반 파이프라인 설정"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # YouTube OAuth
    yt_client_secret_path: str = "client_secret.json"
    yt_oauth_token_path: str = "oauth2_token.json"
    yt_category_id: int = 24
    
    # FFmpeg
    ffmpeg_path: str = "ffmpeg"
    audio_isolation_mode: str = "native"  # native | demucs
    
    # TTS & Subtitle
    tts_voice: str = "ko-KR-InHeeNeural"
    subtitle_font_size: int = 24
    subtitle_style: str = "PrimaryColour=&HFFFFFF&H000000FF&H000000FF&HFFFFFF00"
    
    # Paths
    output_dir: str = "output"
    cache_dir: str = ".cache"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()