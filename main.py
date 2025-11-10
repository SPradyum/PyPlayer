import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *


class GlassFrame(QFrame):
    """A translucent glass container"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
        """)


class HoverButton(QPushButton):
    """Button with soft hover animation"""
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.12);
                color: white;
                padding: 10px 20px;
                border-radius: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.25);
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window
        self.setWindowTitle("PyPlayer")
        self.setMinimumSize(700, 500)
        self.setStyleSheet("background: #0f0f0f;")

        # ------------------------------
        # Player + Playlist
        # ------------------------------
        self.playlist = QMediaPlaylist()
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

        self.player = QMediaPlayer()
        self.player.setPlaylist(self.playlist)

        # Track name
        self.track_label = QLabel("No track loaded")
        self.track_label.setStyleSheet("color: white; font-size: 16px; padding: 10px;")

        # Time slider
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.sliderMoved.connect(self.seek_position)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: white; font-size: 14px;")

        # Playlist Display
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: rgba(255,255,255,0.05);
                color: white;
                border-radius: 12px;
                padding: 10px;
            }
            QListWidget::item:selected {
                background: rgba(255,255,255,0.2);
            }
        """)
        self.list_widget.itemDoubleClicked.connect(self.play_selected)

        # Buttons
        self.btn_open = HoverButton("Add Songs")
        self.btn_play = HoverButton("Play")
        self.btn_pause = HoverButton("Pause")
        self.btn_stop = HoverButton("Stop")
        self.btn_next = HoverButton("Next")
        self.btn_prev = HoverButton("Previous")

        # Connections
        self.btn_open.clicked.connect(self.open_files)
        self.btn_play.clicked.connect(self.player.play)
        self.btn_pause.clicked.connect(self.player.pause)
        self.btn_stop.clicked.connect(self.player.stop)
        self.btn_next.clicked.connect(self.playlist.next)
        self.btn_prev.clicked.connect(self.playlist.previous)

        # Layouts
        main_container = GlassFrame()
        vbox = QVBoxLayout()

        vbox.addWidget(self.track_label)
        vbox.addWidget(self.time_slider)
        vbox.addWidget(self.time_label)
        vbox.addWidget(self.list_widget)

        hcontrols = QHBoxLayout()
        hcontrols.addWidget(self.btn_open)
        hcontrols.addWidget(self.btn_prev)
        hcontrols.addWidget(self.btn_play)
        hcontrols.addWidget(self.btn_pause)
        hcontrols.addWidget(self.btn_stop)
        hcontrols.addWidget(self.btn_next)

        vbox.addLayout(hcontrols)
        main_container.setLayout(vbox)

        outer = QVBoxLayout()
        outer.addWidget(main_container)
        outer.setContentsMargins(30, 30, 30, 30)

        widget = QWidget()
        widget.setLayout(outer)
        self.setCentralWidget(widget)

        # Player signals
        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)
        self.playlist.currentIndexChanged.connect(self.update_track_name)

    # ---------------------------------------------------------------

    def open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.wav)"
        )
        if paths:
            for path in paths:
                url = QUrl.fromLocalFile(path)
                self.playlist.addMedia(QMediaContent(url))
                self.list_widget.addItem(os.path.basename(path))

            if self.player.state() != QMediaPlayer.PlayingState:
                self.playlist.setCurrentIndex(0)
                self.player.play()

    # ---------------------------------------------------------------

    def play_selected(self):
        index = self.list_widget.currentRow()
        self.playlist.setCurrentIndex(index)
        self.player.play()

    # ---------------------------------------------------------------

    def update_duration(self, duration):
        self.time_slider.setRange(0, duration)

    def update_position(self, pos):
        self.time_slider.setValue(pos)
        self.update_time_label(pos)

    def update_time_label(self, pos):
        total = self.player.duration()

        def fmt(ms):
            s = int(ms / 1000)
            return f"{s//60:02}:{s%60:02}"

        self.time_label.setText(f"{fmt(pos)} / {fmt(total)}")

    def update_track_name(self, index):
        if index >= 0:
            item = self.list_widget.item(index)
            if item:
                self.track_label.setText(item.text())

    # ---------------------------------------------------------------

    def seek_position(self, pos):
        self.player.setPosition(pos)


# ---------------------------------------------------------------

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
