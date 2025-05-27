BACKEND_DIR=backend
BACKEND_PORT=8080
FRONTEND_DIR=frontend


run-backend:
	cd $(BACKEND_DIR) && python3 manage.py runserver $(BACKEND_PORT)

run-frontend:
	cd $(FRONTEND_DIR) && npm start

run: run-backend run-frontend

test:
	cd $(BACKEND_DIR) && pytest

check:
	poetry run pre-commit run --show-diff-on-failure --color=always -c tools/.pre-commit-config.yaml

pip-tools:
	.venv/bin/pip install -U pip
	@echo "Checking if requests is installed..."
	@python -c "import requests" || (echo "requests not found, installing..."; pip install requests)
	.venv/bin/pip install -U poetry

update: pip-tools
	poetry update