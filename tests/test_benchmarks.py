"""Tests for benchmark comparison logic."""

from aggregator.benchmarks import classify_skill, compute_metrics


def test_classify_skill_tp():
    aguara_cats = {"prompt-injection"}
    vendor_flags = {("agent-trust-hub", "PROMPT_INJECTION")}
    result = classify_skill(aguara_cats, vendor_flags)
    assert result["prompt-injection"]["result"] == "TP"


def test_classify_skill_fp():
    aguara_cats = {"prompt-injection"}
    vendor_flags = set()  # no vendor flags
    result = classify_skill(aguara_cats, vendor_flags)
    assert result["prompt-injection"]["result"] == "FP"


def test_classify_skill_fn():
    aguara_cats = set()  # Aguara missed it
    vendor_flags = {("agent-trust-hub", "PROMPT_INJECTION")}
    result = classify_skill(aguara_cats, vendor_flags)
    assert result["prompt-injection"]["result"] == "FN"


def test_classify_skill_tn():
    aguara_cats = set()
    vendor_flags = set()
    result = classify_skill(aguara_cats, vendor_flags)
    assert result["prompt-injection"]["result"] == "TN"


def test_compute_metrics_perfect():
    comparisons = {
        "skill-1": {
            "classification": {
                "prompt-injection": {"result": "TP"},
                "exfiltration": {"result": "TN"},
                "credential-leak": {"result": "TN"},
                "supply-chain": {"result": "TN"},
                "external-download": {"result": "TN"},
                "command-execution": {"result": "TN"},
                "indirect-injection": {"result": "TN"},
                "third-party-content": {"result": "TN"},
                "unicode-attack": {"result": "TN"},
                "mcp-config": {"result": "TN"},
                "rug-pull": {"result": "TN"},
                "toxic-flow": {"result": "TN"},
            }
        }
    }
    metrics = compute_metrics(comparisons)
    assert metrics["overall"]["precision"] == 1.0
    assert metrics["overall"]["recall"] == 1.0
    assert metrics["overall"]["f1"] == 1.0


def test_compute_metrics_with_errors():
    comparisons = {
        "s1": {"classification": {"prompt-injection": {"result": "TP"}, "exfiltration": {"result": "FP"},
                                   "credential-leak": {"result": "TN"}, "supply-chain": {"result": "FN"},
                                   "external-download": {"result": "TN"}, "command-execution": {"result": "TN"},
                                   "indirect-injection": {"result": "TN"}, "third-party-content": {"result": "TN"},
                                   "unicode-attack": {"result": "TN"}, "mcp-config": {"result": "TN"},
                                   "rug-pull": {"result": "TN"}, "toxic-flow": {"result": "TN"}}},
    }
    metrics = compute_metrics(comparisons)
    # 1 TP, 1 FP, 1 FN
    assert metrics["overall"]["tp"] == 1
    assert metrics["overall"]["fp"] == 1
    assert metrics["overall"]["fn"] == 1
    assert metrics["overall"]["precision"] == 0.5
    assert metrics["overall"]["recall"] == 0.5
