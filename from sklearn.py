from sklearn.tree import DecisionTreeClassifier
import pandas as pd

# Sample data
data = {
    'soil_ph': [6.5, 7.0, 5.5, 6.0, 7.5, 5.0],
    'rainfall': [120, 150, 100, 110, 160, 90],
    'crop': ['maize', 'wheat', 'rice', 'barley', 'sorghum', 'millet']
}

# Create DataFrame
df = pd.DataFrame(data)

# Features and target
X = df[['soil_ph', 'rainfall']]
y = df['crop']

# Initialize and train the model
model = DecisionTreeClassifier()
model.fit(X, y)

# Function to recommend crop
def recommend_crop(soil_ph, rainfall):
    prediction = model.predict([[soil_ph, rainfall]])
    return prediction[0]

# Example usage
soil_ph = 6.8
rainfall = 130
recommended_crop = recommend_crop(soil_ph, rainfall)
print(f"Recommended crop: {recommended_crop}")