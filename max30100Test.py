import time
import max30100  

def main():
    sensor = max30100(mode=0x03)  # SPO2 mode

    print("MAX30100 initialized. Reading sensor data...\n")
    try:
        while True:
            num_samples = sensor.get_number_of_samples()

            for _ in range(num_samples):
                sensor.read_sensor()
                ir_value = sensor.ir
                red_value = sensor.red
                print(f"IR (Heart rate): {ir_value}, RED (SpO₂): {red_value}")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting...")
        sensor.shutdown()

if __name__ == "__main__":
    main()