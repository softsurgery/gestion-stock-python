import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from services import ShelfService
from models import Product, Shelf
import uuid
class MainWindow(QMainWindow):
    shelves_list = []
    shelfService = ShelfService.ShelfService()
    
    def __init__(self):
        super().__init__()
        self.shelves_list = self.shelfService.load_shelves()
        
        # Define image directory
        self.image_dir = "assets/images"
        os.makedirs(self.image_dir, exist_ok=True)  # Ensure the directory exists
        
        # Load the UI from the .ui file
        loadUi("ui/interface.ui", self)
        
        # Connect buttons
        self.add_product_button.clicked.connect(self.add_product)
        self.add_shelf_button.clicked.connect(self.add_shelf)
        
        # Add functionality to upload an image
        self.picture.mousePressEvent = self.upload_picture
        
        # Connect the shelf table click event to load products
        self.shelves.itemClicked.connect(self.load_shelf_products)
        
        # Placeholder for the picture path
        self.picture_path = None

        # Load shelves and products into the respective tables
        self.load_shelves_to_table()

    def upload_picture(self, event):
        """Upload a picture and save it to the assets/images directory."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Picture", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # Copy the file to the assets/images directory with a unique name
            filename = os.path.basename(file_path)
            unique_filename = f"{uuid.uuid4()}_{filename}"  # Make the filename unique
            saved_path = os.path.join(self.image_dir, unique_filename)
            shutil.copy(file_path, saved_path)
            
            # Update picture path and display the image
            self.picture_path = saved_path
            pixmap = QPixmap(saved_path)
            self.picture.setPixmap(pixmap)
            self.picture.setScaledContents(True)

    def add_product(self):
        """Add a new product and save its picture."""
        # Gather product information
        name = self.product_name.text()
        brand = self.brand.text()
        price = self.price.text()
        description = self.description.toPlainText()
        shelf = self.comboBox.currentText()
        
        # Verify all fields are filled
        if not (name and brand and price and description and shelf and self.picture_path):
            self.statusBar().showMessage("Please fill all fields of product and upload a picture.", 5000)
            return
        
        # Find the shelf object to add the product
        for sh in self.shelves_list:
            if sh.name == shelf:
                sh.products.append(Product.Product(name, brand, price, description, self.picture_path))
                break
        
        # Save the updated shelves list
        self.shelfService.save_shelves(self.shelves_list)
        
        # Reset the form
        self.product_name.clear()
        self.brand.clear()
        self.price.clear()
        self.description.clear()
        self.comboBox.setCurrentIndex(0)
        self.picture.setText("Picture")
        self.picture_path = None
        self.statusBar().showMessage("Product added successfully!", 5000)

    def add_shelf(self):
        """Add a new shelf."""
        name = self.shelf_name.text()
        location = self.location.text()
        capacity = self.capacity.text()
        
        # Verify all fields are filled
        if not (name and location and capacity):
            self.statusBar().showMessage("Please fill all fields of shelf", 5000)
            return
        
        # Add shelf details to the shelf table
        row_count = self.shelves.rowCount()
        self.shelves.insertRow(row_count)
        self.shelves.setItem(row_count, 0, QTableWidgetItem(name))
        self.shelves.setItem(row_count, 1, QTableWidgetItem(location))
        self.shelves.setItem(row_count, 2, QTableWidgetItem(capacity))
        
        # Save the shelf to the file
        self.shelves_list.append(Shelf.Shelf(name, location, capacity, []))
        self.shelfService.save_shelves(self.shelves_list)
        
        # Add shelf name to the comboBox for product assignment
        self.comboBox.addItem(name)
        
        # Reset the form
        self.shelf_name.clear()
        self.location.clear()
        self.capacity.clear()
        self.statusBar().showMessage("Shelf added successfully!", 5000)

    def load_shelves_to_table(self):
        """Load shelves from the list to the table widget."""
        for shelf in self.shelves_list:
            row_count = self.shelves.rowCount()
            self.shelves.insertRow(row_count)
            self.shelves.setItem(row_count, 0, QTableWidgetItem(shelf.name))
            self.shelves.setItem(row_count, 1, QTableWidgetItem(shelf.location))
            self.shelves.setItem(row_count, 2, QTableWidgetItem(str(shelf.capacity)))
            
            # Add shelf name to the comboBox for product assignment
            self.comboBox.addItem(shelf.name)

    def load_shelf_products(self, item):
        """Load products for the selected shelf."""
        selected_row = item.row()
        shelf_name = self.shelves.item(selected_row, 0).text()
        
        selected_shelf = next((shelf for shelf in self.shelves_list if shelf.name == shelf_name), None)
        if not selected_shelf:
            self.statusBar().showMessage("Shelf not found!", 5000)
            return
        
        self.products.setRowCount(0)
        
        for product in selected_shelf.products:
            row_count = self.products.rowCount()
            self.products.insertRow(row_count)
            self.products.setItem(row_count, 0, QTableWidgetItem(product.name))
            self.products.setItem(row_count, 1, QTableWidgetItem(product.brand))
            self.products.setItem(row_count, 2, QTableWidgetItem(product.price))
            self.products.setItem(row_count, 3, QTableWidgetItem(product.description))


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
