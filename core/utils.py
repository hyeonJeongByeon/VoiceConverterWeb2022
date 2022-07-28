from django.core.files.storage import FileSystemStorage
from django.conf import settings

from core.manipulator.voice_manipulator import *
from core.manipulator.voice_filter import *

import os
from gtts import gTTS
from datetime import datetime

def save_uploaded_file(file):
    fs = FileSystemStorage()
    filename = fs.save(file.name, file)
    filepath = fs.path(filename)
    uploaded_file_url = fs.url(filename)

    return filename, filepath, uploaded_file_url

def save_sound_file(sound, filename):
    """
    Sound 타입의 파일을 저장
    """
    filename_without_ext = filename.split('.')[0]
    save_filename = f"{filename_without_ext}_manipulated.wav"

    # media 폴더에 파일 저장
    save_path = os.path.join(settings.MEDIA_ROOT, save_filename)
    sound.save(save_path, "WAV")

    # 저장된 파일 path 생성
    manipulated_file_url = os.path.join(settings.MEDIA_URL, save_filename)

    return manipulated_file_url

def save_audio_by_text(text, lang='en'):
    tts = gTTS(text=text, lang=lang)

    save_filename = str(datetime.now()).replace(' ', '')

    # media 폴더에 파일 저장
    save_path = os.path.join(settings.MEDIA_ROOT, save_filename)
    tts.save(save_path)

    uploaded_file_url = os.path.join(settings.MEDIA_URL, save_filename)

    return save_filename, save_path, uploaded_file_url

def calculate_audio_features_by_filepath(filepath):
    sound = get_sound(filepath)

    # Calculate audio feature
    pitchs = measure_pitch(sound)
    formants = measure_formant(sound)

    result = {
        'pitch': pitchs["Mean Pitch (F0)"],
        'f1': formants["F1 Mean"],
        'f2': formants["F2 Mean"],
        'f3': formants["F3 Mean"],
        'f4': formants["F4 Mean"],
    }

    return result