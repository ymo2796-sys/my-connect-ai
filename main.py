import os
import argparse
from dotenv import load_dotenv

from downloader import download_video
from video_editor import remove_audio_and_blur_text, apply_edits_and_audio
from ai_processor import generate_script_from_video, generate_tts

def main():
    parser = argparse.ArgumentParser(description="Douyin/TikTok Video Automation Pipeline")
    parser.add_argument("url", help="The URL of the Douyin/TikTok video to process")
    parser.add_argument("--bgm", help="Path to an optional BGM file (mp3/wav)", default=None)
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if os.path.exists("API_KEY.txt"):
        with open("API_KEY.txt", "r") as f:
            key = f.read().strip()
            if key and "여기에" not in key:
                api_key = key
                
    if not api_key or api_key == "your_openai_api_key_here":
        print("Error: API Key is not set in API_KEY.txt or .env file.")
        return

    url = args.url
    bgm_path = args.bgm
    
    # Setup paths
    base_dir = "downloads"
    os.makedirs(base_dir, exist_ok=True)
    
    original_video = os.path.join(base_dir, "1_original.mp4")
    cropped_video = os.path.join(base_dir, "2_cropped_no_audio.mp4")
    tts_audio = os.path.join(base_dir, "3_tts.mp3")
    final_video = os.path.join(base_dir, "4_final_shorts.mp4")

    print("\n=== [Step 1 & 2] Downloading Video ===")
    download_video(url, original_video)

    print("\n=== [Step 4] Extracting Audio & Generating Script ===")
    # We do this before cropping so we can extract the original audio.
    script = generate_script_from_video(original_video)

    print("\n=== [Step 5] Generating TTS from Script ===")
    generate_tts(script, tts_audio)

    print("\n=== [Step 3] Removing Audio and Blurring Subtitles ===")
    remove_audio_and_blur_text(original_video, cropped_video)

    print("\n=== [Step 6 & 7] Applying Edits, Syncing TTS and BGM ===")
    apply_edits_and_audio(cropped_video, tts_audio, bgm_path, final_video, script_text=script)

    print(f"\n✅ Pipeline Complete! Final video is ready at: {final_video}")

if __name__ == "__main__":
    main()
