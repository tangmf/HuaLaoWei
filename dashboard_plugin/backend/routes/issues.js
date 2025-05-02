const express = require('express');
const router = express.Router();
const {
    pool
} = require('../db/pool');

// GET open issues (status != 'Resolved')
router.get('/open', async (req, res) => {
    const {
        subzoneName,
        from,
        to,
        types,
        subtypes,
        severity,
        page = 1,
        limit = 10000
    } = req.query;

    try {
        const filters = [];
        const values = [];

        if (subzoneName) {
            filters.push(`sz.name = $${values.length + 1}`);
            values.push(subzoneName);
        }
        if (from) {
            filters.push(`i.datetime_updated >= $${values.length + 1}`);
            values.push(from);
        }
        if (to) {
            filters.push(`i.datetime_updated <= $${values.length + 1}`);
            values.push(to);
        }
        if (types) {
            const typeList = types.split(',').map((_, i) => `$${values.length + i + 1}`);
            filters.push(`it.name IN (${typeList.join(',')})`);
            values.push(...types.split(','));
        }
        if (subtypes) {
            const subtypeList = subtypes.split(',').map((_, i) => `$${values.length + i + 1}`);
            filters.push(`isc.name IN (${subtypeList.join(',')})`);
            values.push(...subtypes.split(','));
        }
        if (severity) {
            filters.push(`i.severity = $${values.length + 1}`);
            values.push(severity);
        }

        const whereClause = filters.length ?
            `WHERE ${filters.join(' AND ')} AND i.status != 'Resolved'` :
            `WHERE i.status != 'Resolved'`;

        const offset = (parseInt(page) - 1) * parseInt(limit);
        const limitInt = parseInt(limit);

        const query = `
      SELECT 
        i.description, i.severity, i.latitude, i.longitude, i.address, i.status, sz.name AS subzone_name, 
        i.datetime_reported, i.datetime_acknowledged, i.datetime_closed, i.datetime_updated,
        it.name AS issue_type, isc.name AS issue_subtype, a.name AS agency_name, tc.name AS town_council_name
      FROM issues i
      JOIN subzones sz ON i.subzone_id = sz.subzone_id
      JOIN issue_types it ON i.issue_type_id = it.issue_type_id
      JOIN issue_subtypes isc ON i.issue_subtype_id = isc.issue_subtype_id
      JOIN agencies a ON i.agency_id = a.agency_id
      JOIN town_councils tc ON i.town_council_id = tc.town_council_id
      ${whereClause}
      ORDER BY i.datetime_updated DESC
      LIMIT $${values.length + 1} OFFSET $${values.length + 2}
    `;

        values.push(limitInt, offset);
        const result = await pool().query(query, values);
        res.json(result.rows);
    } catch (err) {
        console.error('Query failed:', err);
        res.status(500).send('Server error');
    }
});

// GET resolved issues (status = 'Resolved')
router.get('/resolved', async (req, res) => {
    const {
        subzoneName,
        from,
        to,
        types,
        subtypes,
        severity,
        page = 1,
        limit = 10000
    } = req.query;

    try {
        const filters = [];
        const values = [];

        if (subzoneName) {
            filters.push(`sz.name = $${values.length + 1}`);
            values.push(subzoneName);
        }
        if (from) {
            filters.push(`i.datetime_updated >= $${values.length + 1}`);
            values.push(from);
        }
        if (to) {
            filters.push(`i.datetime_updated <= $${values.length + 1}`);
            values.push(to);
        }
        if (types) {
            const typeList = types.split(',').map((_, i) => `$${values.length + i + 1}`);
            filters.push(`it.name IN (${typeList.join(',')})`);
            values.push(...types.split(','));
        }
        if (subtypes) {
            const subtypeList = subtypes.split(',').map((_, i) => `$${values.length + i + 1}`);
            filters.push(`isc.name IN (${subtypeList.join(',')})`);
            values.push(...subtypes.split(','));
        }
        if (severity) {
            filters.push(`i.severity = $${values.length + 1}`);
            values.push(severity);
        }

        const whereClause = filters.length ?
            `WHERE ${filters.join(' AND ')} AND i.status = 'Resolved'` :
            `WHERE i.status = 'Resolved'`;

        const offset = (parseInt(page) - 1) * parseInt(limit);
        const limitInt = parseInt(limit);

        const query = `
      SELECT 
        i.description, i.severity, i.latitude, i.longitude, i.address,
        i.datetime_reported, i.datetime_acknowledged, i.datetime_closed, i.datetime_updated,
        it.name AS issue_type, isc.name AS issue_subtype, a.name, tc.name AS town_council_name
      FROM issues i
      JOIN subzones sz ON i.subzone_id = sz.subzone_id
      JOIN issue_types it ON i.issue_type_id = it.issue_type_id
      JOIN issue_subtypes isc ON i.issue_subtype_id = isc.issue_subtype_id
      JOIN agencies a ON i.agency_id = a.agency_id
      JOIN town_councils tc ON i.town_council_id = tc.town_council_id
      ${whereClause}
      ORDER BY i.datetime_closed DESC
      LIMIT $${values.length + 1} OFFSET $${values.length + 2}
    `;

        values.push(limitInt, offset);
        const result = await pool().query(query, values);
        res.json(result.rows);
    } catch (err) {
        console.error('Query failed:', err);
        res.status(500).send('Server error');
    }
});

// GET issue count by subzone and issue type
router.get('/daily-count', async (req, res) => {
    const { subzoneName, issueTypeName } = req.query;

    try {
        const filters = [];

        if (subzoneName) {
            filters.push(`sz.name = $${filters.length + 1}`);
        }
        if (issueTypeName) {    
            filters.push(`it.name = $${filters.length + 1}`);
        }

        const baseWhere = `
            WHERE i.datetime_reported >= (CURRENT_DATE - INTERVAL '20 days')
            ${filters.length ? 'AND ' + filters.join(' AND ') : ''}
        `;

        const query = `
            SELECT 
                DATE(i.datetime_reported) AS report_date,
                COUNT(*) AS issue_count
            FROM issues i
            JOIN subzones sz ON i.subzone_id = sz.subzone_id
            JOIN issue_types it ON i.issue_type_id = it.issue_type_id
            ${baseWhere}
            GROUP BY report_date
            ORDER BY report_date ASC
        `;

        const values = [];
        if (subzoneName) values.push(subzoneName);
        if (issueTypeName) values.push(issueTypeName);

        const { rows } = await pool().query(query, values);

        // Generate all dates from 20 days ago until today
        const today = new Date();
        const dateCounts = {};

        for (let i = 20; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(today.getDate() - i);
            const isoDate = date.toISOString().split('T')[0]; // YYYY-MM-DD
            dateCounts[isoDate] = 0;
        }

        // Fill counts from the database
        for (const row of rows) {
            const dateKey = row.report_date.toISOString().split('T')[0];
            dateCounts[dateKey] = parseInt(row.issue_count, 10);
        }

        // Prepare final output
        const finalResult = Object.entries(dateCounts).map(([date, count]) => ({
            report_date: date,
            issue_count: count
        }));

        res.json(finalResult);
    } catch (error) {
        console.error('Failed to fetch daily issue counts:', error.message);
        res.status(500).send('Server error');
    }
});

module.exports = router;