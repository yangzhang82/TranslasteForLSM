# TranslasteForLSM 将视频转成wav文件，使用whisper识别，发送到翻译api进行翻译，最后生成与视频文件同名的srt文件
# 我在处理的时候，租用了一台4090的虚拟机，处理速度大概是视频时间*0.8，大家可以参考
# Ubuntu ↓
# sudo apt update
# sudo apt install python3.10 python3.10-venv
# python3.10 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
# python generate_bilingual_srt_gpu.py