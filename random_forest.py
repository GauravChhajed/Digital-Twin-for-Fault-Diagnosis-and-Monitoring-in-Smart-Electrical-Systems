import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Load the dataset
file_path = r"C:/Users/hp/OneDrive/Desktop/mini_project/Processed_SENSOR_DATA.csv"  # Update path
df = pd.read_csv(file_path)

# Drop timestamp (not needed for ML)
if 'Timestamp' in df.columns:
    df.drop(columns=['Timestamp'], inplace=True)

# Handle missing values (optional, if dataset has NaN values)
df.dropna(inplace=True)

# Encode categorical target variable (Fault Condition)
label_encoder = LabelEncoder()
df['Fault Condition'] = label_encoder.fit_transform(df['Fault Condition'])

# Split data into features (X) and target (y)
X = df.drop(columns=['Fault Condition'])
y = df['Fault Condition']

# Save feature names for consistency during prediction
feature_names = X.columns.to_list()
joblib.dump(feature_names, "feature_names.pkl")

# Split dataset into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)

print(f"Model Accuracy: {accuracy * 100:.2f}%")
print("Classification Report:\n", report)

# Save the model and label encoder
joblib.dump(model, "random_forest_fault_detection.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

print("Model and label encoder saved successfully.")
