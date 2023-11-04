from werkzeug.security import generate_password_hash
import csv
import os
from faker import Faker
from PIL import Image, ImageDraw, ImageFont

num_users = 50
num_products = 2000
num_purchases = 2500

Faker.seed(0)
fake = Faker()

generated_path = os.path.join(os.getcwd(), 'db/generated')

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
            users_writer.writerow([uid, address, email, password, firstname, lastname, balance, isSeller])
            passwords_writer.writerow([uid, plain_password])

        print(f'{num_users} generated')

    return

def gen_products(num_products):
    columns = ['product_id', 'product_name', 'category', 'about_product', 'img_link', 'product_link']
    # Open the source file and the output file
    with open(csv_path('ProductSource.csv'), 'r') as source_path, open(csv_path('Products.csv'), 'w') as output_path:
        reader = csv.DictReader(source_path)
        writer = get_csv_writer(output_path)

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
            description = row['about_product']
            category = row['category']
            image_path = row['product_link']
            available = available = fake.random_element(elements=('true', 'false'))
            avg_rating = fake.random_int(min=0, max=500) / 100
            seller_id = fake.random_int(min=0, max=num_users)

            #if available == 'true':
                #available_pids.append(pid)
            writer.writerow([productid, name, price, description, category, image_path, available, avg_rating, seller_id])
        print(f'{num_products} generated')
    return


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
# available_pids = gen_products(num_products)
# gen_purchases(num_purchases, available_pids)
