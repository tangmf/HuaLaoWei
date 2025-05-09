class FeatureEngineeringService:
    def prepare_forecast_features(self, weather_features, poi_features, socioeconomic_features, temporal_features):
        features = []
        num_days = len(weather_features)

        for i in range(num_days):
            day = {
                # Weather Features
                "temperature": weather_features[i].get("temperature_2m"),
                "humidity": weather_features[i].get("relative_humidity_2m"),
                "precipitation": weather_features[i].get("precipitation"),
                "windspeed": weather_features[i].get("wind_speed_10m"),

                # Air Quality Features
                "pm10": weather_features[i].get("pm10"),
                "pm2_5": weather_features[i].get("pm2_5"),
                "carbon_monoxide": weather_features[i].get("carbon_monoxide"),
                "nitrogen_dioxide": weather_features[i].get("nitrogen_dioxide"),
                "ozone": weather_features[i].get("ozone"),
                "sulphur_dioxide": weather_features[i].get("sulphur_dioxide"),

                # POI Features (constant across all days)
                **poi_features,

                # Socioeconomic Features (constant across all days)
                **socioeconomic_features,

                # Temporal Features (varies day by day)
                "day_of_week": temporal_features[i]["day_of_week"],
                "is_weekend": temporal_features[i]["is_weekend"],
                "month": temporal_features[i]["month"]
            }
            features.append(day)

        return features
