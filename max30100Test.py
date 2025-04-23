import time
from max30100 import MAX30100  

def main():
    sensor1 = MAX30100(mode=0x03)  # SPO2 mode
    sensor2 = MAX30100(mode=0x02)  # HR mode

    print("MAX30100 initialized. Reading sensor data...\n")
    try:
        while True:
            num_samples = sensor1.get_number_of_samples()

            for _ in range(num_samples):
                sensor1.read_sensor()
                sensor2.read_sensor()
                ir_value = sensor2.ir
                red_value = sensor1.red
                print(f"IR (Heart rate): {ir_value}, RED (SpO₂): {red_value}")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")
        sensor1.shutdown()
        sensor2.shutdown()


if __name__ == "__main__":
    main()