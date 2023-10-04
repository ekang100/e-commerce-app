-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

-- if you look in psql for some reason when you change the primary keys in here it doesn't actually change so that might be why idk

CREATE TABLE Users (
    uid INT NOT NULL GENERATED BY DEFAULT AS IDENTITY,
    address VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (balance >= 0.00), --constraint balance > 0
    isSeller BOOLEAN DEFAULT FALSE,
    -- cartid INT NOT NULL GENERATED BY DEFAULT AS IDENTITY, (what if we just dont have this in user table..)
    -- PRIMARY KEY (uid, email)
    PRIMARY KEY (uid) -- this overwrites the previous primary key but idk if that's what we want (but it makes the tables that reference uid work)
);

--withdraw needs to be a function to add or remove balance
--pubProfile should be a view from User (name, accountID, PubProfileID)

CREATE TABLE Seller (
    --address VARCHAR NOT NULL REFERENCES Users(address),
    --email VARCHAR REFERENCES Users(email),
    uid INT NOT NULL PRIMARY KEY REFERENCES Users(uid)
);

CREATE TABLE Products (
    productid INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    description VARCHAR(255),
    category VARCHAR(255) NOT NULL,
    available BOOLEAN DEFAULT FALSE,
    avg_rating DECIMAL DEFAULT 0,
    seller_id INT REFERENCES Users (uid)
);

CREATE TABLE Purchases (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(uid),
    pid INT NOT NULL REFERENCES Products(productid),
    time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

CREATE TABLE ProductsForSale ( -- do we need price here
    -- id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY
    productid INT NOT NULL REFERENCES Products(productid),
    uid INT NOT NULL REFERENCES Seller(uid),
    quantity INT NOT NULL,
    PRIMARY KEY (productid, uid)
);

CREATE TABLE Cart (
    buyerid INT NOT NULL REFERENCES Users (uid), -- trying to identify cart by the user instead of using the cartid in Users table
    -- cartid INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY REFERENCES Users(cartid),
    cartid INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uniqueItemCount INT NOT NULL 
); 

CREATE TABLE LineItem (
    lineid INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, -- updated
    cartid INT NOT NULL REFERENCES Cart(cartid),
    productid INT NOT NULL REFERENCES Products(productid),
    quantities INT NOT NULL,
    unitPrice DECIMAL(65,2) NOT NULL,
    status BOOLEAN DEFAULT FALSE,
    date timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
    -- PRIMARY KEY (lineid) -- updated
);

CREATE TABLE OrdersInProgress (
    -- address VAsRCHAR NOT NULL REFERENCES Users(address), -- this doesn't work because it has to reference a primary key or a unique key
    -- do we need address here? im not gonna change it rn
    orderid INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    lineid INT NOT NULL REFERENCES LineItem(lineid), -- update maybe
    -- quantities INT NOT NULL REFERENCES LineItem(quantities), -- this is causing issues
    productid INT NOT NULL REFERENCES Products(productid)
    --get status, date, quantities from lineItem
);

CREATE TABLE ProductReviews (
    productid INT NOT NULL REFERENCES Products(productid),
    uid INT NOT NULL REFERENCES Users(uid),
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comments VARCHAR(255),
    date timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    PRIMARY KEY (productid, uid)
);

CREATE TABLE SellerReviews (
    sellerid INT NOT NULL REFERENCES Seller(uid),
    uid INT NOT NULL REFERENCES Users(uid),
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comments VARCHAR(255),
    date timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    PRIMARY KEY (sellerid, uid)
);
