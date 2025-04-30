const { pool, initializePool } = require('./pool');
const { faker } = require('@faker-js/faker');

(async () => {
    await initializePool();
    await seedUsersData();
})();

async function seedUsersData() {
    try {
        await pool().query('TRUNCATE TABLE users RESTART IDENTITY CASCADE');
        console.log('All existing users deleted.');

        for (let i = 0; i < 20; i++) {
            const username = faker.internet.username();
            const email = faker.internet.email();
            const passwordHash = faker.string.uuid();
            const lastLogin = faker.date.recent({
                days: 10
            });

            await pool().query(
                `INSERT INTO users (username, email, password_hash, last_login) VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING`,
                [username, email, passwordHash, lastLogin]
            );
        }

        console.log('Users seeded.');

    } catch (error) {
        console.log(error);
        console.error('Seeding reference data failed:', error.message);
    }
}

module.exports = {
    seedUsersData,
};