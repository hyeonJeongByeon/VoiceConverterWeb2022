from django.urls import path
from core.views import *

urlpatterns = [
    path('case1/', case1, name='case1'),
    path('case2/', case2, name='case2'),
    path('case3/', case3, name='case3'),
    path('case4/', case4, name='case4'),
    path('case5/', case5, name='case5'),
    path('case6/', case6, name='case6'),
    path('case7/', case7, name='case7'),
    path('manipulate_audio/', manipulate_audio, name='manipulate_audio'),
    path('calculate_audio_feature/', calculate_audio_feature, name='calculate_audio_feature'),
    path('manipulate_audio_with_target/', manipulate_audio_with_target, name='manipulate_audio_with_target'),
    path('manipulate_audio_with_reflect/', manipulate_audio_with_reflect, name='manipulate_audio_with_reflect'),
    path('convert_text_to_audio/', convert_text_to_audio, name='convert_text_to_audio'),
    path('switch_gender/', switch_gender, name='switch_gender'),
    path('switch_child/', switch_child, name='switch_child'),
]