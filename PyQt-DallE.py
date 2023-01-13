import configparser
import os
import sys
import urllib.request

import openai
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QLineEdit, QLabel


class Dalle:
    def __init__(self, img_size="512"):
        self._api_keys_location = "./config"
        self._generated_image_location = "./output"
        self._img_size = img_size

    def create_template_ini_file(self):
        """
        If the ini file does not exist create it and add the organization_id and
        secret_key
        """
        if not os.path.isfile(self._api_keys_location):
            with open(self._api_keys_location, 'w') as f:
                f.write('[openai]\n')
                f.write('organization_id=\n')
                f.write('secret_key=\n')

            print('OpenAI API config file created at {}'.format(
                self._api_keys_location))
            print('Please edit it and add your organization ID and secret key')
            print('If you do not yet have an organization ID and secret key, you\n'
                  'need to register for OpenAI Codex: \n'
                  'https://openai.com/blog/openai-codex/')
            sys.exit(1)

    def initialize_openai_api(self):
        """
        Initialize the OpenAI APIn
        """
        # Check if file at API_KEYS_LOCATION exists
        self.create_template_ini_file()
        config = configparser.ConfigParser()
        config.read(self._api_keys_location)

        openai.organization_id = config['openai']['organization_id'].strip(
            '"').strip("'")
        openai.api_key = config['openai']['secret_key'].strip('"').strip("'")
        del config


    def generate_image(self, prompt):
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size=f"{self._img_size}x{self._img_size}",
        )

        image_url = response['data'][0]['url']

        if not os.path.isdir(self._generated_image_location):
            os.mkdir(self._generated_image_location)

        file_path = f"{self._generated_image_location}/{prompt}.png"
        urllib.request.urlretrieve(image_url, file_path)

        return file_path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(10, 10, 400, 140)
        self.setWindowTitle("Dall:E")

        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280, 40)

        # Create a button in the window
        self.button = QPushButton('Give me Ai!', self)
        self.button.move(20, 80)

        # connect button to function on_click
        self.button.clicked.connect(self.on_click, Qt.QueuedConnection)

        self.dalle = Dalle()
        self.dalle.initialize_openai_api()


    @pyqtSlot()
    def on_click(self):
        self.button.setDisabled(True)
        prompt = self.textbox.text()

        try:
            print("Generating image for " + prompt)
            image_path = self.dalle.generate_image(prompt)
            print(f"Generated image stored in: {image_path}")
            self.image_window = ImageWindow(image_path)
            self.image_window.show()
        finally:
            self.textbox.setText("")
            self.button.setDisabled(False)


class ImageWindow(QWidget):
    def __init__(self, image_path):
        super().__init__()

        self.setGeometry(640, 256, 512, 512)
        self.setWindowTitle("Dall:E")
        self.label = QLabel(self)
        self.pixmap = QPixmap(image_path)
        self.label.setPixmap(self.pixmap)
        self.label.resize(512, 512)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
