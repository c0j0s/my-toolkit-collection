import argparse
import os
import sys

from notion.smoke_test import run_live_smoke_test

if __name__ == "__main__":
    description = "Run notion-py client smoke tests"
    # parser = argparse.ArgumentParser(description=description)
    # parser.add_argument(
    #     "--page", dest="page", help="page URL or ID", required=True, type=str
    # )
    # parser.add_argument("--token", dest="token", help="token_v2", type=str)
    # args = parser.parse_args()

    # token = args.token
    # if not token:
    #     token = os.environ.get("NOTION_TOKEN")
    # if not token:
    #     print(
    #         "Must either pass --token option or set NOTION_TOKEN environment variable"
    #     )
    #     sys.exit(1)

    run_live_smoke_test("ac03018c7b94a27f3a5361a207255deb1cdc83e840f5895c5f6382dd97890de1aba1d3a9bb7889493702e571caa90803b4ba85a5899118a60cab111754cc073dca0ef548317e034041b96e538f37", "https://www.notion.so/c0j0s/test-6220376a1fce43f2a630bfd3b4768100")
