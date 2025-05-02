pip install --upgrade pip
pip install sentence-transformers psycopg2 requests python-dotenv

npm install -g pm2

curl -k -X DELETE http://192.168.0.101:9200/issues

pm2 delete all
pm2 unstartup
pm2 start embed_and_sync.py --interpreter python3 --name embed-sync
pm2 start embed_and_sync.py --interpreter ./venv/bin/python --name embed-sync
pm2 restart embed-sync
pm2 startup
pm2 save
pm2 logs embed-sync
    