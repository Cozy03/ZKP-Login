import json
import random
import time

def generate_temperature(device_id, above_37=False):
    if above_37:
        temperature = round(random.uniform(37.0, 40.0), 2)
    else:
        temperature = round(random.uniform(25.0, 37.0), 2)
    return {
        "device_id": device_id,
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "temp": temperature
    }

def generate_temperature_data(device_id, above_37=False):
    data = []
    for i in range(7):
        temperature_data = generate_temperature(device_id, above_37)
        data.append(temperature_data)
    return data

def send_temperature_data(data):
    for temperature_data in data:
        json_data = json.dumps(temperature_data)
        print(json_data)
        time.sleep(3)

# device_id = "DEVICE001"

# # Generate temperature data above 37
# temperature_data_above_37 = generate_temperature_data(device_id, above_37=True)
# send_temperature_data(temperature_data_above_37)

# # Generate temperature data below 37
# temperature_data_below_37 = generate_temperature_data(device_id, above_37=False)
# send_temperature_data(temperature_data_below_37)