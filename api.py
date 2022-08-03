import requests


def get_access_token(client_id: str) -> str:
    response_token_request = requests.post('https://api.moltin.com/oauth/access_token',
                                           data={
                                                'client_id': client_id,
                                                'grant_type': 'implicit'
                                                }
                                           )
    response_token_request.raise_for_status()
    return response_token_request.json()['access_token']


def get_products(access_token: str) -> dict:
    headers = {'Authorization': access_token}
    response_products = requests.get('https://api.moltin.com/v2/products',
                                     headers=headers
                                     )
    response_products.raise_for_status()
    return response_products.json()


def add_product_cart(product: dict, access_token: str):
    headers = {'Authorization': access_token}
    print(product['id'])
    json_data = {
        'data': {
            'id': product['id'],
            'type': 'cart_item',
            'quantity': 1,
        },
    }
    response_add_product_to_cart = requests.post('https://api.moltin.com/v2/carts/1/items', headers=headers, json=json_data)
    response_add_product_to_cart.raise_for_status()


def get_cart(cart_id: str, access_token: str) -> dict:
    headers = {'Authorization': access_token}
    response_get_cart = requests.get(f'https://api.moltin.com/v2/carts/{cart_id}/items', headers=headers)
    return response_get_cart.json()