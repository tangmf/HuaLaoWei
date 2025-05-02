const dayjs = require('dayjs'); // Lightweight date library
require('dayjs/locale/en'); // Ensure English

function generateTemporalFeatures(startDate, numDays = 7) {
    const temporalFeatures = [];

    for (let i = 0; i < numDays; i++) {
        const date = dayjs(startDate).add(i, 'day');

        temporalFeatures.push({
            date: date.format('YYYY-MM-DD'),
            day_of_week: date.day(), // 0=Sunday, 1=Monday, ..., 6=Saturday
            is_weekend: [0, 6].includes(date.day()), // true for Sunday or Saturday
            month: date.month() + 1 // month() is 0-indexed, so add 1
        });
    }

    return temporalFeatures;
}

module.exports = {
    generateTemporalFeatures
};
