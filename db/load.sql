-- \COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- -- since id is auto-generated; we need the next command to adjust the counter
-- -- for auto-generation so next INSERT will not clash with ids loaded above:
-- SELECT pg_catalog.setval('public.users_uid_seq',
--                          (SELECT MAX(uid)+1 FROM Users),
--                          false);

-- \COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.products_productid_seq',
--                          (SELECT MAX(productid)+1 FROM Products),
--                          false);

-- \COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM Purchases),
--                          false);

-- \COPY Seller FROM 'Seller.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM Seller),
--                          false);

-- \COPY ProductsForSale FROM 'ProductsForSale.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM ProductsForSale),
--                          false);

-- \COPY OrdersInProgress FROM 'OrdersInProgress.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM OrdersInProgress),
--                          false);

-- \COPY Cart FROM 'Cart.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM Cart),
--                          false);

-- \COPY LineItem FROM 'LineItem.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM LineItem),
--                          false);

-- \COPY ProductReviews FROM 'ProductReviews.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM ProductReviews),
--                          false);

-- \COPY SellerReviews FROM 'SellerReviews.csv' WITH DELIMITER ',' NULL '' CSV
-- SELECT pg_catalog.setval('public.purchases_id_seq',
--                          (SELECT MAX(id)+1 FROM SellerReviews),
--                          false);
--DELETE AFTER
\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_id_seq',
                         (SELECT MAX(id)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_id_seq',
                         (SELECT MAX(id)+1 FROM Products),
                         false);

\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.purchases_id_seq',
                         (SELECT MAX(id)+1 FROM Purchases),
                         false);

\COPY Wishlist FROM 'Wishlist.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.wishlist_id_seq',
                         (SELECT MAX(id)+1 FROM Wishlist),
                         false);