# models/database.py
import sqlite3
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base
from contextlib import contextmanager

load_dotenv()

Base = declarative_base()

DB_PATH = "sweetcandyco.db"

def get_connection():
    """Get a new database connection."""
    return sqlite3.connect(DB_PATH)

@contextmanager
def get_cursor():
    """Context manager for getting a cursor and committing/closing automatically."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        conn.close()

def execute(query, params=None):
  try:
    with get_cursor() as cursor:
      cursor.execute(query, params)
      return True
  except Exception as e:
    print(f"Error: {e} ", query)
    return False

def fetchall(query, params=None):
    """Fetch all results for a query."""
    with get_cursor() as cursor:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

def fetchone(query, params=None):
    """Fetch one result for a query."""
    with get_cursor() as cursor:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()

def setup_database():
    """Create all tables and constraints for the candystore database."""
    schema = """
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------
-- DDL: CREATE TABLES
-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS store_location (
    locationId INTEGER PRIMARY KEY AUTOINCREMENT,
    locationName TEXT NOT NULL,
    address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customer (
    customerId TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT,
    email TEXT UNIQUE,
    phone TEXT NOT NULL,
    totalRewardPoints INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cart (
    cartId INTEGER PRIMARY KEY AUTOINCREMENT,
    customerId TEXT,
    totalCartPrice REAL NOT NULL,
    totalRewardPoints INTEGER DEFAULT 0,
    checkoutDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customerId) REFERENCES customer(customerId)
);

CREATE TABLE IF NOT EXISTS product (
    productId INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    price REAL NOT NULL,
    expirationDate TEXT NOT NULL,
    discountPercentage REAL DEFAULT 1.00,
    manufacturerName TEXT,
    upc TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cart_item (
    cartItemId INTEGER PRIMARY KEY AUTOINCREMENT,
    cartId INTEGER NOT NULL,
    productId INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    totalProductPrice REAL NOT NULL,
    FOREIGN KEY (cartId) REFERENCES cart(cartId),
    FOREIGN KEY (productId) REFERENCES product(productId)
);

CREATE TABLE IF NOT EXISTS environment_reading (
    readingId INTEGER PRIMARY KEY AUTOINCREMENT,
    locationId INTEGER NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (locationId) REFERENCES store_location(locationId)
);

CREATE TABLE IF NOT EXISTS inventory (
    inventoryId INTEGER PRIMARY KEY AUTOINCREMENT,
    productId INTEGER NOT NULL,
    locationId INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    lastUpdated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (productId) REFERENCES product(productId),
    FOREIGN KEY (locationId) REFERENCES store_location(locationId)
);

CREATE TABLE IF NOT EXISTS maintenance_threshold (
    thresholdId INTEGER PRIMARY KEY AUTOINCREMENT,
    locationId INTEGER NOT NULL UNIQUE,
    minTemperature REAL NOT NULL,
    maxTemperature REAL NOT NULL,
    minHumidity REAL NOT NULL,
    maxHumidity REAL NOT NULL,
    FOREIGN KEY (locationId) REFERENCES store_location(locationId)
);

CREATE TABLE IF NOT EXISTS maintenance_alert (
    alertId INTEGER PRIMARY KEY AUTOINCREMENT,
    locationId INTEGER NOT NULL,
    parameterType TEXT CHECK(parameterType IN ('temperature', 'humidity')),
    value REAL NOT NULL,
    thresholdBreach TEXT CHECK(thresholdBreach IN ('LOW', 'HIGH')),
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (locationId) REFERENCES store_location(locationId)
);

CREATE TABLE IF NOT EXISTS payment (
    paymentId INTEGER PRIMARY KEY AUTOINCREMENT,
    cartId INTEGER UNIQUE,
    cardNumber TEXT NOT NULL,
    expiryDate TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cartId) REFERENCES cart(cartId)
);

CREATE TABLE productInstance (
    productInstanceId INTEGER PRIMARY KEY AUTOINCREMENT,
    productId INTEGER NOT NULL,
    epcCode TEXT UNIQUE NOT NULL,
    FOREIGN KEY (productId) REFERENCES product(productId)
);

-- ----------------------------------------------------------------------
-- INDEXES
-- ----------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_cart_customerId ON cart(customerId);
CREATE INDEX IF NOT EXISTS idx_cartitem_cartId ON cart_item(cartId);
CREATE INDEX IF NOT EXISTS idx_cartitem_productId ON cart_item(productId);
CREATE INDEX IF NOT EXISTS idx_envreading_locationId ON environment_reading(locationId);
CREATE INDEX IF NOT EXISTS idx_inventory_productId ON inventory(productId);
CREATE INDEX IF NOT EXISTS idx_inventory_locationId ON inventory(locationId);
CREATE INDEX IF NOT EXISTS idx_alert_locationId ON maintenance_alert(locationId);

-- ----------------------------------------------------------------------
-- DML: INSERT DATA
-- ----------------------------------------------------------------------

INSERT INTO store_location (locationName, address) VALUES
('Sweet Candy Co. - Laval', '545 Boulevard des Laurentides, Laval, QC H9S4K9'),
('Sweet Candy Co. - West Island', '20 Avenue Cartier, Pointe-Claire, QC H9R2V4');

INSERT INTO maintenance_threshold (locationId, minTemperature, maxTemperature, minHumidity, maxHumidity) VALUES
(1, 5.00, 13.00, 35.00, 45.00),
(2, 4.00, 12.00, 35.00, 45.00);

INSERT INTO product (name, type, price, expirationDate, discountPercentage, manufacturerName, upc) VALUES
('Chocolate Dream Bar', 'Chocolate', 3.99, '2026-12-31', 1.00, 'Sweet Candy Co', '123456789012'),
('Rainbow Sour Strips', 'Gummy', 4.50, '2026-10-15', 1.00, 'Sweet Candy Co', '123456789029'),
('Peanut Butter Cups 4pk', 'Chocolate', 5.99, '2026-11-30', 1.00, 'Sweet Candy Co', '123456789036'),
('Cherry Licorice Twists', 'Licorice', 3.50, '2026-09-20', 1.00, 'Sweet Candy Co', '123456789043'),
('Sea Salt Caramels 6pc', 'Caramel', 6.99, '2026-08-15', 1.00, 'Sweet Candy Co', '123456789050'),
('Mixed Fruit Hard Candy', 'Hard Candy', 2.99, '2027-01-15', 1.00, 'Sweet Candy Co', '123456789067'),
('Mint Chocolate Thins', 'Chocolate', 4.99, '2026-11-15', 1.00, 'Sweet Candy Co', '123456789074'),
('Gummy Bears Pack', 'Gummy', 3.99, '2026-10-01', 1.00, 'Sweet Candy Co', '123456789081'),
('Toffee Crunch Bar', 'Toffee', 4.50, '2026-12-15', 1.00, 'Sweet Candy Co', '123456789098'),
('Assorted Lollipops 5pk', 'Lollipop', 5.99, '2027-02-28', 1.00, 'Sweet Candy Co', '123456789104');


INSERT INTO customer (customerId, password, name, email, phone, totalRewardPoints) VALUES
('987654321012', 'scrypt:32768:8:1$119fU81mnH3H5noC$629274f97157e19e4d35c95a8cc1da3960a7a11d0201eb0fc7bf5379f12ba64d89c5fe735ba6c09ee97e4d6996da6a8031edd3db8dcb0ed1796ea46050066381', 'Sarah Johnson', 'melanie.l.swain@gmail.com', '438-555-0101', 0),
('987654321029', 'scrypt:32768:8:1$119fU81mnH3H5noC$629274f97157e19e4d35c95a8cc1da3960a7a11d0201eb0fc7bf5379f12ba64d89c5fe735ba6c09ee97e4d6996da6a8031edd3db8dcb0ed1796ea46050066381', 'Michael Chen', 'mchen@email.com', '514-555-0102', 0),
('987654321036', '', 'Emily Rodriguez', 'emily.r@email.com', '613-555-0103', 0),
('987654321043', '', 'David Kim', 'davidk@email.com', '514-555-0104', 0);

INSERT INTO cart (customerId, totalCartPrice, totalRewardPoints) VALUES
('987654321012', 8.45, 0),
('987654321029', 12.00, 0),
('987654321036', 7.00, 0),
('987654321043', 14.00, 0),
('987654321012', 9.25, 0),
('987654321029', 12.00, 0),
('987654321036', 8.00, 0),
('987654321043', 6.50, 0),
('987654321012', 7.40, 0),
('987654321029', 11.00, 0);

INSERT INTO inventory (productId, locationId, quantity) VALUES
(1, 1, 50), (1, 2, 50),
(2, 1, 50), (2, 2, 50),
(3, 1, 50), (3, 2, 50),
(4, 1, 50), (4, 2, 50),
(5, 1, 50), (5, 2, 50),
(6, 1, 50), (6, 2, 50),
(7, 1, 50), (7, 2, 50),
(8, 1, 50), (8, 2, 50),
(9, 1, 50), (9, 2, 50),
(10, 1, 50), (10, 2, 50);

INSERT INTO cart_item (cartId, productId, quantity, totalProductPrice) VALUES
(1, 2, 1, 5.25),
(1, 6, 1, 3.20),
(2, 3, 1, 6.50),
(2, 9, 1, 5.50),
(3, 5, 1, 7.00),
(4, 1, 2, 8.00),
(4, 10, 1, 6.00),
(5, 7, 1, 5.00),
(5, 8, 1, 4.25),
(6, 10, 2, 12.00),
(7, 4, 2, 8.00),
(8, 3, 1, 6.50),
(9, 6, 2, 6.40),
(9, 4, 1, 1.00),
(10, 9, 2, 11.00);

INSERT INTO productInstance (productId, epcCode) VALUES 
(1, 'A00000000000000000004925'),
(1, 'A00000000000000000004930'),
(2, 'A00000000000000000004932'),
(2, 'A00000000000000000004933'),
(3, 'A00000000000000000004934'),
(3, 'A00000000000000000004935'),
(4, 'A00000000000000000004936'),
(4, 'A00000000000000000004937'),
(5, 'A00000000000000000004938'),
(5, 'A00000000000000000004939'),
(6, 'A00000000000000000004940'),
(6, 'A00000000000000000004941'),
(7, 'A00000000000000000004942'),
(7, 'A00000000000000000004943'),
(8, 'A00000000000000000004944'),
(8, 'A00000000000000000004945'),
(9, 'A00000000000000000004946'),
(9, 'A00000000000000000004947'),
(10, 'A00000000000000000004948'),
(10, 'A00000000000000000004949');

    """
    with get_connection() as conn:
        conn.executescript(schema)
        conn.commit()


def ensure_customer_password_column():
  """Ensure the 'password' column exists on the customer table. If missing, add it."""
  try:
    with get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute("PRAGMA table_info(customer)")
      cols = cursor.fetchall()
      names = [c[1] for c in cols]
      if 'password' not in names:
        cursor.execute("ALTER TABLE customer ADD COLUMN password TEXT")
        conn.commit()
        print('Added password column to customer table')
  except Exception as e:
    print('Error ensuring password column:', e)