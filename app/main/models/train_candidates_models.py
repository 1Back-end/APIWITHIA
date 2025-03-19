import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
from app.main import models
from datetime import datetime
import pickle

# Fonction pour calculer l'expérience en années
def calculate_experience(start_date, end_date=None):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
    delta = end_date - start_date
    return delta.days // 365

# Fonction pour extraire les données des candidats
def extract_candidate_data(session):
    candidates = session.query(models.Candidat).all()
    data = []

    for candidate in candidates:
        total_experience = sum([calculate_experience(exp.start_date, exp.end_date) for exp in candidate.experiences])
        highest_degree = max([diploma.end_year for diploma in candidate.diplomas], default=None)

        # Exemple de caractéristiques extraites
        features = {
            'years_of_experience': total_experience,
            'highest_degree_year': highest_degree,
            'is_new_user': 1 if candidate.is_new_user else 0,
            'has_avatar': 1 if candidate.avatar else 0,
            'is_deleted': 1 if candidate.is_deleted else 0,
        }
        data.append(features)

    return pd.DataFrame(data)

# Extraire les données des candidats
session = None  # Assurez-vous de définir la session SQLAlchemy appropriée
candidate_data = extract_candidate_data(session)

# Simuler un label pour l'exemple (vous pouvez définir un label réel basé sur vos critères)
candidate_data['label'] = np.random.choice([0, 1], size=len(candidate_data))  # 0 = Rejeté, 1 = Accepté

# Sélectionner les caractéristiques (features) et les étiquettes (labels)
X = candidate_data.drop(columns=['label'])
y = candidate_data['label']

# Diviser les données en jeu d'entraînement et test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner un modèle de forêt aléatoire
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Faire des prédictions
y_pred = model.predict(X_test)

# Évaluer le modèle
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy du modèle : {accuracy * 100:.2f}%")

# Sauvegarder le modèle pour l'utiliser plus tard
with open("candidate_model.pkl", "wb") as f:
    pickle.dump(model, f)

# Message indiquant que le modèle a été entraîné et sauvegardé
print("Le modèle a été entraîné et sauvegardé avec succès sous 'candidate_model.pkl'.")
