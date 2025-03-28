.PHONY: lint, format, test


lint:
	ruff check

format:
	black .

test:
	pytest
