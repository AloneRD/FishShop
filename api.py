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


def get_product(access_token: str, id: str) -> dict:
    headers = {'Authorization': access_token}
    response_products = requests.get(f'https://api.moltin.com/v2/products/{id}',
                                     headers=headers
                                     )
    response_products.raise_for_status()
    return response_products.json()


def get_image_product(access_token: str, id_image: str) -> dict:
    headers = {'Authorization': access_token}
    response_products = requests.get(f'https://api.moltin.com/v2/files/{id_image}',
                                     headers=headers
                                     )
    response_products.raise_for_status()
    return response_products.json()


def add_product_cart(product: dict, access_token: str, quantity: int, cart_id: str):
    headers = {'Authorization': access_token}
    json_data = {
        'data': {
            'id': product['id'],
            'type': 'cart_item',
            'quantity': quantity,
        },
    }
    response_add_product_to_cart = requests.post(f'https://api.moltin.com/v2/carts/{cart_id}/items',
                                                 headers=headers,
                                                 json=json_data
                                                 )
    response_add_product_to_cart.raise_for_status()


def remove_product_from_cart(cart_id: str, product_id: str, access_token: str):
    headers = {'Authorization': access_token}
    response_add_product_to_cart = requests.delete(f'https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}',
                                                   headers=headers,
                                                   )
    response_add_product_to_cart.raise_for_status()


def get_cart(cart_id: str, access_token: str) -> dict:
    headers = {'Authorization': access_token}
    response_get_cart = requests.get(f'https://api.moltin.com/v2/carts/{cart_id}/items', headers=headers)
    return response_get_cart.json()


def get_cart_total(cart_id: str, access_token: str) -> str:
    headers = {'Authorization': access_token}
    response_get_cart = requests.get(f'https://api.moltin.com/v2/carts/{cart_id}', headers=headers).json()
    total_cart = response_get_cart['data']['meta']['display_price']['with_tax']['formatted']
    return total_cart
