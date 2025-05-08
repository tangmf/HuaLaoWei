from datetime import datetime, timedelta

class TemporalFeaturesService:
    def generate_temporal_features(self, start_date: datetime = None, num_days: int = 7):
        if start_date is None:
            start_date = datetime.now()

        features = []
        for i in range(num_days):
            date = start_date + timedelta(days=i)
            features.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_of_week": date.weekday(),   # 0 = Monday, 6 = Sunday
                "is_weekend": date.weekday() in [5, 6],
                "month": date.month
            })
        return features
