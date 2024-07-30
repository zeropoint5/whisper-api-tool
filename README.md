## 音视频转录工具

这是一个音视频转脚本，能够将各种格式的音频和视频文件转换为MP3格式，并生成对应的字幕文件（SRT格式）。该工具利用OpenAI的Whisper模型进行语音识别，支持长音频的分段处理，并能自动调整时间戳。

### 主要功能

1. 音视频格式转换：将各种格式的音频和视频文件转换为MP3格式。
2. 语音转录：使用OpenAI的Whisper模型将音频转换为文本。
3. 字幕生成：生成SRT格式的字幕文件，包含准确的时间戳。
4. 长音频处理：自动将长音频分割成3分钟的片段进行处理，提高效率和准确性。
5. 重试机制：确保转录过程的稳定性。

### 依赖项

- Python 3.x
- openai
- pydub
- pysubs2
- dotenv
- ffmpeg（需要单独安装）

### 安装

1. 克隆此仓库到本地。
2. 安装所需的Python包：
   ```
   pip install -r requirements.txt
   ```
3. 安装ffmpeg（如果尚未安装）。
4. 在项目根目录创建一个`.env`文件，并添加以下内容：
   ```
   OPENAI_API_KEY=你的 OpenAI API 密钥
   OPENAI_API_BASE=你的 OpenAI API Base
   MAX_RETRIES=3
   ```

### 使用方法

1. 将要处理的音频或视频文件放在适当的目录中。
2. 修改`__main__`部分的`media_file`变量，指向你要处理的文件。
3. 运行脚本：
   ```
   python your_script_name.py
   ```
4. 脚本将自动处理文件，并在同一目录下生成SRT字幕文件。

### 主要函数

- `convert2mp3`: 将音频/视频文件转换为MP3格式。
- `transcribe_audio`: 使用OpenAI的Whisper模型转录音频。
- `segment_and_transcribe`: 将长音频分割并转录。
- `adjust_timestamps`: 调整SRT文件的时间戳。
- `process_media_file`: 处理单个媒体文件的主函数。

### 注意事项

- 确保您有足够的OpenAI API额度。
- 处理大文件可能需要较长时间，请耐心等待。
- 确保ffmpeg和ffprobe的路径设置正确。

### 贡献

欢迎提交问题和拉取请求，帮助改进这个工具。