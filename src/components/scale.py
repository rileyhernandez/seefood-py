import time
from typing import Self
from dataclasses import dataclass

from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
from qwiic_nau7802 import QwiicNAU7802
# from config import Scale as ScaleConfig

'''
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
'''

@dataclass
class Phidget:
    vin: VoltageRatioInput
    gain: float
    offset: float

    @classmethod
    def new(cls, gain: float, offset: float) -> Self:
        vin = VoltageRatioInput()
        vin.setChannel(0)
        vin.openWaitForAttachment(2000)
        time.sleep(2)
        return cls(vin, gain, offset)

    def read(self) -> float:
        return self.vin.getVoltageRatio()

    def read_median(self, samples: int, sample_period_millis: int) -> float:
        readings: list[float] = []
        for _ in range(samples):
            readings.append(self.read())
            time.sleep(sample_period_millis / 1000)
        return sorted(readings)[samples // 2]

    def calibrate(self):
        input("Clear scale and press enter to calibrate...")
        zero_reading = self.read_median(100, 10)
        test_weight = float(input("Add test weight and enter its mass in grams: \n"))
        test_reading = self.read_median(8, 250)
        print("Gain: ", test_weight/(test_reading - zero_reading))
        print("Offset: ", zero_reading)

    def weigh(self) -> float:
        return (self.read() - self.offset) * self.gain

    def weigh_median(self, samples: int, sample_period_millis: int) -> float:
        return (self.read_median(samples, sample_period_millis) - self.offset) * self.gain

    def diagnose(self):
        weights: list[float] = []
        for _ in range(100):
            weights.append(self.weigh())
            time.sleep(0.250)
        print(f"Max weight: {max(weights)}\nMin weight: {min(weights)}\nRange: {max(weights)-min(weights)}\nMedian weight: {sorted(weights)[50]}")



if __name__ == "__main__":
    # config = ScaleConfig(0.0013512, 100)
    # scale = Scale.new(config)
    # for _ in range(10):
    #     print("Weight: ", scale.live_weigh())
    #     time.sleep(0.25)

    phidget = Phidget.new(9775979.599626426, 0.0001310482621192932)
    # weight = phidget.weigh_median(8, 250)
    # print("Weight: ", weight)
    # phidget.calibrate()
    phidget.diagnose()