"""Utility to compute running paces and speeds by VMA percentages.

Run as a script:
    python vma_calc.py --vma 16 --allure 4:15
"""
from __future__ import annotations

import argparse
import json
import re
from typing import List, Dict


def pace_to_speed_kmh(pace: str) -> float:
    """Convert a pace string (min:sec per km) to km/h.

    Accepts formats like "4:15" or "04:15". Raises ValueError for invalid inputs.
    """
    if not isinstance(pace, str):
        raise ValueError("L'allure doit être une chaîne de caractères au format mm:ss")

    match = re.fullmatch(r"\s*(\d+):(\d{1,2})\s*", pace)
    if not match:
        raise ValueError("Format d'allure invalide. Utiliser mm:ss, par ex. 4:15")

    minutes = int(match.group(1))
    seconds = int(match.group(2))
    if seconds >= 60:
        raise ValueError("Les secondes doivent être comprises entre 0 et 59")

    total_seconds = minutes * 60 + seconds
    if total_seconds == 0:
        raise ValueError("L'allure ne peut pas être égale à 0")

    return 3600 / total_seconds


def speed_to_pace_str(speed_kmh: float) -> str:
    """Convert a speed in km/h to a pace string mm:ss per km.

    Returns "inf" when speed is zero or negative to match the expected output.
    """
    if speed_kmh <= 0:
        return "inf"

    seconds_per_km = 3600 / speed_kmh
    rounded_seconds = int(round(seconds_per_km))
    minutes, seconds = divmod(rounded_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def generate_vma_table(vma_kmh: float, percent_max: int = 110, step: int = 5) -> List[Dict[str, object]]:
    """Generate the VMA table for paces at every percentage increment."""
    if vma_kmh < 0:
        raise ValueError("La VMA doit être positive")
    if percent_max < 0 or step <= 0:
        raise ValueError("Les paramètres percent_max et step doivent être positifs")

    table: List[Dict[str, object]] = []
    for percent in range(0, percent_max + 1, step):
        speed = round(vma_kmh * percent / 100, 1)
        table.append(
            {
                "percent_vma": percent,
                "vitesse_kmh": speed,
                "allure_min_km": speed_to_pace_str(speed),
            }
        )
    return table


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calcule les allures pour chaque palier de VMA entre 0% et 110%.",
    )
    parser.add_argument("--vma", type=float, required=True, help="VMA en km/h")

    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "--vitesse", type=float, help="Vitesse saisie en km/h (sera validée)",
    )
    input_group.add_argument(
        "--allure", type=str, help="Allure saisie au format mm:ss (convertie en vitesse)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.vitesse is not None and args.vitesse < 0:
        raise ValueError("La vitesse saisie doit être positive")

    if args.allure:
        user_speed = pace_to_speed_kmh(args.allure)
    else:
        user_speed = args.vitesse

    # The provided speed/allure is validated and converted if needed, then
    # the VMA table is generated from the given VMA value.
    _ = user_speed  # retained for potential extension; ensures conversion occurs.

    table = generate_vma_table(args.vma)
    print(json.dumps(table, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
