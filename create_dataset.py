"""
create_dataset.py
-----------------
Generates a realistic crop_data.csv file with sample agricultural data.
Run this script ONCE to populate the dataset folder.
 
Usage:
    python create_dataset.py
"""
 
import csv
import random
import os
 
# ─────────────────────────────────────────────
# Crop profiles: each crop has realistic ranges
# for rainfall (mm), temperature (°C), and yield (tons/hectare)
# ─────────────────────────────────────────────
CROP_PROFILES = {
    "Rice": {
        "rainfall": (900, 2000),    # mm per year
        "temperature": (20, 35),    # °C
        "area": (0.5, 10.0),        # hectares
        "base_yield": (2.5, 6.0),   # tons per hectare
    },
    "Wheat": {
        "rainfall": (300, 900),
        "temperature": (10, 25),
        "area": (0.5, 12.0),
        "base_yield": (2.0, 5.0),
    },
    "Maize": {
        "rainfall": (500, 1200),
        "temperature": (18, 32),
        "area": (0.5, 8.0),
        "base_yield": (3.0, 7.5),
    },
    "Sugarcane": {
        "rainfall": (1000, 1800),
        "temperature": (24, 38),
        "area": (1.0, 15.0),
        "base_yield": (40.0, 80.0),  # higher because sugarcane yields are in tons
    },
    "Cotton": {
        "rainfall": (500, 1000),
        "temperature": (22, 35),
        "area": (0.5, 10.0),
        "base_yield": (1.0, 3.5),
    },
    "Soybean": {
        "rainfall": (450, 900),
        "temperature": (15, 30),
        "area": (0.5, 8.0),
        "base_yield": (1.5, 4.0),
    },
    "Potato": {
        "rainfall": (400, 800),
        "temperature": (10, 22),
        "area": (0.2, 5.0),
        "base_yield": (15.0, 40.0),
    },
    "Tomato": {
        "rainfall": (400, 700),
        "temperature": (18, 28),
        "area": (0.2, 4.0),
        "base_yield": (20.0, 60.0),
    },
}
 
def calculate_yield(crop, rainfall, temperature, area):
    """
    Simulates a realistic yield calculation based on:
    - Crop's base yield range
    - Bonus/penalty for rainfall being in optimal range
    - Bonus/penalty for temperature being in optimal range
    - Slight random noise to simulate real-world variation
    """
    profile = CROP_PROFILES[crop]
 
    # Base yield = random value within the crop's normal range
    base = random.uniform(*profile["base_yield"])
 
    # Rainfall factor: check if rainfall is close to the midpoint (optimal)
    rain_min, rain_max = profile["rainfall"]
    rain_mid = (rain_min + rain_max) / 2
    rain_deviation = abs(rainfall - rain_mid) / (rain_max - rain_min)
    rain_factor = 1.0 - (rain_deviation * 0.3)   # up to ±30% impact
 
    # Temperature factor: same logic
    temp_min, temp_max = profile["temperature"]
    temp_mid = (temp_min + temp_max) / 2
    temp_deviation = abs(temperature - temp_mid) / (temp_max - temp_min)
    temp_factor = 1.0 - (temp_deviation * 0.25)  # up to ±25% impact
 
    # Random noise: ±10%
    noise = random.uniform(0.90, 1.10)
 
    # Final yield = base × factors × area (total production)
    total_yield = base * rain_factor * temp_factor * noise * area
 
    return round(total_yield, 2)
 
 
def generate_dataset(num_records=500, output_path="dataset/crop_data.csv"):
    """
    Generates 'num_records' rows of synthetic crop data
    and saves to a CSV file.
    """
    # Make sure the dataset folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
 
    crop_names = list(CROP_PROFILES.keys())
 
    # CSV column headers
    fieldnames = ["crop", "rainfall", "temperature", "area", "yield"]
 
    rows = []
 
    for _ in range(num_records):
        # Pick a random crop
        crop = random.choice(crop_names)
        profile = CROP_PROFILES[crop]
 
        # Generate random values within that crop's realistic range
        rainfall    = round(random.uniform(*profile["rainfall"]), 1)
        temperature = round(random.uniform(*profile["temperature"]), 1)
        area        = round(random.uniform(*profile["area"]), 2)
 
        # Calculate yield based on the values
        yield_val = calculate_yield(crop, rainfall, temperature, area)
 
        rows.append({
            "crop":        crop,
            "rainfall":    rainfall,
            "temperature": temperature,
            "area":        area,
            "yield":       yield_val,
        })
 
    # Write to CSV
    with open(output_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
 
    print(f"✅ Dataset created: '{output_path}'")
    print(f"   Total records : {num_records}")
    print(f"   Crops covered : {', '.join(crop_names)}")
    print(f"   Columns       : {', '.join(fieldnames)}")
 
 
# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    generate_dataset(
        num_records=500,                    # Change to generate more/fewer rows
        output_path="dataset/crop_data.csv" # Saves inside the dataset/ folder
    )