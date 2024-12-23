import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, f1_score
from sklearn.preprocessing import MultiLabelBinarizer

# Data True Diagnosis
true_diagnosis = {
    "A01": ["G01", "G02", "G03", "G04"],
    "A02": ["G07", "G08", "G09", "G10"],
    "A03": ["G01", "G03", "G06", "G13"],
    "A04": ["G04", "G05", "G14"],
    "A05": ["G10", "G15", "G20"],
    "A06": ["G12", "G17", "G18"]
}

# Membaca file history.csv
history_df = pd.read_csv("history1.csv")

# Menyusun data history ke dalam format dictionary
history = {}
for index, row in history_df.iterrows():
    symptoms = row['Symptoms'].split(',')  # Mengambil gejala dan memisahkannya
    diagnosis = row['Diagnosis']
    history[diagnosis] = symptoms

# Fungsi untuk menghitung metrik evaluasi per diagnosis
def evaluate_model_per_disease(true_diagnosis, predicted_diagnosis):
    mlb = MultiLabelBinarizer()
    
    # Menyiapkan data true dan prediksi dalam bentuk biner
    y_true = mlb.fit_transform([true_diagnosis[disease] for disease in true_diagnosis])
    
    # Memastikan bahwa hanya gejala yang ada di dalam MultiLabelBinarizer yang digunakan
    known_symptoms = mlb.classes_
    
    # Filter gejala yang tidak dikenali
    y_pred = []
    for disease in predicted_diagnosis:
        symptoms = predicted_diagnosis[disease]
        valid_symptoms = [symptom for symptom in symptoms if symptom in known_symptoms]
        y_pred.append(valid_symptoms)
    
    y_pred = mlb.transform(y_pred)
    
    # Hitung akurasi, presisi, dan F1-score per penyakit
    results = {}
    for disease_idx, disease in enumerate(true_diagnosis):
        y_true_disease = y_true[disease_idx]
        y_pred_disease = y_pred[disease_idx]
        
        accuracy = accuracy_score(y_true_disease, y_pred_disease)
        precision = precision_score(y_true_disease, y_pred_disease, zero_division=1)
        f1 = f1_score(y_true_disease, y_pred_disease)
        
        results[disease] = {
            'accuracy': accuracy,
            'precision': precision,
            'f1': f1
        }
    
    return results

# Evaluasi model dengan riwayat yang diberikan
results = evaluate_model_per_disease(true_diagnosis, history)

# Hitung rata-rata dari semua metrik
total_accuracy = total_precision = total_f1 = 0
num_diseases = len(results)

for disease, metrics in results.items():
    total_accuracy += metrics['accuracy']
    total_precision += metrics['precision']
    total_f1 += metrics['f1']

avg_accuracy = total_accuracy / num_diseases
avg_precision = total_precision / num_diseases
avg_f1 = total_f1 / num_diseases

# Cetak hasil per penyakit dan rata-rata
for disease, metrics in results.items():
    print(f"Penyakit: {disease}")
    print(f"  Akurasi: {metrics['accuracy']}")
    print(f"  Presisi: {metrics['precision']}")
    print(f"  F1-score: {metrics['f1']}\n")

print(f"Rata-rata Akurasi: {avg_accuracy}")
print(f"Rata-rata Presisi: {avg_precision}")
print(f"Rata-rata F1-score: {avg_f1}")
