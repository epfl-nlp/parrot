import argparse
import requests
from tqdm import tqdm

def report_stats(accounts, api_url):
    num_accounts = len(accounts)
    num_chats = 0
    num_messages = 0

    for account in tqdm(accounts, total=len(accounts), desc=f"Getting stats for accounts", leave=False, position=0):
        response = requests.get(f"{api_url}/chats", headers={"Authorization": f"Bearer {account['api_key']}"})
        chats = response.json()
        if response.status_code == 200:
            num_chats += len(chats)
        else:
            raise Exception(f"Error getting chats for account {account['name']}: {response.json()}")

        for chat in tqdm(chats, total=len(chats), desc=f"Getting stats for account {account['name']}", leave=False, position=1):
            response = requests.get(f"{api_url}/chats/{chat['id']}/num_messages", headers={"Authorization": f"Bearer {account['api_key']}"})
            if response.status_code == 200:
                num_messages += response.json()["num_messages"]
            else:
                raise Exception(f"Error getting num_messages for chat {chat['id']}: {response.json()}")

    print(f"Number of accounts: {num_accounts}")
    print(f"Number of chats: {num_chats}")
    print(f"Number of messages: {num_messages}")


def main():
    parser = argparse.ArgumentParser(description="This script reports stats for all accounts.")
    parser.add_argument("--admin-token", type=str, required=True, help="Admin token")
    parser.add_argument("--url", type=str, default="http://localhost:5000", help="Server URL")

    args = parser.parse_args()

    api_url = f"{args.url}/api"

    response = requests.get(f"{api_url}/accounts", headers={"Authorization": f"Bearer {args.admin_token}"})
    all_accounts = response.json()
    project_accounts = [account for account in all_accounts if account["name"].startswith("Account")]
    other_accounts = [account for account in all_accounts if not account["name"].startswith("Account")]

    print("Project accounts:")
    report_stats(project_accounts, api_url)
    print()
    print("Other accounts:")
    report_stats(other_accounts, api_url)

if __name__ == "__main__":
    main()