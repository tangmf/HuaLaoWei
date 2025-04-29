# Municipal Services VLM classifier

Utilises fine-tuned VLMs for multimodal classification tasks in municipal services.

## Building the Docker Image

```bash
cd ./inference
```

```bash
docker build -t vlm:latest .
```

## Running the container
```bash
docker run --rm -it \
  -v model_weights:/app/weights \
  -p 8000:8000 \
  vlm:latest
```