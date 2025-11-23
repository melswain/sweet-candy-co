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
        print('Creating a new customer...')
        customer_id = Customer.generate_next_customer_id()
        print("New customer id: ", customer_id)
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
    def calculate_checksum(base_digits: str) -> str:
        total = 0
        for i, d in enumerate(reversed(base_digits)):
            weight = 3 if (i % 2 == 0) else 1
            total += int(d) * weight
        return str((10 - (total % 10)) % 10)

    @staticmethod
    def generate_next_customer_id():
        # Get last ID
        result = fetchone("SELECT customerId FROM customer ORDER BY customerId DESC LIMIT 1")
        if result:
            last_id = str(result[0])
            base = int(last_id[:-1]) + 1
        else:
            base = 987654321

        while True:
            base_str = str(base).zfill(9)
            checksum = Customer.calculate_checksum(base_str)
            candidate_id = base_str + checksum
            
            # check if candidate exists
            check_query = "SELECT COUNT(1) FROM customer WHERE customerId = ?"
            count = fetchone(check_query, (candidate_id,))
            print(count)
            if count[0] == 0:
                return candidate_id

            base += 1
    
    @staticmethod
    def getCustomerById(customer_id):
        query = " SELECT customerId, totalRewardPoints, email FROM customer WHERE customerId = ? "
        result = fetchone(query, (customer_id,))
        if result:
            return True, result
        return False, None
    
    @staticmethod
    def getCustomerData(customer_id):
        query = "SELECT customerId, name, email, phone, totalRewardPoints, created_at FROM customer WHERE customerId = ?"
        result = fetchone(query, (customer_id,))
        if len(result) > 0:
            keys = ['customerId', 'name', 'email', 'phone', 'totalRewardPoints', 'created_at']
            customer_data = SimpleNamespace(**dict(zip(keys, result)))
            return True, customer_data
        return False, None

    @staticmethod
    def get_password_hash(customer_id):
        query = "SELECT password FROM customer WHERE customerId = ?"
        password = fetchone(query, (customer_id,))
        print("Password: ", password[0])
        return password[0]

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
            print(check_password_hash(pw_hash, password))
            return check_password_hash(pw_hash, password)
        except Exception as e:
            print('Error during login_customer:', e)
            return False
