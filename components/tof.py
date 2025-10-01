import time
import VL53L0X

tof = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=0x29)
tof.open()
tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)

timing = tof.get_timing()
if timing < 20_000:
    timing = 20_000
print("Timing %d ms" % (timing / 1000))

for count in range(1, 1001):
    distance = tof.get_distance()
    if distance > 0:
        print("%d mm, %d cm, %d" % (distance, (distance/10), count))
    time.sleep(timing/1_000_000.00)

tof.stop_ranging()
tof.close()
