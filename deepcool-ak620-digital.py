import sys
import time
import hid
import psutil

# Default values for Vendor ID and Product ID
DEFAULT_VENDOR_ID = 0x3633  # DeepCool's Vendor ID
DEFAULT_PRODUCT_ID = 0x0002  # AK620's Product ID
INTERVAL = 2

# Check for command-line arguments and assign them if provided
VENDOR_ID = int(sys.argv[1], 0) if len(sys.argv) > 1 else DEFAULT_VENDOR_ID
PRODUCT_ID = int(sys.argv[2], 0) if len(sys.argv) > 2 else DEFAULT_PRODUCT_ID

def get_bar_value(input_value):
    return (input_value - 1) // 10 + 1

def get_data(value=0, mode='util'):
    base_data = [16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    numbers = [int(char) for char in str(value)]
    base_data[2] = get_bar_value(value)
    if mode == 'util':
        base_data[1] = 76
    elif mode == 'start':
        base_data[1] = 170
        return base_data
    elif mode == 'temp':
        base_data[1] = 19
    if len(numbers) == 1:
        base_data[5] = numbers[0]
    elif len(numbers) == 2:
        base_data[4] = numbers[0]
        base_data[5] = numbers[1]
    elif len(numbers) == 3:
        base_data[3] = numbers[0]
        base_data[4] = numbers[1]
        base_data[5] = numbers[2]
    elif len(numbers) == 4:
        base_data[3] = numbers[0]
        base_data[4] = numbers[1]
        base_data[5] = numbers[2]
        base_data[6] = numbers[3]
    return base_data

def get_cpu_temperature(label="CPU"):
    sensors = psutil.sensors_temperatures()
    for sensor_label, sensor_list in sensors.items():
        for sensor in sensor_list:
            if sensor.label == label:
                return sensor.current
    return 0

def get_temperature():
    try:
        temp = round(psutil.sensors_temperatures()['nct6687'][0].current)
    except KeyError:
        temp = get_cpu_temperature()
    return get_data(value=temp, mode='temp')

def get_utils():
    utils = round(psutil.cpu_percent())
    return get_data(value=utils, mode='util')

try:
    h = hid.device()
    h.open(VENDOR_ID, PRODUCT_ID)  # Use the dynamic values
    h.set_nonblocking(1)
    h.write(get_data(mode="start"))
    while True:
        h.set_nonblocking(1)
        temp = get_temperature()
        h.write(temp)
        time.sleep(INTERVAL)
        utils = get_utils()
        h.write(utils)
        time.sleep(INTERVAL)
except IOError as ex:
    print(ex)
    print("Ensure that the AK620 is connected and the script has the correct Vendor ID and Product ID.")
    print("Update the VENDOR_ID and PRODUCT_ID variables in this script or pass them as command-line arguments.")
except KeyboardInterrupt:
    print("Script terminated by user.")
finally:
    if 'h' in locals():
        h.close()
