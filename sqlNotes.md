# Notes from SQLite website and SQL Language Expressions
The notes from SQLite are for terminal, I found other sources letting me know about cursors and connections.
~~~
conn = sqlite3.connect("databaseName)   # The way to open a database, also checks if created or not
cursor = conn.cursor()                  # The way of writing and reading data from the database

conn.commit()                           # The way to save changes to the database
conn.close()                            # The way to close the connection so database is nice and secure
~~~
## Basic SQLite Commands
sqlite3 is included in Python natively, just need to import.
~~~
.tables         : List names of tables in the database
CREATE TABLE    : Create a new table
INSERT          : Insert a new row into a table
SELECT          : Query data from a table
UPDATE          : Modify existing data in a table
DELETE          : Delete rows from a table
DROP TABLE      : Delete an entire table from the database
~~~
Other important commands:
~~~
.databases  : List names of attached databases
.mode       : Set output mode of queries
.headers    : Toggle display of column headers
.nullvalue  : Set text to display for NULL values
~~~
## SQLite Data Types
SQLite does not enforce data type constraints so any type of data can be inserted into any column.  
* INTEGER   : Singed integers  
* REAL      : Floating point values  
* TEXT      : Character strings
* **BLOB**  : Binary data
* NUMERIC   : Decimal numbers
* BOOLEAN   : True or False     (not a real storage class, stored as 0[false] and 1[true])
* DATE      : Date in YYYY-MM-DD
* DATETIME  : Date and time
### Example: How to create table
~~~
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    name TEXT,
    height REAL,
    birthday, DATE
);
~~~
## Creating a new SQLite Database
~~~
$ sqlite3 tutorial.db

SQLite version 3.7.15.2
Enter ".help" for instructions
ENter SQL statements terminated with a ";"
sqlite>
~~~
From here you can run commands like **CREATE TABLE, INSERT** to populate the database.  
## Creating Tables in SQLite
~~~
CREATE TABLE products (                     With constraints:       CREATE TABLE users (
    id INTEGER PRIMARY KEY,                                             id INTEGER PRIMARY KEY,
    name TEXT,                                                          name TEXT NOT NULL,
    quantity INTEGER,                                                   email TEXT UNIQUE,
    price REAL                                                          country TEXT DEFAULT 'US'
);                                                                  );
~~~
Then good practice is to use *.tables* to ensure the table was created successfully.
## Inserting data into a Table
~~~
INSERT INTO products VALUES (1, 'Keyboard', 15, 19.99);

INSERT INTO products (name, quantity, price) VALUES ('Mouse', 25, 9.99);

INSERT INTO users (name, email, country)
VALUES ('John', 'john@example.com', 'UK');
~~~
##  Querying Data in SQLite w/ SELECT
~~~
SELECT * FROM products;

SELECT name, price FROM products;

SELECT * FROM products WHERE price > 10;

SELECT * FROM users JOIN products ON users.id = products.user_id;
~~~
## Updating Data in SQLite Tables
~~~
UPDATE products SET price = price * 1.1;

UPDATE users SET country = 'CA' WHERE name LIKE 'A%';
~~~
## Deleting Data in SQLite Tables
~~~
DELETE FROM products WHERE quantity = 0;

DELETE FROM users WHERE id IN (5, 18, 22);
~~~
## Dropping Tables in SQLite
~~~
DROP TABLE products;
~~~