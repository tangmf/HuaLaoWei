const express = require('express');
const router = express.Router();
const forecastController = require('../controllers/forecastController');

// Forecast Issue Counts for the next 7 days
router.get('/issues', forecastController.forecastIssues);

module.exports = router;
