import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MySystem.settings')
django.setup()

import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from core.models import SoilData  

soil_data = SoilData.objects.all().values('nitrogen', 'phosphorus', 'potassium', 'ph', 'rainfall', 'temperature', 'recommended_crop')
df = pd.DataFrame(soil_data)

features = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'rainfall', 'temperature']
X = df[features]
y = df['recommended_crop']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=150, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

with open('crop_model.pkl', 'wb') as file:
    pickle.dump(model, file)

print("✅ Model training completed and saved as 'crop_model.pkl'")
