
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox

class InventoryManager(QMainWindow):
    def __init__(self):
        super().__init__()

        # Connect buttons to their respective methods
        self.addShelfButton.clicked.connect(self.add_or_update_shelf)
        self.deleteShelfButton.clicked.connect(self.delete_shelf)
        self.addProductButton.clicked.connect(self.add_or_update_product)
        self.deleteProductButton.clicked.connect(self.delete_product)
        self.shelvesTable.itemSelectionChanged.connect(self.load_products)

    def add_or_update_shelf(self):
        """Add a new shelf or update the selected shelf's name."""
        shelf_name = self.shelfNameInput.text().strip()
        if not shelf_name:
            QMessageBox.warning(self, "Input Error", "Shelf name cannot be empty.")
            return

        selected_items = self.shelvesTable.selectedItems()
        if selected_items:
            # Update the selected shelf
            selected_row = selected_items[0].row()
            old_shelf_name = self.shelvesTable.item(selected_row, 0).text()
            for shelf in self.shelves_list:
                if shelf.name == old_shelf_name:
                    shelf.name = shelf_name
                    break
            self.shelvesTable.item(selected_row, 0).setText(shelf_name)
        else:
            # Add a new shelf
            new_shelf = Shelf(shelf_name)
            self.shelves_list.append(new_shelf)
            self.shelvesTable.insertRow(self.shelvesTable.rowCount())
            self.shelvesTable.setItem(
                self.shelvesTable.rowCount() - 1, 0, QTableWidgetItem(shelf_name)
            )

        self.shelfNameInput.clear()

    def delete_shelf(self):
        """Delete the selected shelf and its products."""
        selected_items = self.shelvesTable.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "No shelf selected for deletion.")
            return

        selected_row = selected_items[0].row()
        shelf_name = self.shelvesTable.item(selected_row, 0).text()

        # Remove from the shelves list
        self.shelves_list = [shelf for shelf in self.shelves_list if shelf.name != shelf_name]

        # Remove from the UI
        self.shelvesTable.removeRow(selected_row)
        self.productsTable.setRowCount(0)  # Clear products view

    def load_products(self):
        """Load products of the selected shelf into the products table."""
        selected_items = self.shelvesTable.selectedItems()
        if not selected_items:
            return

        selected_row = selected_items[0].row()
        shelf_name = self.shelvesTable.item(selected_row, 0).text()

        for shelf in self.shelves_list:
            if shelf.name == shelf_name:
                self.current_shelf = shelf
                break

        self.productsTable.setRowCount(0)
        for product in self.current_shelf.products:
            row_position = self.productsTable.rowCount()
            self.productsTable.insertRow(row_position)
            self.productsTable.setItem(row_position, 0, QTableWidgetItem(product.name))
            self.productsTable.setItem(row_position, 1, QTableWidgetItem(str(product.quantity)))

    def add_or_update_product(self):
        """Add a new product or update the selected product's details."""
        if not self.current_shelf:
            QMessageBox.warning(self, "Selection Error", "No shelf selected.")
            return

        product_name = self.productNameInput.text().strip()
        product_quantity = self.productQuantityInput.text().strip()

        if not product_name or not product_quantity.isdigit():
            QMessageBox.warning(self, "Input Error", "Invalid product name or quantity.")
            return

        product_quantity = int(product_quantity)
        selected_items = self.productsTable.selectedItems()

        if selected_items:
            # Update the selected product
            selected_row = selected_items[0].row()
            old_product_name = self.productsTable.item(selected_row, 0).text()
            for product in self.current_shelf.products:
                if product.name == old_product_name:
                    product.name = product_name
                    product.quantity = product_quantity
                    break

            self.productsTable.item(selected_row, 0).setText(product_name)
            self.productsTable.item(selected_row, 1).setText(str(product_quantity))
        else:
            # Add a new product
            new_product = Product(product_name, product_quantity)
            self.current_shelf.products.append(new_product)

            row_position = self.productsTable.rowCount()
            self.productsTable.insertRow(row_position)
            self.productsTable.setItem(row_position, 0, QTableWidgetItem(product_name))
            self.productsTable.setItem(row_position, 1, QTableWidgetItem(str(product_quantity)))

        self.productNameInput.clear()
        self.productQuantityInput.clear()

    def delete_product(self):
        """Delete the selected product from the current shelf."""
        if not self.current_shelf:
            QMessageBox.warning(self, "Selection Error", "No shelf selected.")
            return

        selected_items = self.productsTable.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "No product selected for deletion.")
            return

        selected_row = selected_items[0].row()
        product_name = self.productsTable.item(selected_row, 0).text()

        # Remove from the current shelf's product list
        self.current_shelf.products = [
            product for product in self.current_shelf.products if product.name != product_name
        ]

        # Remove from the UI
        self.productsTable.removeRow(selected_row)