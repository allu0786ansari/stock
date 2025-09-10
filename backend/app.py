from flask import Flask, jsonify, request, send_file
from io import BytesIO
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from flask_cors import CORS
import json
import traceback
import plotly
import requests
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import os
from routes.stock_routes import stock_routes
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://aistockanalyzer.onrender.com"]}})

@app.route('/')
def home():
    return "Welcome to the Stock Analysis API"


@app.route('/api/export/history', methods=['GET'])
def export_stock_history():
    ticker = request.args.get('ticker')
    period = request.args.get('period', '1mo')
    filetype = request.args.get('type', 'csv')

    if not ticker:
        return jsonify({'error': 'Ticker is required'}), 400

    data = fetch_stock_data(ticker, period)
    if isinstance(data, str):
        return jsonify({'error': data}), 500

    data = clean_stock_data(data)

    file_io = BytesIO()
    if filetype == 'excel':
        data.to_excel(file_io, index=False, engine='openpyxl')
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ext = 'xlsx'
    else:
        data.to_csv(file_io, index=False)
        mimetype = 'text/csv'
        ext = 'csv'

    file_io.seek(0)
    return send_file(file_io, mimetype=mimetype, as_attachment=True, download_name=f"{ticker}_history.{ext}")


@app.route('/api/export/prediction', methods=['GET'])
def export_predictions():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({'error': 'Ticker is required'}), 400

    try:
        data = yf.download(ticker, period='5y')
        if data.empty:
            return jsonify({'error': 'No data found'}), 404

        data['Date'] = data.index
        data['Date'] = data['Date'].map(datetime.toordinal)
        X = data['Date'].values.reshape(-1, 1)
        y = data['Close'].values.flatten()

        model = LinearRegression()
        model.fit(X, y)

        future_dates = [datetime.now() + timedelta(days=i*365) for i in range(1, 11)]
        predictions = model.predict(np.array([d.toordinal() for d in future_dates]).reshape(-1, 1))

        df_pred = pd.DataFrame({
            'Date': [d.strftime('%Y-%m-%d') for d in future_dates],
            'Predicted Price': [round(float(p), 2) for p in predictions]
        })

        file_io = BytesIO()
        filetype = request.args.get('type', 'csv')
        if filetype == 'excel':
            df_pred.to_excel(file_io, index=False, engine='openpyxl')
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ext = 'xlsx'
        else:
            df_pred.to_csv(file_io, index=False)
            mimetype = 'text/csv'
            ext = 'csv'

        file_io.seek(0)
        return send_file(file_io, mimetype=mimetype, as_attachment=True, download_name=f"{ticker}_prediction.{ext}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stock/predict', methods=['GET', 'OPTIONS'])
def predict_stock():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        data = yf.download(ticker, period='5y')
        if data.empty:
            return jsonify({'error': 'No data found for the given ticker'}), 404

        data['Date'] = data.index
        data['Date'] = data['Date'].map(datetime.toordinal)
        X = data['Date'].values.reshape(-1, 1)
        y = data['Close'].values.flatten()

        model = LinearRegression()
        model.fit(X, y)

        future_dates = [datetime.now() + timedelta(days=i*365) for i in range(1, 11)]
        predictions = model.predict(np.array([d.toordinal() for d in future_dates]).reshape(-1, 1))

        stocks = [10, 20, 50, 100]
        returns = []
        current_price = float(y[-1])

        for stock in stocks:
            returns.append({
                'stocks_bought': stock,
                'current_price': round(current_price * stock, 2),
                'after_1_year': round(float(predictions[0]) * stock, 0),
                'after_5_years': round(float(predictions[4]) * stock, 0),
                'after_10_years': round(float(predictions[9]) * stock, 0)
            })

        return jsonify({
            "future_predictions": [round(float(p), 2) for p in predictions],
            "returns": returns
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


app.register_blueprint(stock_routes, url_prefix="/api")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
