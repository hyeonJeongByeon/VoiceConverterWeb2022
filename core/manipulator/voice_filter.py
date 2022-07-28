import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats
from sklearn.impute import SimpleImputer
import sys
import os
from parselmouth.praat import call

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

def formant_max(sound):
  try:
    pitch_floor, pitch_ceiling = pitch_bounds(sound)
    pitch = call(
        sound, "To Pitch", 0.0, pitch_floor, pitch_ceiling
    ) # check pitch to set formant settings
    mean_f0 = call(pitch, "Get mean", 0, 0, "Hertz")
    if 140 <= mean_f0 <= 300:
      max_formant = 5500
    
    elif mean_f0 < 140:
      max_formant = 5000
    
    else:
      max_formant = 8000
    return max_formant
  except:
    return 5500

def get_values_function (object, fn, command):
  if command == "Get mean":
    return call(object, command, fn, 0, 0, "hertz")
  elif command == "Get quantile":
    return call(object, command, fn, 0, 0, "hertz", 0.5)

def measure_formant(sound):
  # measure formants
  formant_args = {
      "time step": 0.0025, # a zero value is equal to 25% of the window length
      "max number of formants": 5.5, # must be divisible by 0.5
      "window length(s)": 0.025,
      "pre emphasis from": 50,
      # formant Burg-Specific settings
      "max_formant (To Formant Burg...)": ('Auto', ['Auto', '5500']),
      # formant Path-Specific settings
      "Center Formant (Formant Path)": ('Auto', ['Auto', '5500']),
      "Ceiling Step Size (Formant Path)": 0.05,
      'Number of Steps (Formant Path)': 4,
      'method': ('To Formant Burg...', ['To Formant Burg...', 'Formant Path'],),
  }

  # check that max number of formants is divisible by 0.5
  if formant_args['max number of formants'] % 0.5 != 0:
    # If it's not, round that to the nearest integer
    formant_args['max number of formants'] = round(formant_args['max number of formants'])

  formant_state = {
      "f1 means": [],
      "f2 means": [],
      "f3 means": [],
      "f4 means": [],
      "f1 medians": [],
      "f2 medians": [],
      "f3 medians": [],
      "f4 medians": [],
  }

  method = formant_args['method'][0]
  try:
    # Burg Method
    if method == 'To Formant Burg...':
      # Set Maximum Formant Value Automatically
      if formant_args['max_formant (To Formant Burg...)'] == 'Auto':
        try:
          formant_args['max_formant (To Formant Burg...)'] = formant_max(sound)
        except:
          # Otherwise default to 5500Hz as max_formant value, Praat's default
          formant_args['max_formant (To Formant Burg...)'] == 5500
      # Set any user defined max formant values
      else:
        try:
          formant_args['max_formant (To Formant Burg...)'] == int(formant_args['max_formant (To Formant Burg...)'])
        except:
          # Otherwise default to 5500Hz as max_formant value, Praat's default
          formant_args['max_formant (To Formant Burg...)'] = 5500

      # Create a Praat Formant Object
      formant_object = sound.to_formant_burg(
          formant_args["time step"],
          formant_args["max number of formants"],
          formant_args["max_formant (To Formant Burg...)"],
          formant_args["window length(s)"],
          formant_args["pre emphasis from"],
    )

    # measure_PCA = formant_args['Measure PCA']

      # Generate max_formant parameter
      formant_args["max_formant"] = formant_max(sound)
      formant_path_object = call(sound, "To FormantPath (burg)", 0.005, 5, formant_args["max_formant"], 0.025, 50.0, 0.025, 5)
      formant_object = call(formant_path_object, "Extract Formant")

      # formant_object = sound.to_formant_burg(
      #    self.args["time step"],
      #    self.args["max number of formants"],
      #    self.args["max_formant"],
      #    self.args["window length(s)"],
      #    self.args["pre emphasis from"],
      # )

      # Formant Path Method
    elif formant_args['method'] == 'Formant Path':
      try: # Try formant path first
        # Find centre max formant
        if formant_args['Center Formant (Formant Path)'] == 'Auto':
          try:
            formant_args['Center Formant (Formant Path)'] = formant_max(sound)
          except:
            # Otherwise default to 5500Hz as max_formant value, Praat's default
            formant_args['Center Formant (Formant Path)'] = 5500
        # Set any user defined max formant values
        else:
          try:
            formant_args['Center Formant (Formant Path)'] = int(
                formant_args['Center Formant (Formant Path)'])
          except:
            # Otherwise default to 5500 Hz as max_formant value, Praat's default
            formant_args['Center Formant (Formant Path)'] = 5500

        # Create A Praat Formant Path Object
        formant_path_object = call(sound,
                                   "To FormantPath (burg)",
                                   formant_args["time step"],
                                   formant_args["max number of formants"],
                                   formant_args["Center Formant (Formant Path)"],
                                   formant_args["window length(s)"],
                                   formant_args["pre emphasis from"],
                                   formant_args["Ceiling Step Size (Formant Path)"],
                                   formant_args["Number of Steps (Formant Path)"])
        # Extract the Praat Formant Object from the Formant Path Object
        formant_object = call(formant_path_object, "Extract Formant")
        # Reset the method value in case previous voice failed at formant path and instead,
        ## 'To Formant Burg...' was used
        formant_args["method"] = 'Formant Path'

      except:
        # If formant path fails, get formant object formant_burg with max_formant from formant_args
        formant_object = sound.to_formant_burg(
            formant_args["time step"],
            formant_args["max number of formants"],
            formant_args["max_formant (To Formant Burg...)"],
            formant_args["window length(s)"],
            formant_args["pre emphasis from"],
        )
      # Set the method to To formant burg to ensure we record the method change in the output data file
      formant_args["method"] = 'To formant burg...'

    # vectorise gathering the formants in Numpy to prevent nested loops
    # set up lists to apply the functions across, the list needs to be 8 items long
    # 4 Formants, mean and median ('Get quantile') = 8 items
    # 8 Formant objects
    objects = [formant_object] * 8
    # 8 formant numbers
    formant_number = [1, 2, 3, 4] * 2
    # 8 measures of central tendency
    command = ['Get mean'] * 4 + ['Get quantile'] * 4
    # creates a vectorised function from our get_values_function function
    get_values = np.frompyfunc(get_values_function, 3, 1)
    # runs the vectorised function and returns a list of formant means and medians
    formant_means_and_medians = get_values(objects, formant_number, command)
    # expands the list into the proper variable names to report the results
    f1_mean, f2_mean, f3_mean, f4_mean, f1_median, f2_median, f3_median, f4_median = formant_means_and_medians
    # reports the results
    results = {
        "F1 Mean": f1_mean,
        "F2 Mean": f2_mean,
        "F3 Mean": f3_mean,
        "F4 Mean": f4_mean,
        "F1 Median": f1_median,
        "F2 Median": f2_median,
        "F3 Median": f3_median,
        "F4 Median": f4_median,
    }

  except: 
    # If something went wrong beyond what's already been tested for, report nan values and move on
    results = {
        "F1 Mean": np.nan,
        "F2 Mean": np.nan,
        "F3 Mean": np.nan,
        "F4 Mean": np.nan,
        "F1 Median": np.nan,
        "F2 Median": np.nan,
        "F3 Median": np.nan,
        "F4 Median": np.nan,
    }     
  return results

