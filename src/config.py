from dataclasses import dataclass

@dataclass
class Scale:
    gain: float
    sample_period_millis: int

@dataclass
class Tof:
    sample_period_millis: int

@dataclass
class Camera:
    device_index: int
    max_dim: int
    warmup_frames: int
    burst_size: int