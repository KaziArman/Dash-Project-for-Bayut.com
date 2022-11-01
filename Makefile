.PHONY: test
test:
		PYTHONPATH=./src pytest
build:
		python3 -m build