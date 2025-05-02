const axios = require('axios');

/**
 * Fetches 7-day weather and air quality forecast using Open-Meteo APIs.
 * Aggregates hourly data into daily means (except precipitation = sum).
 * @param {number} latitude 
 * @param {number} longitude 
 * @returns {Promise<Array<Object>>}
 */
async function getWeatherAndAirForecast(latitude, longitude) {
    try {
        const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&forecast_days=7&timezone=Asia%2FSingapore`;
        const airQualityUrl = `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=${latitude}&longitude=${longitude}&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,sulphur_dioxide&forecast_days=7&timezone=Asia%2FSingapore`;

        const [weatherResponse, airResponse] = await Promise.all([
            axios.get(weatherUrl),
            axios.get(airQualityUrl)
        ]);

        const weatherData = weatherResponse.data.hourly;
        const airData = airResponse.data.hourly;

        if (!weatherData || !airData) {
            throw new Error('Incomplete forecast data received');
        }

        // Combine both hourly datasets
        const combined = weatherData.time.map((datetime, idx) => ({
            date: datetime.split('T')[0],
            temperature_2m: weatherData.temperature_2m[idx],
            relative_humidity_2m: weatherData.relative_humidity_2m[idx],
            precipitation: weatherData.precipitation[idx],
            windspeed_10m: weatherData.wind_speed_10m[idx],
            pm10: airData.pm10[idx],
            pm2_5: airData.pm2_5[idx],
            carbon_monoxide: airData.carbon_monoxide[idx],
            nitrogen_dioxide: airData.nitrogen_dioxide[idx],
            ozone: airData.ozone[idx],
            sulphur_dioxide: airData.sulphur_dioxide[idx]
        }));

        // Aggregate by date
        const grouped = {};

        for (const entry of combined) {
            if (!grouped[entry.date]) {
                grouped[entry.date] = {
                    count: 0,
                    sum_temperature_2m: 0,
                    sum_relative_humidity_2m: 0,
                    sum_precipitation: 0,
                    sum_windspeed_10m: 0,
                    sum_pm10: 0,
                    sum_pm2_5: 0,
                    sum_carbon_monoxide: 0,
                    sum_nitrogen_dioxide: 0,
                    sum_ozone: 0,
                    sum_sulphur_dioxide: 0
                };
            }

            grouped[entry.date].count += 1;
            grouped[entry.date].sum_temperature_2m += entry.temperature_2m;
            grouped[entry.date].sum_relative_humidity_2m += entry.relative_humidity_2m;
            grouped[entry.date].sum_precipitation += entry.precipitation;
            grouped[entry.date].sum_windspeed_10m += entry.windspeed_10m;
            grouped[entry.date].sum_pm10 += entry.pm10;
            grouped[entry.date].sum_pm2_5 += entry.pm2_5;
            grouped[entry.date].sum_carbon_monoxide += entry.carbon_monoxide;
            grouped[entry.date].sum_nitrogen_dioxide += entry.nitrogen_dioxide;
            grouped[entry.date].sum_ozone += entry.ozone;
            grouped[entry.date].sum_sulphur_dioxide += entry.sulphur_dioxide;
        }

        const dailyAggregated = Object.entries(grouped).map(([date, values]) => ({
            date,
            temperature_2m: values.sum_temperature_2m / values.count,
            relative_humidity_2m: values.sum_relative_humidity_2m / values.count,
            precipitation: values.sum_precipitation, // SUM not mean
            windspeed_10m: values.sum_windspeed_10m / values.count,
            pm10: values.sum_pm10 / values.count,
            pm2_5: values.sum_pm2_5 / values.count,
            carbon_monoxide: values.sum_carbon_monoxide / values.count,
            nitrogen_dioxide: values.sum_nitrogen_dioxide / values.count,
            ozone: values.sum_ozone / values.count,
            sulphur_dioxide: values.sum_sulphur_dioxide / values.count
        }));

        return dailyAggregated;
    } catch (error) {
        console.error('Failed to fetch weather and air forecast:', error.message);
        throw new Error('Weather and air API failure');
    }
}

module.exports = {
    getWeatherAndAirForecast
};
