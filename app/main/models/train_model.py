from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pickle

# Liste des titres d'emplois
job_titles = [
    'Développeur Backend', 'Infirmier(ère) Diplômé(e) d\'État', 'Professeur d\'Informatique', 
    'Spécialiste en Marketing Digital', 'Responsable RH', 'Développeur React JS', 
    'Comptable Senior', 'Ingénieur DevOps', 'Designer UI/UX', 'Chef de Projet IT'
]

# Fonction pour garantir que le salaire commence à 50 000 FCFA
def adjust_salary(salary):
    return max(salary, 50000)

# Données d'entraînement, avec les titres d'emplois, l'expérience, le salaire, etc.
X_train = np.array([
    [5, adjust_salary(600000), 1],  # Accepté
    [3, adjust_salary(350000), 0],  # Pré-emploi
    [4, adjust_salary(500000), 1],  # Rejeté
    [7, adjust_salary(700000), 1],  # Accepté
    [6, adjust_salary(650000), 1],  # Pré-emploi
    [2, adjust_salary(450000), 1],  # Rejeté
    [8, adjust_salary(1000000), 0], # Accepté
    [10, adjust_salary(750000), 0], # Rejeté
    [5, adjust_salary(500000), 0],  # Accepté
    [6, adjust_salary(550000), 1]   # Pré-emploi
])

y_train = np.array([
    1, 2, 3, 1, 2, 3, 1, 3, 1, 2  # 1 = Accepté, 2 = Pré-emploi, 3 = Rejeté
])

# Entraîner le modèle
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Sauvegarder le modèle
with open("app/main/models/ml_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Modèle d'entraînement avec les titres d'emplois et salaires sauvegardé avec succès !")
