import pandas as pd
import tkinter as tk
from tkinter import messagebox

def load_data(symptoms_file, diseases_file):
    """Load datasets from CSV files."""
    symptoms = pd.read_csv(symptoms_file)
    diseases = pd.read_csv(diseases_file)
    return symptoms, diseases

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
    input_symptoms = [symptom_codes[symptom] for symptom in selected_symptoms]

    try:
        results = diagnose(symptoms, diseases, input_symptoms)
        result_text = "\n".join([f"{disease}: {similarity * 100:.2f}% similarity" for disease, similarity in results])
        messagebox.showinfo("Diagnosis Results", result_text)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main_gui():
    global symptoms, diseases, symptom_codes

    symptoms_file = "symptoms1.csv"
    diseases_file = "diseases1.csv"
    symptoms, diseases = load_data(symptoms_file, diseases_file)
    symptom_codes = dict(zip(symptoms['Symptom'], symptoms['Code']))

    # Create GUI 
    root = tk.Tk()
    root.title("Eye Disease Diagnosis")

    tk.Label(root, text="Select the symptoms you experience:").pack(pady=10)
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    symptom_vars = {}
    
    # checkboxes
    for symptom in symptoms['Symptom']:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(scrollable_frame, text=symptom, variable=var)
        chk.pack(anchor="w")
        symptom_vars[symptom] = var

    def collect_selected_symptoms():
        selected = [symptom for symptom, var in symptom_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("Warning", "Please select at least one symptom.")
            return
        run_diagnosis(selected)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    tk.Button(root, text="Diagnose", command=collect_selected_symptoms).pack(pady=20)

    root.geometry("400x500")
    
    root.mainloop()

if __name__ == "__main__":
    main_gui()