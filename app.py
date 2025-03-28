import serial
import joblib
import numpy as np
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import threading
import time
from collections import deque
from datetime import datetime

# Load trained models
try:
    model = joblib.load("random_forest_fault_detection.pkl")
    health_index_model = joblib.load("health_index_model.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    feature_names = joblib.load("feature_names.pkl")
except FileNotFoundError:
    print("Error: Model, Label Encoder, or Feature Names file not found.")
    exit()
except Exception as e:
    print(f"Error loading model or encoder: {e}")
    exit()

# Serial Communication Setup
SERIAL_PORT = "COM4"  # Adjust based on your system
BAUD_RATE = 9600
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

print("Listening for sensor data from Arduino...")

# Data Storage for Real-Time Plotting
BUFFER_SIZE = 100
time_data = deque(maxlen=BUFFER_SIZE)
current_data = deque(maxlen=BUFFER_SIZE)
voltage_data = deque(maxlen=BUFFER_SIZE)
temperature_data = deque(maxlen=BUFFER_SIZE)
power_data = deque(maxlen=BUFFER_SIZE)
health_index_data = deque(maxlen=BUFFER_SIZE)
fault_predictions = deque(maxlen=BUFFER_SIZE)

# Initialize Dash Web App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

def get_fault_color(fault):
    fault_colors = {
        "No Fault": "green",
        "Overcurrent": "red",
        "Overvoltage": "orange",
        "Overtemperature": "yellow",
        "Undervoltage": "blue",
        "Unknown": "white"
    }
    return fault_colors.get(fault, "white")

app.layout = dbc.Container([
    html.H1("Digital Twin for Fault Diagnosis and Monitoring", className="text-center mb-4 text-white"),
    
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Fault Condition", className="text-white"),
            dbc.CardBody(html.H3(id="fault-condition", className="text-center"))
        ]), width=6),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("Health Index", className="text-white"),
            dbc.CardBody(html.H3(id="health-index", className="text-center"))
        ], id="health-card"), width=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id="sensor-plot", style={"height": "600px"})),
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id="multi-feature-3d-plot", style={"height": "900px"})),
    ]),
    
    dcc.Interval(id="interval-update", interval=1000, n_intervals=0)
], fluid=True, className="bg-dark text-white")

# Function to Read Data from Serial and Predict
def read_sensor_data():
    while True:
        try:
            serial_data = ser.readline().decode("utf-8").strip()
            if serial_data:
                values = serial_data.split(',')
                if len(values) < 3:
                    continue  # Skip incomplete data

                current = float(values[0])
                voltage = float(values[1])
                temperature = float(values[2])
                power = voltage * current  # Compute power
                
                input_data = np.array([[current, voltage, temperature, power]])
                input_df = pd.DataFrame(input_data, columns=feature_names)

                prediction = model.predict(input_df)
                predicted_label = label_encoder.inverse_transform(prediction)[0]

                health_index = health_index_model.predict(input_data)[0]
                health_status = "Healthy" if health_index > 80 else "Moderate Risk" if health_index >= 50 else "Faulty"

                time_data.append(datetime.now().strftime("%H:%M:%S"))
                current_data.append(current)
                voltage_data.append(voltage)
                temperature_data.append(temperature)
                power_data.append(power)
                health_index_data.append(health_index)
                fault_predictions.append(predicted_label)

        except Exception as e:
            print(f"Error: {e}")

sensor_thread = threading.Thread(target=read_sensor_data, daemon=True)
sensor_thread.start()

@app.callback(
    [Output("fault-condition", "children"),
     Output("fault-condition", "style"),
     Output("health-index", "children"),
     Output("health-card", "color")],
    [Input("interval-update", "n_intervals")]
)
def update_predictions(n):
    if not fault_predictions:
        return "Waiting for data...", {"color": "white"}, "Waiting for data...", "secondary"
    
    fault = fault_predictions[-1]
    fault_color = get_fault_color(fault)
    
    health_index = health_index_data[-1]
    health_card_color = "success" if health_index > 80 else "warning" if health_index >= 50 else "danger"
    
    return f"{fault}", {"color": fault_color}, f"{health_index:.2f}%", health_card_color

@app.callback(
    Output("sensor-plot", "figure"),
    [Input("interval-update", "n_intervals")]
)
def update_sensor_plot(n):
    if not time_data:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(time_data), y=list(current_data), mode="lines", name="Current (A)"))
    fig.add_trace(go.Scatter(x=list(time_data), y=list(voltage_data), mode="lines", name="Voltage (V)"))
    fig.add_trace(go.Scatter(x=list(time_data), y=list(temperature_data), mode="lines", name="Temperature (°C)"))
    fig.add_trace(go.Scatter(x=list(time_data), y=list(power_data), mode="lines", name="Power (W)"))
    fig.add_trace(go.Scatter(x=list(time_data), y=list(health_index_data), mode="lines", name="Health Index (%)"))

    fig.update_layout(title="Sensor Data Over Time", xaxis_title="Time", yaxis_title="Value", template="plotly_dark")
    return fig

@app.callback(
    Output("multi-feature-3d-plot", "figure"),
    [Input("interval-update", "n_intervals")]
)
def update_3d_plot(n):
    if not current_data:
        return go.Figure()
    
    fig = go.Figure(data=[go.Scatter3d(
        x=list(current_data),
        y=list(voltage_data),
        z=list(temperature_data),
        mode="markers",
        marker=dict(size=5, color=list(health_index_data), colorscale="Viridis", opacity=0.8)
    )])
    
    fig.update_layout(
        title="Multi-Dimensional Sensor Data",
        scene=dict(
            xaxis_title="Current (A)",
            yaxis_title="Voltage (V)",
            zaxis_title="Temperature (°C)"
        ),
        template="plotly_dark"
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
