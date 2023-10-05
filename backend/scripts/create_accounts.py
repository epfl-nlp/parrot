import argparse
import requests
import os
import json

def create_accounts(num_accounts, course, api_url):
    print('Creating {} accounts'.format(num_accounts))
    accounts = []

    for i in range(num_accounts):
        data = {
            "name": "Account {}".format(i+1),
            "course": course
        }
        response = requests.post(f'{api_url}/api/accounts',
                                 json=data,
                                 headers={"Authorization": f"Bearer {os.getenv('PARROT_ADMIN_TOKEN')}"})

        if response.status_code == 201:
            respone_json = response.json()
            accounts.append(respone_json)
            print('Created account {}'.format(respone_json['id']))
        else:
            print('Error creating account: {}'.format(response.json()))

    return accounts

def main():
    parser = argparse.ArgumentParser(description='This script creates batch of accounts.')
    parser.add_argument('--num-accounts', type=int, help='Number of accounts to create')
    parser.add_argument('--course', type=str, help='Course name')
    parser.add_argument('--api-url', type=str, help='API URL')

    args = parser.parse_args()
    accounts = create_accounts(args.num_accounts, args.course, args.api_url)

    with open('accounts.json', 'w') as f:
        json.dump(accounts, f, indent=4)

if __name__ == '__main__':
    main()