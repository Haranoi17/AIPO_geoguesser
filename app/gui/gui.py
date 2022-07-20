from sys import argv
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QCloseEvent, QResizeEvent, QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QMessageBox, QFileDialog, QLabel
from cv2 import VideoCapture
from app import run_module

WIDTH = 800
HEIGHT = 600
MENU_SPACE = 110
IMAGE_SPACE_WIDTH = 5
IMAGE_SPACE_HEIGHT = 75


class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.Window)
        QMainWindow.setWindowTitle(self, "Geo guesser cracked")
        QMainWindow.resize(self, WIDTH, HEIGHT)
        self.load_button: QPushButton = QPushButton("Load file", self)
        self.predict_button: QPushButton = QPushButton("Predict", self)
        self.quit_button: QPushButton = QPushButton("Quit", self)
        self.button_list = [
            self.load_button,
            self.predict_button,
            self.quit_button
        ]
        self.load_button.clicked.connect(self.load_file_dialog)
        self.predict_button.clicked.connect(self.predict_action)
        self.quit_button.clicked.connect(self.emit_quit)
        self.current_file: str = ""
        self.pixmap_original: QPixmap = None
        self.pixmap_copy: QPixmap = None
        self.image_label: QLabel = QLabel(self)
        self.text_label: QLabel = QLabel(self)
        self.prediction_title: str = "Predictions:\n{}"
        self.prediction_processing: str = "Processing..."
        self.current_prediction = "None"
        self.prediction_fail = "Unknown location"

        self.render_buttons()
        self.render_text_label(self.current_prediction)

    def render_buttons(self):
        current_height = self.height()
        for idx, button in enumerate(self.button_list):
            button.move(
                int(self.width() - MENU_SPACE), 
                int((idx + 1) * 0.15 * current_height)
            )
            button.show()

        self.predict_button.setEnabled(bool(self.current_file))

    def render_text_label(self, prediction_text: str):
        self.text_label.setMinimumWidth(self.width())
        self.text_label.setText(self.prediction_title.format(prediction_text))
        self.text_label.move(
            25, 
            int(self.height() - IMAGE_SPACE_HEIGHT * 0.66)
        )

    def resizeEvent(self, a0: QtGui.QResizeEvent):
        if self.pixmap_original:
            self.load_image()
        self.render_text_label(self.current_prediction)
        self.render_buttons()

    def emit_quit(self):
        QApplication.sendEvent(self, QCloseEvent())

    def closeEvent(self, event: QCloseEvent):
        exit_dialog = QMessageBox.question(self, "Quit program", "Are you sure to exit the program?",
                                           QMessageBox.Yes | QMessageBox.Cancel)
        if exit_dialog == QMessageBox.Yes:
            exit(0)
        else:
            event.ignore()

    def load_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load file", "",
                                                   "MP4 Files (*.mp4);;JPG Files (*.jpg);;PNG Files (*.png)",
                                                    options=options)
        if file_name:
            self.current_file = file_name
        if str(file_name).endswith(".mp4"):
            self.load_video(file_name)
        else:
            self.load_image(file_name, True)
            self.emit_update()

    def predict_action(self):
        self.current_prediction = self.prediction_processing
        self.emit_update()
        output_text_list = []
        try:
            predictions = run_module(self.current_file)
            self.current_prediction = ", ".join(f"{country} ({possibility}%)" for country, possibility in predictions)
        except IndexError:
            self.current_prediction = self.prediction_fail
        except Exception as e:
            print(e)
        self.emit_update()

    def emit_update(self):
        QApplication.sendEvent(self, QResizeEvent(QSize(0, 0), QSize(self.width(), self.height())))
        return

    def load_video(self, file_name: str):
        cap = VideoCapture(file_name)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888).rgbSwapped()
            self.pixmap_original = QPixmap.fromImage(image)
            self.emit_update()

    def load_image(self, file_name: str = "", load_flag: bool = False):
        if load_flag:
            self.pixmap_original = QPixmap(file_name)
        self.pixmap_copy = self.pixmap_original.scaled(self.width() - (MENU_SPACE + IMAGE_SPACE_WIDTH),
                                                       self.height() - IMAGE_SPACE_HEIGHT)

        self.image_label.setPixmap(self.pixmap_copy)

        self.image_label.resize(self.width() - (MENU_SPACE + IMAGE_SPACE_WIDTH), self.height() - IMAGE_SPACE_HEIGHT)


def run_GUI():
    app = QApplication(argv)
    gui = MainGUI()
    gui.show()

    try:
        exit(app.exec_())
    except SystemExit:
        pass
