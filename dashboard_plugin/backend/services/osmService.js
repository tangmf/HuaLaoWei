const axios = require('axios');
const turf = require('@turf/turf');

/**
 * Fetch POIs from Overpass API based on bounding box and tags.
 * @param {Object} bbox - Bounding box { minLat, minLon, maxLat, maxLon }
 * @param {Object} tags - Key-value tags for filtering POIs
 * @returns {Promise<Array<Object>>}
 */
async function fetchPOIs(bbox, tags) {
    const { minLat, minLon, maxLat, maxLon } = bbox;

    const overpassQuery = `
[out:json][timeout:25];
(
    ${Object.entries(tags).map(([key, value]) => {
        if (Array.isArray(value)) {
            return value.map(v => `node["${key}"="${v}"](${minLat},${minLon},${maxLat},${maxLon});`).join('');
        } else if (value === true) {
            return `node["${key}"](${minLat},${minLon},${maxLat},${maxLon});`;
        } else {
            return `node["${key}"="${value}"](${minLat},${minLon},${maxLat},${maxLon});`;
        }
    }).join('')}
);
out center;
`;

    try {
        const response = await axios.post('https://overpass-api.de/api/interpreter', overpassQuery, {
            headers: { 'Content-Type': 'text/plain' }
        });

        const elements = response.data.elements || [];

        return elements.map(el => ({
            id: el.id,
            lat: el.lat,
            lon: el.lon
        }));
    } catch (error) {
        console.error('Failed to fetch POIs:', error.message);
        return [];
    }
}


/**
 * Computes proximity (in meters) to nearest POI for each input point.
 * @param {Array<Object>} points - [{ lat, lon }]
 * @param {Array<Object>} pois - [{ lat, lon }]
 * @returns {Array<number>}
 */
function computeProximity(points, pois) {
    if (pois.length === 0) {
        return Array(points.length).fill(null);
    }

    return points.map(point => {
        const from = turf.point([point.lon, point.lat]);
        const distances = pois.map(poi => {
            const to = turf.point([poi.lon, poi.lat]);
            return turf.distance(from, to, {
                units: 'meters'
            });
        });

        return Math.min(...distances);
    });
}

/**
 * Computes number of POIs within buffer radius (in meters) around each point.
 * @param {Array<Object>} points - [{ lat, lon }]
 * @param {Array<Object>} pois - [{ lat, lon }]
 * @param {number} bufferMeters - Buffer radius in meters
 * @returns {Array<number>}
 */
function computeDensity(points, pois, bufferMeters) {
    if (pois.length === 0) {
        return Array(points.length).fill(0);
    }

    return points.map(point => {
        const center = turf.point([point.lon, point.lat]);
        const buffer = turf.buffer(center, bufferMeters, {
            units: 'meters'
        });

        return pois.filter(poi => {
            const p = turf.point([poi.lon, poi.lat]);
            return turf.booleanPointInPolygon(p, buffer);
        }).length;
    });
}

async function getPOIFeatures(latitude, longitude) {
    const bbox = {
        minLat: latitude - 0.01,
        minLon: longitude - 0.01,
        maxLat: latitude + 0.01,
        maxLon: longitude + 0.01
    };

    const poiTagsByGroup = {
        commercial: { shop: true, amenity: ["marketplace", "mall"] },
        residential: { landuse: "residential", building: ["apartments", "residential"] },
        facilities: { amenity: ["school", "hospital"] },
        recreation: { leisure: "park", tourism: true },
        transit: { highway: "bus_stop", railway: ["station", "subway_entrance"], public_transport: ["platform", "stop_position"] }
    };

    const point = { lat: latitude, lon: longitude };

    const features = {};

    for (const [groupName, tags] of Object.entries(poiTagsByGroup)) {
        const pois = await fetchPOIs(bbox, tags);

        const density = computeDensity([point], pois, 200)[0];  // 200 meters
        const proximity = computeProximity([point], pois)[0];

        features[`density_${groupName}`] = density;
        features[`proximity_${groupName}`] = proximity;
    }

    return features;
}


module.exports = {
    getPOIFeatures
};