"""Tests for vendor audit parsers."""

from crawlers.vendor_audits import parse_agent_trust_hub, parse_socket, parse_snyk


def test_parse_ath_pass():
    html = '<div>Verdict: Pass Risk Level: Safe</div>'
    result = parse_agent_trust_hub(html)
    assert result["verdict"] == "Pass"


def test_parse_ath_fail_with_findings():
    html = '''
    Verdict: Fail
    Risk Level: High
    PROMPT_INJECTION severity HIGH detected
    DATA_EXFILTRATION severity MEDIUM detected
    NO_CODE informational
    '''
    result = parse_agent_trust_hub(html)
    assert result["verdict"] == "Fail"
    assert any(f["category"] == "PROMPT_INJECTION" for f in result["findings"])
    assert any(f["category"] == "DATA_EXFILTRATION" for f in result["findings"])
    # NO_CODE should also appear (parser doesn't filter, benchmark code filters)
    assert any(f["category"] == "NO_CODE" for f in result["findings"])


def test_parse_socket_clean():
    html = '<div>No alerts found</div>'
    result = parse_socket(html)
    assert result["verdict"] == "clean"
    assert result["alert_count"] == 0


def test_parse_socket_with_alerts():
    html = '''
    3 alerts found
    SC006: third-party script
    CI003: backtick substitution
    Malware detected
    Confidence: 85%
    '''
    result = parse_socket(html)
    assert result["alert_count"] == 3
    assert any(a.get("code") == "SC006" for a in result["alerts"])
    assert any(a.get("code") == "CI003" for a in result["alerts"])
    assert any(a.get("category") == "Malware" for a in result["alerts"])
    assert result["confidence_pct"] == 85


def test_parse_snyk_clean():
    html = '<div>Risk Score: 0.1 Low risk</div>'
    result = parse_snyk(html)
    assert result["risk_score"] == 0.1
    assert result["risk_level"] == "Low"
    assert len(result["findings"]) == 0


def test_parse_snyk_with_findings():
    html = '''
    Risk Score: 0.8
    Risk Level: High
    W007 Insecure Credential Handling
    W011 Third-Party Content Exposure
    '''
    result = parse_snyk(html)
    assert result["risk_score"] == 0.8
    assert len(result["findings"]) == 2
    codes = [f["code"] for f in result["findings"]]
    assert "W007" in codes
    assert "W011" in codes
