const {
    pool
} = require('../db/pool');

// Get centroid coordinates (latitude, longitude) for a given subzone
async function getSubzoneCentroid(subzoneName) {
    const {
        rows
    } = await pool().query(`
        SELECT ST_X(ST_Centroid(geom::geometry)) AS longitude, ST_Y(ST_Centroid(geom::geometry)) AS latitude 
        FROM subzones 
        WHERE name = $1
        LIMIT 1
    `, [subzoneName]);

    if (!rows.length) {
        throw new Error('Subzone not found');
    }

    return {
        latitude: rows[0].latitude,
        longitude: rows[0].longitude
    };
}

// Get planning area name for a given subzone
async function getPlanningAreaBySubzone(subzoneName) {
    const {
        rows
    } = await pool().query(`
        SELECT pa.name
        FROM subzones sz
        JOIN planning_areas pa ON sz.planning_area_id = pa.planning_area_id
        WHERE sz.name = $1
        LIMIT 1
    `, [subzoneName]);

    if (!rows.length) {
        throw new Error('Planning area not found');
    }

    return rows[0].name;
}

module.exports = {
    getSubzoneCentroid,
    getPlanningAreaBySubzone
};