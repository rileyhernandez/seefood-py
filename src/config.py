from dataclasses import dataclass
import tomllib


@dataclass
class Device:
    model: str
    serial: str


@dataclass
class Scale:
    gain: float
    offset: float
    sample_period_millis: int
    samples: int


@dataclass
class Camera:
    device_index: int
    width: int
    height: int
    pix_fmt: str
    fps: int
    brightness: int
    contrast: int
    saturation: int
    gain: int
    white_balance_temp: int
    sharpness: int
    auto_exposure: int
    exposure_time: int
    focus_absolute: int
    focus_auto_continuous: int
    white_balance_auto: int

@dataclass
class Button:
    pin: int

@dataclass
class RedLed:
    pin: int

@dataclass
class GreenLed:
    pin: int

@dataclass
class Config:
    device: Device
    scale: Scale
    camera: Camera
    button: Button
    red_led: RedLed
    green_led: GreenLed


def load_config(filepath: str) -> Config:
    with open(filepath, 'rb') as f:
        data = tomllib.load(f)

    return Config(
        device=Device(**data['device']),
        scale=Scale(**data['scale']),
        camera=Camera(**data['camera']),
        button=Button(**data['button']),
        red_led=RedLed(**data['red_led']),
        green_led=GreenLed(**data['green_led'])
    )
