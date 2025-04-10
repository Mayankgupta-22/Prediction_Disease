# app.py (Add date/time context)

from flask import Flask, render_template, request
import pickle
import numpy as np
import os
import suggestions
import warnings
from datetime import datetime
import pytz # For timezone handling (pip install pytz)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

app = Flask(__name__)

# --- Load ML Components (same as before) ---
# ... (loading code for model, encoder, symptoms) ...
MODEL_PATH = "disease_model.pkl"
ENCODER_PATH = "label_encoder.pkl"
SYMPTOMS_PATH = "symptom_list.pkl"

model = None
label_encoder = None
symptom_list = ["Error: symptom list not found"] # Default value

try:
    if os.path.exists(MODEL_PATH): model = pickle.load(open(MODEL_PATH, 'rb'))
    else: print(f"Error: Model file not found at {MODEL_PATH}")
    if os.path.exists(ENCODER_PATH): label_encoder = pickle.load(open(ENCODER_PATH, 'rb'))
    else: print(f"Error: Label encoder file not found at {ENCODER_PATH}")
    if os.path.exists(SYMPTOMS_PATH): symptom_list = pickle.load(open(SYMPTOMS_PATH, 'rb'))
    else: print(f"Error: Symptom list file not found at {SYMPTOMS_PATH}")

    if model and label_encoder and isinstance(symptom_list, list): print("ML components loaded successfully.")
    else: print("Warning: One or more ML components failed to load.")
    if not isinstance(symptom_list, list): symptom_list = ["Error: symptom list not loaded"]
except Exception as e:
    print(f"An error occurred loading pickle files: {e}")
    model, label_encoder, symptom_list = None, None, ["Error: loading failed"]
# --- End Loading ML Components ---


# Function to get current context
def get_context():
    # Set timezone to India Standard Time
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    return {
        "current_year": now_ist.year,
        "current_time": now_ist.strftime("%I:%M:%S %p %Z"), # e.g., 11:30:00 PM IST
        "current_location": "Raipur, Chhattisgarh, India" # As per context
    }

# --- Flask Routes ---
@app.route('/', methods=['GET'])
def home():
    context = get_context()
    return render_template('index.html',
                           all_symptoms=symptom_list,
                           **context) # Pass context dictionary

@app.route('/predict', methods=['POST'])
def predict():
    context = get_context() # Get current context
    if model is None or label_encoder is None or "Error" in symptom_list[0]:
         error_msg = "Error: Model or supporting files not loaded correctly. Cannot predict."
         print(error_msg)
         return render_template('index.html',
                                all_symptoms=symptom_list,
                                prediction_text=error_msg,
                                remedy_text="", doctor_text="",
                                **context) # Pass context

    pred_text = ""
    remedy_text = ""
    doctor_text = ""
    selected_symptoms = request.form.getlist('symptoms')

    try:
        if not selected_symptoms:
            pred_text = "Please select at least one symptom."
        else:
            # ... (prediction logic remains the same) ...
            input_vector = np.zeros(len(symptom_list))
            symptoms_found = []
            for symptom in selected_symptoms:
                if symptom in symptom_list:
                    index = symptom_list.index(symptom)
                    input_vector[index] = 1
                    symptoms_found.append(symptom)

            if not symptoms_found:
                 pred_text = "No valid symptoms selected from the list."
            else:
                input_vector_reshaped = input_vector.reshape(1, -1)
                prediction_encoded = model.predict(input_vector_reshaped)
                predicted_disease = label_encoder.inverse_transform(prediction_encoded)[0]
                remedy, doctor = suggestions.get_suggestions(predicted_disease)
                pred_text = f"Predicted Disease: {predicted_disease}"
                remedy_text = remedy
                doctor_text = doctor

    except Exception as e:
        print(f"Error during prediction or suggestion lookup: {e}")
        pred_text = "An error occurred during processing. Please check logs."
        import traceback
        traceback.print_exc()

    # Render template with results, selected symptoms, and context
    return render_template('index.html',
                           all_symptoms=symptom_list,
                           prediction_text=pred_text,
                           remedy_text=remedy_text,
                           doctor_text=doctor_text,
                           selected_symptoms=selected_symptoms,
                           **context) # Pass context dictionary

# --- Run the App ---
if __name__ == '__main__':
    essential_files_exist = all([ os.path.exists(p) for p in [MODEL_PATH, ENCODER_PATH, SYMPTOMS_PATH] ])
    if not essential_files_exist:
         print("\nERROR: Model pickle files (.pkl) not found. Run 'create_pickle.py'.\n")
    else:
         print("Starting Flask server...")
         suggestions._load_data() # Pre-load suggestion data
         app.run(debug=True, host='0.0.0.0') # Accessible on local network