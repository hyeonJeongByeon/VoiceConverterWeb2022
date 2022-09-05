from parselmouth.praat import call
import parselmouth

def pitch_bounds(sound):
  # measure pitch ceiling and floor
  broad_pitch = sound.to_pitch_ac(
      None, 50, 15, True, 0.03, 0.45, 0.01, 0.35, 0.14, 500
  )
  # get mean pitch
  broad_mean_f0: float = call(
      broad_pitch, "Get mean", 0, 0, "hertz"
  )

  if broad_mean_f0 > 170:
    pitch_floor = 100
    pitch_ceiling = 500
  elif broad_mean_f0 < 170:
    pitch_floor = 50
    pitch_ceiling = 300
  else:
    pitch_floor = 50
    pitch_ceiling = 500
  return pitch_floor, pitch_ceiling


def manipulate_voice(file_path, sound, original_pitch, original_formant, new_pitch, new_formant, reflect):
  args = {"unit": ("percent", ["percent"]),
          "pitch_range_factor": 1,
          "duration_factor": 1,
          "normalise amplitude": True
          }
  

  new_f1 = (new_formant["F1 Mean"] - original_formant["F1 Mean"]) * reflect + original_formant["F1 Mean"]
  new_f2 = (new_formant["F2 Mean"] - original_formant["F2 Mean"]) * reflect + original_formant["F2 Mean"]
  new_f3 = (new_formant["F3 Mean"] - original_formant["F3 Mean"]) * reflect + original_formant["F3 Mean"]
  new_f4 = (new_formant["F4 Mean"] - original_formant["F4 Mean"]) * reflect + original_formant["F4 Mean"]
  new_pitch_mean = (new_pitch["Mean Pitch (F0)"] - original_pitch["Mean Pitch (F0)"]) * reflect + original_pitch["Mean Pitch (F0)"]
  pitch_factor = new_pitch_mean / original_pitch["Mean Pitch (F0)"]
  formant_factor = (new_f1 / original_formant["F1 Mean"] + new_f2 / original_formant["F2 Mean"] + new_f3 / original_formant["F3 Mean"] + new_f4 / original_formant["F4 Mean"]) / 4
  duration = sound.get_total_duration()
  pitch_range_factor = args["pitch_range_factor"]
  duration_factor = 1
  pitch_range_factor = 1
  f0min, f0max = pitch_bounds(sound)
  args['f0min'], args['f0max'] = f0min, f0max
  pitch = sound.to_pitch()
  median_pitch = call(pitch, "Get quantile", 0, duration, 0.5, "Hertz")

  new_pitch_median = pitch_factor * median_pitch

  output_file_name = file_path.split("/")[-1].split(".wav")[0]
  output_file_name = (
      f"{output_file_name}_lower_pitch_and_formants_{pitch_factor}_{formant_factor}"
  )
  number_of_channels = call(sound, 'Get number of channels')
  if number_of_channels == 2:
    sound = call(sound, 'Convert to mono')

  manipulated_sound = call(
      sound,
      "Change gender",
      f0min,
      f0max,
      formant_factor,
      new_pitch_median,
      pitch_range_factor,
      duration_factor,
  )

  if args["normalise amplitude"]:
    manipulated_sound.scale_intensity(70)

  manipulated_sound.name = output_file_name

  return manipulated_sound

def get_sound(filename):
  return parselmouth.Sound(filename)

def switch_gender_sound(sound):
  call(sound, "Scale intensity", 70)
  pitch = call(sound, "To Pitch", 0.0, 60, 500)
  meanF0 = call(pitch, "Get mean", 0, 0, "Hertz")

  if meanF0 > 159:
    gender = "female"
  else:
    gender = "male"

  if gender == "female":
    switched_sound = call(sound, "Change gender", 60, 500, 0.8, 100, 1, 1)
  elif gender == "male":
    switched_sound = call(sound, "Change gender", 60, 500, 1.2, 220, 1, 1)

  return switched_sound

def switch_child_sound(sound):
  call(sound, "Scale intensity", 70)
  pitch = call(sound, "To Pitch", 0.0, 60, 500)
  meanF0 = call(pitch, "Get mean", 0, 0, "Hertz")

  if meanF0 > 159:
    gender = "female"
  else:
    gender = "male"

  if gender == "female":
    switched_sound = call(sound, "Change gender", 60, 500, 1.5, 350, 1, 1)
  elif gender == "male":
    switched_sound = call(sound, "Change gender", 60, 500, 1.6, 350, 1, 1)
  return switched_sound

def reflection(sound, reflect):
  pitch_factor = reflect
  formant_factor = reflect
  duration = sound.get_total_duration()
  pitch_range_factor = 1
  duration_factor = reflect
  f0min, f0max = pitch_bounds(sound)
  pitch = sound.to_pitch()
  median_pitch = call(pitch, "Get quantile", 0, duration, 0.5, "Hertz")

  new_pitch_median = pitch_factor * median_pitch

  number_of_channels = call(sound, 'Get number of channels')
  if number_of_channels == 2:
    sound = call(sound, 'Convert to mono')

  manipulated_sound = call(
      sound,
      "Change gender",
      f0min,
      f0max,
      formant_factor,
      new_pitch_median,
      pitch_range_factor,
      duration_factor,
  )

  manipulated_sound.scale_intensity(70)
  return manipulated_sound          