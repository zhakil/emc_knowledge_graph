import json
from faker import Faker

fake = Faker()

def generate_standards(count=50):
    return [
        {
            "id": f"std-{i:03d}",
            "name": f"IEC 61000-4-{fake.random_int(1, 30)}",
            "category": fake.random_element(["Immunity", "Emission", "Safety"]),
            "version": fake.year()
        }
        for i in range(count)
    ]

if __name__ == "__main__":
    standards = generate_standards()
    with open("tests/test_data/standards.json", "w") as f:
        json.dump(standards, f, indent=2) 