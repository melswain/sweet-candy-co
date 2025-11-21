# models/customer.py
from types import SimpleNamespace
from sqlalchemy import Column, Integer, String
from .database import Base, execute, fetchone, fetchall, get_connection
from werkzeug.security import generate_password_hash, check_password_hash

class Customer(Base):
    __tablename__ = 'customer'

    customer_id = Column(String(12), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(100), nullable=False, unique=True)
    total_reward_points = Column(Integer, default=0)

    def __repr__(self):
        return f"<Customer(name='{self.name}', email='{self.email}', points={self.total_reward_points})>"

    @staticmethod        
    def create(name, email, phone):

        customer_id = Customer.generate_next_customer_id()
        query = """
            INSERT INTO customer (customerId, name, email, phone)
            VALUES (?, ?, ?, ?)
        """
        result = execute(query, (customer_id, name, email, phone))
        if result is True:
            return True, "Customer added successfully."
        else:
            raise Exception('Error adding customer')
        
    @staticmethod
    def addRewardPoints(customer_id, points_to_add):
        query = """
            UPDATE customer
            SET totalRewardPoints = totalRewardPoints + ?
            WHERE customerId = ?
        """
        result = execute(query, (points_to_add, customer_id))

        if result:
            return True, f"Added {points_to_add} points to customer {customer_id}."
        else:
            raise Exception("Failed to update reward points.")
        
    @staticmethod
    def calculate_checksum(base_digits):
        # GS1-style Modulo-10 checksum
        weights = [3 if i % 2 == 0 else 1 for i in range(len(base_digits))]
        total = sum(int(d) * w for d, w in zip(base_digits[::-1], weights))
        return str((10 - (total % 10)) % 10)

    @staticmethod
    def generate_next_customer_id():
        # Get last customer ID from db
        query = "SELECT customer_id FROM customer ORDER BY customer_id DESC LIMIT 1"
        result = execute(query)
        if result and isinstance(result, list) and len(result) > 0:
            last_id = result[0][0]
            base = int(last_id[:11]) + 1
        else:
            base = 98765432101  # Starting base

        base_str = str(base).zfill(11)
        checksum = Customer.calculate_checksum(base_str)
        return base_str + checksum
    
    @staticmethod
    def getCustomerById(customer_id):
        query = " SELECT customerId, totalRewardPoints FROM customer WHERE customerId = ? "
        result = fetchone(query, (customer_id,))
        if result:
            return True, result
        return False, None
    @staticmethod
    def getCustomerData(customer_id):
        # query = "SELECT customerId, totalRewardPoints FROM customer WHERE customerId = ?"
        query = """
                FROM customer WHERE customerId = ?
                """
        result = fetchall(query, (customer_id,))
        if result and len(result) > 0:
            row = result[0]
            keys = ['customerId','name','email','phone','totalRewardPoints','created_at'];
            customer_data = [
                            SimpleNamespace(**{k: r[i] for i, k in enumerate(keys)}) 
                            for r in result
                            ]
            # return True, Customer(customer_id=row[0],
            #                       name=row[1],
            #                       email=row[2],
            #                       phone=row[3],
            #                       totalRewardPoints=row[4],
            #                       created_at=row[5],)
            return True, customer_data
        return False, None

    @staticmethod
    def get_password_hash(customer_id):
        query = "SELECT password FROM customer WHERE customerId = ?"
        if res:
            return res[0]
        return None

    @staticmethod
    def set_password(customer_id, password_plain):
        # store hashed password
        pw_hash = generate_password_hash(password_plain)
        query = "UPDATE customer SET password = ? WHERE customerId = ?"
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (pw_hash, customer_id))
                conn.commit()
                return True
        except Exception as e:
            print('Error setting password:', e)
            return False
    
    @staticmethod
    def subtractRewardPoints(customer_id, points):
        query = "UPDATE customer SET totalRewardPoints = totalRewardPoints - ? WHERE customerId = ?"
    
    @staticmethod
    def login_customer(customer_id, password):
        try:
            pw_hash = Customer.get_password_hash(customer_id)
            if not pw_hash:
                # no password set
                return False
            return check_password_hash(pw_hash, password)
        except Exception as e:
            print('Error during login_customer:', e)
            return False
