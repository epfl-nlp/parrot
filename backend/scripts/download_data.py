import argparse
import requests
import pathlib
import json
from tqdm import tqdm
import multiprocessing

def write_json(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def download_account_data(account, data_dir, api_url, position=0):
    account_dir = pathlib.Path(f"{data_dir}/{account['id']}")
    account_dir.mkdir(parents=True, exist_ok=True)
    write_json(account, f"{account_dir}/account.json")
    chats_dir = pathlib.Path(f"{account_dir}/chats")
    chats_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(f"{api_url}/chats", headers={"Authorization": f"Bearer {account['api_key']}"})
    chats = response.json()

    for chat in tqdm(chats, total=len(chats), desc=f"Downloading account {account['name']}", leave=False, position=position):
        chat_dir = pathlib.Path(f"{chats_dir}/{chat['id']}")
        chat_dir.mkdir(parents=True, exist_ok=True)
        write_json(chat, f"{chat_dir}/chat.json")
        messages_dir = pathlib.Path(f"{chat_dir}/messages")
        messages_dir.mkdir(parents=True, exist_ok=True)
        response = requests.get(f"{api_url}/chats/{chat['id']}/messages", headers={"Authorization": f"Bearer {account['api_key']}"})
        messages = response.json()

        for message in messages:
            write_json(message, f"{messages_dir}/{message['id']}.json")

def download_accounts_batch(accounts, data_dir, api_url, position=0):
    for account in tqdm(accounts, total=len(accounts), desc=f"Downloading accounts", leave=False, position=position):
        download_account_data(account, data_dir, api_url, position=position)

def download_accounts(accounts, data_dir, api_url):
    num_cores = multiprocessing.cpu_count()
    num_cores = 48
    batch_size = (len(accounts) // num_cores) + 1

    procs = []

    for i in range(num_cores):
        start = i * batch_size
        end = (i + 1) * batch_size
        accounts_batch = accounts[start:end]
        
        if accounts_batch:
            p = multiprocessing.Process(target=download_accounts_batch, args=(accounts_batch, data_dir, api_url, i))
            p.start()
            procs.append(p)
    
    for p in procs:
        p.join()

def main():
    parser = argparse.ArgumentParser(description="This script downloads all data from the server.")
    parser.add_argument("--admin-token", type=str, required=True, help="Admin token")
    parser.add_argument("--url", type=str, default="http://localhost:5000", help="Server URL")

    args = parser.parse_args()

    api_url = f"{args.url}/api"

    response = requests.get(f"{api_url}/accounts", headers={"Authorization": f"Bearer {args.admin_token}"})
    all_accounts = response.json()
    project_accounts = [account for account in all_accounts if account["name"].startswith("Account")]
    other_accounts = [account for account in all_accounts if not account["name"].startswith("Account")]

    pathlib.Path("data").mkdir(parents=True, exist_ok=True)
    project_dir = pathlib.Path("data/project")
    project_dir.mkdir(parents=True, exist_ok=True)
    other_dir = pathlib.Path("data/other")
    other_dir.mkdir(parents=True, exist_ok=True)

    download_accounts(project_accounts, project_dir, api_url)
    download_accounts(other_accounts, other_dir, api_url)

if __name__ == "__main__":
    main()