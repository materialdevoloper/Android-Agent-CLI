import argparse
import location_scraper

def main():
    parser = argparse.ArgumentParser(description="Google Maps Automation CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # search command
    search_parser = subparsers.add_parser("search", help="Search for a location")
    search_parser.add_argument("--query", type=str, required=True, help="Location to search for")

    # read-results command
    read_parser = subparsers.add_parser("read-results", help="Expand bottom sheet and extract text")

    # sort command
    sort_parser = subparsers.add_parser("sort", help="Sort the results")
    sort_parser.add_argument("--by", type=str, choices=["top_rated", "distance"], required=True, help="Sort metric")

    # scrape-details command
    scrape_details_parser = subparsers.add_parser("scrape-details", help="Scroll down the place details and save full image")
    scrape_details_parser.add_argument("--auto", action="store_true", default=True, help="Automatically detect bottom")

    # scrape-list command
    scrape_list_parser = subparsers.add_parser("scrape-list", help="Scroll the search results list and save full image")
    scrape_list_parser.add_argument("--scrolls", type=int, default=3, help="Number of scrolls (default: 3)")

    args = parser.parse_args()

    if args.command == "search":
        location_scraper.execute_search(args.query)
    elif args.command == "read-results":
        location_scraper.read_results()
    elif args.command == "sort":
        location_scraper.sort_results(args.by)
    elif args.command == "scrape-details":
        location_scraper.scrape_details(args.auto)
    elif args.command == "scrape-list":
        location_scraper.scrape_list(args.scrolls)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
