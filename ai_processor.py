import os
import cv2
import base64
import openai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if os.path.exists("API_KEY.txt"):
    with open("API_KEY.txt", "r") as f:
        key = f.read().strip()
        if key and "여기에" not in key:
            api_key = key
            
client = openai.OpenAI(api_key=api_key)

def extract_audio_for_transcription(video_path: str, output_audio_path: str) -> str:
    """Extracts mp3 from video for Whisper API"""
    import ffmpeg
    print("Extracting audio for transcription...")
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
    stream = ffmpeg.input(video_path)
    out = ffmpeg.output(stream.audio, output_audio_path, format='mp3', audio_bitrate='128k')
    ffmpeg.run(out, overwrite_output=True, quiet=True)
    return output_audio_path

def extract_frames_for_vision(video_path: str, max_frames: int = 10) -> list:
    """Extracts evenly spaced frames from the video to send to Vision API."""
    print(f"Extracting up to {max_frames} frames for Vision API...")
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if total_frames == 0 or fps == 0:
        return []

    # Calculate interval to get max_frames
    interval = max(1, total_frames // max_frames)
    
    base64_frames = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % interval == 0 and len(base64_frames) < max_frames:
            # Resize frame to save bandwidth
            height, width = frame.shape[:2]
            new_width = 480
            new_height = int(height * (new_width / width))
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', resized_frame)
            base64_image = base64.b64encode(buffer).decode('utf-8')
            base64_frames.append(base64_image)
            
        frame_count += 1

    cap.release()
    return base64_frames

def generate_script_from_video(video_path: str) -> str:
    """
    1. Extracts audio & transcribes via Whisper.
    2. Extracts frames for Vision context.
    3. Generates a Shorts script using GPT-4o Vision.
    """
    temp_audio = "downloads/temp_transcribe.mp3"
    extract_audio_for_transcription(video_path, temp_audio)
    
    print("Transcribing audio using Whisper...")
    with open(temp_audio, "rb") as audio_file:
        transcription_res = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )
    
    transcription = transcription_res.strip()
    print("Original Transcription:", transcription)
    
    # Extract frames
    base64_frames = extract_frames_for_vision(video_path)
    
    print("Generating Korean shorts script using GPT-4o (Vision)...")
    
    # Prepare message content
    content = [
        {"type": "text", "text": f"다음은 중국(또는 외국) 영상의 원본 오디오를 텍스트로 변환한 것입니다:\n\"{transcription}\"\n\n첨부된 이미지들은 이 영상의 주요 장면들입니다. 이 내용을 바탕으로 한국의 틱톡이나 유튜브 쇼츠에 어울리는 흥미롭고 짧은(약 30초~1분 분량) 대본을 만들어주세요.\n- 도입부는 매우 시선을 끌어야 합니다(Hook).\n- 말투는 친근하고 트렌디한 반말이나 '~요' 체를 섞어주세요.\n- 결과물에는 지시문(예: [음악 시작], [화면 전환])을 빼고 **오직 성우가 읽을 나레이션 텍스트만** 연속해서 적어주세요."}
    ]
    
    # Add images to content
    for frame in base64_frames:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame}",
                "detail": "low"
            }
        })
        
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 센스있는 숏폼 콘텐츠 기획자이자 대본 작가입니다."},
            {"role": "user", "content": content}
        ],
        max_tokens=500
    )
    
    script = response.choices[0].message.content.strip()
    print("Generated Script:\n", script)
    return script

def generate_tts(text: str, output_path: str) -> str:
    """
    Generates TTS audio from text using OpenAI TTS
    """
    print(f"Generating TTS for script... Saving to {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova", # or alloy, echo, fable, onyx, shimmer
        input=text
    )
    response.stream_to_file(output_path)
    print("TTS generated successfully.")
    return output_path
