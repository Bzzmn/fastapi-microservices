import requests, os, time, redis

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import HashModel
from starlette.requests import Request
from enum import Enum, auto

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


class OrderStatus(str, Enum):
    pending = 'pending'
    paid = 'paid'
    canceled = 'canceled'
    shipped = 'shipped'
    delivered = 'delivered'
    refunded = 'refunded'

class Order(HashModel):
    product_id: str
    price: float
    quantity: int
    fee: float
    total: float
    status: OrderStatus = OrderStatus.pending

    class Meta:
        database = r

@app.get('/orders/{id}')
async def get_order_by_id(id: str):
    order = Order.get(id)
    return order

@app.post('/orders')
async def create_order(request: Request, background_tasks: BackgroundTasks): #id, quantity
    data = await request.json()

    req = requests.get(f'http://localhost:8000/products/{data["id"]}')

    if req.status_code != 200:
        return {"error": "Product not found"}
    
    product = req.json()

    order = Order(
        product_id=product['id'],
        price=product['price'],
        fee=0.19 * product['price'],
        quantity=data['quantity'],
        total=(product['price'] * data['quantity']) * 1.19,
        status=OrderStatus.pending
    )

    order.save()

    background_tasks.add_task(order_completed, order)

    return order

def order_completed(order: Order):
    time.sleep(5)
    order.status = OrderStatus.paid
    order.save()
    r.xadd('order_completed', order.dict(), '*')

