import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QListWidget
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import pyqtSlot, QMetaObject, Qt

class ChatbotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chatbot Giao Tiếp")
        # Đặt biểu tượng cửa sổ
        self.setWindowIcon(QIcon("icon\window_icon.png"))

        # Đặt kích thước cửa sổ ban đầu phù hợp với màn hình
        screen = QApplication.primaryScreen().size()
        max_width = min(800, screen.width() - 100)
        max_height = min(600, screen.height() - 100)
        self.setGeometry(100, 100, max_width, max_height)

        # Widget chính với gradient nền
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                        stop:0 #e0f7fa, stop:1 #80deea);
        """)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        central_widget.setLayout(main_layout)

        # Phần Settings
        settings_widget = QWidget()
        settings_widget.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
            padding: 5px;
        """)
        settings_layout = QHBoxLayout()
        settings_layout.setContentsMargins(10, 5, 10, 5)
        settings_widget.setLayout(settings_layout)

        self.toggle_button = QPushButton(" Bật/Tắt App")
        self.toggle_button.setIcon(QIcon("icon\power.png"))
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        settings_layout.addWidget(self.toggle_button)
        settings_layout.addStretch()

        main_layout.addWidget(settings_widget)

        # Phần Hội thoại
        chat_widget = QWidget()
        chat_widget.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
            padding: 10px;
        """)
        chat_layout = QVBoxLayout()
        chat_layout.setSpacing(8)
        chat_widget.setLayout(chat_layout)

        # Khung hiển thị tin nhắn chính
        main_chat_label = QLabel(" Tin nhắn chính:")
        main_chat_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_chat_label.setStyleSheet("background-color: transparent;")
        main_chat_label.setPixmap(QIcon("icon\chat.png").pixmap(20, 20))
        chat_layout.addWidget(main_chat_label)

        self.main_chat_display = QTextEdit()
        self.main_chat_display.setReadOnly(True)
        self.main_chat_display.setFont(QFont("Arial", 12))
        self.main_chat_display.setStyleSheet("""
            background-color: #f5f5f5;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 5px;
        """)
        chat_layout.addWidget(self.main_chat_display)

        # Hai khung gợi ý tin nhắn
        suggestion_widget = QWidget()
        suggestion_widget.setStyleSheet("background-color: transparent;")
        suggestion_layout = QHBoxLayout()
        suggestion_layout.setSpacing(10)
        suggestion_widget.setLayout(suggestion_layout)

        # Gợi ý 1
        self.suggestion1_label = QLabel(" Gợi ý 1:")
        self.suggestion1_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.suggestion1_label.setStyleSheet("background-color: transparent;")
        self.suggestion1_label.setPixmap(QIcon("icon\suggestion1.png").pixmap(20, 20))
        suggestion_layout.addWidget(self.suggestion1_label)

        self.suggestion1_list = QListWidget()
        self.suggestion1_list.setFont(QFont("Arial", 12))
        self.suggestion1_list.setStyleSheet("""
            background-color: #e3f2fd;
            border: 1px solid #90caf9;
            border-radius: 5px;
            padding: 5px;
        """)
        suggestion_layout.addWidget(self.suggestion1_list)

        # Gợi ý 2
        self.suggestion2_label = QLabel(" Gợi ý 2:")
        self.suggestion2_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.suggestion2_label.setStyleSheet("background-color: transparent;")
        self.suggestion2_label.setPixmap(QIcon("icon\suggestion2.png").pixmap(20, 20))
        suggestion_layout.addWidget(self.suggestion2_label)

        self.suggestion2_list = QListWidget()
        self.suggestion2_list.setFont(QFont("Arial", 12))
        self.suggestion2_list.setStyleSheet("""
            background-color: #e8f5e9;
            border: 1px solid #a5d6a7;
            border-radius: 5px;
            padding: 5px;
        """)
        suggestion_layout.addWidget(self.suggestion2_list)

        chat_layout.addWidget(suggestion_widget)
        main_layout.addWidget(chat_widget, stretch=1)

         # Phần Hiển thị
        display_widget = QWidget()
        display_widget.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 10px;
            padding: 5px;
        """)
        display_layout = QHBoxLayout()
        display_layout.setContentsMargins(10, 5, 10, 5)
        display_widget.setLayout(display_layout)

        # Sửa emotion_label để hiển thị chữ rõ ràng
        emotion_container = QWidget()
        emotion_layout = QHBoxLayout()
        emotion_layout.setContentsMargins(0, 0, 0, 0)
        emotion_layout.setSpacing(5)
        emotion_container.setLayout(emotion_layout)

        self.emotion_icon = QLabel()
        self.emotion_icon.setPixmap(QIcon("icon/emotions.png").pixmap(20, 20))
        self.emotion_icon.setStyleSheet("background-color: transparent;")
        emotion_layout.addWidget(self.emotion_icon)

        self.emotion_label = QLabel("Chỉ số cảm xúc hiện tại của người nói:")
        self.emotion_label.setFont(QFont("Times New Roman", 12))  # Tăng cỡ chữ
        self.emotion_label.setStyleSheet("""
            background-color: transparent;
            color: #01579b;  /* Màu xanh đậm để tương phản */
        """)
        emotion_layout.addWidget(self.emotion_label)

        display_layout.addWidget(emotion_container)
        display_layout.addStretch()

        main_layout.addWidget(display_widget)

        # Cập nhật kích thước ban đầu của khung gợi ý
        self.update_suggestion_width()

    def resizeEvent(self, event):
        """Xử lý sự kiện thay đổi kích thước cửa sổ"""
        self.update_suggestion_width()
        super().resizeEvent(event)

    def update_suggestion_width(self):
        """Cập nhật chiều rộng của khung gợi ý bằng 1/2 chiều rộng cửa sổ"""
        window_width = self.width()
        screen_width = QApplication.primaryScreen().size().width()
        label_width = 70  # Tăng ước lượng do có icon
        padding = 60  # Tăng padding cho khoảng cách và viền
        available_width = (window_width - 2 * label_width - padding) // 2
        max_suggestion_width = (screen_width - 2 * label_width - padding) // 2
        suggestion_width = min(available_width, max_suggestion_width, 800)  # Giảm tối đa xuống 400
        suggestion_width = max(suggestion_width, 500)  # Tăng tối thiểu lên 200
        self.suggestion1_list.setFixedWidth(suggestion_width)
        self.suggestion2_list.setFixedWidth(suggestion_width)
        
    def get_current_time(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    @pyqtSlot(str)
    def safe_append_message(self, message):
        self.main_chat_display.append(message)

    @pyqtSlot(str)
    def safe_update_emotion(self, emotion_text):
        self.emotion_label.setText(emotion_text)

    @pyqtSlot(str)
    def safe_add_suggestions1(self, suggestion1):
        if suggestion1:
            self.suggestion1_list.addItem(suggestion1)
    
    @pyqtSlot(str)
    def safe_add_suggestions2(self, suggestion2):
        if suggestion2:
            self.suggestion2_list.addItem(suggestion2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatbotWindow()
    window.show()
    sys.exit(app.exec_())
    