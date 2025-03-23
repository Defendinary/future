import faker

# https://pypi.org/project/Faker/

# Create a Faker instance
fake = faker.Faker()

def generate_fake_user():
    """Generate a dictionary containing fake user data"""
    return {
        'name': fake.name(),
        'email': fake.email(),
        'address': fake.address(),
        'phone': fake.phone_number(),
        'job': fake.job(),
        'company': fake.company(),
        'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d')
    }

def generate_fake_users(count=5):
    """Generate a list of fake users"""
    return [generate_fake_user() for _ in range(count)]

if __name__ == '__main__':
    # Example usage
    users = generate_fake_users(3)
    for user in users:
        print("\nUser Details:")
        for key, value in user.items():
            print(f"{key}: {value}")

