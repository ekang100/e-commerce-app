from werkzeug.security import generate_password_hash
import csv
import os
from faker import Faker
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from collections import defaultdict
import random

num_users = 50
num_giftcard = 50
num_products = 2000
num_products_for_sale = 2500
# num_purchases = 2500
num_reviews = 100
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
productid_to_sellerid2 = defaultdict(set)

sellerid_to_productid = defaultdict(set)
productid_to_available = {}


orderid_cartid_map = {}  # dictionary to track the mapping from orderid to cartid
orderid_fulfillmentStatus = {}
product_id_list = []

product_id_to_available = {}


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

            if "." not in name_components[-1]:
                lastname = name_components[-1]
            else:
                lastname = name_components[-2]

            balance = fake.pyint(0, 9999)
            isSeller = fake.pybool()
            isVerified = fake.pybool()
            verifiedDate = fake.date_time_this_decade()
            five_star_reviews = 0

            if isSeller:
                seller_list.append(uid)
            bio = None
            avatar = 1
            users_writer.writerow([uid, address, email, password, firstname, lastname, balance, isSeller, isVerified, verifiedDate, bio, avatar, five_star_reviews])
            passwords_writer.writerow([uid, plain_password])
        print(f'{num_users} generated')
    return

def gen_giftcard(num_giftcard):
    with open(csv_path('GiftCard.csv'), 'w') as f:
        giftcard = get_csv_writer(f)
        print('GiftCard...', end=' ', flush=True)
        for cardid in range(num_giftcard):
            if cardid % 10 == 0:
                print(f'{cardid}', end=' ', flush=True)
            code = fake.pystr(min_chars=8, max_chars=8)
            amount = fake.pyint(1, 9999)
            redeem = False
            giftcard.writerow([cardid, code, amount, redeem])
        print(f'{num_giftcard} generated')
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
            available = fake.random_element(elements=(True, False))
            # available = fake.pybool()
            avg_rating = fake.random_int(min=0, max=500) / 100
            seller_id = fake.random_element(seller_list) # i think i can still keep this i just wont put it in the csv?

            n = fake.random_int(min=1, max=10)
            seller_id_list = random.sample(seller_list, n) # list of sellers for the product

            productid_to_available[productid] = available

            for seller_id in seller_id_list: # bc we want multiple sellers for multiple products
                # productid_to_sellerid[productid].add(seller_id) # add the seller to to the set of sellers for the current product
                sellerid_to_productid[seller_id].add(productid) # add the product to the set of products for a given seller
                productid_to_sellerid2[productid].add(seller_id) # add the seller to to the set of sellers for the current product

                productid_to_sellerid[productid].add(seller_id) # add the seller to to the set of sellers for the current product

            # productid_to_sellerid[productid].add(seller_id) # add the seller to to the set of sellers for the current product
            # sellerid_to_productid[seller_id].add(productid) # add the product to the set of products for a given seller

            if available:
                product_list.append([productid, name])
                product_id_list.append(productid)

            product_id_to_available[productid] = available

            # Add to seller set if seller has products
            # sellers_with_products.add(seller_id)

            product_writer.writerow([productid, name, price, description, category, image_path, available, avg_rating])
        print(f'{num_products} generated')
    return

# generate inventory
def gen_products_for_sale(sellerid_to_productid):
    with open(csv_path('ProductsForSale.csv'), 'w') as f:
        writer = get_csv_writer(f)
        #check = set()
        sellers_with_products = sellerid_to_productid.keys()

        for seller in sellers_with_products:
            productList = sellerid_to_productid[seller]
            for product in productList:
                productid = product
                uid = seller
                if product_id_to_available[productid]:
                    quantity = fake.random_int(min=1, max=50)
                else:
                    quantity = 0
                    # productid_to_sellerid[productid].remove(seller)
                    # if(len(productid_to_sellerid[product]) == 0):
                    #     del productid_to_sellerid[product]

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
    cartid_productid_map = {}

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
                
                # if cartid in cartid_productid_map:
                #     productids_in_cart = cartid_productid_map[cartid]
                # else:
                #     productids_in_cart = []
                    
            else:
                orderid = None
                cartid = fake.random_int(min=0, max=num_users-1)  # Generate a cartid for cases where buyStatus is False
                time_purchased = fake.date_time_this_decade()
                # productid = fake.random_int(min=0, max=len(product_list)-1)  # Assume productid exists in Products table
                if cartid in cartid_productid_map:
                    productids_in_cart = cartid_productid_map[cartid]
                else:
                    productids_in_cart = []
                while productid in productids_in_cart or not product_id_to_available[productid]:
                    productid = fake.random_element(product_id_list)
                
                productids_in_cart.append(productid)
                cartid_productid_map[cartid] = productids_in_cart
            

                
            # productid = fake.random_element(product_id_list)

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
                # sellerid = fake.random_element(productid_to_sellerid2[productid])
            else:
                time_fulfilled = time_purchased
                # sellerid = fake.random_element(productid_to_sellerid[productid])


            sellerid = fake.random_element(productid_to_sellerid[productid])
            present = fake.pybool()
    
            

            writer.writerow([lineid, cartid, productid, quantities, unitPrice, buyStatus, fulfilledStatus, time_purchased, time_fulfilled, orderid, sellerid,present])

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
            tipAmount = f'{str(fake.random_int(max=50))}.{fake.random_int(max=99):02}'

            writer.writerow([orderid, buyerid, entireOrderFulfillmentStatus, tipAmount])

        print(f'{num_orders} generated')

