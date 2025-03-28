import serial
import joblib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import pandas as pd

# Load trained models
try:
    model = joblib.load("random_forest_fault_detection.pkl")
    health_index_model = joblib.load("health_index_model.pkl")  # Load HI model
    label_encoder = joblib.load("label_encoder.pkl")
    feature_names = joblib.load("feature_names.pkl")
except FileNotFoundError:
    print("Error: Model, Label Encoder, or Feature Names file not found.")
    exit()
except Exception as e:
    print(f"Error loading model or encoder: {e}")
    exit()

# Set up serial communication
SERIAL_PORT = "COM4"  # Change based on your setup
BAUD_RATE = 9600
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

print("Listening for sensor data from Arduino...")

# Data storage for plotting
BUFFER_SIZE = 100
current_data = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
voltage_data = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
temperature_data = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
power_data = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
health_index_data = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
time_data = deque(range(BUFFER_SIZE), maxlen=BUFFER_SIZE)

# Create figure for plotting
fig, axs = plt.subplots(5, 1, figsize=(8, 12))
plot_titles = ["Current (A)", "Voltage (V)", "Temperature (°C)", "Power (W)", "Health Index (%)"]
for i, ax in enumerate(axs):
    ax.set_title(plot_titles[i])

lines = [ax.plot(time_data, [0] * BUFFER_SIZE)[0] for ax in axs]

def update(frame):
    try:
        # Read data from Arduino
        serial_data = ser.readline().decode("utf-8").strip()
        if serial_data:
            print(f"Received: {serial_data}")

            try:
                values = serial_data.split(',')
                if len(values) < 3:
                    print("Error: Incomplete data received, skipping...")
                    return lines

                # Extract values and compute power
                current = float(values[0])
                voltage = float(values[1])
                temperature = float(values[2])
                power = voltage * current  # Compute power

                # Prepare input data
                input_data = np.array([[current, voltage, temperature, power]])
                input_df = pd.DataFrame(input_data, columns=feature_names)

                # Predict fault condition
                prediction = model.predict(input_df)
                predicted_label = label_encoder.inverse_transform(prediction)

                # Predict Health Index
                health_index = health_index_model.predict(input_data)[0]
                health_status = "Healthy ✅" if health_index > 80 else "Moderate Risk ⚠️" if health_index >= 50 else "Faulty ❌"

                print(f"Fault Condition: {predicted_label[0]}")
                print(f"Health Index: {health_index:.2f}% - Status: {health_status}\n")

                # Update data for plotting
                current_data.append(current)
                voltage_data.append(voltage)
                temperature_data.append(temperature)
                power_data.append(power)
                health_index_data.append(health_index)
                time_data.append(time_data[-1] + 1)

                # Update plot lines
                for i, data in enumerate([current_data, voltage_data, temperature_data, power_data, health_index_data]):
                    lines[i].set_data(time_data, data)
                    axs[i].relim()
                    axs[i].autoscale_view()

                return lines

            except (ValueError, IndexError) as e:
                print(f"Error parsing numerical data: {e}")
                return lines

    except Exception as e:
        print(f"Error: {e}")
        return lines

ani = animation.FuncAnimation(fig, update, blit=False, interval=1000)
plt.show(block=False)

try:
    plt.pause(100000)
except KeyboardInterrupt:
    print("Plot closed")

ser.close()
