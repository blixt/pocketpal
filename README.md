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
➜ 🏎️ make build
# run image
➜ 🏎️ make run
# inside container
➜ 🏎️ make dev
# get logs
➜ 🏎️ make logs
```

Build and push Docker image to Google Cloud's artifact registry, that will update our Google Cloud Run's service:

```bash
➜ 🏎️ make push
```

Run the React app locally:

```bash
➜ 🏎️ make dev-react
```
