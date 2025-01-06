.PHONY: clear-log
clear-log:
	rm -rf ./logs
.PHONY: isort
isort:
	ruff check --select I --fix
.PHONY: check
check:
	ruff check
.PHONY: check-fix
check-fix:isort check-imports
	ruff check --fix 
.PHONY: check-imports
check-imports:
	ruff check --select F401 --fix
.PHONY:clean
clean:clear-log
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf ./.ruff_cache
	rm -rf ./.pytest_cache
	rm -rf ./celerybeat-schedule.db
	rm -rf ./celerybeat-schedule
	rm -rf ./.coverage
	rm -rf ./htmlcov
.PHONY:create-keys
create-keys:
	python scripts/keygen_crypto.py