from datetime import datetime


def get_current_datetime() -> str:
    """Returns the current date and time.
    
    Returns:
        The current date and time in the format 'YYYY-MM-DD HH:MM:SS TZ'.
    """
    # Use a default timezone or system timezone
    # For better consistency, let's use UTC or EST as a default, or try to detect
    # But for a simple tool, returning local system time is usually expected unless specified
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

def analyze_portfolio_risk(file_path: str) -> str:
    """Analyzes a portfolio CSV for concentration risk.
    
    Expects a CSV with columns: 'Symbol' (or 'Ticker'), 'Market Value' (or 'Value'), and optionally 'Sector'.
    
    Args:
        file_path: Absolute path to the portfolio CSV file.
        
    Returns:
        A markdown-formatted analysis of the portfolio.
    """
    import csv
    import os
    from collections import defaultdict

    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        positions = []
        total_value = 0.0
        sector_allocations = defaultdict(float)
        
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # Normalize headers
            headers = [h.lower() for h in reader.fieldnames] if reader.fieldnames else []
            
            # Identify columns
            symbol_col = next((h for h in reader.fieldnames if h.lower() in ['symbol', 'ticker', 'instrument']), None)
            value_col = next((h for h in reader.fieldnames if h.lower() in ['market value', 'value', 'amount', 'current value']), None)
            sector_col = next((h for h in reader.fieldnames if h.lower() in ['sector', 'industry', 'category']), None)
            
            if not symbol_col or not value_col:
                return f"Error: Could not identify 'Symbol' and 'Market Value' columns. Found: {reader.fieldnames}"
                
            for row in reader:
                try:
                    symbol = row[symbol_col]
                    # Clean value string (remove $ and ,)
                    val_str = row[value_col].replace('$', '').replace(',', '').strip()
                    if not val_str: continue
                    
                    value = float(val_str)
                    sector = row[sector_col] if sector_col else "Unknown"
                    
                    positions.append({'symbol': symbol, 'value': value, 'sector': sector})
                    total_value += value
                    sector_allocations[sector] += value
                    
                except ValueError:
                    continue # Skip invalid rows

        if total_value == 0:
            return "Error: Total portfolio value is 0."

        # Analysis
        positions.sort(key=lambda x: x['value'], reverse=True)
        top_holdings = positions[:5]
        
        output = [f"## Portfolio Analysis for {os.path.basename(file_path)}", ""]
        output.append(f"**Total Value:** ${total_value:,.2f}")
        output.append("")
        
        output.append("### Top 5 Holdings (Concentration risk)")
        for p in top_holdings:
            weight = (p['value'] / total_value) * 100
            output.append(f"- **{p['symbol']}**: {weight:.1f}% (${p['value']:,.2f})")
            
        output.append("")
        output.append("### Sector Allocation")
        sorted_sectors = sorted(sector_allocations.items(), key=lambda x: x[1], reverse=True)
        for sector, value in sorted_sectors:
            weight = (value / total_value) * 100
            output.append(f"- **{sector}**: {weight:.1f}%")
            
        # Risk Flags
        output.append("")
        output.append("### Risk Warnings")
        if top_holdings and (top_holdings[0]['value'] / total_value) > 0.10:
            output.append(f"- ⚠️ **High Single Stock Concentration**: {top_holdings[0]['symbol']} is >10% of portfolio.")
            
        if any((val / total_value) > 0.25 for val in sector_allocations.values()):
             output.append("- ⚠️ **High Sector Concentration**: One or more sectors make up >25% of portfolio.")
             
        if not output[-1].startswith("-"):
            output.append("- No immediate major concentration risks detected.")

        return "\n".join(output)

    except Exception as e:
        return f"Error analyzing portfolio: {str(e)}"
