const fetch = require('node-fetch');
const { Client } = require('pg');

const PG_CONFIG = {
  user: 'postgres',
  host: 'localhost',
  database: 'municipal_app',
  password: 'fyukiAmane03!',
  port: 5432,
};

const BASE_API = 'https://api-production.data.gov.sg/v2/public/api/datasets';
const DOWNLOAD_API = 'https://api-open.data.gov.sg/v1/public/api/datasets';

async function findAllMatchingDatasets() {
  let page = 1;
  const matches = [];

  while (true) {
    const res = await fetch(`${BASE_API}?page=${page}`);
    const json = await res.json();
    const datasets = json.data.datasets;
    if (!datasets || datasets.length === 0) break;

    const filtered = datasets.filter(d => d.format === 'GEOJSON' && d.name.toLowerCase().includes('subzone'));
    matches.push(...filtered);
    page++;
  }

  return matches;
}

async function run() {
  try {
    const datasets = await findAllMatchingDatasets();
    if (datasets.length === 0) throw new Error('No matching datasets found.');

    const client = new Client(PG_CONFIG);
    await client.connect();

    await client.query(`
      CREATE TABLE IF NOT EXISTS geojson_data (
        id SERIAL PRIMARY KEY,
        filename TEXT,
        feature JSONB,
        created_at TIMESTAMP,
        last_updated_at TIMESTAMP
      )
    `);

    for (const dataset of datasets) {
      const resultId = dataset.datasetId;
      const createdAt = dataset.createdAt;
      const lastUpdatedAt = dataset.lastUpdatedAt;
      const dateStr = new Date(createdAt).toISOString().slice(0, 10).replace(/-/g, '');
      const filename = `${dateStr}_SG_SubZonePlnArea.geojson`;

      const downloadRes = await fetch(`${DOWNLOAD_API}/${resultId}/poll-download`);
      const downloadJson = await downloadRes.json();
      if (downloadJson.code !== 0) {
        console.warn(`Skipping ${resultId}: ${downloadJson.errMsg}`);
        continue;
      }

      const fileRes = await fetch(downloadJson.data.url);
      const content = await fileRes.text();
      const geojson = JSON.parse(content);

      const insertQuery = `
        INSERT INTO geojson_data (filename, feature, created_at, last_updated_at)
        VALUES ($1, $2, $3, $4)
      `;
      for (const feature of geojson.features) {
        await client.query(insertQuery, [filename, feature, createdAt, lastUpdatedAt]);
      }

      console.log(`Inserted ${geojson.features.length} features from ${filename}`);
    }

    await client.end();
    console.log('All datasets processed.');
  } catch (err) {
    console.error('Error:', err);
  }
}

run();