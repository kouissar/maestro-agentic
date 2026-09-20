import os
import pytest
from finance_agent.tools import analyze_portfolio_risk, get_current_datetime

def test_get_current_datetime():
    dt = get_current_datetime()
    assert isinstance(dt, str)
    assert len(dt) > 10

def test_analyze_portfolio_risk_valid():
    csv_path = os.path.join(os.path.dirname(__file__), "sample_portfolio.csv")
    result = analyze_portfolio_risk(csv_path)
    
    assert "Portfolio Analysis" in result
    assert "Total Value" in result
    assert "AAPL" in result
    assert "Technology" in result
    assert "High Sector Concentration" in result # 35k technology out of 47k total is > 25%

def test_analyze_portfolio_risk_invalid_path():
    result = analyze_portfolio_risk("non_existent.csv")
    assert "Error: File not found" in result

def test_analyze_portfolio_risk_empty_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "empty.csv"
    p.write_text("")
    
    # DictReader on empty file results in no rows, which triggers "could not identify columns" or similar
    result = analyze_portfolio_risk(str(p))
    assert "Error" in result
