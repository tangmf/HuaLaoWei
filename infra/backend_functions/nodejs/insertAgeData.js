// JavaScript
const fs = require('fs');
const csv = require('csv-parser');
const { Client } = require('pg');

const PG_CONFIG = {
  user: 'postgres',
  host: 'localhost',
  database: 'municipal_app',
  password: 'fyukiAmane03!',
  port: 5432,
};

const client = new Client(PG_CONFIG);

async function main() {
  await client.connect();

  await client.query(`
    CREATE TABLE IF NOT EXISTS population_data (
      id SERIAL PRIMARY KEY,
      "PlanningArea" TEXT,
      "Subzone" TEXT,
      "Age" TEXT,
      "Sex" TEXT,
      "Population" INTEGER,
      "createdAt" TIMESTAMP,
      "lastUpdatedAt" TIMESTAMP
    );
  `);

  const rows = [];

  fs.createReadStream('age2024.csv')
    .pipe(csv())
    .on('data', (data) => {
      const createdAt = new Date(`${data.Time}-01-01T00:00:00Z`);
      const lastUpdatedAt = new Date();

      rows.push({
        PlanningArea: data.PA,
        Subzone: data.SZ,
        Age: data.Age === '90_and_Over' ? '90+' : data.Age,
        Sex: data.Sex,
        Population: parseInt(data.Pop, 10),
        createdAt,
        lastUpdatedAt,
      });
    })
    .on('end', async () => {
      for (const row of rows) {
        await client.query(
          `INSERT INTO population_data ("PlanningArea", "Subzone", "Age", "Sex", "Population", "createdAt", "lastUpdatedAt")
           VALUES ($1, $2, $3, $4, $5, $6, $7);`,
          [
            row.PlanningArea,
            row.Subzone,
            row.Age,
            row.Sex,
            row.Population,
            row.createdAt,
            row.lastUpdatedAt,
          ]
        );
      }
      console.log('Data inserted successfully.');
      await client.end();
    });
}

main().catch(console.error);