from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.manipulator.voice_manipulator import *
from core.manipulator.voice_filter import *
from core.utils import *

def case1(request):
    return render(request, 'core/case1.html')

def case2(request):
    return render(request, 'core/case2.html')

def case3(request):
    return render(request, 'core/case3.html')

def case4(request):
    return render(request, 'core/case4.html')

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
    manipulated_sound = change_voice(sound, pitch_factor, formant_factor, duration_factor=1)
    
    # save manipulated_sound
    manipulated_file_url = save_sound_file(manipulated_sound, filename)

    return JsonResponse({'manipulated_sound_url': manipulated_file_url})

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

    return JsonResponse({
        'manipulated_sound_url': manipulated_file_url,
        'original_uploaded_file_url': original_uploaded_file_url,
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