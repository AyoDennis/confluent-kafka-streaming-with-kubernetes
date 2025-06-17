from faker import Faker
import uuid
fake = Faker()


def get_customer_info():
    """
    Generate a dictionary with customer information.
    Returns:
        dict: A dictionary containing customer information.
    """
    unique_id = uuid.uuid4()
    return {
        "customer_id": str(unique_id),
        "name": fake.name(),
        "address1": fake.address(),
        "email": fake.email(),
        "occupation": fake.job(),
        "created_at": fake.year()
    }


if __name__ == "__main__":
    print(get_customer_info())
