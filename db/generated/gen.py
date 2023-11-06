from werkzeug.security import generate_password_hash
import csv
import os
from faker import Faker

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


# def gen_products(num_products):
#     available_pids = []
#     with open('Products.csv', 'w') as f:
#         writer = get_csv_writer(f)
#         print('Products...', end=' ', flush=True)
#         for pid in range(num_products):
#             if pid % 100 == 0:
#                 print(f'{pid}', end=' ', flush=True)
#             name = fake.sentence(nb_words=4)[:-1]
#             price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
#             available = fake.random_element(elements=('true', 'false'))
#             if available == 'true':
#                 available_pids.append(pid)
#             writer.writerow([pid, name, price, available])
#         print(f'{num_products} generated; {len(available_pids)} available')
#     return available_pids


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
# available_pids = gen_products(num_products)
# gen_purchases(num_purchases, available_pids)
