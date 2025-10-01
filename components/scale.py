import time
from typing import Self
from dataclasses import dataclass
from qwiic_nau7802 import QwiicNAU7802


@dataclass
class Scale:
    nau7802: QwiicNAU7802
    gain: float
    offset: float
    sample_period_millis: int

    @classmethod
    def new(cls, gain: float, offset: float, sample_period_millis: int = 250) -> Self:
        nau7802 = QwiicNAU7802()
        nau7802.begin()
        # Run analog front end calibration
        nau7802.calibrate_afe()
        time.sleep(0.5)

        # Throw away several startup readings until filter settles
        for _ in range(20):
            _ = nau7802.get_reading()
            time.sleep(0.05)
        return cls(nau7802, gain, offset, sample_period_millis)

    def read(self) -> float:
        return self.nau7802.get_reading()

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