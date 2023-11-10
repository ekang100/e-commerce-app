from werkzeug.security import generate_password_hash
import csv
import os
from faker import Faker
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from collections import defaultdict

num_users = 50
num_products = 2000
num_products_for_sale = 2500
# num_purchases = 2500

num_lineitems = 500
num_orders = 100

Faker.seed(0)
fake = Faker()

generated_path = os.path.join(os.getcwd(), 'db/generated')

seller_list = [] # from box
product_list = [] # from ekang for general use
product_id_list = [] # from ekang for bryant
# sellers_with_products = set() # will probably overwrite this
productid_to_price = {}
productid_to_sellerid = defaultdict(set)
sellerid_to_productid = defaultdict(set)


orderid_cartid_map = {}  # dictionary to track the mapping from orderid to cartid
orderid_fulfillmentStatus = {}
product_id_list = []


def csv_path(csv_name):
    return os.path.join(generated_path, csv_name)

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

def gen_users(num_users):
    with open(csv_path('Users.csv'), 'w') as f_users, open(csv_path('Password.csv'), 'w') as f_passwords:
        users_writer = get_csv_writer(f_users)
        passwords_writer = get_csv_writer(f_passwords)

        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            address = fake.address()
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            if "." not in name_components[0]:
                firstname = name_components[0]
            else:
                firstname = name_components[1]
            lastname = name_components[-1]
            balance = fake.pyint(0, 9999)
            isSeller = fake.pybool()
            if isSeller:
                seller_list.append(uid)
            users_writer.writerow([uid, address, email, password, firstname, lastname, balance, isSeller])
            passwords_writer.writerow([uid, plain_password])

        print(f'{num_users} generated')

    return



def gen_product_image(image_path, productid, product_name):
    # Download the image from the URL
    response = requests.get(image_path)
    static_path = 'app/static/'

    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        new_path = os.path.join(static_path, str(productid) + '.png')
        #os.mkdir(new_path)
        image.save(new_path)
        return new_path

    else:
        img = Image.new('RGB', size=(500, 500), color='white')
        draw = ImageDraw.Draw(img)

        # Set up the font
        font = ImageFont.load_default()

        # Draw the product name in the center of the image
        x = (300) / 2
        y = (300) / 2
        draw.text((x, y), product_name, fill='black', font=font)
        # Save the image
        new_path = os.path.join(static_path, str(productid) + '.png')
        #os.mkdir(new_path)
        img.save(new_path)
        return new_path
    

# generate product data and sellers with products
def gen_products(num_products):
    # columns = ['product_id', 'product_name', 'category', 'category_original', 'about_product', 'img_link', 'product_link']
    static_path = 'app/static/'
    #os.mkdir(static_path)
    # Open the source file and the output file
    with open(csv_path('ProductSource.csv'), 'r') as source_path, open(csv_path('Products.csv'), 'w') as product_path:
        reader = csv.DictReader(source_path)
        product_writer = get_csv_writer(product_path)

        print('Products...', end=' ', flush=True)

        # Iterate over each row in the source file
        for pid, row in enumerate(reader):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            if pid >= num_products:
                break
            # Extract the desired columns from the row
            productid = pid
            name = row['product_name']
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'

            productid_to_price[pid] = price

            description = row['about_product']
            category = row['category']
            image_path = os.path.join(static_path, str(pid) + '.png')
            if not os.path.isfile(image_path):
                image_path = gen_product_image(row['img_link'], productid, name)
            available = available = fake.random_element(elements=('true', 'false'))
            avg_rating = fake.random_int(min=0, max=500) / 100
            seller_id = fake.random_element(seller_list) # i think i can still keep this i just wont put it in the csv?

            productid_to_sellerid[productid].add(seller_id) # add the seller to to the set of sellers for the current product
            sellerid_to_productid[seller_id].add(productid) # add the product to the set of products for a given seller

            if available == 'true':
                product_list.append([productid, name])
                product_id_list.append(productid)
                sellerid_to_productid

            # Add to seller set if seller has products
            # sellers_with_products.add(seller_id)

            product_writer.writerow([productid, name, price, description, category, image_path, available, avg_rating])
        print(f'{num_products} generated')
    return

