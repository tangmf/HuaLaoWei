require('dotenv').config();
const axios = require('axios');
const {
    getOneMapAuthToken
} = require('../utils/oneMapAuth');

async function getRealSingaporeAddress(latitude, longitude) {
    return null;
    const token = await getOneMapAuthToken();
    const url = `https://www.onemap.gov.sg/api/public/revgeocode?location=${latitude},${longitude}&buffer=40&addressType=All&otherFeatures=N`;

    try {
        const response = await axios.get(url, {
            headers: {
                Authorization: token
            }
        });

        const geocodeInfo = response.data.GeocodeInfo;
        if (geocodeInfo.length > 0) {
            const info = geocodeInfo[0];
            const block = info.BLOCK ? `Block ${info.BLOCK}` : '';
            const building = info.BUILDINGNAME ? `${info.BUILDINGNAME}` : '';
            const road = info.ROAD ? `${info.ROAD}` : '';
            const postal = info.POSTALCODE ? `Singapore ${info.POSTALCODE}` : '';

            const parts = [block, building, road, postal].filter(Boolean);
            return parts.join(', ').replace(/\s+/g, ' ').trim();
        } else {
            throw new Error('No address found');
        }
    } catch (error) {
        console.error('OneMap reverse geocode failed:', error.message);
        return null;
    }
}

module.exports = {
    getRealSingaporeAddress
};