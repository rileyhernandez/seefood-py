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

        # idk if i need this?
        timing = vl530x.get_timing()
        if timing < 20_000:
            timing = 20_000
        print("Timing %d ms" % (timing / 1000))
        time.sleep(timing/1_000_000)

        vl530x.stop_ranging()
        # tof.close()
        return cls(vl530x)

    def read(self, samples: int, sample_period_millis: int) -> float:
        self.vl53l0x.start_ranging(Vl53l0xAccuracyMode.BETTER)
        distances: list[int] = []
        for _ in range(samples):
            distances.append(self.vl53l0x.get_distance())
            time.sleep(sample_period_millis / 1000)
        self.vl53l0x.stop_ranging()
        return sum(distances)/len(distances)

    def close(self):
        self.vl53l0x.close()

if __name__ == "__main__":
    tof = Tof.new()
    for _ in range(10):
        print("Distance: ", tof.read(100, 10))
    tof.close()

# tof = VL53L0X(i2c_bus=1, i2c_address=0x29)
# tof.open()
# tof.start_ranging(Vl53l0xAccuracyMode.BETTER)
#
# timing = tof.get_timing()
# if timing < 20_000:
#     timing = 20_000
# print("Timing %d ms" % (timing / 1000))
#
# for count in range(1, 1001):
#     distance = tof.get_distance()
#     if distance > 0:
#         print("%d mm, %d cm, %d" % (distance, (distance/10), count))
#     time.sleep(timing/1_000_000.00)
#
# tof.stop_ranging()
# tof.close()
