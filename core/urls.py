from django.urls import path
from core.views import *

urlpatterns = [
    path('case1/', case1, name='case1'),
    path('case2/', case2, name='case2'),
    path('case3/', case3, name='case3'),
    path('case4/', case4, name='case4'),
    path('manipulate_audio/', manipulate_audio, name='manipulate_audio'),
    path('calculate_audio_feature/', calculate_audio_feature, name='calculate_audio_feature'),
    path('manipulate_audio_with_target/', manipulate_audio_with_target, name='manipulate_audio_with_target'),
    path('convert_text_to_audio/', convert_text_to_audio, name='convert_text_to_audio'),


]