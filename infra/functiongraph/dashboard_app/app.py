# app.py (Flask Entry Point)
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from features.build_features import build_input_df
from model.predictor import load_model, forecast_issue_counts

app = Flask(__name__)
tft = load_model()

@app.route("/api/forecast", methods=["POST"])
def forecast():
    data = request.get_json()
    subzone = data.get("subzone")
    issue_type = data.get("issue_type")
    lat = data.get("lat")
    lon = data.get("lon")
    planning_area = data.get("planning_area")

    df = build_input_df(lat, lon, planning_area, issue_type)
    predictions = forecast_issue_counts(tft, df)

    results = [
        {"date": (datetime.utcnow().date() + timedelta(days=i)).isoformat(), "count": int(p)}
        for i, p in enumerate(predictions)
    ]

    return jsonify({
        "subzone": subzone,
        "issue_type": issue_type,
        "forecast": results
    })

# For Huawei FunctionGraph
def handler(environ, start_response):
    return app.wsgi_app(environ, start_response)

if __name__ == "__main__":
    app.run(debug=True)