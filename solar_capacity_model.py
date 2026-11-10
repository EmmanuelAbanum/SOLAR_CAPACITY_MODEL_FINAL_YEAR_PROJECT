"""
B.Sc. solar PV laboratory capacity model (design estimates, not live telemetry).

Run: python solar_capacity_model.py

All power ratings are design assumptions and should be confirmed from equipment labels.
"""

from dataclasses import dataclass
import csv
from pathlib import Path


@dataclass(frozen=True)
class SolarDesign:
    panel_count: int = 18
    panel_w: float = 650.0
    array_derating: float = 0.80
    inverter_nameplate_kva: float = 12.0
    assumed_power_factor: float = 1.00
    ac_planning_factor: float = 0.90
    additional_energy_loss: float = 0.05
    battery_kwh: float = 20.0
    battery_usable_fraction: float = 0.90
    battery_to_ac_efficiency: float = 0.90
    computer_w: float = 125.0
    networking_units: int = 8
    networking_w: float = 25.0
    efficient_fans: int = 6
    efficient_fan_w: float = 20.0
    light_units: int = 10
    light_w: float = 20.0
    projectors: int = 2
    projector_w: float = 250.0
    lecture_hours: float = 2.0
    peak_sun_hours_example: float = 5.0

    @property
    def support_load_kw(self):
        watts = (
            self.networking_units * self.networking_w
            + self.efficient_fans * self.efficient_fan_w
            + self.light_units * self.light_w
            + self.projectors * self.projector_w
        )
        return watts / 1000.0

    @property
    def pv_kw_peak(self):
        return self.panel_count * self.panel_w / 1000.0

    @property
    def inverter_kw_planning_limit(self):
        # A planning estimate; manufacturer's real continuous
        # output is authoritative.
        return (
            self.inverter_nameplate_kva
            * self.assumed_power_factor
            * self.ac_planning_factor
        )

    def load_kw(self, computers: int):
        if computers < 0:
            raise ValueError("Computer count must be non-negative")

        return (
            computers * self.computer_w / 1000.0
            + self.support_load_kw
        )

    def lecture_energy_kwh(self, computers: int):
        return self.load_kw(computers) * self.lecture_hours

    def solar_power_kw_example(self):
        # Example near strong sunlight; NOT guaranteed every
        # hour of daylight.
        return (
            self.pv_kw_peak
            * self.array_derating
            / (1.0 + self.additional_energy_loss)
        )

    def daily_solar_energy_kwh_example(self):
        return (
            self.pv_kw_peak
            * self.array_derating
            * self.peak_sun_hours_example
        )

    def battery_backup_hours(self, computers: int):
        usable_ac_kwh = (
            self.battery_kwh
            * self.battery_usable_fraction
            * self.battery_to_ac_efficiency
        )
        return usable_ac_kwh / self.load_kw(computers)

    def minimum_battery_kwh(
        self,
        computers: int,
        target_hours: float
    ):
        return (
            self.load_kw(computers) * target_hours
            / (
                self.battery_usable_fraction
                * self.battery_to_ac_efficiency
            )
        )

    def sunshine_capacity_computers(self):
        available_kw = min(
            self.solar_power_kw_example(),
            self.inverter_kw_planning_limit
        )

        return max(
            0,
            int(
                (available_kw - self.support_load_kw)
                * 1000
                / self.computer_w
            )
        )


def main():
    design = SolarDesign()

    scenarios = [50, 60, 63, 64]
    rows = []

    for computers in scenarios:
        load = design.load_kw(computers)

        row = {
            "computers": computers,
            "ac_load_kw": round(load, 3),
            "lecture_2h_kwh": round(
                design.lecture_energy_kwh(computers), 3
            ),
            "sunny_pv_example_kw": round(
                design.solar_power_kw_example(), 3
            ),
            "sunny_pv_example_sufficient":
                load <= design.solar_power_kw_example(),
            "inverter_planning_limit_sufficient":
                load <= design.inverter_kw_planning_limit,
            "battery_20kwh_backup_hours": round(
                design.battery_backup_hours(computers), 2
            ),
        }

        rows.append(row)

        print(
            f"{computers} computers: load={load:.2f} kW; "
            f"class={row['lecture_2h_kwh']:.2f} kWh; "
            f"20-kWh backup={row['battery_20kwh_backup_hours']:.2f} h; "
            f"PV example strong sun={'YES' if row['sunny_pv_example_sufficient'] else 'NO'}"
        )

    # Checks to verify important calculations
    assert abs(design.load_kw(50) - 7.27) < 1e-9
    assert abs(design.load_kw(60) - 8.52) < 1e-9
    assert 2.0 <= design.battery_backup_hours(50) < 2.3
    assert design.sunshine_capacity_computers() == 63

    print(f"\nPV nameplate: {design.pv_kw_peak:.2f} kW")
    print(
        f"Strong-sun model AC: "
        f"{design.solar_power_kw_example():.2f} kW"
    )
    print(
        f"Minimum nominal storage for 50 computers / 2h: "
        f"{design.minimum_battery_kwh(50, 2):.2f} kWh"
    )
    print(
        f"Illustrative daily PV yield: "
        f"{design.daily_solar_energy_kwh_example():.2f} kWh"
    )
    print(
        "These are model predictions. Field testing and "
        "inverter/battery specifications are required."
    )

    with open(
        Path(__file__).with_name("solar_capacity_results.csv"),
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0])
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()