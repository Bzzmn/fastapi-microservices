from main import r, Product
import time

key = 'order_completed'
group = 'inventory-group'

try: 
    r.xgroup_create(key, group)
except: 
    print ('Group already exists!')

while True:
    try:
        results = r.xreadgroup(group, key, {key: '>'}, None)

        if results != []:
            for result in results:
                obj = result[1][0][1]
                product = Product.get(obj['product_id'])
           
                try: 
                    if product & product.quantity >= int(obj['quantity']):
                        print('product_quantity', product.quantity)
                        print('obj_quantity', obj['quantity'])

                        product.quantity -= int(obj['quantity'])
                        product.save()
                        print (f'Product {product.name} updated')
                except:
                    r.xadd('refund_order', obj, '*')
                    print (f'Product {product.name} out of stock')
    except Exception as e:
        print (str(e))
    time.sleep(1)