def pitch_value(
    sound, floor=50, ceiling=500, method="ac", time_step=0, max_number_of_candidates=15,
    silence_threshold=0.03, voicing_threshold=0.45, octave_cost=0.01,
    octave_jump_cost=0.35, voiced_unvoiced_cost=0.14, unit="Hertz", very_accurate="no",
):
  pitch: object = call(
      sound, method, time_step, floor, max_number_of_candidates, very_accurate,
      silence_threshold, voicing_threshold, octave_cost, octave_jump_cost,
      voiced_unvoiced_cost, ceiling,
  )
  mean_f0: float = call(pitch, "Get mean", 0, 0, unit)
  stdev_f0: float = call(
      pitch, "Get standard deviation", 0, 0, unit
  )
  min_f0: float = call(pitch, "Get minimum", 0, 0, unit, "Parabolic")
  max_f0: float = call(pitch, "Get maximum", 0, 0, unit, "Parabolic")

  return pitch, mean_f0, stdev_f0, min_f0, max_f0

def measure_pitch(sound):
  pitch_args = {
      # simple default values
      "Time Step": 0, # positive float or 0
      "Max Number of Candidates": 15, # positive integers
      "Silence Threshold": 0.03, # positive number
      "Voicing Threshold": 0.45, # positive number
      "Octave Cost": 0.01, # positive number
      "Octave Jump Cost": 0.35, # positive number
      "Voiced Unvoiced Cost": 0.14, # positive number
      "Unit": ("Hertz", ["Hertz",
                        "Hertz (Logarithmic)",
                        "mel",
                        "logHertz",
                        "semitones re 1 Hz",
                        "semitones re 100 Hz",
                        "semitones re 200 Hz",
                        "semitones re 440 Hz",
                        "ERB",
                        ]
              ),
      # tuple defines a discrete set of options, 0 = selected value, 1 = a list of all options
      "Algorithm": ("To Pitch (ac)", ["To Pitch (ac)", "To Pitch (cc)"]),
      "Very Accurate": ("yes", ["yes", "no"]),
  }

  file_duration: float = call(sound, "Get total duration")
  
  time_step = pitch_args["Time Step"]
  max_number_of_candidates = pitch_args["Max Number of Candidates"]
  silence_threshold = pitch_args["Silence Threshold"]
  voicing_threshold = pitch_args["Voicing Threshold"]
  octave_cost = pitch_args["Octave Cost"]
  octave_jump_cost = pitch_args["Octave Jump Cost"]
  voiced_unvoiced_cost = pitch_args["Voiced Unvoiced Cost"]
  unit = pitch_args["Unit"][0]

  method = pitch_args["Algorithm"][0]
  very_accurate = pitch_args["Very Accurate"][0]

  try:
    pitch_floor, pitch_ceiling = pitch_bounds(sound)
    pitch, mean_f0, stdev_f0, min_f0, max_f0 = pitch_value(
        sound,
        floor=pitch_floor,
        ceiling=pitch_ceiling,
        method=method,
        time_step=time_step,
        max_number_of_candidates=max_number_of_candidates,
        silence_threshold=silence_threshold,
        voicing_threshold=voicing_threshold,
        octave_cost=octave_cost,
        octave_jump_cost=octave_jump_cost,
        voiced_unvoiced_cost=voiced_unvoiced_cost,
        unit=unit,
        very_accurate=very_accurate,
    )

    return {
        "Mean Pitch (F0)": mean_f0,
        "Standard Deviation Pitch (F0)": stdev_f0,
        "Pitch Min (F0)": min_f0,
        "Pitch Max (F0)": max_f0,
        "Pitch Floor": pitch_floor,
        "Pitch Ceiling": pitch_ceiling,
    }
  except:
    return {
        "Mean Pitch (F0)": "Pitch Measurement Failed",
        "Standard Deviation Pitch (F0)": "Pitch Measurement Failed",
        "Pitch Min (F0)": "Pitch Measurement Failed",
        "Pitch Max (F0)": "Pitch Measurement Failed",
        "Pitch Floor": "Pitch Measurement Failed",
        "Pitch Ceiling": "Pitch Measurement Failed",
    }

def change_voice(sound, pitch_factor, formant_factor, duration_factor):
  manipulation = call(sound, "To Manipulation", 0.001, 75, 600)
  pitch = sound.to_pitch()
  median_pitch = call(pitch, "Get quantile", 0, 0, 0.5, "Hertz")
  pitch_multiply = median_pitch * pitch_factor
  manipulated_sound = call(sound, "Change gender", 100,
                           500, formant_factor, pitch_multiply, 1, duration_factor)
  # minimum pitch, maximum pitch, formant shift ratio, new pitch median, pitch range factor, duration factor

  return manipulated_sound

def calculateFactors(data):
    pitch_factor = float(data['pitchValue']) / float(data['originalPitchValue'])
    DIVIDER_FACTOR = 4
    formant_factor = (
        float(data['f1Value']) / float(data['originalF1Value']) + 
        float(data['f2Value']) / float(data['originalF2Value']) + 
        float(data['f3Value']) / float(data['originalF3Value']) + 
        float(data['f4Value']) / float(data['originalF4Value'])
        ) / DIVIDER_FACTOR
    return pitch_factor, formant_factor