import json
import os
from PIL import ImageFilter, Image, ImageOps
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, \
    QListWidget, QLabel, QListWidgetItem, QFileDialog

from ascii_convert import ImageToAsciiConverter


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
        self.current_filepath = ""
        self.current_index = 0
        self.ascii_converter = ImageToAsciiConverter()

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
        self.image_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_info_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_info_label.setFixedHeight(20)

        # image fileter buttons
        self.filter_buttons_layout = QHBoxLayout()
        self.contour_button = QPushButton("Contour")
        self.blur_button = QPushButton("Blur")
        self.invert_button = QPushButton("Invert")
        self.gray_button = QPushButton("Grayscale")
        self.ascii_button = QPushButton("ASCII")
        self.filter_buttons_layout.addWidget(self.contour_button)
        self.filter_buttons_layout.addWidget(self.blur_button)
        self.filter_buttons_layout.addWidget(self.invert_button)
        self.filter_buttons_layout.addWidget(self.gray_button)
        self.filter_buttons_layout.addWidget(self.ascii_button)
        #
        self.image_layout.addWidget(self.image_label)
        self.image_layout.addWidget(self.image_info_label)
        self.image_layout.addLayout(self.filter_buttons_layout)

        self.master_layout.addLayout(self.file_layout, 1)
        self.master_layout.addLayout(self.image_layout, 3)

        self.setLayout(self.master_layout)

        self.style()

    def style(self):

        # style the selection in the file list widget
        self.file_list.setStyleSheet("""
            QListWidget::item:selected {
                background-color: #4A90E2; /* Strong blue highlight */
                color: white; /* White text for contrast */
                border: 2px solid #357ABD; /* Optional border */
            }
            QListWidget::item:hover {
                background-color: #A0C4FF; /* Light blue when hovering */
            }
        """)

    def event_handler(self):
        self.open_folder_button.clicked.connect(self.set_directory)
        self.file_list.itemClicked.connect(self.display_image)
        self.contour_button.clicked.connect(self.contour)
        self.blur_button.clicked.connect(self.blur)
        self.invert_button.clicked.connect(self.invert)
        self.gray_button.clicked.connect(self.grayscale)
        self.ascii_button.clicked.connect(self.ascii)

    def set_directory(self):
        path = QFileDialog.getExistingDirectory()
        if os.path.exists(path) and os.path.isdir(path):
            self.folder_path = path
            self.load_images(self.folder_path)
            self.save_paths()

    def display_image(self, item):
        # Get full file path
        self.current_filepath = os.path.join(self.folder_path, item.text())

        # Set the index of the current item here on click
        self.current_index = self.file_list.row(item)

        # Create QPixmap object
        pixmap = self.create_pixmap_from_url(self.current_filepath)
        # Set the QPixmap object on the label to display the image
        self.display_image_info()
        self.image_label.setPixmap(pixmap)

    def display_image_info(self):
        self.image_info_label.setText(
            f"Image {self.current_index + 1} of {len(self.file_list)}: {os.path.basename(self.current_filepath)}")


    def load_images(self, folder_path):
        self.file_list.clear()  # Clear any existing items

        for filename in os.listdir(folder_path):
            # Check valid image files
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")):
                item = QListWidgetItem(filename)
                self.file_list.addItem(item)

        # Check for the first item on the list
        first_item = self.file_list.item(0)
        if first_item:
            # If it exists display it on startup
            first_filename = first_item.text()
            first_filepath = os.path.join(folder_path, first_filename)

            # Load and display the first image
            pixmap = self.create_pixmap_from_url(first_filepath)
            self.current_filepath = first_filepath

            self.image_label.setPixmap(pixmap)
            self.display_image_info()
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





    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:  # Scroll up
            self.current_index = (self.current_index - 1) % len(self.file_list)
        else:  # Scroll down
            self.current_index = (self.current_index + 1) % len(self.file_list)

        self.load_image(self.current_index)
        #print(self.current_index)

    def load_image(self, index):
        if 0 <= index < len(self.file_list):
            item = self.file_list.item(index)

            if item:
                item_filename = item.text()
                item_filepath = os.path.join(self.folder_path, item_filename)

                # Load and display the current image
                pixmap = self.create_pixmap_from_url(item_filepath)
                self.current_filepath = item_filepath

                self.image_label.setPixmap(pixmap)
                self.display_image_info()

            print(index)

    def create_pixmap_from_url(self, image):
        """Creates a pixmap object to be displayed"""
        # Load and display the current image
        pixmap = QPixmap(image).scaled(
            self.scaled_max_dimension,
            self.scaled_max_dimension,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
            )

        return pixmap


    def create_pixmap_from_image(self, image):
        """Creates a pixmap object to be displayed"""
        # Load and display the current image
        pixmap = QPixmap.fromImage(image).scaled(
            self.scaled_max_dimension,
            self.scaled_max_dimension,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
            )

        return pixmap

    def contour(self):

        image = Image.open(self.current_filepath)
        print(f"Image Mode: {image.mode}")

        image = image.filter(ImageFilter.CONTOUR)
        #image.show()
        # Convert to RGB if the image has an alpha channel
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        try:

            q_image = ImageQt(image)

            pixmap = self.create_pixmap_from_image(q_image)

            self.image_label.setPixmap(pixmap)

        except IOError as e:
            print(f"Error processing image {self.current_filepath}: {e}")

    def blur(self):

        image = Image.open(self.current_filepath)
        print(f"Image Mode: {image.mode}")

        image = image.filter(ImageFilter.GaussianBlur(radius=9))

        #image.show()
        # Convert to RGB if the image has an alpha channel
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        try:

            q_image = ImageQt(image)

            pixmap = self.create_pixmap_from_image(q_image)

            self.image_label.setPixmap(pixmap)

        except IOError as e:
            print(f"Error processing image {self.current_filepath}: {e}")

    def invert(self):

        image = Image.open(self.current_filepath)
        print(f"Image Mode: {image.mode}")

        image = ImageOps.invert(image.convert('RGB'))

        #image.show()
        # Convert to RGB if the image has an alpha channel
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        try:

            q_image = ImageQt(image)

            pixmap = self.create_pixmap_from_image(q_image)

            self.image_label.setPixmap(pixmap)

        except IOError as e:
            print(f"Error processing image {self.current_filepath}: {e}")

    def grayscale(self):

        image = Image.open(self.current_filepath)
        print(f"Image Mode: {image.mode}")

        image = image.convert('L')

        # image.show()
        # Convert to RGB if the image has an alpha channel
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        try:

            q_image = ImageQt(image)

            pixmap = self.create_pixmap_from_image(q_image)

            self.image_label.setPixmap(pixmap)

        except IOError as e:
            print(f"Error processing image {self.current_filepath}: {e}")

    def ascii(self):

        image = self.ascii_converter.convert(self.current_filepath)

        # image.show()
        # Convert to RGB if the image has an alpha channel
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        try:

            q_image = ImageQt(image)

            pixmap = self.create_pixmap_from_image(q_image)

            self.image_label.setPixmap(pixmap)

        except IOError as e:
            print(f"Error processing image {self.current_filepath}: {e}")




if __name__ == "__main__":
    import sys
    app = QApplication([])
    image_viewer = ImageViewer()
    image_viewer.show()
    sys.exit(app.exec())