import os
import cv2
import ffmpeg
import easyocr
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, TextClip, vfx

def detect_text_regions(video_path: str, sample_interval: int = 15) -> list:
    """
    Samples frames from the video and uses EasyOCR to detect text bounding boxes.
    Returns a merged bounding box covering common text areas (mostly bottom subtitles).
    """
    print("Detecting text regions using EasyOCR...")
    reader = easyocr.Reader(['ch_sim', 'ch_tra', 'en'], gpu=False) # Fallback to CPU if GPU not available
    cap = cv2.VideoCapture(video_path)
    
    frame_count = 0
    all_boxes = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % sample_interval == 0:
            results = reader.readtext(frame)
            for (bbox, text, prob) in results:
                if prob > 0.3:
                    # bbox is [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                    xs = [pt[0] for pt in bbox]
                    ys = [pt[1] for pt in bbox]
                    all_boxes.append([min(xs), min(ys), max(xs), max(ys)])
                    
        frame_count += 1
        
    cap.release()
    
    if not all_boxes:
        return None
        
    # Find the bounding box that covers the lower half text, usually subtitles
    # We can just take the union of boxes that are in the lower 40% of the screen.
    # Alternatively, just return a generalized box for all detected text.
    # For simplicity, let's find the max extents of all text found in the bottom half.
    # We need video height
    cap = cv2.VideoCapture(video_path)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    cap.release()
    
    bottom_boxes = [box for box in all_boxes if box[3] > height * 0.5]
    
    if not bottom_boxes:
        return None
        
    min_x = min([box[0] for box in bottom_boxes])
    min_y = min([box[1] for box in bottom_boxes])
    max_x = max([box[2] for box in bottom_boxes])
    max_y = max([box[3] for box in bottom_boxes])
    
    # Add some padding
    padding = 10
    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = max_x + padding
    max_y = max_y + padding
    
    return [int(min_x), int(min_y), int(max_x), int(max_y)]

def remove_audio_and_blur_text(input_path: str, output_path: str):
    """
    Removes audio from the video and blurs the dynamically detected text region.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    bbox = detect_text_regions(input_path, sample_interval=30)
    
    stream = ffmpeg.input(input_path)
    
    if bbox:
        x1, y1, x2, y2 = bbox
        w = x2 - x1
        h = y2 - y1
        print(f"Applying blur to detected text region: x={x1}, y={y1}, w={w}, h={h}")
        # Apply boxblur to the specific region
        # ffmpeg filter syntax for blurring a specific area
        # crop the area, blur it, and overlay it back
        blurred = stream.video.crop(x1, y1, w, h).filter('boxblur', 20, 5)
        video = stream.video.overlay(blurred, x=x1, y=y1)
    else:
        print("No text detected in the lower half. Proceeding without blur.")
        video = stream.video
        
    # anull output (no audio)
    out = ffmpeg.output(video, output_path, vcodec='libx264', an=None, preset='fast')
    ffmpeg.run(out, overwrite_output=True, quiet=True)
    print(f"Processed video saved to {output_path}")
    return output_path

def apply_edits_and_audio(video_path: str, tts_audio_path: str, bgm_path: str, output_path: str, script_text: str = None):
    """
    Applies mirror effect, speed adjustment, mixes TTS + BGM, and optionally adds Korean subtitles.
    """
    print(f"Applying final edits, audio, and subtitles to {video_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    video = VideoFileClip(video_path)
    
    # Visual Edits (Abuse evasion)
    video = video.fx(vfx.mirror_x)
    video = video.fx(vfx.speedx, 1.05)
    
    # Audio
    tts_audio = AudioFileClip(tts_audio_path)
    bgm_audio = None
    if bgm_path and os.path.exists(bgm_path):
        bgm_audio = AudioFileClip(bgm_path).volumex(0.15)
        if bgm_audio.duration < video.duration:
            from moviepy.audio.fx.all import audio_loop
            bgm_audio = audio_loop(bgm_audio, duration=video.duration)
        else:
            bgm_audio = bgm_audio.subclip(0, video.duration)
            
    # Sync Video length with TTS length
    if tts_audio.duration > video.duration:
        from moviepy.video.fx.all import loop
        video = loop(video, duration=tts_audio.duration)

    if bgm_audio:
        final_audio = CompositeAudioClip([tts_audio, bgm_audio])
    else:
        final_audio = tts_audio
        
    video = video.set_audio(final_audio)
    
    # Currently moviepy TextClip requires ImageMagick installed on the system.
    # To avoid failure if ImageMagick is missing, we wrap it in a try-except.
    final_video = video
    if script_text:
        try:
            # Create a simple static subtitle at the bottom (or where the blur was)
            # In a real app, we'd use whisper timestamps to sync word-by-word, 
            # but for shorts, a static engaging title or simple paragraph works if synced text is hard.
            # Here we just put a "shorts style" title.
            txt_clip = TextClip(
                "🎬 " + script_text[:15] + "...", 
                fontsize=50, 
                color='white', 
                bg_color='black',
                font='AppleGothic' # Mac default font
            )
            txt_clip = txt_clip.set_position(('center', 0.75), relative=True).set_duration(video.duration)
            final_video = CompositeVideoClip([video, txt_clip])
            print("Successfully added TextClip.")
        except Exception as e:
            print(f"Skipping subtitles (ImageMagick might be missing): {e}")
    
    final_video.write_videofile(
        output_path, 
        codec="libx264", 
        audio_codec="aac", 
        temp_audiofile="temp-audio.m4a", 
        remove_temp=True,
        logger=None
    )
    print(f"Final video created at: {output_path}")
    return output_path
