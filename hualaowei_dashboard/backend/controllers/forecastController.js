const subzoneService = require('../services/subzoneService');
const featureEngineeringService = require('../services/featureEngineeringService');
const oneMapSocioeconomicService = require('../services/oneMapSocioeconomicService');
const osmService = require('../services/osmService');
const openMeteoWeatherService = require('../services/openMeteoWeatherService');
const modelInferenceService = require('../services/modelInferenceService');
const temporalFeaturesService = require('../services/temporalFeaturesService');

/**
 * Controller: Forecast Issue Counts for next 7 days
 * Request Query Parameters: subzoneName, issueTypeName
 */
async function forecastIssues(req, res) {
    try {
        const {
            subzoneName,
            issueTypeName
        } = req.query;

        if (!subzoneName || !issueTypeName) {
            return res.status(400).json({
                error: 'Missing subzoneName or issueTypeName in request'
            });
        }

        // Retrieve subzone information
        const {
            latitude,
            longitude
        } = await subzoneService.getSubzoneCentroid(subzoneName);

        const planningAreaName = await subzoneService.getPlanningAreaBySubzone(subzoneName);

        if (!latitude || !longitude || !planningAreaName) {
            return res.status(404).json({
                error: 'Subzone not found'
            });
        }

        // Fetch 7-day Weather Forecast (temperature, humidity, windspeed, precipitation) and Air Quality Forecast (pm10, pm2_5, etc.)
        const weatherAndAirForecast = await openMeteoWeatherService.getWeatherAndAirForecast(latitude, longitude);

        // Fetch POIs near Subzone and compute density and proximity
        const geospatialFeatures = await osmService.getPOIFeatures(latitude, longitude);

        // Fetch Socioeconomic Data from OneMap (Age group and Household Income)
        const socioeconomicFeatures = await oneMapSocioeconomicService.getSocioeconomicFeatures(planningAreaName);

        // Generate Temporal Features (Day of Week, Month, etc.)
        const temporalFeatures = temporalFeaturesService.generateTemporalFeatures(new Date(), 7);

        // Assemble Feature Matrix for Model Input
        const featureMatrix = featureEngineeringService.prepareForecastFeatures(
            weatherAndAirForecast,
            geospatialFeatures,
            socioeconomicFeatures,
            temporalFeatures
        );

        // Run Model Inference (Load Model and Forecast)
        const forecast = await modelInferenceService.forecastIssueCounts(issueTypeName, featureMatrix);

        return res.json({
            subzone: subzoneName,
            issueType: issueTypeName,
            forecast: forecast // Should be an array of objects of the next 7 daily forecasts (inclusive of today)
        });

    } catch (error) {
        console.log(error);
        return res.status(500).json({
            error: 'Internal server error during forecasting'
        });
    }
}

module.exports = {
    forecastIssues
};