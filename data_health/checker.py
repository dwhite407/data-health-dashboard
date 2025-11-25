import pandas as pd
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from pathlib import Path
import json
from datetime import datetime


@dataclass
class CheckResult:
    name: str
    status: str  # "PASS" or "FAIL"
    details: Dict[str, Any]


class DataHealthChecker:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.df = None

    def load_data(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"File not found: {self.csv_path}")
        
        self.df = pd.read_csv(self.csv_path, sep=None, engine="python")


    def run_all_checks(self) -> List[CheckResult]:
        if self.df is None:
            self.load_data()

        results: List[CheckResult] = []
        results.append(self._check_missing_values())
        results.append(self._check_duplicates())

        # in later phases, you can add:
        # results.append(self._check_value_ranges(config))
        # results.append(self._check_allowed_categories(config))

        return results

    def _check_missing_values(self) -> CheckResult:
        missing_counts = self.df.isna().sum()
        total_missing = int(missing_counts.sum())

        status = "PASS" if total_missing == 0 else "FAIL"

        return CheckResult(
            name="Missing Values",
            status=status,
            details={
                "total_missing": total_missing,
                "missing_by_column": missing_counts.to_dict()
            }
        )

    def _check_duplicates(self) -> CheckResult:
        dup_count = int(self.df.duplicated().sum())
        status = "PASS" if dup_count == 0 else "FAIL"

        return CheckResult(
            name="Duplicate Rows",
            status=status,
            details={"duplicate_rows": dup_count}
        )


def results_to_dict(csv_path: str, results: List[CheckResult]) -> Dict[str, Any]:
    return {
        "file": csv_path,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total_checks": len(results),
            "failed_checks": sum(1 for r in results if r.status == "FAIL"),
        },
        "checks": [asdict(r) for r in results],
    }


def save_report(report: Dict[str, Any], output_dir: str = "reports") -> str:
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"report_{ts}.json"
    out_path = output_dir_path / filename

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return str(out_path)
