import time
from typing import Self
from cedargrove_nau7802 import NAU7802  # type: ignore
from dataclasses import dataclass
import board   # type: ignore
import sys
sys.modules['digitalio'] = object()


@dataclass
class Scale:
    nau7802: NAU7802
    gain: float
    offset: float
    sample_period_millis: int

    @classmethod
    def new(cls, gain: float, offset: float, sample_period_millis: int = 250) -> Self:
        nau7802 = NAU7802(board.I2C(), address=0x2A, active_channels=1)
        nau7802.reset()
        nau7802.enable()
        return cls(nau7802, gain, offset, sample_period_millis)

    def read(self) -> float:
        return self.nau7802.read()
    #
    # def live_weigh(self) -> float:
    #     return self.read()*self.gain + self.offset
    #
    # def weigh(self, samples) -> float:
    #     weights: list[float] = []
    #     for _sample in range(samples):
    #         weights += [self.live_weigh()]
    #         time.sleep(self.sample_period_millis/1000)
    #     weights.sort()
    #     return weights[samples//2]

if __name__ == "__main__":
    scale = Scale.new(gain=10072484.2624, offset=35.065176)
    for _ in range(10):
        print("Weight: ", scale.read())
        time.sleep(0.25)