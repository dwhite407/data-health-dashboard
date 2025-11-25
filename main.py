import argparse
from data_health.checker import DataHealthChecker, results_to_dict, save_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run data health checks on a CSV file."
    )
    parser.add_argument("csv_path", help="Path to the CSV file to analyze.")
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save a JSON report, only print to console.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    checker = DataHealthChecker(args.csv_path)
    results = checker.run_all_checks()
    report = results_to_dict(args.csv_path, results)

    # Pretty-print summary
    print(f"\nData Health Report for: {report['file']}")
    print(f"Timestamp (UTC): {report['timestamp']}")
    print(f"Total checks: {report['summary']['total_checks']}")
    print(f"Failed checks: {report['summary']['failed_checks']}\n")

    for check in report["checks"]:
        print(f"✅ {check['name']}" if check["status"] == "PASS" else f"❌ {check['name']}")
        print(f"   Status: {check['status']}")
        print(f"   Details: {check['details']}\n")

    if not args.no_save:
        path = save_report(report)
        print(f"Report saved to: {path}")


if __name__ == "__main__":
    main()
