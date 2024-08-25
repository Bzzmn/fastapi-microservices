import os
import redis
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import HashModel

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    r = redis.Redis(
        host=os.getenv('REDIS_DATABASE_URL'),
        port=os.getenv('REDIS_DATABASE_PORT'),
        password=os.getenv('REDIS_DATABASE_PASSWORD'),
        decode_responses=True
    )

    r.ping()
    print ('Connected to Redis')

except redis.ConnectionError as e:
    print(f'Error connecting to Redis: {e}')

class Product(HashModel):
    name: str
    price: float
    quantity: int
    
    class Meta:
        database = r

@app.get("/products")
def get_all_products():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)
    return {
        'id': pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }

@app.post("/products")
def create_product(product: Product):
    product.save()
    return product

@app.get("/products/{product_id}")
def get_product_by_id(product_id: str):
    product = Product.get(product_id)
    return format(product_id)


@app.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    baseProduct = Product.get(product_id)

    if not baseProduct:
        return {'message': f'Product {product_id} not found'}
    
    baseProduct.name = product.name
    baseProduct.price = product.price
    baseProduct.quantity = product.quantity
    baseProduct.save()
    return {'message': f'Product {product_id} updated'}


@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    Product.delete(product_id)
    return {'message': f'Product {product_id} deleted'}




