build:
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