# Generates product reviews using ellie's dataset
def gen_product_reviews(num_reviews, user_ids, product_ids):
    with open(csv_path('ReviewSource.csv'), 'r', encoding='utf-8') as source_file, \
         open(csv_path('Reviews.csv'), 'w', encoding='utf-8', newline='') as reviews_file:
        
        source_reader = csv.DictReader(source_file)
        print('Generating Product Reviews...', end=' ', flush=True)

        for review_id in range(num_reviews):
            if review_id % 10 == 0:
                print(f'{review_id}', end=' ', flush=True)
            
            try:
                review_source_data = next(source_reader)
            except StopIteration:
                source_file.seek(0)
                next(source_reader)  
                review_source_data = next(source_reader)
            user_id = fake.random_element(elements=user_ids)
            product_id = fake.random_element(elements=product_ids)
            comments = '"' + review_source_data['review_content'].replace('"', '""') + '"'

            rating = str(fake.random_int(min=1, max=5))
            date = fake.date_time_this_year(before_now=True, after_now=False, tzinfo=None).isoformat()

            row = ','.join([
                str(review_id),
                str(product_id),
                str(user_id),
                "",  # seller_id is empty since these are product reviews
                "product",
                rating,
                comments,
                date
            ])

            reviews_file.write(row + '\n')

        print(f'{num_reviews} generated')
    return

# Generates seller reviews and appends them onto the product reviews CSV
# There isn't a data source for these so i had to use faker to generate bogus comments
def gen_seller_reviews(num_reviews, user_ids, seller_ids, csv_file_path):
    existing_reviews = set()
    last_review_id = 0

    with open(csv_file_path, 'r', encoding='utf-8') as existing_file:
        existing_reader = csv.reader(existing_file)
        next(existing_reader)
        for row in existing_reader:
            review_id = int(row[0])
            last_review_id = max(last_review_id, review_id)  # Tracks the highest review ID
            user_id = row[2]
            seller_id = row[3]
            review_type = row[4]
            entity_id = seller_id if review_type == 'seller' else ""
            existing_reviews.add((user_id, entity_id, review_type))

    with open(csv_file_path, 'a', encoding='utf-8', newline='') as reviews_file:
        print('Appending Seller Reviews...', end=' ', flush=True)
        review_count = 0
        while review_count < num_reviews:
            user_id = random.choice(user_ids)
            seller_id = random.choice(seller_ids)
            review_type = 'seller'
            if (user_id, seller_id, review_type) in existing_reviews:
                continue 
            existing_reviews.add((user_id, seller_id, review_type))
            last_review_id += 1
            comments = '"' + fake.text().replace('"', '""') + '"'
            rating = str(fake.random_int(min=1, max=5))
            date = fake.date_time_this_year(before_now=True, after_now=False, tzinfo=None).isoformat()
            row = [
                str(last_review_id), 
                "",  # Product ID is empty for seller reviews
                str(user_id),
                str(seller_id), 
                review_type,
                rating,
                comments,
                date
            ]

            reviews_file.write(','.join(row) + '\n')
            review_count += 1

        print(f'{num_reviews} appended')
    return

gen_users(num_users)
gen_products(num_products)
gen_products_for_sale(sellerid_to_productid)
gen_carts(num_users)
gen_lineitems(num_lineitems)
removeQuotations('db/generated/LineItem-PreProcess.csv', 'db/generated/LineItem.csv')
gen_orders_in_progress(num_orders)
removeQuotations('db/generated/OrdersInProgress-PreProcess.csv','db/generated/OrdersInProgress.csv')
user_ids = list(range(50))
num_reviews = 100
gen_product_reviews(num_reviews, user_ids, product_id_list)
gen_seller_reviews(100, user_ids, seller_list, 'db/generated/Reviews.csv')
gen_giftcard(num_giftcard)