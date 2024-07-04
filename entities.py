class Allocation:
    def __init__(self, name, amount_free, amount_occupied):
        self.amount_free = amount_free
        self.amount_occupied = amount_occupied
        self.name = name

    def get_amount_free(self):
        return self.amount_free

    def get_amount_occupied(self):
        return self.amount_occupied

    def get_name(self):
        return self.name

    def set_amount_free(self, amount_free):
        self.amount_free = amount_free

    def set_amount_occupied(self, amount_occupied):
        self.amount_occupied = amount_occupied

    def set_name(self, name):
        self.name = name

    def display_data(self):
        print(f"Name: {self.name}")
        print(f"Amount Free: {self.amount_free}")
        print(f"Amount Occupied: {self.amount_occupied}")

    def toString(self):
        return f"{self.name} Amount free: {self.amount_free} | Amount occupied: {self.amount_occupied}"

