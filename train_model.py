import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib


# Sample student data
data = {
    "cgpa": [
        6.2, 6.5, 6.8, 7.0, 7.2,
        7.4, 7.5, 7.7, 7.8, 8.0,
        8.1, 8.2, 8.4, 8.5, 8.7,
        8.8, 9.0, 9.1, 9.2, 9.4
    ],

    "internships": [
        0, 0, 1, 0, 1,
        1, 1, 1, 2, 1,
        2, 2, 2, 2, 2,
        3, 2, 3, 3, 3
    ],

    "projects": [
        1, 1, 1, 2, 2,
        2, 3, 2, 3, 3,
        3, 3, 4, 4, 4,
        4, 4, 5, 5, 5
    ],

    "aptitude_score": [
        45, 50, 52, 55, 58,
        60, 62, 65, 66, 68,
        70, 72, 75, 76, 78,
        80, 82, 85, 88, 90
    ],

    "communication_score": [
        45, 48, 50, 52, 55,
        58, 60, 62, 64, 65,
        68, 70, 72, 75, 76,
        78, 80, 82, 85, 88
    ],

    "placed": [
        0, 0, 0, 0, 0,
        0, 0, 0, 0, 0,
        1, 1, 1, 1, 1,
        1, 1, 1, 1, 1
    ]
}

df = pd.DataFrame(data)

# Features
X = df[
    [
        "cgpa",
        "internships",
        "projects",
        "aptitude_score",
        "communication_score"
    ]
]

# Target
y = df["placed"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Create Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train model
model.fit(X_train, y_train)

# Test model
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("Model trained successfully!")
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save model
joblib.dump(model, "placement_model.pkl")

print("Model saved as placement_model.pkl")