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
    print(f"Error: {e}")
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
    CREATE TABLE IF NOT EXISTS cart (
      cartId INTEGER PRIMARY KEY AUTOINCREMENT,
      customerId VARCHAR(12),
      totalCartPrice DECIMAL(10,2) NOT NULL,
      totalRewardPoints INTEGER DEFAULT 0,
      checkoutDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (customerId) REFERENCES customer(customerId)
    );

    CREATE TABLE IF NOT EXISTS cart_item (
      cartItemId INTEGER PRIMARY KEY AUTOINCREMENT,
      cartId INTEGER NOT NULL,
      productId INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      totalProductPrice DECIMAL(10,0) NOT NULL,
      FOREIGN KEY (cartId) REFERENCES cart(cartId),
      FOREIGN KEY (productId) REFERENCES product(productId)
    );

    CREATE TABLE IF NOT EXISTS customer (
      customerId VARCHAR(12) PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      password VARCHAR(100),
      email VARCHAR(100) UNIQUE,
      phone VARCHAR(20) NOT NULL,
      totalRewardPoints INTEGER DEFAULT 0,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS environment_reading (
      readingId INTEGER PRIMARY KEY AUTOINCREMENT,
      locationId INTEGER NOT NULL,
      temperature DECIMAL(5,2) NOT NULL,
      humidity DECIMAL(5,2) NOT NULL,
      timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (locationId) REFERENCES store_location(locationId)
    );

    CREATE TABLE IF NOT EXISTS inventory (
      inventoryId INTEGER PRIMARY KEY AUTOINCREMENT,
      productId INTEGER NOT NULL,
      locationId INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      lastUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (productId) REFERENCES product(productId),
      FOREIGN KEY (locationId) REFERENCES store_location(locationId)
    );

    CREATE TABLE IF NOT EXISTS maintenance_alert (
      alertId INTEGER PRIMARY KEY AUTOINCREMENT,
      locationId INTEGER NOT NULL,
      parameterType TEXT CHECK(parameterType IN ('temperature', 'humidity')),
      value DECIMAL(5,2) NOT NULL,
      thresholdBreach TEXT CHECK(thresholdBreach IN ('LOW', 'HIGH')),
      timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (locationId) REFERENCES store_location(locationId)
    );

    CREATE TABLE IF NOT EXISTS maintenance_threshold (
      thresholdId INTEGER PRIMARY KEY AUTOINCREMENT,
      locationId INTEGER NOT NULL UNIQUE,
      minTemperature DECIMAL(5,2) NOT NULL,
      maxTemperature DECIMAL(5,2) NOT NULL,
      minHumidity DECIMAL(5,2) NOT NULL,
      maxHumidity DECIMAL(5,2) NOT NULL,
      FOREIGN KEY (locationId) REFERENCES store_location(locationId)
    );

    CREATE TABLE IF NOT EXISTS payment (
      paymentId INTEGER PRIMARY KEY AUTOINCREMENT,
      cartId INTEGER UNIQUE,
      cardNumber VARCHAR(20) NOT NULL,
      expiryDate VARCHAR(7) NOT NULL,
      timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (cartId) REFERENCES cart(cartId)
    );

    CREATE TABLE IF NOT EXISTS product (
      productId INTEGER PRIMARY KEY AUTOINCREMENT,
      name VARCHAR(100) NOT NULL,
      type VARCHAR(50) NOT NULL,
      price DECIMAL(10,0) NOT NULL,
      expirationDate DATE NOT NULL,
      discountPercentage DECIMAL(3,2) DEFAULT 1.00,
      manufacturerName VARCHAR(100),
      upc VARCHAR(12) NOT NULL UNIQUE,
      epc VARCHAR(50) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS store_location (
      locationId INTEGER PRIMARY KEY AUTOINCREMENT,
      locationName VARCHAR(100) NOT NULL,
      address VARCHAR(255) NOT NULL
    );

    -- Foreign keys (SQLite requires PRAGMA foreign_keys=ON)
    PRAGMA foreign_keys = ON;

    -- Create indexes to match MySQL schema
    CREATE INDEX IF NOT EXISTS idx_cart_customerId ON cart(customerId);
    CREATE INDEX IF NOT EXISTS idx_cartitem_cartId ON cart_item(cartId);
    CREATE INDEX IF NOT EXISTS idx_cartitem_productId ON cart_item(productId);
    CREATE INDEX IF NOT EXISTS idx_envreading_locationId ON environment_reading(locationId);
    CREATE INDEX IF NOT EXISTS idx_inventory_productId ON inventory(productId);
    CREATE INDEX IF NOT EXISTS idx_inventory_locationId ON inventory(locationId);
    CREATE INDEX IF NOT EXISTS idx_alert_locationId ON maintenance_alert(locationId);

    INSERT INTO store_location (locationName, address) VALUES
    ('Sweet Candy Co. - Laval', '545 Boulevard des Laurentides, Laval, QC H9S4K9'),
    ('Sweet Candy Co. - West Island', '20 Avenue Cartier, Pointe-Claire, QC H9R2V4');

    INSERT INTO maintenance_threshold (locationId, minTemperature, maxTemperature, minHumidity, maxHumidity) VALUES
    (1, 5.00, 13.00, 35.00, 45.00),  -- Laval location
    (2, 4.00, 12.00, 35.00, 45.00);  -- West Island location

    INSERT INTO customer (customerId, password, name, email, phone, totalRewardPoints) VALUES
    ('987654321012', 'Dog1', 'Sarah Johnson', 'sarah.j@email.com', '438-555-0101', 0),
    ('987654321029', 'Cat2', 'Michael Chen', 'mchen@email.com', '514-555-0102', 0),
    ('987654321036', 'Bird3', 'Emily Rodriguez', 'emily.r@email.com', '613-555-0103', 0),
    ('987654321043', 'Bunny4', 'David Kim', 'davidk@email.com', '514-555-0104', 0);

    INSERT INTO product (name, type, price, expirationDate, discountPercentage, manufacturerName, upc, epc) VALUES
    ('Chocolate Dream Bar', 'Chocolate', 3.99, '2026-12-31', 1.00, 'Sweet Candy Co', '123456789012', 'A00000000000000000004917'),
    ('Rainbow Sour Strips', 'Gummy', 4.50, '2026-10-15', 1.00, 'Sweet Candy Co', '123456789029', 'A00000000000000000004921'),
    ('Peanut Butter Cups 4pk', 'Chocolate', 5.99, '2026-11-30', 1.00, 'Sweet Candy Co', '123456789036', 'EPC123003'),
    ('Cherry Licorice Twists', 'Licorice', 3.50, '2026-09-20', 1.00, 'Sweet Candy Co', '123456789043', 'EPC123004'),
    ('Sea Salt Caramels 6pc', 'Caramel', 6.99, '2026-08-15', 1.00, 'Sweet Candy Co', '123456789050', 'EPC123005'),
    ('Mixed Fruit Hard Candy', 'Hard Candy', 2.99, '2027-01-15', 1.00, 'Sweet Candy Co', '123456789067', 'EPC123006'),
    ('Mint Chocolate Thins', 'Chocolate', 4.99, '2026-11-15', 1.00, 'Sweet Candy Co', '123456789074', 'EPC123007'),
    ('Gummy Bears Pack', 'Gummy', 3.99, '2026-10-01', 1.00, 'Sweet Candy Co', '123456789081', 'EPC123008'),
    ('Toffee Crunch Bar', 'Toffee', 4.50, '2026-12-15', 1.00, 'Sweet Candy Co', '123456789098', 'EPC123009'),
    ('Assorted Lollipops 5pk', 'Lollipop', 5.99, '2027-02-28', 1.00, 'Sweet Candy Co', '123456789104', 'EPC123010');
        
    INSERT INTO inventory (productId, locationId, quantity) VALUES
    (1, 1, 10), (1, 2, 10),
    (2, 1, 10), (2, 2, 10),
    (3, 1, 10), (3, 2, 10),
    (4, 1, 10), (4, 2, 10),
    (5, 1, 10), (5, 2, 10),
    (6, 1, 10), (6, 2, 10),
    (7, 1, 10), (7, 2, 10),
    (8, 1, 10), (8, 2, 10),
    (9, 1, 10), (9, 2, 10),
    (10, 1, 10), (10, 2, 10);
    """
    with get_connection() as conn:
        conn.executescript(schema)
        conn.commit()