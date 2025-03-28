import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Load dataset
file_path = "C:/Users/hp/OneDrive/Desktop/mini_project/Processed_SENSOR_DATA.csv"  # Update with correct path
df = pd.read_csv(file_path)

# Compute Health Index (HI) in Percentage
V_avg = df["Voltage"].mean()
I_avg = df["Current"].mean()
T_avg = df["Temperature"].mean()

max_deviation = max(df["Voltage"].max() - V_avg, df["Current"].max() - I_avg, df["Temperature"].max() - T_avg)

df["Health_Index"] = 100 - ((abs(df["Voltage"] - V_avg) + abs(df["Current"] - I_avg) + abs(df["Temperature"] - T_avg)) / max_deviation) * 100

# Ensure values are within 0-100%
df["Health_Index"] = df["Health_Index"].clip(0, 100)

# Define features and target
features = ["Current", "Voltage", "Temperature", "Power"]
target = "Health_Index"

X = df[features]
y = df[target]

# Train-test split (80-20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluate model
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model Evaluation:\nMAE: {mae:.2f}, R² Score: {r2:.2f}")

# Save Model
joblib.dump(model, "health_index_model.pkl")
print("Health Index model saved as 'health_index_model.pkl'")
