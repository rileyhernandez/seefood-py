import time
from typing import Self
from dataclasses import dataclass
from qwiic_nau7802 import QwiicNAU7802
from ..config import Scale as ScaleConfig


@dataclass
class Scale:
    nau7802: QwiicNAU7802
    config: ScaleConfig

    @classmethod
    def new(cls, scale_config: ScaleConfig) -> Self:
        nau7802 = QwiicNAU7802()
        nau7802.begin()
        # Run analog front end calibration
        nau7802.calibrate_afe()
        time.sleep(1)

        # Throw away several startup readings until filter settles
        for _ in range(20):
            _ = nau7802.get_reading()
            time.sleep(0.05)
        return cls(nau7802, scale_config)

    def read(self) -> float:
        return self.nau7802.get_reading()

    def live_weigh(self) -> float:
        return self.read()*self.config.gain


if __name__ == "__main__":
    config = ScaleConfig(0.0013512, 100)
    scale = Scale.new(config)
    for _ in range(10):
        print("Weight: ", scale.live_weigh())
        time.sleep(0.25)