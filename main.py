import os
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from services import ShelfService
from models import Product, Shelf
import uuid
class MainWindow(QMainWindow):
    shelves_list = []
    shelfService = ShelfService.ShelfService()
    shelf_mode = "ADD"
    product_mode  = "ADD"
    
    def __init__(self):
        super().__init__()
        self.shelves_list = self.shelfService.load_shelves()
        
        # Define image directory
        self.image_dir = "assets/images"
        os.makedirs(self.image_dir, exist_ok=True)  # Ensure the directory exists
        
        # Load the UI from the .ui file
        loadUi("ui/interface.ui", self)
        
        # Connect buttons
        self.add_product_button.clicked.connect(self.add_or_update_product)
        self.add_shelf_button.clicked.connect(self.add_or_update_shelf)
        
        # Add functionality to upload an image
        self.picture.mousePressEvent = self.upload_picture
        
        # Connect the shelf table click event to load products
        self.shelves.itemClicked.connect(self.load_shelf_products)
        self.delete_shelf_button.clicked.connect(self.delete_shelf)  # Delete shelf button
        self.empty.clicked.connect(self.empty_shelf_products)  # Empty button

        # Connect the shelf table click event to load products
        self.shelves.itemClicked.connect(self.load_shelf)
        
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

    def add_or_update_product(self):
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

    def add_or_update_shelf(self):
        """Add or update a shelf."""
        name = self.shelf_name.text()
        location = self.location.text()
        capacity = self.capacity.text()

        # Verify all fields are filled
        if not (name and location and capacity):
            self.statusBar().showMessage("Please fill all fields of shelf", 5000)
            return

        if self.shelf_mode == "UPDATE":
            # Identify the selected shelf to update
            selected_row = self.shelves.currentRow()
            if selected_row == -1:
                self.statusBar().showMessage("No shelf selected for update", 5000)
                return

            # Update the selected shelf in the table
            self.shelves.setItem(selected_row, 0, QTableWidgetItem(name))
            self.shelves.setItem(selected_row, 1, QTableWidgetItem(location))
            self.shelves.setItem(selected_row, 2, QTableWidgetItem(capacity))

            # Update the shelf in the shelf list
            self.shelves_list[selected_row].name = name
            self.shelves_list[selected_row].location = location
            self.shelves_list[selected_row].capacity = capacity

            # Update the comboBox entry
            self.comboBox.setItemText(selected_row, name)

            self.statusBar().showMessage("Shelf updated successfully!", 5000)
        else:  # Default to ADD mode
            # Add shelf details to the shelf table
            row_count = self.shelves.rowCount()
            self.shelves.insertRow(row_count)
            self.shelves.setItem(row_count, 0, QTableWidgetItem(name))
            self.shelves.setItem(row_count, 1, QTableWidgetItem(location))
            self.shelves.setItem(row_count, 2, QTableWidgetItem(capacity))

            # Save the shelf to the shelf list
            self.shelves_list.append(Shelf.Shelf(name, location, capacity, []))
            self.shelfService.save_shelves(self.shelves_list)

            # Add shelf name to the comboBox for product assignment
            self.comboBox.addItem(name)

            self.statusBar().showMessage("Shelf added successfully!", 5000)

        # Reset the form after addition or update
        self.shelf_name.clear()
        self.location.clear()
        self.capacity.clear()
        self.shelf_mode = "ADD"  # Reset mode to ADD

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

    def load_shelf(self, item):
        selected_row = item.row()
        shelf_name = self.shelves.item(selected_row, 0).text()
        selected_shelf = next((shelf for shelf in self.shelves_list if shelf.name == shelf_name), None)
        self.shelf_mode = "UPDATE"
        self.shelf_name.setText(selected_shelf.name)
        self.location.setText(selected_shelf.location)
        self.capacity.setText(str(selected_shelf.capacity))


    def empty_shelf_products(self):
        """Clear all products from the selected shelf."""
        selected_row = self.shelves.currentRow()
        if selected_row == -1:
            self.statusBar().showMessage("No shelf selected", 5000)
            return
        
        shelf_name = self.shelves.item(selected_row, 0).text()
        selected_shelf = next((shelf for shelf in self.shelves_list if shelf.name == shelf_name), None)
        
        if selected_shelf:
            selected_shelf.products.clear()
            self.shelfService.save_shelves(self.shelves_list)
            self.load_shelf_products(self.shelves.item(selected_row, 0))  # Refresh the products list
            self.statusBar().showMessage(f"All products removed from shelf '{shelf_name}'", 5000)

    def delete_shelf(self):
        """Delete the selected shelf."""
        selected_row = self.shelves.currentRow()
        if selected_row == -1:
            self.statusBar().showMessage("No shelf selected", 5000)
            return
        
        shelf_name = self.shelves.item(selected_row, 0).text()
        selected_shelf = next((shelf for shelf in self.shelves_list if shelf.name == shelf_name), None)
        
        if selected_shelf:
            self.shelves_list.remove(selected_shelf)
            self.shelves.removeRow(selected_row)
            self.shelfService.save_shelves(self.shelves_list)
            self.statusBar().showMessage(f"Shelf '{shelf_name}' deleted", 5000)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
