from dotenv import load_dotenv
import os
import requests


def get_access_token(client_id: str) -> str:
    response_token_request = requests.post('https://api.moltin.com/oauth/access_token',
                                           data={
                                                'client_id': client_id,
                                                'grant_type': 'implicit'
                                                }
                                           )
    return response_token_request.json()['access_token']


def get_products(access_token: str):
    headers = {'Authorization': access_token}
    response_products = requests.get('https://api.moltin.com/v2/products',
                                     headers=headers
                                     )
    print(response_products.json())


def main():
    load_dotenv()

    CLIENT_ID = os.getenv("CLIENT_ID")

    access_token = get_access_token(CLIENT_ID)
    get_products(access_token)


if __name__ == '__main__':
    main()
