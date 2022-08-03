from dotenv import load_dotenv
import os
import api


def main():
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")

    access_token = api.get_access_token(client_id)
    products = api.get_products(access_token)
    #api.add_product_cart(dict(products['data'][0]), access_token)
    api.get_cart(1, access_token)


if __name__ == '__main__':
    main()
