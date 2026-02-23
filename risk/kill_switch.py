def should_pause(consecutive_losses: int, rolling_pf: float, rolling_expectancy: float, rolling_dd_r: float) -> bool:
    if consecutive_losses >= 6:
        return True
    if rolling_pf < 1.1:
        return True
    if rolling_expectancy < 0:
        return True
    if rolling_dd_r <= -10:
        return True
    return False
