const { Client } = require('pg');
require('dotenv').config();

var clientConfig = {
    host: process.env.DB_HOST, // e.g., 'your-db-hostname.rds.amazonaws.com'
    port: process.env.DB_PORT,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
  }

if (process.env.DB_HOST !== 'localhost') {
    clientConfig.ssl = {
        rejectUnauthorized: false  // Needed if RDS requires SSL
    };
}


const client = new Client(clientConfig);

async function connectAndQuery() {
  try {
    await client.connect();
    console.log('Connected to Huawei Cloud RDS PostgreSQL');

    const res = await client.query('SELECT NOW()');
    console.log('Server time:', res.rows[0]);
  } catch (err) {
    console.error('Connection error', err.stack);
  } finally {
    await client.end();
  }
}

connectAndQuery();
