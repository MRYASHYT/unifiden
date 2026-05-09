# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-05-08
### Added
- Complete Multi-Agent Debate Protocol (4 Rounds).
- 5 Agent Architectures (ReAct, Plan-and-Execute, Reflexion, Claude-ReAct, LangGraph).
- Semantic Rubric Engine using LLMs.
- RSA-4096 Cryptographic Local Ledger.
- Advanced Behavioral Metrics (Stubbornness, Overconfidence Collapse, Drift).
- `AUDIT_OS` Command Center Dashboard.
- Full 30-Task benchmark suite across 3 clarity levels.

### Changed
- Rebranded framework to AgentStress.
- Upgraded models to `gpt-4o` and `claude-3-5-sonnet-latest`.

## [1.1.0] - 2026-05-10
### Added
- **Cryptographic Hash-Chaining**: Upgraded the local ledger to use a tamper-evident Merkle-tree style hash chain.
- **Network Resilience**: Integrated `tenacity` for exponential backoff on all API calls (OpenAI, Anthropic, Google) to prevent crashes on rate limits or server errors.
- **SDK Modernization**: Completely migrated from deprecated `google.generativeai` to the modern `google.genai` SDK.

### Security
- **Strict Secret Management**: Eliminated fallback passphrases. `AGENTSTRESS_KEY_PASS` must now be securely provided via environment variables.

