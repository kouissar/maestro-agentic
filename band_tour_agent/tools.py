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
