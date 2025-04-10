# suggestions.py (Updated for JSON)

import json # Use json module
# import pandas as pd # No longer needed here if not using CSV
import os
import warnings

# --- Configuration ---
REMEDIES_FILE = "remedies.json"
DOCTORS_FILE = "doctors.json" # <--- Changed to .json

# --- Global Variables to hold loaded data ---
_remedies_data = {}
_doctors_data = {} # This will now hold the dict loaded from JSON
_data_loaded = False

def _load_data():
    """Loads remedy (JSON) and doctor (JSON) data from files."""
    global _remedies_data, _doctors_data, _data_loaded
    if _data_loaded:
        return

    print("Loading suggestion data (remedies.json and doctors.json)...")

    # Load Remedies (remains the same)
    try:
        if os.path.exists(REMEDIES_FILE):
            with open(REMEDIES_FILE, 'r', encoding='utf-8') as f:
                _remedies_data = json.load(f)
            print(f"Remedies loaded successfully from {REMEDIES_FILE}.")
        else:
            print(f"Warning: {REMEDIES_FILE} not found. Remedies unavailable.")
            _remedies_data['_default_'] = "Remedy data file not found."
    # ... (rest of remedy error handling remains same) ...
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {REMEDIES_FILE}.")
        _remedies_data['_default_'] = "Error reading remedy data."
    except Exception as e:
        print(f"Error loading remedies: {e}")
        _remedies_data['_default_'] = "Error loading remedy data."
    if '_default_' not in _remedies_data:
         _remedies_data['_default_'] = "Consult a doctor for advice."


    # Load Doctors (Updated to read JSON)
    try:
        if os.path.exists(DOCTORS_FILE):
            with open(DOCTORS_FILE, 'r', encoding='utf-8') as f:
                # Load the entire JSON object directly
                _doctors_data = json.load(f)
                # Ensure keys are lowercase if they aren't already (optional, depends on JSON)
                # _doctors_data = {k.lower(): v for k, v in loaded_doctors.items()}
            print(f"Doctors loaded successfully from {DOCTORS_FILE}.")
        else:
            print(f"Warning: {DOCTORS_FILE} not found. Doctor info unavailable.")
            _doctors_data['_default_'] = {"notes": "Doctor data file not found."} # Set a default dict structure
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {DOCTORS_FILE}.")
        _doctors_data['_default_'] = {"notes": "Error reading doctor data."}
    except Exception as e:
        print(f"Error loading doctors: {e}")
        _doctors_data['_default_'] = {"notes": f"Error loading doctor data: {e}"}
    # Ensure a default entry exists
    if '_default_' not in _doctors_data:
         _doctors_data['_default_'] = {
            "doctor_name": "General Physician",
            "specialization": "General Medicine",
            "contact": "Search Local Clinics",
            "notes": "Default suggestion."
         }

    _data_loaded = True


def get_suggestions(disease_name):
    """
    Retrieves remedy and doctor suggestions for a given disease name.

    Args:
        disease_name (str): The name of the predicted disease.

    Returns:
        tuple: (remedy_suggestion, doctor_suggestion_string)
    """
    if not _data_loaded:
         _load_data()

    disease_key = str(disease_name).strip().lower()

    # --- Get Remedy ---
    default_remedy = _remedies_data.get('_default_', "Consult a doctor.")
    remedy = _remedies_data.get(disease_key, default_remedy)

    # --- Get Doctor Info (from dictionary) ---
    default_doctor_info = _doctors_data.get('_default_', {"notes": "Consult GP."})
    doctor_info = _doctors_data.get(disease_key, default_doctor_info)

    # --- Format Doctor Info into a String ---
    if doctor_info:
         # Build the string piece by piece, handling potentially missing keys
         parts = [doctor_info.get('doctor_name', None), doctor_info.get('specialization', None)]
         # Filter out None values and join with ' - '
         name_spec = " - ".join(filter(None, parts))

         contact = doctor_info.get('contact', None)
         notes = doctor_info.get('notes', None)

         full_suggestion = name_spec
         if contact and contact != 'N/A':
             full_suggestion += f", Contact: {contact}"
         if notes:
             full_suggestion += f". ({notes})"

         # Handle case where only notes might be present in default/error
         if not name_spec and not contact and notes:
             doctor_suggestion_string = notes
         elif not name_spec and not contact and not notes:
              doctor_suggestion_string = "No specific doctor information available."
         else:
              doctor_suggestion_string = full_suggestion

    else: # Should not happen if default exists, but as safety
         doctor_suggestion_string = "Doctor information lookup failed."


    return remedy, doctor_suggestion_string

# --- Optional: Preload data ---
_load_data()

# --- Example Usage (for testing the module directly) ---
if __name__ == "__main__":
    print("\n--- Testing suggestions module (with JSON) ---")
    test_diseases = ["Cold", "cough", "Diabetes ", "Unknown Disease", "    Malaria   "]
    for disease in test_diseases:
        rem, doc = get_suggestions(disease)
        print(f"\nDisease: {disease}")
        print(f"  Remedy: {rem}")
        print(f"  Doctor: {doc}")