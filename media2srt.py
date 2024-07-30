import math
import os
import subprocess
import tempfile
import time
from pathlib import Path

import dotenv
from openai import OpenAI
from pydub import AudioSegment
import pysubs2

dotenv.load_dotenv()

# 设置你的OpenAI client
API_KEY = os.getenv('OPENAI_API_KEY')
API_BASE = os.getenv('OPENAI_API_BASE')

# ffmpeg 和 ffprobe 的路径
ffmpeg_path = "/usr/local/bin/ffmpeg"
ffprobe_path = "/usr/local/bin/ffprobe"

# 片段重试次数
MAX_RETRIES = os.getenv('MAX_RETRIES', 3)

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE,
)


def adjust_timestamps(srt_content, start_ms):
    """
    调整SRT格式的时间戳
    """
    with tempfile.NamedTemporaryFile(suffix=".srt") as temp_srt_file:
        # 将SRT格式的文本保存到临时文件
        temp_srt_file.write(srt_content.encode("utf-8"))
        # 刷新缓冲区
        temp_srt_file.flush()
        # 将文件指针移回文件开始处
        temp_srt_file.seek(0)
        # 从临时文件中加载字幕对象
        subs = pysubs2.load(temp_srt_file.name, encoding="utf-8", format_="srt")
        # 调整时间戳
        for i, sub in enumerate(subs):
            sub.start += start_ms
            sub.end += start_ms
        # 将字幕对象转换回SRT格式的文本
        adjusted_srt_content = subs.to_string(format_="srt")
    return adjusted_srt_content


def segment_and_transcribe(audio_path, output_path, format=None):
    """
    将音频文件分割成 3 分钟的片段并转录
    """
    if format is None:
        format = "srt"
    # 读取音频文件
    audio = AudioSegment.from_file(audio_path)
    # 计算音频总时长（毫秒）
    total_duration_ms = len(audio)
    # 每个片段时长为 3 分钟
    segment_duration_ms = 3 * 60 * 1000
    # 计算片段数量
    num_segments = math.ceil(total_duration_ms / segment_duration_ms)

    # 分割音频文件
    for i in range(num_segments):
        print("正在处理第 %d/%d 个音频片段" % (i + 1, num_segments))
        start_ms = i * segment_duration_ms
        end_ms = min(start_ms + segment_duration_ms, total_duration_ms)
        segment = audio[start_ms:end_ms]
        # 将音频片段存成临时文件
        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_audio_file:
            # 将音频片段保存到临时文件
            segment.export(temp_audio_file.name, format="mp3")
            retries = 0
            while retries < MAX_RETRIES:
                try:
                    if format == "txt":
                        content = transcribe_audio(temp_audio_file.name, "json")
                        new_content = content.text
                    else:
                        # 转录音频片段
                        srt_content = transcribe_audio(temp_audio_file.name)
                        # 转录时间戳调整
                        new_content = adjust_timestamps(srt_content, start_ms)
                    with open(output_path, "a") as f:
                        f.write(new_content)
                    break
                except Exception as e:
                    retries += 1
                    print(f"转录失败，重试 {retries}/{MAX_RETRIES} 次: {e}")
                    if retries == MAX_RETRIES:
                        print("达到最大重试次数，跳过该片段")
                        break
    if format == "txt":
        return
    # 调整 srt id 顺序
    subs = pysubs2.load(output_path, encoding="utf-8", format_="srt")
    with open(output_path, "w") as f:
        subs.to_file(f, format_="srt")


def transcribe_audio(audio_file_path, format=None):
    """
    转录音频文件
    """
    if format is None:
        format = "srt"
    start_time = time.time()
    with open(audio_file_path, "rb") as audio_file:
        # 读取音频文件
        transcription = client.audio.transcriptions.create(model="whisper-1",
                                                           file=audio_file,
                                                           response_format=format)
        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算执行时间
        print(f"Transcription completed in {elapsed_time:.4f} seconds")
    return transcription


def convert2mp3(input_file, output_file):
    """
    将给定的音/视频文件转换为MP3格式
    """
    try:
        # 使用ffprobe获取输入文件信息
        probe_cmd = [ffprobe_path, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of",
                     "default=nokey=1:noprint_wrappers=1", input_file]
        codec_name = subprocess.check_output(probe_cmd, universal_newlines=True).strip()
        print(f"{codec_name}")

        # 构建ffmpeg命令
        cmd = [ffmpeg_path, "-i", input_file, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", "-f", "mp3",
               output_file]

        # 运行ffmpeg命令
        subprocess.run(cmd, check=True)

        print(f"成功将 {input_file} 转换为 {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg错误: {e.stderr}")

    except Exception as e:
        print(f"发生错误: {e}")


def process_media_file(media_path: str, srt_file=None):
    media = Path(media_path)
    if srt_file is None:
        srt_file = media.with_suffix('.srt')
    if srt_file.exists():
        print(f"{srt_file} 已存在，跳过")

    if media.suffix != '.mp3':
        mp3_file = media.with_suffix('.mp3')
        convert2mp3(str(media), str(mp3_file))
        segment_and_transcribe(str(media), str(srt_file), "srt")
    else:  # .mp3 file
        segment_and_transcribe(str(media), str(srt_file), "srt")


if __name__ == "__main__":
    # test_result = transcribe_audio("10s.mp3", "json")
    media_file = "/Users/bingwang/code/ai_toolkit/whisper/10s.mp3"
    process_media_file(media_file)
