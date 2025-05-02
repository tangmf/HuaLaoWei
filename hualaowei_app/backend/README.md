# Backend DB server

DB server for the mobile app.

## Building the Docker Image

```bash
docker build -t db_server:latest .
```

## Running the container (Live)
```bash
docker run -d --name db_server -p 5432:5432 -p 5000:5000 db_server:latest
```

## Running the container (Dev)
```bash
docker run -it -v ${PWD}:/app -p 5432:5432 -p 5000:5000 db_server:latest bash
```