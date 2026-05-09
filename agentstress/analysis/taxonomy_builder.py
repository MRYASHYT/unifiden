import json


class TaxonomyBuilder:
    """Aggregates failure modes into the 8-mode taxonomy format."""

    @staticmethod
    def build_taxonomy(results_data: list) -> dict:
        taxonomy_counts = {
            "NO_FAILURE": 0,
            "INSTRUCTION_DRIFT": 0,
            "PREMATURE_TERMINATION": 0,
            "TOOL_CALL_HALLUCINATION": 0,
            "OVERCONFIDENCE_COLLAPSE": 0,
            "STUBBORN_FAILURE": 0,
            "CONTAMINATION": 0,
            "PARTIAL_FAILURE": 0,
        }

        for res in results_data:
            mode = res.get("failure_mode", "UNKNOWN")
            if mode in taxonomy_counts:
                taxonomy_counts[mode] += 1

        return taxonomy_counts
