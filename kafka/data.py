from faker import Faker

fake = Faker()


def get_customer_info():
    return {
        "name": fake.name(),
        "address": fake.address(),
        "email": fake.email(),
        "occupation": fake.job(),
        "created_at": fake.year()
    }


if __name__ == "__main__":
    print(get_customer_info())
