import time
from VL53L0X import VL53L0X, Vl53l0xAccuracyMode
from dataclasses import dataclass
from typing import Self

@dataclass
class Tof:
    vl53l0x: VL53L0X

    @classmethod
    def new(cls, i2c_bus=1, i2c_address=0x29) -> Self:
        vl530x = VL53L0X(i2c_bus=i2c_bus, i2c_address=i2c_address)
        vl530x.open()
        vl530x.start_ranging(Vl53l0xAccuracyMode.BETTER)
        time.sleep(1)
        return cls(vl530x)

    def read(self, samples: int, sample_period_millis: int) -> float:
        distances: list[int] = []
        for _ in range(samples):
            distances.append(self.vl53l0x.get_distance())
            time.sleep(sample_period_millis / 1000)
        return sum(distances)/len(distances)

    def close(self):
        self.vl53l0x.stop_ranging()
        self.vl53l0x.close()

if __name__ == "__main__":
    tof = Tof.new()
    try:
        for _ in range(10):
            print("Distance: ", tof.read(100, 10))
    finally:
        tof.close()