# generate inventory
def gen_products_for_sale(num_products_for_sale, product_id_list, sellerid_to_productid):
    with open(csv_path('ProductsForSale.csv'), 'w') as f:
        writer = get_csv_writer(f)
        #check = set()
        sellers_with_products = sellerid_to_productid.keys()

        for seller in sellers_with_products:
            productList = sellerid_to_productid[seller]
            for product in productList:
                productid = product
                uid = seller
                quantity = fake.random_int(min=1, max=50)
                writer.writerow([productid, uid, quantity])

        print('inventory generated')

    return



def gen_carts(num_users):
    with open(csv_path('Cart.csv'), 'w') as f:
        writer = get_csv_writer(f)

        print('Generating Carts...', end=' ', flush=True)
        for buyerid in range(0, num_users):  # Assuming user IDs start from 0
            cartid = buyerid  # Set cartid to be the same as the userid
            unique_item_count = fake.random_int(min=0, max=10)  # this and total_cart_price will be updated anyways by the schema
            total_cart_price = round(fake.random_int(min=0, max=1000) + fake.random.random(), 2)
            writer.writerow([buyerid, cartid, unique_item_count, total_cart_price])

        print(f'Carts generated for {num_users} users')


def gen_lineitems(num_lineitems):
    #generated constraints: 
    # 1) all lineitems with the same orderid must have the same cartid
    # 2) all orderid must have the same time_purchased
    # 3) time_fulfilled must be at least after time_purchased
    # 4) fulfilledStatus can not be true if buyStatus is false


    #questions:
    #what about the unitprice???
    #so lineitemID has productID and orderID, orders in progress sellerID has to align with that productID

    #productID to sellersID
    #lineitemID to orderID
    # #orderID to sellersID

    # orderid_cartid_map = {}  # dictionary to track the mapping from orderid to cartid
    orderid_time_purchased_map = {}  # dictionary to track the mapping from orderid to time_purchased
    orderid_productid_map = {} 

    with open(csv_path('LineItem-PreProcess.csv'), 'w') as f:
        writer = get_csv_writer(f)

        print('Generating LineItems...', end=' ', flush=True)
        for lineid in range(num_lineitems):
            if lineid % 100 == 0:
                print(f'{lineid}', end=' ', flush=True)

            buyStatus = fake.pybool()

            if buyStatus:
                orderid = fake.random_int(min=1, max=num_orders-1)  # Assume num_orders is defined

                # check if the orderid is already in the mapping dictionary
                if orderid in orderid_cartid_map:
                    cartid = orderid_cartid_map[orderid]
                else:
                    cartid = fake.random_int(min=0, max=num_users-1)  # Generate a new cartid for the unique orderid
                    orderid_cartid_map[orderid] = cartid

                # check if the orderid is already in the time_purchased mapping dictionary
                if orderid in orderid_time_purchased_map:
                    time_purchased = orderid_time_purchased_map[orderid]
                else:
                    time_purchased = fake.date_time_this_decade()
                    orderid_time_purchased_map[orderid] = time_purchased
                
                if orderid in orderid_productid_map:
                    productid = fake.random_int(min=0, max=len(product_list)-1)
                    while productid in orderid_productid_map[orderid]:  # Ensure unique productid for the orderid
                        productid = fake.random_int(min=0, max=len(product_list)-1)
                    orderid_productid_map[orderid].append(productid)
                else:
                    productid = fake.random_int(min=0, max=len(product_list)-1)
                    orderid_productid_map[orderid] = [productid]
            else:
                orderid = None
                cartid = fake.random_int(min=0, max=num_users-1)  # Generate a cartid for cases where buyStatus is False
                time_purchased = fake.date_time_this_decade()
                productid = fake.random_int(min=0, max=len(product_list)-1)  # Assume productid exists in Products table


            # productid = fake.random_int(min=0, max=len(product_list)-1)  # Assume productid exists in Products table
            quantities = fake.random_int(min=1, max=20)
            unitPrice = productid_to_price.get(productid)
            # round(fake.random_int(min=1, max=1000) + fake.random.random(), 2) #doesn't this have to get from products ????

            # gen fulfilledStatus only if buyStatus is True
            if buyStatus:
                fulfilledStatus = fake.pybool()
                if orderid in orderid_fulfillmentStatus:
                    if orderid_fulfillmentStatus.get(orderid) and fulfilledStatus==False: #if order is true but false dont change 
                        orderid_fulfillmentStatus[orderid] = False
                else:
                    orderid_fulfillmentStatus[orderid] = fulfilledStatus

            else:
                fulfilledStatus = False

            # gen time_fulfilled only if buyStatus is True
            if buyStatus:
                time_fulfilled = fake.date_time_between(start_date=time_purchased, end_date='now')  # Generate a time after purchase
            else:
                time_fulfilled = time_purchased

            sellerid = fake.random_element(productid_to_sellerid[productid])

            writer.writerow([lineid, cartid, productid, quantities, unitPrice, buyStatus, fulfilledStatus, time_purchased, time_fulfilled, orderid, sellerid])

        print(f'{num_lineitems} generated')


