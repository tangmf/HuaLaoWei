async function batchProcess(items, handler, concurrency = 5) {
    const results = [];
    const executing = [];

    for (const item of items) {
        const p = Promise.resolve().then(() => handler(item));
        results.push(p);

        if (concurrency <= items.length) {
            const e = p.then(() => executing.splice(executing.indexOf(e), 1));
            executing.push(e);
            if (executing.length >= concurrency) {
                await Promise.race(executing);
            }
        }
    }
    return Promise.all(results);
}

module.exports = {
    batchProcess
};