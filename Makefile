.PHONY: test lint format run-pilot run-experiment run-dashboard clean

test:
	python -m pytest tests/

lint:
	python -m flake8 agentstress/ tests/
	black --check agentstress/ tests/

format:
	black agentstress/ tests/

run-pilot:
	python main.py --mode pilot

run-experiment:
	python main.py --mode experiment

run-dashboard:
	streamlit run dashboard/app.py

clean:
	python -c "import os, shutil; [shutil.rmtree(os.path.join(root, d)) for root, dirs, files in os.walk('.') for d in dirs if d == '__pycache__']"
	python -c "import os, shutil; shutil.rmtree('.pytest_cache', ignore_errors=True)"