def removeQuotations(input_csv_path, output_csv_path):
            # Open the input and output CSV files
        # input_csv_path = 'db/generated/LineItem-PreProcess.csv'  # Update with the correct file path
        # output_csv_path = 'db/generated/LineItem.csv'  # Update with the desired output file path
        with open(input_csv_path, 'r', newline='') as input_file, open(output_csv_path, 'w', newline='') as output_file:
            csv_reader = csv.reader(input_file)
            csv_writer = csv.writer(output_file)

            # Iterate through the rows and delete empty strings
            for row in csv_reader:
                modified_row = [cell.replace('""', '') for cell in row]
                csv_writer.writerow(modified_row)

        print(f'Delete all quotation marks in {output_csv_path}')



def gen_orders_in_progress(num_orders):
    with open(csv_path('OrdersInProgress-PreProcess.csv'), 'w') as f:
        writer = get_csv_writer(f)

        print('Generating OrdersInProgress...', end=' ', flush=True)
        for orderid in range(num_orders):
            if orderid % 10 == 0:
                print(f'{orderid}', end=' ', flush=True)

            # Randomly select a sellerid from the list of possible seller IDs
            # sellerid = fake.random_element(elements=list(sellers_with_products)) #have to change this, seller_ids should be an array with all seller_ids
            
            buyerid = orderid_cartid_map.get(orderid)  # Assume num_users is defined
            entireOrderFulfillmentStatus = orderid_fulfillmentStatus.get(orderid)


            writer.writerow([orderid, buyerid, entireOrderFulfillmentStatus])

        print(f'{num_orders} generated')


        


# def gen_purchases(num_purchases, available_pids):
#     with open('Purchases.csv', 'w') as f:
#         writer = get_csv_writer(f)
#         print('Purchases...', end=' ', flush=True)
#         for id in range(num_purchases):
#             if id % 100 == 0:
#                 print(f'{id}', end=' ', flush=True)
#             uid = fake.random_int(min=0, max=num_users-1)
#             pid = fake.random_element(elements=available_pids)
#             time_purchased = fake.date_time()
#             writer.writerow([id, uid, pid, time_purchased])
#         print(f'{num_purchases} generated')
#     return

gen_users(num_users)
gen_products(num_products)
gen_products_for_sale(num_products_for_sale, product_id_list, sellerid_to_productid)
gen_carts(num_users)
gen_lineitems(num_lineitems)
removeQuotations('db/generated/LineItem-PreProcess.csv', 'db/generated/LineItem.csv')
gen_orders_in_progress(num_orders)
removeQuotations('db/generated/OrdersInProgress-PreProcess.csv','db/generated/OrdersInProgress.csv')

# gen_users(num_users)
# gen_products(num_products)
# gen_products_for_sale(num_products_for_sale, product_list)
# available_pids = gen_products(num_products)
# gen_purchases(num_purchases, available_pids)
