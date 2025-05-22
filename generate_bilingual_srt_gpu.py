import os
import whisper
import requests
import uuid
from dotenv import load_dotenv
from datetime import datetime

# ✅ 初始化日志记录
def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {message}")
    with open("transcribe.log", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

# ✅ 加载 Translator API 配置
load_dotenv()
ENDPOINT = (
    os.getenv("endpoint") or
    os.getenv("TRANSLATE_endpoint") or
    os.getenv("translate_endpoint")
)
REGION = os.getenv("SERVICE_REGION")
KEY = os.getenv("TRANSLATE_KEY")

if not ENDPOINT or not REGION or not KEY:
    log("❌ 缺少翻译接口配置，请检查 .env 文件")
    exit(1)

# ✅ Whisper 转录
def transcribe_with_whisper(audio_path):
    log("🧠 加载 Whisper medium 模型中（使用 GPU）...")
    model = whisper.load_model("medium")
    log("🎧 开始识别音频...")
    result = model.transcribe(audio_path, fp16=True, language="en")
    return result["segments"]

# ✅ Microsoft Translator 翻译
def translate_to_chinese(text):
    url = ENDPOINT.rstrip("/") + "/translate"
    headers = {
        "Ocp-Apim-Subscription-Key": KEY,
        "Ocp-Apim-Subscription-Region": REGION,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4())
    }
    params = {"api-version": "3.0", "from": "en", "to": "zh-Hans"}
    body = [{"text": text}]

    try:
        response = requests.post(url, headers=headers, params=params, json=body, timeout=10)
        response.raise_for_status()
        translation = response.json()[0]['translations'][0]['text']
        return translation
    except Exception as e:
        log(f"⚠️ 翻译失败：{e}")
        return text

# ✅ 格式化时间为 SRT 格式
def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# ✅ 生成 SRT 字幕文件
def generate_srt(segments, output_path):
    log("📝 生成双语 SRT 字幕...")
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, start=1):
            start = format_srt_time(seg["start"])
            end = format_srt_time(seg["end"])
            original = seg["text"].strip()
            translated = translate_to_chinese(original)
            f.write(f"{idx}\n{start} --> {end}\n{original}\n{translated}\n\n")
            log(f"📌 第 {idx} 段完成")

    log(f"✅ 字幕已保存到：{output_path}")

# ✅ 主程序
if __name__ == "__main__":
    audio_file = "20250508_103201.wav"
    output_file = "20250508_103201.srt"

    try:
        segments = transcribe_with_whisper(audio_file)
        generate_srt(segments, output_file)
    except Exception as e:
        log(f"❌ 脚本执行出错：{e}")
