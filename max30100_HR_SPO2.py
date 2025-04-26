from max30100 import MAX30100
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

def detect_peaks(signal, threshold):
    peaks = []
    for i in range(1, len(signal)-1):
        if signal[i] > threshold and signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            peaks.append(i)
    return peaks

def calculate_bpm(peaks, times):
    if len(peaks) < 2:
        return None
    intervals = [times[peaks[i]] - times[peaks[i-1]] for i in range(1, len(peaks))]
    avg_interval = np.mean(intervals)
    return 60 / avg_interval if avg_interval > 0 else None

def basic_spo2_estimation(ir, red):
    if ir and red:
        ratio = red / (ir + 1)
        return max(0, min(100, 110 - 15 * ratio))
    return None

def main():
    sensor = MAX30100(
        mode=0x03,
        sample_rate=100,
        pulse_width=1600,
        led_current_red=27.1,
        led_current_ir=27.1
    )
    sensor.enable_spo2()

    # Ring buffers for live data
    ir_data = deque(maxlen=500)
    red_data = deque(maxlen=500)
    timestamps = deque(maxlen=500)

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)
    ax.set_title("IR Signal")
    ax.set_ylim(0, 70000)
    ax.set_xlim(0, 500)

    try:
        print("Monitoring... Press Ctrl+C to stop.")
        while True:
            sensor.read_sensor()
            ir = sensor.ir
            red = sensor.red
            t = time.time()

            if ir is None or ir < 1000:
                print("[WARN] No finger detected or weak signal.")
                time.sleep(0.1)
                continue

            ir_data.append(ir)
            red_data.append(red)
            timestamps.append(t)

            # Plot live signal
            line.set_ydata(ir_data)
            line.set_xdata(range(len(ir_data)))
            ax.set_ylim(min(ir_data)-500, max(ir_data)+500)
            fig.canvas.draw()
            fig.canvas.flush_events()

            # Peak detection
            if len(ir_data) > 100:
                peaks = detect_peaks(ir_data, threshold=np.mean(ir_data)*1.05)
                bpm = calculate_bpm(peaks, list(timestamps)) if peaks else None
            else:
                bpm = None

            spo2 = basic_spo2_estimation(ir, red)
            sensor.refresh_temperature()
            temp = sensor.get_temperature()

            print(f"Temp: {temp:.1f}°C | SpO2: {spo2:.1f}% | HR: {bpm:.1f} bpm" if bpm else "HR: --")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        plt.ioff()
        plt.close()

if __name__ == "__main__":
    main()
