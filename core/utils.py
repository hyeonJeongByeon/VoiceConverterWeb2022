from django.core.files.storage import FileSystemStorage
from django.conf import settings

from core.manipulator.voice_manipulator import *
from core.manipulator.voice_filter import *
from voice_django.settings.base import S3_URL

import os
from gtts import gTTS
from datetime import datetime
from fastdtw import fastdtw
import pickle
import pandas as pd


def get_project_file_path(postfixes: list):
    from voice_django.settings.base import BASE_DIR
    return os.path.join(BASE_DIR, *postfixes)

def get_s3_file_url(filename):
    return f'{S3_URL}recordings/{filename}'

def save_uploaded_file(file, name=None):
    fs = FileSystemStorage()
    if name:
        filename = fs.save(name, file)
    else:
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
    duration = sound.get_total_duration()

    result = {
        'pitch': pitchs["Mean Pitch (F0)"],
        'f1': formants["F1 Mean"],
        'f2': formants["F2 Mean"],
        'f3': formants["F3 Mean"],
        'f4': formants["F4 Mean"],
        'duration': duration,
    }

    return result

def hashtag_feature(sound, choice):
  from scipy.spatial.distance import euclidean
  pickle_path = get_project_file_path(["feature.pickle"])
  with open (pickle_path, "rb") as fr:
    feature = pickle.load(fr)

  files = feature[choice]
  print(files)
  candidates = {}

  for filename in files:
    filepath = get_project_file_path(['media','recordings', f'{filename}.mp3'])
    sound_comp = parselmouth.Sound(filepath)

    if sound.values.shape[1] >= sound_comp.values.shape[1]:
      distance, path = fastdtw(sound.values[:, sound_comp.values.shape[1]], sound_comp.values, dist=euclidean)
    else:
      distance, path = fastdtw(sound.values, sound_comp.values[:, sound.values.shape[1]], dist=euclidean)

    candidates[filename] = distance

  result = dict(sorted(candidates.items(), key=lambda x: x[1]))

  top10_keys = list(result.keys())[:10]  # desc
  return result, top10_keys

def hashtag_values(f1, f2, f3, f4, pitch): # remove sound argument
  pickle_path = get_project_file_path(["value.pickle"])  # change 'value.pickle' -> project path

  ############### ORIGINAL CODE ################
  with open(pickle_path, "rb") as fr:  # pickle_path <- changed
    value = pickle.load(fr)

  files = value.keys()
  distance = {}

  for filename in files:
    distance[filename] = abs(pitch - value[filename]['pitch']) + abs(f1 - value[filename]['f1']) + abs(f2 - value[filename]['f2']) + abs(f3 - value[filename]['f3']) + abs(f4 - value[filename]['f4'])

  result = dict(sorted(distance.items(), key=lambda x: x[1]))

  ###############################################

  top10_keys = list(result.keys())[:10]  # desc
  print(f'result: {result}')
  print(f'top10_keys: {top10_keys}')
  return result, top10_keys  # change return


def get_distance_top10():
  pickle_path = get_project_file_path(["distance.pickle"])

  with open(pickle_path, "rb") as fr:  # pickle_path <- changed
    distance = pickle.load(fr)

  result = dict(sorted(distance.items(), key=lambda x: x[1]))

  top10_keys = list(result.keys())[1:1+10]  # desc (remove original audio)

  return result, top10_keys  # change return


def get_hashtag_top(hashtags: list):
  csv_path = get_project_file_path(["labelled_data.csv"])
  df = pd.read_csv(csv_path)

  threshold = 3
  filter = df[hashtags[0]] >= threshold

  for hashtag in hashtags[1:]:
    new_filter = df[hashtag] >= threshold
    filter = filter & new_filter

  top_df = df[filter]
  top_filenames = top_df['filename']

  return list(top_filenames)


def get_distance_top10_from_filenames(filenames):
  pickle_path = get_project_file_path(["distance.pickle"])

  with open(pickle_path, "rb") as fr:  # pickle_path <- changed
    distance = pickle.load(fr)

  print(distance)
  filtered_distance = {k: v for k, v in distance.items() if k in filenames}

  result = dict(sorted(filtered_distance.items(), key=lambda x: x[1]))

  top10_keys = list(result.keys())[1:1+10]  # desc (remove original audio)

  return result, top10_keys  # change return


def get_hashtag_top_from_tag(hashtags: list):
  csv_path = get_project_file_path(["voice_tagging.csv"])
  df = pd.read_csv(csv_path)

  match_counter = df['Hashtag1'].isin(hashtags).astype(int)

  for column_name in ['Hashtag2', 'Hashtag3', 'Hashtag4', 'Hashtag5', 'Hashtag6']:
    new_match_counter = df[column_name].isin(hashtags).astype(int)
    match_counter = match_counter + new_match_counter

  top_df = df[match_counter == len(hashtags)]
  top_filenames = top_df['Speaker ID']

  return list(top_filenames)