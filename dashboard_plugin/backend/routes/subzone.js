const express = require('express');
const router = express.Router();
const { getPlanningArea } = require('../controllers/subzoneController');

// API: /api/subzone/planning-area
router.get('/planning-area', getPlanningArea);

module.exports = router;
