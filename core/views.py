from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.manipulator.voice_manipulator import *
from core.manipulator.voice_filter import *
from core.utils import *
from voice_django.settings.base import S3_URL

import requests




def case1(request):
    return render(request, 'core/case1.html')

def case2(request):
    return render(request, 'core/case2.html')

def case3(request):
    return render(request, 'core/case3.html')

def case4(request):
    return render(request, 'core/case4.html')

def case5(request):
    path_elements = ['media', 'original.mp3']
    original_file_url = '/' + os.path.join(*path_elements)
    if request.method == 'POST':
        # top 10 -> find -> function

        # Get top 10 list (url)
        result, top10_keys = get_distance_top10()

        #원본 top10_desc = map(lambda key: {'url': get_s3_file_url(key.replace('.wav', '')), 'euclidean': "{:.2f}".format(result[key]) }, top10_keys)
        top10_desc = map(lambda key: {'url': get_s3_file_url(key.replace('.wav', '')), 'euclidean': "{:.2f}".format(100 - result[key]*0.1)}, top10_keys)


        # Make context
        context = {'top10_desc': top10_desc, 'original_audio_url': original_file_url}

        return render(request, 'core/case5.html', context=context)
    else:
        context = {'original_audio_url': original_file_url}
        return render(request, 'core/case5.html', context=context)

def case6(request):
    feature_info = {
        "breathiness": {
            "label": "숨소리가 많다", 
        },
            "hoarseness": {
            "label": "거칠다", 
        },
            "pitch": {
            "label": "높다", 
        },
            "precise": {
            "label": "발음이 명확하다", 
        },
            "speed": {
            "label": "빠르다", 
        },
            "variation": {
            "label": "음 높낮이 차이가 크다", 
        },
            "volume": {
            "label": "음량이 크다", 
        }
    }

    path_elements = ['media', 'original.mp3']
    original_file_url = '/' + os.path.join(*path_elements)

    if request.method == 'POST':
        # top 10 -> find -> function
        # Get top 10 list (url)
        features = request.POST.getlist('feature')
        top_filenames = get_hashtag_top(features)

        result, top10_keys = get_distance_top10_from_filenames(top_filenames)

        top10_desc = map(lambda key: {'url': get_s3_file_url(key), 'euclidean': ("{:.2f}".format(100 - result[key]*0.1))}, top10_keys)
        #원본 top10_desc = map(lambda key: {'url': get_s3_file_url(key), 'euclidean': ("{:.2f}".format(result[key]))}, top10_keys)
        #top10_desc = map(lambda key: {'url': get_s3_file_url(key), 'euclidean': 100 - float("{:.2f}".format(result[key]))*0.1 }, top10_keys)

        feature_labels = map(lambda feature: feature_info[feature]['label'], features)
        # Make context
        context = {'top10_desc': top10_desc, 'original_audio_url': original_file_url, 'feature_labels': feature_labels}

        return render(request, 'core/case6.html', context=context)
    else:
        context = {'original_audio_url': original_file_url}
        return render(request, 'core/case6.html', context=context)

def case7(request):
    feature_info = {
        "느리다": {
            "label": "느리다", 
        },
            "낮다": {
            "label": "낮다", 
        },
            "모노톤이다": {
            "label": "모노톤이다", 
        },
            "명확하다": {
            "label": "명확하다", 
        },
            "발음이 정확하다": {
            "label": "발음이 정확하다", 
        }
    }

    path_elements = ['media', 'original.mp3']
    original_file_url = '/' + os.path.join(*path_elements)

    if request.method == 'POST':
        # top 10 -> find -> function
        # Get top 10 list (url)
        features = request.POST.getlist('feature')

        top_filenames = get_hashtag_top_from_tag(features)

        result, top10_keys = get_distance_top10_from_filenames(top_filenames)

        #원본 top10_desc = map(lambda key: {'url': get_s3_file_url(key), 'euclidean': "{:.2f}".format(result[key]) }, top10_keys)
        top10_desc = map(lambda key: {'url': get_s3_file_url(key), 'euclidean': "{:.2f}".format(100 - result[key]*0.1)}, top10_keys)


        feature_labels = map(lambda feature: feature_info[feature]['label'], features)
        # Make context
        context = {'top10_desc': top10_desc, 'original_audio_url': original_file_url, 'feature_labels': feature_labels}

        return render(request, 'core/case7.html', context=context)
    else:
        context = {'original_audio_url': original_file_url}
        return render(request, 'core/case7.html', context=context)

# API
@csrf_exempt
def calculate_audio_feature(request):
    # Save audio
    filename, filepath, uploaded_file_url = save_uploaded_file(request.FILES['audio'])

    response = {
        'uploaded_file_url': uploaded_file_url,
    }

    result = calculate_audio_features_by_filepath(filepath)

    response.update(result)
    return JsonResponse(response)

@csrf_exempt
def manipulate_audio(request):
    text_for_tts = request.POST.get('textForTTS', None)

    if text_for_tts:
        # original audio comes from text (tts)
        filename, filepath, uploaded_file_url = save_audio_by_text(text_for_tts)
    else:
        # original audio comes from uploaded file
        filename, filepath, uploaded_file_url = save_uploaded_file(request.FILES['audio'])

    pitch_factor, formant_factor = calculateFactors(request.POST)
    sound = get_sound(filepath)
    manipulated_sound = change_voice(sound, pitch_factor, formant_factor, duration_factor=float(request.POST['durationValue']))
    
    # save manipulated_sound
    manipulated_file_url = save_sound_file(manipulated_sound, filename)

    return JsonResponse({'manipulated_sound_url': manipulated_file_url})


