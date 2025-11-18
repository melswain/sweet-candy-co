# models/customer.py
from sqlalchemy import Column, Integer, String
from .database import Base, execute

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
        print('Creating customer...')

        customer_id = Customer.generate_next_customer_id()
        query = """
            INSERT INTO customer (customerId, name, email, phone)
            VALUES (?, ?, ?, ?)
        """
        result = execute(query, (customer_id, name, email, phone))
        if result is True:
            print('Customer added successfully.')
            return True, "Customer added successfully."
        else:
            print('Error adding customer.')
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
        query = "SELECT customerId, totalRewardPoints FROM customer WHERE customerId = ?"
        result = execute(query, (customer_id,))
        if result and len(result) > 0:
            row = result[0]
            return True, Customer(customer_id=row[0], total_reward_points=row[1])
        return False, None
    
    @staticmethod
    def subtractRewardPoints(customer_id, points):
        query = "UPDATE customer SET totalRewardPoints = totalRewardPoints - ? WHERE customerId = ?"
        return execute(query, (points, customer_id)) is True