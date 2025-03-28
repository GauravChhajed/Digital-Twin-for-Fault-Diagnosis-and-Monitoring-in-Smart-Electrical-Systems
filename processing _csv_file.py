import pandas as pd

# Load the dataset
file_path = r"C:/Users/hp/OneDrive/Desktop/mini_project/SENSOR_DATA01.csv"
df = pd.read_csv(file_path)

# Convert timestamp to datetime format
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')

# Fill missing temperature values safely
df['Temperature'] = df['Temperature'].fillna(df['Temperature'].mean())

# Create a Power feature (P = V * I)
df['Power'] = df['Voltage'] * df['Current']

# Define fault conditions
def classify_fault(row):
    if row['Voltage'] > 240:
        return "Overvoltage"
    elif row['Current'] > 0.415:
        return "Overcurrent"
    elif row['Voltage'] < 180:
        return "Low Voltage"
    elif row['Temperature'] > 42:
        return "Overheating"
    elif row['Current'] < 0.05:  
        return "Off Condition"
    else:
        return "Normal Condition"

# Apply the function to classify each row
df['Fault Condition'] = df.apply(classify_fault, axis=1)

# Save the processed data to a valid Windows path
processed_file_path = r"C:/Users/hp/OneDrive/Desktop/mini_project/Processed_SENSOR_DATA.csv"
df.to_csv(processed_file_path, index=False)

print(f"Processed data saved to: {processed_file_path}")
df.head()
