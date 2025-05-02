const axios = require('axios');
const {
    getOneMapAuthToken
} = require('../utils/oneMapAuth');

/**
 * Fetches population age distribution for a planning area.
 * @param {string} planningArea
 * @returns {Promise<Object>} - Object with extracted features
 */
async function fetchAgeData(planningArea) {
    const token = await getOneMapAuthToken();

    const url = `https://www.onemap.gov.sg/api/public/popapi/getPopulationAgeGroup?planningArea=${encodeURIComponent(planningArea)}&year=2020&gender=female`;

    try {
        const response = await axios.get(url, {
            headers: {
                Authorization: token
            }
        });

        const data = response.data[0];

        if (!data) {
            throw new Error('No age data found.');
        }

        // Calculate average age
        let totalPopulation = 0;
        let weightedAgeSum = 0;

        for (const [key, value] of Object.entries(data)) {
            if (key.startsWith('age_')) {
                const range = key.replace('age_', '');
                const [minAge, maxAge] = range.includes('_') ? range.split('_').map(Number) : [parseInt(range), parseInt(range)];
                const midAge = (minAge + maxAge) / 2;
                weightedAgeSum += (value || 0) * midAge;
                totalPopulation += (value || 0);
            }
        }

        const averageAge = totalPopulation > 0 ? weightedAgeSum / totalPopulation : null;

        return {
            averageAge,
            totalPopulation
        };
    } catch (error) {
        console.error('Failed to fetch age data:', error.message);
        return {
            averageAge: null,
            totalPopulation: null
        };
    }
}

/**
 * Fetches average household income for a planning area.
 * @param {string} planningArea
 * @returns {Promise<Object>} - Object with extracted features
 */
async function fetchIncomeData(planningArea) {
    const token = await getOneMapAuthToken();

    const url = `https://www.onemap.gov.sg/api/public/popapi/getHouseholdMonthlyIncomeWork?planningArea=${encodeURIComponent(planningArea)}&year=2020`;

    try {
        const response = await axios.get(url, {
            headers: {
                Authorization: token
            }
        });

        const data = response.data[0];

        if (!data) {
            throw new Error('No income data found.');
        }

        // Calculate weighted average income
        const incomeRanges = [{
                min: 0,
                max: 999,
                key: 'below_sgd_1000'
            },
            {
                min: 1000,
                max: 1999,
                key: 'sgd_1000_to_1999'
            },
            {
                min: 2000,
                max: 2999,
                key: 'sgd_2000_to_2999'
            },
            {
                min: 3000,
                max: 3999,
                key: 'sgd_3000_to_3999'
            },
            {
                min: 4000,
                max: 4999,
                key: 'sgd_4000_to_4999'
            },
            {
                min: 5000,
                max: 5999,
                key: 'sgd_5000_to_5999'
            },
            {
                min: 6000,
                max: 6999,
                key: 'sgd_6000_to_6999'
            },
            {
                min: 7000,
                max: 7999,
                key: 'sgd_7000_to_7999'
            },
            {
                min: 8000,
                max: 8999,
                key: 'sgd_8000_to_8999'
            },
            {
                min: 9000,
                max: 9999,
                key: 'sgd_9000_to_9999'
            },
            {
                min: 10000,
                max: 10999,
                key: 'sgd_10000_to_10999'
            },
            {
                min: 11000,
                max: 11999,
                key: 'sgd_11000_to_11999'
            },
            {
                min: 12000,
                max: 12999,
                key: 'sgd_12000_to_12999'
            },
            {
                min: 13000,
                max: 13999,
                key: 'sgd_13000_to_13999'
            },
            {
                min: 14000,
                max: 14999,
                key: 'sgd_14000_to_14999'
            },
            {
                min: 15000,
                max: 17499,
                key: 'sgd_15000_to_17499'
            },
            {
                min: 17500,
                max: 19999,
                key: 'sgd_17500_to_19999'
            },
            {
                min: 20000,
                max: 20000,
                key: 'sgd_20000_over'
            }
        ];

        let weightedSum = 0;
        let totalHouseholds = 0;

        for (const {
                min,
                max,
                key
            }
            of incomeRanges) {
            const count = data[key] || 0;
            const mid = (min + max) / 2;
            weightedSum += mid * count;
            totalHouseholds += count;
        }

        const averageIncome = totalHouseholds > 0 ? weightedSum / totalHouseholds : null;

        return {
            averageIncome,
            totalHouseholds
        };
    } catch (error) {
        console.error('Failed to fetch income data:', error.message);
        return {
            averageIncome: null,
            totalHouseholds: null
        };
    }
}

async function getSocioeconomicFeatures(planningArea) {
    try {
        const [ageData, incomeData] = await Promise.all([
            fetchAgeData(planningArea),
            fetchIncomeData(planningArea)
        ]);

        return {
            averageAge: ageData.averageAge,
            totalPopulation: ageData.totalPopulation,
            averageIncome: incomeData.averageIncome,
            totalHouseholds: incomeData.totalHouseholds
        };
    } catch (error) {
        console.error('Failed to fetch socioeconomic features:', error.message);
        return {
            averageAge: null,
            totalPopulation: null,
            averageIncome: null,
            totalHouseholds: null
        };
    }
}

module.exports = {
    getSocioeconomicFeatures
};