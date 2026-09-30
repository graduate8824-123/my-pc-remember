from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .device import get_hardware_profile
from ..core.logging import logger

class InferenceBackend(ABC):
    """
    Hardware abstraction interface for model inference.
    Decouples semantic search and embedding generation from specific NPU/CPU architectures.
    """

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def target_device(self) -> str:
        pass

    @abstractmethod
    def is_hardware_accelerated(self) -> bool:
        pass

    @abstractmethod
    def get_specs(self) -> Dict[str, Any]:
        pass


class CPUInferenceBackend(InferenceBackend):
    """
    Current development backend for Apple Silicon Mac (M1 8GB).
    Uses quantized ONNX Runtime (CPUExecutionProvider) and ARM NEON vector instructions.
    Low power consumption, zero cloud dependency.
    """

    def name(self) -> str:
        return "CPU / Apple Silicon Backend"

    def target_device(self) -> str:
        return "Apple Silicon M1 (ARM64 / CPU)"

    def is_hardware_accelerated(self) -> bool:
        return False

    def get_specs(self) -> Dict[str, Any]:
        profile = get_hardware_profile()
        return {
            "backend": self.name(),
            "target": self.target_device(),
            "npu_accelerated": False,
            "architecture": profile["machine"],
            "notes": "Quantized CPU inference optimized for 8GB RAM laptops."
        }


class FutureSnapdragonBackend(InferenceBackend):
    """
    Target deployment backend for Snapdragon X Elite / AI PC.
    When ported to Snapdragon hardware, this uses the Qualcomm Neural Processing SDK (QNN)
    or ONNX Runtime QNNExecutionProvider for 45+ TOPS Hexagon NPU acceleration.
    """

    def name(self) -> str:
        return "Snapdragon AI Hexagon NPU Backend"

    def target_device(self) -> str:
        return "Qualcomm Snapdragon X Elite (Hexagon NPU)"

    def is_hardware_accelerated(self) -> bool:
        return True

    def get_specs(self) -> Dict[str, Any]:
        return {
            "backend": self.name(),
            "target": self.target_device(),
            "npu_accelerated": True,
            "acceleration_provider": "QNNExecutionProvider / DirectML",
            "target_npu": "Qualcomm Hexagon NPU",
            "notes": "Seamless drop-in replacement for the Snapdragon AI Lab Build & Present Challenge."
        }


def get_inference_backend() -> InferenceBackend:
    profile = get_hardware_profile()
    if profile.get("is_snapdragon"):
        return FutureSnapdragonBackend()
    return CPUInferenceBackend()
