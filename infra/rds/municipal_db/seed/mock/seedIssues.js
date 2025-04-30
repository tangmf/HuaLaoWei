const { pool, initializePool } = require('./pool');
const { faker } = require('@faker-js/faker');
const format = require('pg-format');
const wellknown = require('wellknown');
const turf = require('@turf/turf');

(async () => {
    await initializePool();
    await seedIssuesData();
})();


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

async function seedIssuesData() {
    try {
        await pool().query('TRUNCATE TABLE issues RESTART IDENTITY CASCADE');
        console.log('All existing issues deleted.');

        // Fetch reference data
        const { rows: users } = await pool().query('SELECT user_id FROM users');
        const { rows: issueTypes } = await pool().query('SELECT issue_type_id, name FROM issue_types');
        const { rows: subtypes } = await pool().query('SELECT issue_subtype_id, issue_type_id, name FROM issue_subtypes');
        const { rows: agencies } = await pool().query('SELECT agency_id FROM agencies');
        const { rows: councils } = await pool().query('SELECT town_council_id FROM town_councils');
        const { rows: planningAreas } = await pool().query('SELECT planning_area_id FROM planning_areas');
        const { rows: subzonesRaw } = await pool().query('SELECT subzone_id, planning_area_id, name, geom FROM subzones');

        // Build issueTypes to issueSubTypes mapping
        const typeToSubtypes = {};
        for (const subtype of subtypes) {
            if (!typeToSubtypes[subtype.issue_type_id]) {
                typeToSubtypes[subtype.issue_type_id] = [];
            }
            typeToSubtypes[subtype.issue_type_id].push(subtype);
        }

        // Build planningArea to subzones mapping
        const planningAreaToSubzones = {};
        for (const subzone of subzonesRaw) {
            const planningId = subzone.planning_area_id;
            if (!planningAreaToSubzones[planningId]) {
                planningAreaToSubzones[planningId] = [];
            }
            planningAreaToSubzones[planningId].push({
                subzone_id: subzone.subzone_id,
                geom: subzone.geom
            });
        }

        const statuses = ['Reported', 'Acknowledged', 'Resolved'];
        const severities = ['Low', 'Medium', 'High'];

        const singaporeStreets = [
            "Ang Mo Kio Avenue 3", "Bedok North Road", "Tampines Street 11",
            "Clementi Avenue 2", "Jurong West Street 41", "Hougang Avenue 8",
            "Yishun Ring Road", "Pasir Ris Drive 6", "Bukit Timah Road", "Toa Payoh Lorong 6",
            "Woodlands Avenue 5", "Sengkang East Way", "Choa Chu Kang Avenue 3",
            "Serangoon Avenue 2", "Punggol Field", "Upper Thomson Road",
            "Telok Blangah Drive", "Jurong East Street 13", "Bishan Street 12", "Commonwealth Avenue"
        ];


        const inserts = [];

        // Generate 5000 fake issues
        for (let i = 0; i < 5000; i++) {
            const userId = faker.helpers.arrayElement(users).user_id;

            const issueType = faker.helpers.arrayElement(issueTypes);
            const issueTypeId = issueType.issue_type_id;
            const issueTypeName = issueType.name;

            const subTypeOptions = typeToSubtypes[issueTypeId];
            if (!subTypeOptions || subTypeOptions.length === 0) {
                console.warn(`No subtypes found for issue type ${issueType.name}, skipping`);
                continue;
            }
            const selectedSubtype = faker.helpers.arrayElement(subTypeOptions);
            const issueSubTypeId = selectedSubtype.issue_subtype_id;

            const agencyId = faker.helpers.arrayElement(agencies).agency_id;
            const councilId = faker.helpers.arrayElement(councils).town_council_id;

            // Choose planning area + random subzone from that area
            const planningAreaId = faker.helpers.arrayElement(planningAreas).planning_area_id;
            const subzonesForArea = planningAreaToSubzones[planningAreaId];

            if (!subzonesForArea || subzonesForArea.length === 0) {
                console.warn(`No subzones found for planning area ${planningAreaId}, skipping`);
                continue;
            }

            const selectedSubzone = faker.helpers.arrayElement(subzonesForArea);
            const subzoneId = selectedSubzone.subzone_id;

            // Random lat/lon inside subzone
            let latitude, longitude;
            try {
                const subzoneGeom = wellknown(selectedSubzone.geom);
                ({ latitude, longitude } = randomPointInPolygon(subzoneGeom));
            } catch (e) {
                console.warn(`Skipping issue due to invalid geom for subzone ${selectedSubzone.name}`);
                continue;
            }

            // Generate a fake Singapore address
            const blockNumber = faker.number.int({
                min: 1,
                max: 999
            });
            const useBlockWord = faker.datatype.boolean();
            address = useBlockWord ?
                `Block ${blockNumber} ${faker.helpers.arrayElement(singaporeStreets)}` :
                `${blockNumber} ${faker.helpers.arrayElement(singaporeStreets)}`;

            const severity = faker.helpers.arrayElement(severities);
            const status = faker.helpers.arrayElement(statuses);

            const descriptionTemplates = [
                `${issueTypeName} issue of ${severity} severity reported at ${address}`,
                `${issueTypeName} spotted at ${address} with ${severity} urgency`,
                `${severity} ${issueTypeName} incident near ${address}`,
                `${issueTypeName} found at ${address}. Severity: ${severity}`,
            ];
            const description = faker.helpers.arrayElement(descriptionTemplates);

            const datetimeReported = faker.date.recent({
                days: 14
            });
            const datetimeAcknowledged = faker.date.between({
                from: datetimeReported,
                to: new Date()
            });

            let datetimeClosed = null;
            let datetimeUpdated = null;

            if (status === 'Resolved') {
                datetimeClosed = faker.date.between({
                    from: datetimeAcknowledged,
                    to: new Date()
                });
                datetimeUpdated = faker.date.between({
                    from: datetimeClosed,
                    to: new Date()
                });
            } else {
                datetimeClosed = null;
                datetimeUpdated = faker.date.between({
                    from: datetimeAcknowledged,
                    to: new Date()
                });
            }

            const isPublic = Math.random() < 0.8;

            inserts.push([
                userId, issueTypeId, issueSubTypeId, latitude, longitude, address,
                description, severity, status,
                datetimeReported, datetimeAcknowledged, datetimeClosed, datetimeUpdated,
                agencyId, councilId, planningAreaId, subzoneId, isPublic
            ]);
        }

        // Bulk Insert
        if (inserts.length > 0) {
            await pool().query(format(`
                INSERT INTO issues (
                    user_id, issue_type_id, issue_subtype_id, latitude, longitude, address,
                    description, severity, status,
                    datetime_reported, datetime_acknowledged, datetime_closed, datetime_updated,
                    agency_id, town_council_id, planning_area_id, subzone_id, is_public
                )
                VALUES %L
            `, inserts));

            console.log(`${inserts.length} issues inserted successfully.`);
        } else {
            console.warn('No issues to insert.');
        }
    } catch (error) {
        console.log(error);
        console.error('Failed to seed issues:', error.message);
    }
}

module.exports = {
    seedIssuesData
};