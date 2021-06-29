from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QListWidget, QLineEdit, QPushButton, QVBoxLayout,
                             QFormLayout, QLabel, QGridLayout, QApplication, QWidget)
import sys
import keyboard

class Todo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-do list app")

        self.to_do_list = QListWidget()
        self.item = QLineEdit("")

        self.addButton = QPushButton("Add to list")
        self.addButton.clicked.connect(self.add_to_list)

        self.deleteButton = QPushButton("Delete item")
        self.deleteButton.clicked.connect(self.delete_item)

        self.clearButton = QPushButton("Clear list")
        self.clearButton.clicked.connect(self.clear_list)

        self.importantButton = QPushButton("Important")
        self.importantButton.setStyleSheet("background-color: red")
        self.importantButton.clicked.connect(self.set_to_important)

        self.doneButton = QPushButton("Done")
        self.doneButton.setStyleSheet("background-color: green")
        self.doneButton.clicked.connect(self.set_to_done)

        #add/delete item if enter/delete is pressed
        keyboard.add_hotkey('enter', lambda: self.add_to_list())
        keyboard.add_hotkey('delete', lambda: self.delete_item())

        outerLayout = QVBoxLayout()
        
        topLayout = QFormLayout()
        topLayout.addRow(QLabel("Enter things to do:"))
        topLayout.addRow(self.item)
        
        optionsLayout = QGridLayout()
        optionsLayout.addWidget(self.addButton, 0,0)
        optionsLayout.addWidget(self.deleteButton, 0,1)
        optionsLayout.addWidget(self.clearButton, 0,2)
        
        listLayout = QVBoxLayout()
        listLayout.addWidget(self.to_do_list)
        
        bottomLayout = QGridLayout()
        bottomLayout.addWidget(self.importantButton, 0,1)
        bottomLayout.addWidget(self.doneButton, 0,2)

        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(optionsLayout)
        outerLayout.addLayout(listLayout)
        outerLayout.addLayout(bottomLayout)
        #outerLayout.addStretch()
        self.setLayout(outerLayout)

    def add_to_list(self):
        item = self.item.text()
        self.to_do_list.addItem(item)

    def delete_item(self):
        for item in self.to_do_list.selectedItems():
            self.to_do_list.takeItem(self.to_do_list.row(item))

    def clear_list(self):
        self.to_do_list.clear()

    def set_to_important(self):
        item = self.item.text()
        for item in self.to_do_list.selectedItems():
            item.setForeground(QColor("red"))

    def set_to_done(self):
        item = self.item.text()
        for item in self.to_do_list.selectedItems():
            item.setText('\u2713')
            item.setForeground(QColor("green"))


if __name__ == '__main__':
    app = QApplication([])
    td = Todo()
    td.resize(600,300)
    td.show()
    sys.exit(app.exec())
