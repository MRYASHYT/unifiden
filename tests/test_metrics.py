import pytest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentstress.metrics.primary_metrics import PrimaryMetrics
from agentstress.metrics.advanced_metrics import AdvancedMetrics


def test_primary_metrics():
    assert PrimaryMetrics.calculate_completion_rate(95.0) == True
    assert PrimaryMetrics.calculate_completion_rate(80.0) == False
    assert PrimaryMetrics.calculate_completeness_score(5, 10) == 5.0


def test_advanced_metrics_initialization():
    # Requires GOOGLE_API_KEY
    if os.getenv("GOOGLE_API_KEY"):
        adv = AdvancedMetrics()
        adv._setup_client()
        assert adv.client is not None
