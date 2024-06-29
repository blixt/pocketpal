# PocketPal

## Environment

Login to gcloud:
```bash
➜ 🏎️ gcloud auth login
➜ 🏎️ gcloud auth application-default login
➜ 🏎️ gcloud config set project pocketpal-427909
```

Build and run locally:
```bash
# build docker image locally
➜ 🏎️ docker build -f Dockerfile -t pocketpal_image .
➜ 🏎️ make build
# run image
➜ 🏎️ docker run -it --rm --entrypoint "/bin/bash" -v "$(pwd)/data:/data" -p 5000:5000 pocketpal_image
➜ 🏎️ make run
➜ 🏎️ make dev
```

Build and push Docker image to Google Cloud's artifact registry:
```bash
➜ 🏎️ make push
```

