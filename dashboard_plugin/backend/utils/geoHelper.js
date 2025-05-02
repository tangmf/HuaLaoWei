const turf = require('@turf/turf');

/**
 * Given a GeoJSON MultiPolygon, returns a random point inside it.
 * Retries up to 10 times, fallback to centroid if still outside.
 */
function randomPointInPolygon(geojson) {
    const bbox = turf.bbox(geojson); // [minX, minY, maxX, maxY]

    for (let i = 0; i < 10; i++) {
        const longitude = Math.random() * (bbox[2] - bbox[0]) + bbox[0];
        const latitude = Math.random() * (bbox[3] - bbox[1]) + bbox[1];

        const point = turf.point([longitude, latitude]);

        if (turf.booleanPointInPolygon(point, geojson)) {
            return {
                latitude,
                longitude
            };
        }
    }

    // Fallback: center of polygon
    const center = turf.centerOfMass(geojson);
    return {
        latitude: center.geometry.coordinates[1],
        longitude: center.geometry.coordinates[0]
    };
}

module.exports = {
    randomPointInPolygon
};