from typing import Union

def natural_bitrate(value: Union[int, float]) -> str:
    """
    Format a bitrate value (bps) into a human-readable string using SI units (1000-based).
    
    Args:
        value: Bitrate in bits per second (bps).
        
    Returns:
        Human-readable bitrate string (e.g., "1 kbps", "5.2 Mbps", "10 Gbps").
    """
    units = ["bps", "kbps", "Mbps", "Gbps", "Tbps"]
    unit_index = 0
    
    while value >= 1000 and unit_index < len(units) - 1:
        value /= 1000
        unit_index += 1
    
    if unit_index == 0:
        return f"{value:.0f} {units[unit_index]}"
    else:
        return f"{value:.1f} {units[unit_index]}"