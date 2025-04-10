# suggestions.py

import pandas as pd
import json
import os

# --- Configuration ---
REMEDIES_FILE = "remedies.json"
DOCTORS_FILE = "doctors.csv"

# --- Global Variables to hold loaded data ---
# Load data once when the module is imported
_remedies_data = {}
_doctors_data = {}
_data_loaded = False

def _load_data():
    """Loads remedy and doctor data from files. Internal function."""
    global _remedies_data, _doctors_data, _data_loaded
    if _data_loaded: # Prevent reloading if already loaded
        return

    print("Loading suggestion data...")
    # Load Remedies
    try:
        if os.path.exists(REMEDIES_FILE):
            with open(REMEDIES_FILE, 'r', encoding='utf-8') as f:
                _remedies_data = json.load(f)
            print(f"Remedies loaded from {REMEDIES_FILE}.")
        else:
            print(f"Warning: {REMEDIES_FILE} not found. Remedies unavailable.")
            _remedies_data['_default_'] = "Remedy data file not found." # Ensure default exists
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {REMEDIES_FILE}.")
        _remedies_data['_default_'] = "Error reading remedy data."
    except Exception as e:
        print(f"Error loading remedies: {e}")
        _remedies_data['_default_'] = "Error loading remedy data."


    # Load Doctors
    try:
        if os.path.exists(DOCTORS_FILE):
            df_doctors = pd.read_csv(DOCTORS_FILE)
            # Create dictionary with lowercase disease names as keys
            _doctors_data = {
                str(row["disease"]).strip().lower(): f"{row['doctor_name']} - {row['specialization']}, Contact: {row['contact']}"
                for _, row in df_doctors.iterrows() if pd.notna(row.get("disease")) # Handle potential missing disease names
            }
            print(f"Doctors loaded from {DOCTORS_FILE}.")
        else:
            print(f"Warning: {DOCTORS_FILE} not found. Doctor info unavailable.")
    except Exception as e:
        print(f"Error loading doctors: {e}")

    _data_loaded = True # Mark data as loaded


def get_suggestions(disease_name):
    """
    Retrieves remedy and doctor suggestions for a given disease name.

    Args:
        disease_name (str): The name of the predicted disease.

    Returns:
        tuple: (remedy_suggestion, doctor_suggestion)
    """
    _load_data() # Ensure data is loaded

    # Normalize the input disease name (lowercase, strip whitespace)
    disease_key = str(disease_name).strip().lower()

    # Get Remedy - Use .get() with a default value referring to the '_default_' key
    default_remedy = _remedies_data.get('_default_', "Consult a doctor for advice.")
    remedy = _remedies_data.get(disease_key, default_remedy)

    # Get Doctor - Use .get() with a default message
    doctor = _doctors_data.get(disease_key, "No specific doctor found in directory. Consult a general healthcare professional.")

    return remedy, doctor

# --- Optional: Preload data when module is imported ---
_load_data()

# --- Example Usage (for testing the module directly) ---
if __name__ == "__main__":
    print("\n--- Testing suggestions module ---")
    test_diseases = ["Cold", "cough", "Diabetes", "Unknown Disease", "    Malaria   "]
    for disease in test_diseases:
        rem, doc = get_suggestions(disease)
        print(f"\nDisease: {disease}")
        print(f"  Remedy: {rem}")
        print(f"  Doctor: {doc}")