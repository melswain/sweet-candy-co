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
      customerId INTEGER,
      totalCartPrice DECIMAL(10,2) NOT NULL,
      totalRewardPoints INTEGER DEFAULT 0,
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS cart_item (
      cartItemId INTEGER PRIMARY KEY AUTOINCREMENT,
      cartId INTEGER NOT NULL,
      productId INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      totalProductPrice DECIMAL(10,0) NOT NULL,
      totalRewardPoints INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS customer (
      customerId INTEGER PRIMARY KEY AUTOINCREMENT,
      name VARCHAR(100) NOT NULL,
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
      timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS inventory (
      inventoryId INTEGER PRIMARY KEY AUTOINCREMENT,
      productId INTEGER NOT NULL,
      locationId INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      lastUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS maintenance_alert (
      alertId INTEGER PRIMARY KEY AUTOINCREMENT,
      locationId INTEGER NOT NULL,
      parameterType TEXT DEFAULT NULL,
      value DECIMAL(5,2) NOT NULL,
      thresholdBreach TEXT DEFAULT NULL,
      timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS maintenance_threshold (
      thresholdId INTEGER PRIMARY KEY AUTOINCREMENT,
      locationId INTEGER NOT NULL UNIQUE,
      minTemperature DECIMAL(5,2) NOT NULL,
      maxTemperature DECIMAL(5,2) NOT NULL,
      minHumidity DECIMAL(5,2) NOT NULL,
      maxHumidity DECIMAL(5,2) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS payment (
      paymentId INTEGER PRIMARY KEY AUTOINCREMENT,
      cartId INTEGER UNIQUE,
      cardNumber VARCHAR(20) NOT NULL,
      expiryDate VARCHAR(7) NOT NULL,
      timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS product (
      productId INTEGER PRIMARY KEY AUTOINCREMENT,
      name VARCHAR(100) NOT NULL,
      type VARCHAR(50) NOT NULL,
      price DECIMAL(10,0) NOT NULL,
      expirationDate DATE NOT NULL,
      discountPercentage DECIMAL(3,2) DEFAULT 1.00,
      associatedRewardPoints INTEGER NOT NULL DEFAULT 0,
      upc VARCHAR(50) NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS store_location (
      locationId INTEGER PRIMARY KEY AUTOINCREMENT,
      locationName VARCHAR(100) NOT NULL,
      address VARCHAR(255) NOT NULL
    );

    -- Foreign keys (SQLite requires PRAGMA foreign_keys=ON)
    PRAGMA foreign_keys = ON;

    -- Add foreign keys
    CREATE INDEX IF NOT EXISTS idx_cart_customerId ON cart(customerId);
    CREATE INDEX IF NOT EXISTS idx_cartitem_cartId ON cart_item(cartId);
    CREATE INDEX IF NOT EXISTS idx_cartitem_productId ON cart_item(productId);
    CREATE INDEX IF NOT EXISTS idx_envreading_locationId ON environment_reading(locationId);
    CREATE INDEX IF NOT EXISTS idx_inventory_productId ON inventory(productId);
    CREATE INDEX IF NOT EXISTS idx_inventory_locationId ON inventory(locationId);
    CREATE INDEX IF NOT EXISTS idx_alert_locationId ON maintenance_alert(locationId);

    -- Add constraints (SQLite only supports some ALTER TABLE operations)
    -- Foreign keys are defined inline in CREATE TABLE above where possible.
    """
    with get_connection() as conn:
        conn.executescript(schema)
        conn.commit()