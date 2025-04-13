# Digital Twin for Fault Diagnosis and Monitoring in Smart Electrical Systems

## 📌 Project Overview
This project implements a **Digital Twin** for **fault diagnosis and real-time monitoring** of smart electrical systems. The system uses **machine learning models** to predict faults based on sensor data collected from an **Arduino Uno**. The project aims to improve reliability and reduce downtime in electrical systems by enabling early fault detection.

## 🔧 Features
- **Real-time Sensor Data Processing**
- **Fault Prediction using Machine Learning**
- **Health Index Calculation for System Monitoring**
- **Digital Twin Representation for Visualization**

## 🛠️ Tech Stack
- **Hardware:** Arduino Uno, Sensors (Voltage, Current, Temperature, etc.)
- **Software:** Python, Arduino IDE
- **Libraries:**
  - `pandas`, `numpy`, `sklearn`, `joblib`
  - `matplotlib` (for visualization)
  - `flask` (if a web-based dashboard is added)

## 📂 Project Structure
```
├── app.py                         # Flask app (if applicable)
├── random_forest.py               # Machine learning training script
├── Real-Time Fault Prediction.py   # Script for real-time fault detection
├── processing_csv_file.py          # Sensor data processing script
├── health_index_model.py           # Health index computation
├── mini_project.ino                # Arduino code for data collection
├── sample_sensor_data.csv          # Sample dataset for training/testing
├── models/                         # Folder for trained models (ignored in Git)
│   ├── random_forest_fault_detection.pkl
│   ├── health_index_model.pkl
│   ├── label_encoder.pkl
│   ├── feature_names.pkl
├── docs/                           # Project documentation
│   ├── Project_Proposal.docx
├── README.md                       # Project documentation (this file)
├── requirements.txt                # Required Python libraries
├── .gitignore                       # Ignore large files like .pkl and dataset
```

## 🚀 Installation & Setup
### 1️⃣ Clone the Repository
```sh
git clone https://GauravChhajed/Digital-Twin-for-Fault-Diagnosis-and-Monitoring-in-Smart-Electrical-Systems.git
cd Digital-Twin-for-Fault-Diagnosis-and-Monitoring-in-Smart-Electrical-Systems
```

### 2️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 3️⃣ Upload Code to Arduino
- Open **`mini_project.ino`** in the **Arduino IDE**.
- Upload it to the Arduino board.

### 4️⃣ Train the Model (Optional)
If you want to retrain the model:
```sh
python random_forest.py
```

### 5️⃣ Run Real-time Fault Detection
```sh
python Real-Time Fault Prediction.py
```

## 📊 Dataset
The dataset consists of:
- **Sensor Readings:** Voltage, Current, Temperature, etc.
- **Labels:** Normal, Faulty Conditions

⚠ **Note:** Full dataset is not included in the repo due to size constraints. A sample dataset is provided.

## 📈 Results & Analysis
- Fault detection accuracy: **~97%** (based on test data)
- Early warning system reduces downtime in electrical systems

## 🤝 Contribution
Want to improve this project? Follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature-name`)
5. Open a Pull Request

## 📧 Contact
For any queries, reach out at **gauravc3082004@gmail.com** or open an issue in the repo.
