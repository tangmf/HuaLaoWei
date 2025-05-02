require('dotenv').config();
const {
    Pool
} = require('pg');

let pool;

async function initializePool() {
    try {
        pool = new Pool({
            host: process.env.PGHOST,
            port: process.env.PGPORT,
            database: process.env.PGDATABASE,
            user: process.env.PGUSER,
            password: process.env.PGPASSWORD,
            ssl: process.env.PGSSL === 'true' ? {
                rejectUnauthorized: false
            } : false,
        });
        await pool.query('SELECT 1');
        console.log('Connected to Huawei RDS PostgreSQL.');
    } catch (rdsError) {
        console.error('Failed to connect to Huawei RDS. Falling back to local PostgreSQL:', rdsError.message);
    }
}

module.exports = {
    pool: () => pool,
    initializePool
};