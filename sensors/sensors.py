import random
from datetime import datetime

def get_sensor_data():
    """Simulate scalp sensor readings."""
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": round(random.uniform(36.0, 38.5), 1),
        "moisture": round(random.uniform(50, 80), 1),
        "tension": round(random.uniform(3, 7), 1)
    }
    return data
