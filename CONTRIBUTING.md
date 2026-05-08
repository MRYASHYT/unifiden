# Contributing to AgentStress

We welcome contributions from the research and engineering community!

## Development Setup
1. Clone the repo: `git clone https://github.com/MRYASHYT/agentstress.git`
2. Create a virtual environment: `python -m venv venv`
3. Activate it and install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your API keys.

## Testing
Run the test suite before submitting a PR:
```bash
pytest tests/
```

## Adding New Agents
To add a new agent architecture:
1. Create a new file in `agents/`.
2. Inherit from `BaseAgent`.
3. Implement `setup`, `run`, and `run_with_peer_context`.
4. Register the agent in `experiments/batch_runner.py`.

## Adding New Metrics
1. Add logic to `metrics/advanced_metrics.py`.
2. Update `evaluation/round_4_judge.py` to call your new metric.
