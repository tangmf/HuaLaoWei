const axios = require('axios');

/**
 * Sends features to the Python FastAPI server to get forecast predictions.
 * @param {string} issueTypeName - Name of the selected issue type (to pick the correct model)
 * @param {Array<Object>} featureArray - Array of 7 feature objects
 * @returns {Promise<Array<number>>} - Predicted issue counts for the next 7 days
 */
async function forecastIssueCounts(issueTypeName, featureArray) {
    try {
        const response = await axios.post(`${process.env.MODEL_SERVER_URL}forecast/tcn`, {
            issueTypeName: issueTypeName,
            features: featureArray
        });

        return response.data.predictions; // Array of numbers, one per day
    } catch (error) {
        console.error('Forecast prediction failed:', error.message);
        throw error;
    }
}

module.exports = {
    forecastIssueCounts
};