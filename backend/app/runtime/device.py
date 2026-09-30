import platform
import os
from typing import Dict, Any

def get_hardware_profile() -> Dict[str, Any]:
    """
    Identifies host hardware platform objectively.
    Does NOT falsely claim Snapdragon NPU execution on macOS.
    """
    sys_name = platform.system()
    machine = platform.machine()
    proc = platform.processor()

    is_mac_apple_silicon = sys_name == "Darwin" and machine.startswith("arm")
    is_snapdragon = "qualcomm" in proc.lower() or "snapdragon" in proc.lower() or "sc8" in proc.lower()

    # Detect execution provider
    if is_snapdragon:
        target = "Snapdragon X Elite / Snapdragon AI"
        npu_supported = True
    elif is_mac_apple_silicon:
        target = "Apple Silicon (MacBook M1 / ARM64)"
        npu_supported = False
    else:
        target = f"{sys_name} ({machine})"
        npu_supported = False

    return {
        "os": sys_name,
        "machine": machine,
        "processor": proc,
        "is_mac_apple_silicon": is_mac_apple_silicon,
        "is_snapdragon": is_snapdragon,
        "active_device": "CPU / Apple Silicon Local Execution" if not is_snapdragon else "Qualcomm Hexagon NPU",
        "npu_available": npu_supported,
        "hardware_target": target,
        "memory_friendly": True
    }
