import argparse

from agent import run_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find plumbing shops for a specific item in the UK.")
    parser.add_argument("--item", required=True, help="Plumbing tool or material to purchase.")
    parser.add_argument("--location", required=True, help="Preferred UK postcode.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    state = run_agent(args.item, args.location)
    results = state.get("final_results", [])
    print(f"Saved {len(results)} shop entries to plumbing_shops.json")


if __name__ == "__main__":
    main()
