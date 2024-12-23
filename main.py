import pandas as pd
import tkinter as tk
from tkinter import messagebox

def load_data(symptoms_file, diseases_file, history_file):
    """Load datasets from CSV files."""
    symptoms = pd.read_csv(symptoms_file)
    diseases = pd.read_csv(diseases_file)
    history = pd.read_csv(history_file)
    return symptoms, diseases, history

def save_history(history_file, new_case):
    """Save a new case to the history file."""
    history = pd.read_csv(history_file)
    history = pd.concat([history, pd.DataFrame([new_case])], ignore_index=True)
    history.to_csv(history_file, index=False)

def jaccard_3w_similarity(input_symptoms, disease_symptoms, symptoms_weights):
    """Calculate the 3W-Jaccard similarity."""
    a = sum([symptoms_weights[s] for s in input_symptoms if s in disease_symptoms])
    b = sum([symptoms_weights[s] for s in input_symptoms if s not in disease_symptoms])
    c = sum([symptoms_weights[s] for s in disease_symptoms if s not in input_symptoms])
    similarity = 3 * a / (3 * a + b + c) if (3 * a + b + c) > 0 else 0
    return similarity

def diagnose(symptoms, diseases, input_symptoms):
    """Diagnose based on input symptoms."""
    symptoms_weights = dict(zip(symptoms['Code'], symptoms['Weight']))
    disease_symptom_map = {
        "A01": ["G01", "G02", "G03", "G04"],
        "A02": ["G07", "G08", "G09", "G10"],
        "A03": ["G01", "G03", "G06", "G13"],
        "A04": ["G04", "G05", "G14"],
        "A05": ["G10", "G15", "G20"],
        "A06": ["G12", "G17", "G18"]
    }
    
    results = []

    for _, disease in diseases.iterrows():
        disease_symptoms = disease_symptom_map.get(disease['Code'], [])
        similarity = jaccard_3w_similarity(input_symptoms, disease_symptoms, symptoms_weights)
        results.append((disease['Disease'], similarity))

    results.sort(key=lambda x: x[1], reverse=True)
    return results

def run_diagnosis(selected_symptoms):
    input_symptoms = [symptom_list[i] for i in selected_symptoms]

    try:
        results = diagnose(symptoms, diseases, input_symptoms)
        result_text = "\n".join([f"{disease}: {similarity * 100:.2f}% similarity" for disease, similarity in results])
        messagebox.showinfo("Diagnosis Results", result_text)

        # Save the diagnosis to history
        if results:
            top_diagnosis = results[0][0]  # Disease with highest similarity
            new_case = {
                "Symptoms": ",".join(input_symptoms),
                "Diagnosis": top_diagnosis
            }
            save_history("history.csv", new_case)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main_gui():
    global symptoms, diseases, history, symptom_list

    # Load datasets
    symptoms_file = "symptoms1.csv"
    diseases_file = "diseases1.csv"
    history_file = "history.csv"
    symptoms, diseases, history = load_data(symptoms_file, diseases_file, history_file)
    symptom_list = symptoms['Code'].tolist()

    # Create GUI window
    root = tk.Tk()
    root.title("Eye Disease Diagnosis")

    tk.Label(root, text="Select the symptoms you experience:").pack(pady=10)

    symptom_vars = []
    for symptom in symptoms['Symptom']:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(root, text=symptom, variable=var)
        chk.pack(anchor="w")
        symptom_vars.append(var)

    def collect_selected_symptoms():
        selected = [i for i, var in enumerate(symptom_vars) if var.get()]
        run_diagnosis(selected)

    tk.Button(root, text="Diagnose", command=collect_selected_symptoms).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
