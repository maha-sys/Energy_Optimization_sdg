from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import os
import tensorflow as tf
from optimization_engine import EnergyOptimizer

app = Flask(__name__)
CORS(app)

# Paths
MODEL_PATH = '../model/energy_predictor.h5'
UPLOAD_FOLDER = '../uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize optimizer
optimizer = EnergyOptimizer()

# Load model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully")
except Exception as e:
    model = None
    print("Model not found or failed to load:", e)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None
    })


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files allowed'}), 400

    try:
        filepath = os.path.join(UPLOAD_FOLDER, 'user_energy_data.csv')
        file.save(filepath)

        df = pd.read_csv(filepath)

        # ✅ MATCHES YOUR DATASET
        required_columns = [
            'Month',
            'Units_kWh',
            'Avg_Daily_kWh',
            'Peak_Usage_Hours',
            'Cost'
        ]

        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            return jsonify({
                'error': f'Missing columns: {missing}',
                'available_columns': list(df.columns)
            }), 400

        stats = {
            'total_records': len(df),
            'avg_units': float(df['Units_kWh'].mean()),
            'total_units': float(df['Units_kWh'].sum()),
            'avg_cost': float(df['Cost'].mean())
        }

        return jsonify({
            'message': 'File uploaded successfully',
            'statistics': stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict', methods=['POST'])
def predict_usage():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        data = request.json

        # ✅ MATCHES TRAINED MODEL INPUT
        features = pd.DataFrame([{
            'Month': data['Month'],
            'Avg_Daily_KWh': data['Avg_Daily_KWh'],
            'Peak_Usage_Hours': data['Peak_Usage_Hours']
        }])

        prediction = model.predict(features)[0][0]

        return jsonify({
            'predicted_units_kwh': float(prediction),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/optimize', methods=['POST'])
def optimize_energy():
    try:
        filepath = os.path.join(UPLOAD_FOLDER, 'user_energy_data.csv')
        if not os.path.exists(filepath):
            return jsonify({'error': 'Upload data first'}), 400

        df = pd.read_csv(filepath)
        data = request.json

        target_reduction = data.get('target_reduction', 0.15)
        time_horizon = data.get('time_horizon', 30)

        recommendations = optimizer.optimize(
            df,
            target_reduction,
            time_horizon
        )

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analytics', methods=['GET'])
def get_analytics():
    try:
        filepath = os.path.join(UPLOAD_FOLDER, 'user_energy_data.csv')
        if not os.path.exists(filepath):
            return jsonify({'error': 'No data uploaded'}), 400

        df = pd.read_csv(filepath)

        analytics = {
            'monthly_avg_units': df.groupby('Month')['Units_kWh'].mean().to_dict(),
            'peak_usage_impact': df.groupby('Peak_Usage_Hours')['Units_kWh'].mean().to_dict(),
            'total_units': float(df['Units_kWh'].sum()),
            'total_cost': float(df['Cost'].sum()),
            'trend': calculate_trend(df)
        }

        return jsonify(analytics)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def calculate_trend(df):
    if len(df) < 2:
        return 'insufficient_data'

    df = df.reset_index()
    corr = np.corrcoef(df.index, df['Units_kWh'])[0, 1]

    if corr > 0.1:
        return 'increasing'
    elif corr < -0.1:
        return 'decreasing'
    return 'stable'


@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    try:
        filepath = os.path.join(UPLOAD_FOLDER, 'user_energy_data.csv')
        if not os.path.exists(filepath):
            return jsonify({'error': 'No data uploaded'}), 400

        df = pd.read_csv(filepath)
        recommendations = optimizer.generate_recommendations(df)

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
