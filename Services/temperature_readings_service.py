# temperature_readings_service.py
from Services.fan_service import toggle_fan

def update_sensor_data(sensor_data, topic, payload):
    """Update `sensor_data` dict using an incoming MQTT topic and payload.

    Expected topic formats:
      - "Frig1/temperature" or "Frig1/humidity"
      - "Frig2/temperature" or "Frig2/humidity"
    """
    try:
        parts = topic.split('/')
        fridge = parts[0]  # e.g. 'Frig1'
        field = parts[1] if len(parts) > 1 else None
        if fridge not in sensor_data:
            return
        if field == 'temperature':
            sensor_data[fridge]['temperature'] = float(payload)
            # run quick check
            handle_temperature(sensor_data[fridge]['temperature'], fridge)
        elif field == 'humidity':
            sensor_data[fridge]['humidity'] = float(payload)
    except Exception as e:
        print('Error updating sensor data:', e)


def handle_temperature(temp_value, location_name=None):
    """Handle temperature readings. If temperature crosses thresholds, take action.

    Current simple policy:
      - If temp > 10C: print warning and turn fan ON
      - If temp <= 8C: turn fan OFF
    Adjust thresholds to taste.
    """
    try:
        temp = float(temp_value)
        if temp > 10:
            print(f"Warning: {location_name or 'Fridge'} temperature too high: {temp}C — turning fan ON")
            try:
                toggle_fan(True)
            except Exception as e:
                print('Failed to toggle fan ON:', e)
        elif temp <= 8:
            print(f"{location_name or 'Fridge'} temperature back to normal: {temp}C — turning fan OFF")
            try:
                toggle_fan(False)
            except Exception as e:
                print('Failed to toggle fan OFF:', e)
        else:
            print(f"{location_name or 'Fridge'} temperature: {temp}C — monitoring")
    except Exception as e:
        print('Error handling temperature:', e)