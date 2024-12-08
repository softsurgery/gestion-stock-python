class Shelf():
    def __init__(self, name, location, capacity, products):
        self.name = name
        self.location = location
        self.capacity = capacity
        self.products = products
        
    def add_product(self, product):
        if len(self.products) < self.capacity:
            self.products.append(product)
        else:
            print(f"Shelf {self.name} is at maximum capacity.")
    
    def remove_product(self, product):
        for product in self.products:
            if product.name == product.name:
                self.products.remove(product)
                break
        else:
            print(f"Product {product.name} not found on shelf {self.name}.")