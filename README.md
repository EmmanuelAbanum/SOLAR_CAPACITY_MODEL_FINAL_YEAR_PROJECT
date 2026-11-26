# Solar PV Capacity Model

A Python-based program developed to evaluate the capacity and expected performance of an expanded solar photovoltaic system.

## Project Overview

This project was developed as part of a final-year project involving the expansion of an existing solar infrastructure.

The Python program calculates the electrical load the solar infrastructure is expected to carry and evaluates different computer capacity scenarios. It also estimates battery backup time when solar power is insufficient and estimates the energy contribution of the solar photovoltaic array.

## Features

The program calculates:

- Total connected electrical load
- Energy required for a two-hour lecture period
- Estimated solar PV contribution under strong sunlight
- Inverter planning capacity
- Estimated battery backup time

## Technologies Used

- Python 3
- CSV
- Dataclasses
- Pathlib

## How to Run

1. Clone this repository.
2. Navigate into the project folder.
3. Run the following command:

```bash
python solar_capacity_model.py
```

## Output

The program generates a CSV file named `solar_capacity_results.csv`, containing results for different computer capacity scenarios.

## Disclaimer

This program provides design estimates and is not connected to a live solar monitoring system. Equipment ratings and assumptions should be confirmed using actual system specifications.