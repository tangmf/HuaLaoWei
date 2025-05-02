const express = require('express');
const router = express.Router();
const {
    pool
} = require('../db/pool');

// GET issue types
router.get('/issue-types', async (req, res) => {
    try {
        const query = `
      SELECT it.name AS type, isc.name AS subtype
      FROM issue_types it
      LEFT JOIN issue_subtypes isc ON it.issue_type_id = isc.issue_type_id
      ORDER BY it.name, isc.name
    `;
        const result = await pool().query(query);

        const grouped = {};
        result.rows.forEach(row => {
            if (!grouped[row.type]) {
                grouped[row.type] = [];
            }
            if (row.subtype) {
                grouped[row.type].push(row.subtype);
            }
        });
        
        res.json(grouped);
    } catch (err) {
        console.error('Failed to fetch issue categories:', err);
        res.status(500).send('Server error');
    }
});

// GET agencies
router.get('/agencies', async (req, res) => {
    try {
        const result = await pool().query(`SELECT agency_name FROM agencies ORDER BY agency_name`);
        res.json(result.rows.map(r => r.agency_name));
    } catch (err) {
        console.error('Failed to fetch agencies:', err);
        res.status(500).send('Server error');
    }
});

// GET town councils
router.get('/town-councils', async (req, res) => {
    try {
        const result = await pool().query(`SELECT council_name FROM town_councils ORDER BY council_name`);
        res.json(result.rows.map(r => r.council_name));
    } catch (err) {
        console.error('Failed to fetch town councils:', err);
        res.status(500).send('Server error');
    }
});

module.exports = router;