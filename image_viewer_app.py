import json
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, \
    QListWidget, QLabel, QListWidgetItem, QFileDialog


class ImageViewer(QWidget):

    def __init__(self):
        super().__init__()
        # set window name and geometry
        self.setWindowTitle("Image Viewer")
        self.resize(1200, 900)
        self.master_layout = QHBoxLayout()

        self.folder_path = None
        self.settings_file = "settings.json"
        self.scaled_max_dimension = 800

        self.init_UI()
        self.event_handler()

        self.check_settings_file()

    def init_UI(self):

        # file layout
        self.file_layout = QVBoxLayout()
        self.file_list = QListWidget()
        self.open_folder_button = QPushButton("Open a folder")
        self.file_layout.addWidget(self.file_list)
        self.file_layout.addWidget(self.open_folder_button)

        # image layout
        self.image_layout = QHBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_layout.addWidget(self.image_label)

        self.master_layout.addLayout(self.file_layout, 1)
        self.master_layout.addLayout(self.image_layout, 3)

        self.setLayout(self.master_layout)
        #self.master_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def event_handler(self):
        self.open_folder_button.clicked.connect(self.set_directory)
        self.file_list.itemClicked.connect(self.display_image)

    def set_directory(self):
        path = QFileDialog.getExistingDirectory()
        if os.path.exists(path) and os.path.isdir(path):
            self.folder_path = path
            self.load_images(self.folder_path)
            self.save_paths()

    def display_image(self, item):
        # Get full file path
        filepath = os.path.join(self.folder_path, item.text())
        # Create QPixmap object
        pixmap = QPixmap(filepath).scaled(
            self.scaled_max_dimension,
            self.scaled_max_dimension,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
            )
        # Set the QPixmap object on the label to display the image
        self.image_label.setPixmap(pixmap)

    def load_images(self, folder_path):
        self.file_list.clear()  # Clear any existing items

        for filename in os.listdir(folder_path):
            # Check valid image files
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                item = QListWidgetItem(filename)
                self.file_list.addItem(item)

        # Check for the first item on the list
        first_item = self.file_list.item(0)
        if first_item:
            # If it exists display it on startup
            first_filename = first_item.text()
            first_filepath = os.path.join(folder_path, first_filename)

            # Load and display the first image
            pixmap = QPixmap(first_filepath).scaled(self.scaled_max_dimension,
                                                    self.scaled_max_dimension,
                                                    Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
        else:
            print("File not found!")


    def check_settings_file(self):
        try:
            with open(self.settings_file, "r") as file:
                data = json.load(file)
                # normalize path to avoid weird slashes configuration
                if data.get("source") is not None:
                    self.folder_path = data.get("source", "")
                    if os.path.isdir(self.folder_path):
                        self.load_images(self.folder_path)

        except FileNotFoundError:
            with open(self.settings_file, "w") as file:
                json.dump({"source": self.folder_path}, file)

    def save_paths(self):
        source_path = os.path.normpath(self.folder_path)
        with open(self.settings_file, "w") as file:
            json.dump({"source": source_path}, file)



if __name__ == "__main__":
    import sys
    app = QApplication([])
    image_viewer = ImageViewer()
    image_viewer.show()
    sys.exit(app.exec())