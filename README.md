# PocketPal

## Environment

```bash
# build docker image locally
➜ 🏎️ docker build -f Dockerfile -t pocketpal_image .
➜ 🏎️ make build
# run image
➜ 🏎️ docker run -it --rm --entrypoint "/bin/bash" -v "$(pwd)/data:/data" -p 5000:5000 pocketpal_image
➜ 🏎️ make run
➜ 🏎️ make dev
```