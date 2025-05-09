import httpx
import asyncio

class OpenMeteoWeatherModule:
    async def get_weather_and_air_forecast(self, latitude: float, longitude: float):
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&forecast_days=7&timezone=Asia%2FSingapore"
        air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={latitude}&longitude={longitude}&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,sulphur_dioxide&forecast_days=7&timezone=Asia%2FSingapore"

        async with httpx.AsyncClient() as client:
            weather_response, air_response = await asyncio.gather(
                client.get(weather_url), client.get(air_url)
            )

            weather_json = await weather_response.json()
            air_json = await air_response.json()

        if "hourly" not in weather_json or "hourly" not in air_json:
            raise ValueError("Incomplete forecast data")

        weather = weather_json["hourly"]
        air = air_json["hourly"]

        combined = [
            {
                "date": t.split('T')[0],
                "temperature_2m": weather["temperature_2m"][idx],
                "relative_humidity_2m": weather["relative_humidity_2m"][idx],
                "precipitation": weather["precipitation"][idx],
                "wind_speed_10m": weather["wind_speed_10m"][idx],
                "pm10": air["pm10"][idx],
                "pm2_5": air["pm2_5"][idx],
                "carbon_monoxide": air["carbon_monoxide"][idx],
                "nitrogen_dioxide": air["nitrogen_dioxide"][idx],
                "ozone": air["ozone"][idx],
                "sulphur_dioxide": air["sulphur_dioxide"][idx]
            }
            for idx, t in enumerate(weather["time"])
        ]

        daily_agg = {}
        for entry in combined:
            if entry["date"] not in daily_agg:
                daily_agg[entry["date"]] = {key: 0 for key in entry if key != "date"}
                daily_agg[entry["date"]]["count"] = 0
            for key, val in entry.items():
                if key != "date":
                    daily_agg[entry["date"]][key] += val
            daily_agg[entry["date"]]["count"] += 1

        return [
            {
                "date": date,
                "temperature_2m": vals["temperature_2m"] / vals["count"],
                "relative_humidity_2m": vals["relative_humidity_2m"] / vals["count"],
                "precipitation": vals["precipitation"],
                "wind_speed_10m": vals["wind_speed_10m"] / vals["count"],
                "pm10": vals["pm10"] / vals["count"],
                "pm2_5": vals["pm2_5"] / vals["count"],
                "carbon_monoxide": vals["carbon_monoxide"] / vals["count"],
                "nitrogen_dioxide": vals["nitrogen_dioxide"] / vals["count"],
                "ozone": vals["ozone"] / vals["count"],
                "sulphur_dioxide": vals["sulphur_dioxide"] / vals["count"]
            }
            for date, vals in daily_agg.items()
        ]
