const axios = require('axios');

let cachedToken = null;
let cachedExpiry = null;

// Refresh OneMap Token if expired
async function getOneMapAuthToken() {
    const now = Math.floor(Date.now() / 1000); // Current timestamp in seconds

    if (cachedToken && cachedExpiry && now < cachedExpiry - 60) { // 1 min buffer
        return cachedToken;
    }

    try {
        const response = await axios.post(
            'https://www.onemap.gov.sg/api/auth/post/getToken', {
                email: process.env.ONEMAP_EMAIL,
                password: process.env.ONEMAP_PASSWORD
            }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        const {
            access_token,
            expiry_timestamp
        } = response.data;

        cachedToken = access_token;
        cachedExpiry = parseInt(expiry_timestamp, 10);

        console.log('[OneMap] Refreshed access token.');
        return cachedToken;
    } catch (error) {
        console.error('[OneMap] Failed to get access token:', error.message);
        throw new Error('Failed to obtain OneMap access token');
    }
}

module.exports = {
    getOneMapAuthToken
};