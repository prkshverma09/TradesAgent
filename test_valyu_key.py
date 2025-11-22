import os

from valyu import Valyu

def main() -> None:
    api_key = os.environ.get("VALYU_API_KEY")
    if not api_key:
        raise SystemExit("Set VALYU_API_KEY before running this test.")

    try:
        client = Valyu(api_key)
        response = client.search(
            "test plumbing shops in London",
            search_type="web",
            max_num_results=1,
            is_tool_call=True,
        )
    except Exception as exc:
        print("Request failed:", exc)
        return

    if getattr(response, "success", True):
        results = getattr(response, "results", []) or []
        if results:
            first = results[0]
            print("Status: success")
            print("Title:", getattr(first, "title", ""))
            print("URL:", getattr(first, "url", ""))
        else:
            print("Status: success but no results returned")
    else:
        print("Status: failed")
        print("Error:", getattr(response, "error", "Unknown error"))


if __name__ == "__main__":
    main()

