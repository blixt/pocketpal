.PHONY: build run dev down status logs redo push build-react dev-react

build: build-react
	@docker-compose build

build-react:
	@cd react && yarn && yarn build
	@# TODO: This is a bit inelegant, let's clean up later.
	rm -rf static templates
	cp -r react/dist/* .

run:
	@docker-compose up -d --build

dev:
	@docker exec -it pocketpal bash

dev-react:
	@mkdir -p react/dist/{static,templates}
	rm -rf static templates
	ln -s react/dist/static static
	ln -s react/dist/templates templates
	@cd react && yarn && yarn dev

down:
	@docker-compose down -v

status:
	@docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

logs:
	@docker logs pocketpal -f

redo:
	make build; make run; make dev

push:
	@gcloud builds submit \
	--config "cloud/cloudbuild.yaml" \
	--substitutions=_DOCKERFILE="Dockerfile",_REPO_NAME="pocketpal"

deploy:
	@gcloud run deploy "pocketpalrun" \
	--image europe-west1-docker.pkg.dev/pocketpal-427909/pocketpal-repo-eu/pocketpal:latest \
	--region europe-west1