@csrf_exempt
def manipulate_audio_with_reflect(request):
    # start audio comes from uploaded file
    start_filename, start_filepath, start_uploaded_file_url = save_uploaded_file(request.FILES['startAudio'])
    reflect = float(request.POST['reflectValue'])

    # make sound
    start_sound = get_sound(start_filepath)

    # manipulate sound
    manipulated_sound = reflection(start_sound, reflect)

    # save manipulated_sound
    manipulated_file_url = save_sound_file(manipulated_sound, start_filename)

    # calculate formant and pitch
    manipulated_formant = measure_formant(manipulated_sound)
    manipulated_pitch = measure_pitch(manipulated_sound)


    return JsonResponse({
        'manipulated_sound_url': manipulated_file_url,
        'original_uploaded_file_url': start_filename,
        'pitchValue': manipulated_pitch["Mean Pitch (F0)"],
        'f1Value': manipulated_formant["F1 Mean"],
        'f2Value': manipulated_formant["F2 Mean"],
        'f3Value': manipulated_formant["F3 Mean"],
        'f4Value': manipulated_formant["F4 Mean"],
        })


@csrf_exempt
def manipulate_audio_with_target(request):
    text_for_tts = request.POST.get('textForTTS', None)

    if text_for_tts:
        # original audio comes from text (tts)
        original_filename, original_filepath, original_uploaded_file_url = save_audio_by_text(text_for_tts)
        reflect = 1
    else:
        # original audio comes from uploaded file
        original_filename, original_filepath, original_uploaded_file_url = save_uploaded_file(request.FILES['yourAudio'])
        reflect = float(request.POST['reflectValue'])


    # file save
    target_filename, target_filepath, target_uploaded_file_url = save_uploaded_file(request.FILES['targetAudio'])

    # make sound
    original_sound = get_sound(original_filepath)
    target_sound = get_sound(target_filepath)

    # calculate formant and pitch
    original_formant = measure_formant(original_sound)
    original_pitch = measure_pitch(original_sound)

    target_formant = measure_formant(target_sound)
    target_pitch = measure_pitch(target_sound)

    # manipulate sound
    manipulated_sound = manipulate_voice(original_filename, original_sound, original_pitch, original_formant, target_pitch, target_formant, reflect)

    # save manipulated_sound
    manipulated_file_url = save_sound_file(manipulated_sound, original_filename)

    # calculate formant and pitch
    manipulated_formant = measure_formant(manipulated_sound)
    manipulated_pitch = measure_pitch(manipulated_sound)


    return JsonResponse({
        'manipulated_sound_url': manipulated_file_url,
        'original_uploaded_file_url': original_uploaded_file_url,
        'pitchValue': manipulated_pitch["Mean Pitch (F0)"],
        'f1Value': manipulated_formant["F1 Mean"],
        'f2Value': manipulated_formant["F2 Mean"],
        'f3Value': manipulated_formant["F3 Mean"],
        'f4Value': manipulated_formant["F4 Mean"],
        })

@csrf_exempt
def convert_text_to_audio(request):
    is_need_features = request.GET.get('need_features', False)

    text_for_tts = request.POST['textForTTS']
    original_filename, original_filepath, original_uploaded_file_url = save_audio_by_text(text_for_tts)
    
    response = {
        'file_url': original_uploaded_file_url,
    }

    # calculate feature
    if is_need_features:
        result = calculate_audio_features_by_filepath(original_filepath)
        response.update(result)

    return JsonResponse(response)

@csrf_exempt
def switch_gender(request):
    text_for_tts = request.POST.get('textForTTS', None)

    if text_for_tts:
        # original audio comes from text (tts)
        filename, filepath, uploaded_file_url = save_audio_by_text(text_for_tts)
    else:
        # original audio comes from uploaded file
        filename, filepath, uploaded_file_url = save_uploaded_file(request.FILES['audio'])

    # make sound
    original_sound = get_sound(filepath)

    # switch gender
    manipulated_sound = switch_gender_sound(original_sound)

    # save manipulated_sound
    manipulated_sound_url = save_sound_file(manipulated_sound, filename)

    # calculate formant and pitch
    manipulated_formant = measure_formant(manipulated_sound)
    manipulated_pitch = measure_pitch(manipulated_sound)

    return JsonResponse({
        'manipulated_sound_url': manipulated_sound_url,
        'pitchValue': manipulated_pitch["Mean Pitch (F0)"],
        'f1Value': manipulated_formant["F1 Mean"],
        'f2Value': manipulated_formant["F2 Mean"],
        'f3Value': manipulated_formant["F3 Mean"],
        'f4Value': manipulated_formant["F4 Mean"],
    })

@csrf_exempt
def switch_child(request):
    text_for_tts = request.POST.get('textForTTS', None)

    if text_for_tts:
        # original audio comes from text (tts)
        filename, filepath, uploaded_file_url = save_audio_by_text(text_for_tts)
    else:
        # original audio comes from uploaded file
        filename, filepath, uploaded_file_url = save_uploaded_file(request.FILES['audio'])

    # make sound
    original_sound = get_sound(filepath)

    # switch gender
    manipulated_sound = switch_child_sound(original_sound)

    # save manipulated_sound
    manipulated_sound_url = save_sound_file(manipulated_sound, filename)

    # calculate formant and pitch
    manipulated_formant = measure_formant(manipulated_sound)
    manipulated_pitch = measure_pitch(manipulated_sound)

    return JsonResponse({
        'manipulated_sound_url': manipulated_sound_url,
        'pitchValue': manipulated_pitch["Mean Pitch (F0)"],
        'f1Value': manipulated_formant["F1 Mean"],
        'f2Value': manipulated_formant["F2 Mean"],
        'f3Value': manipulated_formant["F3 Mean"],
        'f4Value': manipulated_formant["F4 Mean"],
    })

def demo(request):
    return render(request, 'core/demo.html')