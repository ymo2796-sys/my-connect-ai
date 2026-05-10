import os
import yt_dlp

def download_video(url: str, output_path: str = "downloads/original.mp4") -> str:
    """
    Downloads a video from a given URL (Douyin/TikTok) using yt-dlp.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        # 'quiet': True,
    }
    
    print(f"Downloading video from {url}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
    print(f"Video downloaded successfully to {output_path}")
    return output_path

if __name__ == "__main__":
    # Test
    # download_video("https://www.tiktok.com/@tiktok/video/7106594312292453675")
    pass
