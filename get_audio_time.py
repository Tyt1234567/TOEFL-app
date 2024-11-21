from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.wave import WAVE


def get_audio_duration(file_path):
    if file_path.endswith('.mp3'):
        audio = MP3(file_path)
    elif file_path.endswith('.m4a'):
        audio = MP4(file_path)
    elif file_path.endswith('.wav') or file_path.endswith('.WAV'):
        audio = WAVE(file_path)
    else:
        return 0

    return audio.info.length


'''
file_path = 'paper_source\\audio\\模考8-C1.wav'  # 可以是 mp3, m4a 或 wav 文件
duration = get_audio_duration(file_path)
print(f"Audio Duration: {int(duration//1)} seconds")
'''