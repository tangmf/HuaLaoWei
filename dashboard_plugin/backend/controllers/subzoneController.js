const subzoneService = require('../services/subzoneService');

/**
 * Controller: Get Planning Area by Subzone Name
 * @param {*} req 
 * @param {*} res 
 */
async function getPlanningArea(req, res) {
    try {
        const { subzoneName } = req.query;

        if (!subzoneName) {
            return res.status(400).json({ error: 'Missing subzoneName in request' });
        }

        const planningAreaName = await subzoneService.getPlanningAreaBySubzone(subzoneName);

        if (!planningAreaName) {
            return res.status(404).json({ error: 'Subzone not found' });
        }

        return res.json({ 
            subzone: subzoneName,
            planningArea: planningAreaName
        });
    } catch (error) {
        console.error('Failed to retrieve planning area:', error.message);
        return res.status(500).json({ error: 'Internal server error while retrieving planning area' });
    }
}

module.exports = {
    getPlanningArea
};
