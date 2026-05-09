# AgentStress

AgentStress is a Python framework for stress-testing agentic AI pipelines. It runs agents through clear, ambiguous, and adversarial instructions, scores their outputs against rubrics, classifies failure modes, and records signed evaluation results in a local tamper-evident ledger.

The project is currently suitable for research, demos, and early beta evaluation workflows. Production or enterprise claims should be backed by your own large-scale experiments, human validation, and deployment review.

## What It Tests

AgentStress focuses on reliability failures that are easy to miss in simple benchmark scores:

- Instruction drift: the agent solves a related but different task.
- Premature termination: the agent stops before completing all required work.
- Tool-call hallucination: the agent invents data, citations, or tool outputs.
- Overconfidence collapse: the agent abandons a correct answer under peer pressure.
- Stubbornness failure: the agent refuses to update a wrong answer after valid critique.
- Contamination: one agent adopts another agent's hallucination.

## Core Features

- Multi-agent debate protocol with independent answers, peer review, revision, and judging.
- Rubric-based scoring for repeatable task evaluation.
- GPT, Claude, and Gemini agent/judge integrations.
- Signed JSONL evaluation ledger with RSA signatures and hash chaining for new entries.
- Streamlit dashboard for inspecting reliability scores and failure modes.
- Pytest suite, Docker support, and GitHub Actions CI.

## Repository Layout

```text
agentstress/
  agents/        Agent implementations and architecture variants
  analysis/      Research analysis and plotting helpers
  data/          Local ledger module and generated ledger output
  debate/        Multi-agent debate coordination
  evaluation/    Judges, rubrics, and validation helpers
  experiments/   Pilot and paper experiment runners
  metrics/       Reliability and behavior metrics
  security/      RSA signing and verification
dashboard/       Streamlit dashboard
docs/            Technical specification
tasks/           Task sets and rubrics
tests/           Unit and integration tests
main.py          CLI entry point
```

## Installation

Requires Python 3.11 or newer.

```bash
git clone https://github.com/MRYASHYT/agentstress.git
cd agentstress
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Copy the environment template and add your own keys:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | GPT agents and GPT judge |
| `ANTHROPIC_API_KEY` | Claude agents and Claude judge |
| `GOOGLE_API_KEY` | Gemini agents, Gemini judge, and some metrics |
| `AGENTSTRESS_KEY_PASS` | Passphrase for encrypting local RSA private keys |
| `AGENTSTRESS_MOCK` | Set to `True` for tests or dry runs without live model calls |

Do not commit `.env`, private keys, generated ledgers, or experiment outputs.

## Usage

Run a pilot audit:

```bash
python main.py --mode pilot
```

Run a larger experiment:

```bash
python main.py --mode experiment
```

Verify the local ledger:

```bash
python main.py --mode verify
```

Run the dashboard:

```bash
make run-dashboard
```

## Development

Run tests:

```bash
make test
```

Run lint and formatting checks:

```bash
make lint
```

Apply formatting:

```bash
make format
```

CI runs the test suite in mock mode, so pull requests do not need live provider secrets.

## Security Notes

AgentStress signs evaluation entries locally. New ledger entries include a previous-entry hash so append-only tampering can be detected. Legacy signed entries without a hash chain are still accepted for backward compatibility.

Local development may create:

- `.env`
- `security/keys/private_key.pem`
- `security/keys/public_key.pem`
- `agentstress/data/evaluation_ledger.jsonl`
- `results/`
- `paper/figures/`

These are ignored or excluded from Docker builds. Rotate or delete local keys before sharing a machine, image, or archive.

## Roadmap To A Strong Launch

The codebase is close to a credible beta. To claim a mature research or startup launch, complete the remaining validation work:

1. Run real Paper 1 and Paper 2 experiments with live model providers.
2. Generate result tables and figures from those runs.
3. Manually audit a random sample of traces and report human-vs-judge agreement.
4. Publish the dataset size, task categories, model versions, and limitations.
5. Keep the README claims aligned with measured results.

## License

MIT License. See [LICENSE](LICENSE).

## Citation

```bibtex
@software{gupta2026agentstress,
  author = {Gupta, Yash},
  title = {AgentStress: Reliability Stress Testing for Agentic AI Pipelines},
  year = {2026},
  url = {https://github.com/MRYASHYT/agentstress}
}
```
