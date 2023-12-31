\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:

-- also we might need to make one of these for every table

SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY GiftCard FROM 'GiftCard.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.giftcard_cardid_seq',
                         (SELECT MAX(cardid)+1 FROM GiftCard),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_productid_seq',
                         (SELECT MAX(productid)+1 FROM Products),
                         false);

\COPY ProductsForSale FROM 'ProductsForSale.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.cart_cartid_seq',
                         (SELECT MAX(cartid)+1 FROM Cart),
                         false);      


\COPY OrdersInProgress FROM 'OrdersInProgress.csv' WITH DELIMITER ',' NULL '' CSV

SELECT pg_catalog.setval('public.ordersinprogress_orderid_seq',
                         (SELECT MAX(orderid)+1 FROM OrdersInProgress),
                         false);

\COPY LineItem FROM 'LineItem.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.lineitem_lineid_seq',
                         (SELECT MAX(lineid)+1 FROM LineItem),
                         false);


\COPY Reviews FROM 'Reviews.csv' WITH DELIMITER ',' NULL '' CSV
SELECT setval('reviews_entity_id_seq', (SELECT MAX(entity_id) FROM Reviews) + 1);
