.PHONY: test lint run-pilot run-dashboard clean

test:
	pytest tests/

lint:
	flake8 agents/ evaluation/ metrics/
	black agents/ evaluation/ metrics/

run-pilot:
	python main.py --mode pilot

run-experiment:
	python main.py --mode experiment

run-dashboard:
	streamlit run dashboard/app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
