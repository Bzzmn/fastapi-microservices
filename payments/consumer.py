from main import r, Order, OrderStatus
import time

key = 'refund_order'
group = 'payments-group'

try:
    r.xgroup_create(key, group)
except:
    print('Group already exists!')

while True:
    try:
        results = r.xreadgroup(group, key, {key: '>'}, None)

        if results != []:
            for result in results:
                obj = result[1][0][1]
                order = Order.get(obj['pk'])
                order.status = OrderStatus.refunded
                order.save()
                print(f'Order {order.pk} refunded')

    except Exception as e:
        print(str(e))
    time.sleep(1)

