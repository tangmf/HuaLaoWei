const {
    Pool
} = require('pg');
const {
    pool
} = require('./pool');

// Only for local PostgreSQL database creation (optional use)
async function createDatabaseIfNotExists() {
    const adminPool = new Pool({
        host: process.env.LOCAL_HOST,
        port: process.env.LOCAL_PORT,
        database: 'postgres',
        user: process.env.LOCAL_USER,
        password: process.env.LOCAL_PASSWORD,
    });

    try {
        const result = await adminPool.query(
            'SELECT 1 FROM pg_database WHERE datname = $1',
            [process.env.LOCAL_DATABASE]
        );

        if (result.rowCount === 0) {
            console.log(`Creating database '${process.env.LOCAL_DATABASE}'...`);
            await adminPool.query(`CREATE DATABASE ${process.env.LOCAL_DATABASE}`);
        } else {
            console.log(`Database '${process.env.LOCAL_DATABASE}' already exists.`);
        }
    } catch (error) {
        console.error('Error checking or creating database:', error.message);
    } finally {
        await adminPool.end();
    }
}

async function dropAllTables() {
    try {
        console.log('Resetting database: Dropping all tables...');

        // Disable referential integrity temporarily
        await pool().query('DROP TABLE IF EXISTS issues, subzones, planning_areas, users, agencies, issue_types, issue_subtypes, town_councils CASCADE');

        console.log('All tables dropped.');
    } catch (error) {
        console.error('Failed to drop tables:', error.message);
    }
}

async function createReferenceTables() {
    try {
        if (process.env.RESET_DATABASE === 'true') {
            await dropAllTables();
        }

        await pool().query(`
      CREATE EXTENSION IF NOT EXISTS postgis;

      CREATE TABLE IF NOT EXISTS agencies (
        agency_id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
      );

      CREATE TABLE IF NOT EXISTS issue_types (
        issue_type_id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
      );

      CREATE TABLE IF NOT EXISTS issue_subtypes (
        subtype_id SERIAL PRIMARY KEY,
        issue_type_id INTEGER REFERENCES issue_types(issue_type_id),
        name TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS town_councils (
        town_council_id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT
      );

      CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS planning_areas (
        planning_area_id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        geom GEOGRAPHY(MULTIPOLYGON, 4326),
        area_sq_m DOUBLE PRECISION
      );

      CREATE TABLE IF NOT EXISTS subzones (
        subzone_id SERIAL PRIMARY KEY,
        planning_area_id INTEGER REFERENCES planning_areas(planning_area_id),
        name VARCHAR(100) NOT NULL,
        geom GEOGRAPHY(MULTIPOLYGON, 4326),
        area_sq_m DOUBLE PRECISION
      );

      CREATE TABLE IF NOT EXISTS issues (
        issue_id SERIAL PRIMARY KEY,
        user_id INTEGER,
        issue_type_id INTEGER REFERENCES issue_types(issue_type_id),
        issue_subtype_id INTEGER REFERENCES issue_subtypes(subtype_id),
        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL,
        full_address TEXT,
        location GEOGRAPHY(Point, 4326),
        description TEXT,
        severity VARCHAR(50),
        status VARCHAR(50) DEFAULT 'Reported',
        datetime_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        datetime_acknowledged TIMESTAMP,
        datetime_closed TIMESTAMP,
        datetime_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        agency_id INTEGER REFERENCES agencies(agency_id),
        town_council_id INTEGER REFERENCES town_councils(town_council_id),
        subzone_id INTEGER REFERENCES subzones(subzone_id),
        planning_area_id INTEGER REFERENCES planning_areas(planning_area_id),
        is_public BOOLEAN DEFAULT TRUE
      );
    `);

        console.log('Reference tables created.');
    } catch (error) {
        console.error('Failed to create tables:', error.message);
    }
}

module.exports = {
    createDatabaseIfNotExists,
    createReferenceTables,
};