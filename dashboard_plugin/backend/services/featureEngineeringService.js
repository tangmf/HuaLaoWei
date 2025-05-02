/**
 * Prepares a feature vector for forecasting from all the collected data.
 * @param {Object} weatherFeatures - Object with arrays of weather and air hourly data
 * @param {Object} poiFeatures - Object with density and proximity
 * @param {Object} socioeconomicFeatures - Object with averageAge, totalPopulation, averageIncome, totalHouseholds
 * @param {Object} temporalFeatures - Object with temporal features like day_of_week, is_weekend, month
 * @returns {Array<Object>} Array of feature objects for each future day
 */
function prepareForecastFeatures(weatherFeatures, poiFeatures, socioeconomicFeatures, temporalFeatures) {
    const features = [];

    const numDays = 7;
    for (let i = 0; i < numDays; i++) {
        features.push({
            // Weather
            temperature: weatherFeatures[i].temperature_2m ?? null,
            humidity: weatherFeatures[i].relative_humidity_2m ?? null,
            precipitation: weatherFeatures[i].precipitation ?? null,
            windspeed: weatherFeatures[i].wind_speed_10m ?? null,

            // Air Quality
            pm10: weatherFeatures[i].pm10 ?? null,
            pm2_5: weatherFeatures[i].pm2_5 ?? null,
            carbon_monoxide: weatherFeatures[i].carbon_monoxide ?? null,
            nitrogen_dioxide: weatherFeatures[i].nitrogen_dioxide ?? null,
            ozone: weatherFeatures[i].ozone ?? null,
            sulphur_dioxide: weatherFeatures[i].sulphur_dioxide ?? null,

            // POI Features (static per request)
            // poi_density: poiFeatures.density ?? 0,
            // poi_proximity: poiFeatures.proximity ?? 0,

            // Socioeconomic Features (static per request)
            // average_age: socioeconomicFeatures.averageAge ?? 0,
            // total_population: socioeconomicFeatures.totalPopulation ?? 0,
            // average_income: socioeconomicFeatures.averageIncome ?? 0,
            // total_households: socioeconomicFeatures.totalHouseholds ?? 0,

            // (Latent) Temporal Features
            day_of_week: temporalFeatures[i].day_of_week ?? null,
            is_weekend: temporalFeatures[i].is_weekend ?? null,
            month: temporalFeatures[i].month ?? null
        });
    }
    return features;
}

module.exports = {
    prepareForecastFeatures
};