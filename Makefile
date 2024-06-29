.PHONY: build run dev down status logs redo push build-react

build: build-react
	@docker-compose build

run:
	@docker-compose up -d --build

dev:
	@docker exec -it pocketpal bash

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

build-react:
	@cd react && yarn && yarn build
	@# TODO: This is a bit inelegant, let's clean up later.
	rm -rf static templates
	cp -r react/dist/* .

dev-react:
	@mkdir -p react/dist/{static,templates}
	rm -rf static templates
	ln -s react/dist/static static
	ln -s react/dist/templates templates
	@cd react && yarn && yarn dev
