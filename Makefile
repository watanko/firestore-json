.PHONY: check test compl
check:
	task check
test:
	task test
compl:
	uv run xenon --max-absolute B --max-modules A --max-average A src tests
