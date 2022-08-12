import requests
import os
from datetime import datetime


def get_access_token(client_id: str) -> str:
    response_token_request = requests.post(
        'https://api.moltin.com/oauth/access_token',
        data={
            'client_id': client_id,
            'grant_type': 'implicit'
            }
        )
    response_token_request.raise_for_status()
    timestamp = float(datetime.now().timestamp())
    os.environ.setdefault('ACCESS_TOKEN', response_token_request.json()['access_token'])
    os.environ.setdefault('MOLTIN_TOKEN_EXPIRES_TIME', str(timestamp))


def check_access_token(client_id: str):
    token_expires_time = os.getenv('MOLTIN_TOKEN_EXPIRES_TIME')
    timestamp = float(datetime.now().timestamp())
    if not token_expires_time or float(token_expires_time) < timestamp:
        get_access_token(client_id)


def get_products(client_id: str) -> dict:
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_products = requests.get(
        'https://api.moltin.com/v2/products',
        headers=headers
        )
    response_products.raise_for_status()
    return response_products.json()


def get_product(client_id: str, id: str) -> dict:
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_products = requests.get(
        f'https://api.moltin.com/v2/products/{id}',
        headers=headers
        )
    response_products.raise_for_status()
    return response_products.json()


def get_image_product(client_id: str, id_image: str) -> dict:
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_products = requests.get(
        f'https://api.moltin.com/v2/files/{id_image}',
        headers=headers
        )
    response_products.raise_for_status()
    return response_products.json()


def add_product_cart(product: dict, client_id: str, quantity: int, cart_id: str) -> None:
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    json_data = {
        'data': {
            'id': product['id'],
            'type': 'cart_item',
            'quantity': quantity,
        },
    }
    response_add_product_to_cart = requests.post(
        f'https://api.moltin.com/v2/carts/{cart_id}/items',
        headers=headers,
        json=json_data
        )
    response_add_product_to_cart.raise_for_status()


def remove_product_from_cart(cart_id: str, product_id: str, client_id: str) -> None:
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_add_product_to_cart = requests.delete(
        f'https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}',
        headers=headers,
        )
    response_add_product_to_cart.raise_for_status()


def get_cart(cart_id: str, client_id: str) -> dict:
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_get_cart = requests.get(
        f'https://api.moltin.com/v2/carts/{cart_id}/items',
        headers=headers
        )
    response_get_cart.raise_for_status()
    return response_get_cart.json()


def get_cart_total(cart_id: str, client_id: str) -> str:
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_get_cart = requests.get(
        f'https://api.moltin.com/v2/carts/{cart_id}',
        headers=headers
        )
    response_get_cart.raise_for_status()
    cart = response_get_cart.json()
    total_cart = cart['data']['meta']['display_price']['with_tax']['formatted']
    return total_cart


def create_customer(name: str, email: str, client_id: str) -> None:
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    json_data = {
        'data': {
            'type': 'customer',
            'name': name,
            'email': email,
        },
    }
    response_create_customer = requests.post(
        'https://api.moltin.com/v2/customers',
        headers=headers,
        json=json_data
        )
    response_create_customer.raise_for_status()
