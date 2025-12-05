from __future__ import annotations


def natural_bitrate(value: float) -> str:
    """将比特率数值转换为人类可读的字符串格式。

    Args:
        value: 比特率数值，单位为bps (bits per second)

    Returns:
        格式化后的字符串，如 "1 kbps"、"5.2 Mbps" 等

    注意：使用1000进制 (SI Standard)，而非1024。
    单位范围覆盖：bps 到 Tbps
    """
    if value < 0:
        raise ValueError("Bitrate value cannot be negative")

    units = [
        "bps",
        "kbps",
        "Mbps",
        "Gbps",
        "Tbps",
    ]

    for i, unit in enumerate(units):
        if value < 1000:
            if i == 0:
                # 对于 bps，不保留小数
                return f"{int(value)} {unit}"
            else:
                # 对于其他单位，保留一位小数
                return f"{value:.1f} {unit}"
        value /= 1000

    # 如果值超过 Tbps，使用 Tbps 并保留一位小数
    return f"{value:.1f} {units[-1]}"
