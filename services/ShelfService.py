import pickle

class ShelfService:
    def __init__(self, filename="shelves.pkl"):
        self.filename = filename
    
    def save_shelves(self, shelves):
        try:
            with open(self.filename, 'wb') as file:
                pickle.dump(shelves, file)
            print(f"Shelves saved successfully to {self.filename}.")
        except Exception as e:
            print(f"An error occurred while saving shelves: {e}")
    
    def load_shelves(self):
        try:
            with open(self.filename, 'rb') as file:
                shelves = pickle.load(file)
            print(f"Shelves loaded successfully from {self.filename}.")
            return shelves
        except FileNotFoundError:
            print(f"No saved data found. Returning an empty list.")
            return []
        except Exception as e:
            print(f"An error occurred while loading shelves: {e}")
            return []
