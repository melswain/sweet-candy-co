# services/reward_service.py
from Controllers.customer_controller import getCustomerById

def get_points(membership_number):
    success, customer = getCustomerById(membership_number)

    if not success:
        return {
            "status": 404,
            "body": {"status": "error", "message": "Customer not found"}
        }

    points = customer[1][1]  # business rule: where points are stored
    print("Customer points:", points)

    return {
        "status": 200,
        "body": {"status": "success", "points": points}
    }