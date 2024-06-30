import sys
import os
import anthropic
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit,
                             QPushButton, QLabel, QHBoxLayout, QSizePolicy, QSpacerItem, QShortcut)
from PyQt5.QtCore import Qt, QPoint, QTimer, QEvent
from PyQt5.QtGui import QKeySequence, QFont, QPalette, QColor, QFontDatabase, QCursor

class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace and event.modifiers() == Qt.ShiftModifier:
            self.parent.close()
        else:
            super().keyPressEvent(event)

class AIQueryInterface(QWidget):
    def __init__(self):
        super().__init__()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.message_history = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('dodec')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 750, 100)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border-radius: 15px;
            }
            QLineEdit, QTextEdit {
                background-color: #3b3b3b;
                border: 1px solid #5b5b5b;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #5b5b5b;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # Load system font
        font_path_regular = "Raleway-Regular.ttf"
        font_path_bold = "Raleway-Bold.ttf"
        if os.path.exists(font_path_regular) and os.path.exists(font_path_bold):
            font_id_regular = QFontDatabase.addApplicationFont(font_path_regular)
            font_id_bold = QFontDatabase.addApplicationFont(font_path_bold)
            if font_id_regular != -1:
                font_family_regular = QFontDatabase.applicationFontFamilies(font_id_regular)[0]
                self.font = QFont(font_family_regular, 20)
            else:
                print(f"Error loading font: {font_path_regular}")
                self.font = QFont('Arial', 20)  # Fallback font
            if font_id_bold != -1:
                font_family_bold = QFontDatabase.applicationFontFamilies(font_id_bold)[0]
            else:
                print(f"Error loading font: {font_path_regular}")
                self.font = QFont('Arial', 20)  # Fallback font
        else:
            print(f"Font file not found: {font_path_regular}")
            self.font = QFont('Arial', 20)  # Fallback font

        self.setFont(self.font)
        QApplication.setFont(self.font)

        self.setStyleSheet(self.styleSheet() + f"""
            * {{
                font-family: {self.font.family()};
            }}
            QLineEdit, QTextEdit {{
                font-size: 20px;
            }}
            QLabel {{
                font-size: 22px;
                font-weight: bold;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Add header and close button
        header_layout = QHBoxLayout()
        header_label = QLabel("dodec")
        header_label.setStyleSheet("font-size: 26px; font-weight: bold;")
        header_label.font = QFont(font_family_bold, 20)
        close_button = QPushButton('x')
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                color: white;
                font-weight: bold;
                border-radius: 15px;
                font-size: 18px;
                padding-top:-7px;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
        """)
        close_button.setCursor(QCursor(Qt.PointingHandCursor))
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        layout.addLayout(header_layout)

        self.query_input = CustomLineEdit(self)
        self.query_input.setPlaceholderText("What do you need?")
        self.query_input.returnPressed.connect(self.on_query)
        self.query_input.setMinimumHeight(50)
        self.query_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.query_input)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_display.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.result_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_display.textChanged.connect(self.adjust_text_edit_size)
        self.result_display.hide()
        layout.addWidget(self.result_display)
        
        layout.addSpacing(10)
        self.setLayout(layout)

        # Center the widget on the screen and move it up
        self.center()
        self.move(self.x(), self.y() - 200)

        # Set up close shortcut
        self.close_shortcut = QShortcut(QKeySequence("Shift+Backspace"), self)
        self.close_shortcut.activated.connect(self.close)
        
        # Focus on the text box
        QTimer.singleShot(0, self.query_input.setFocus)

    def adjust_text_edit_size(self):
        doc_height = self.result_display.document().size().height()
        margins = self.result_display.contentsMargins()
        max_height = 400

        # Calculate the ideal height
        ideal_height = doc_height + margins.top() + margins.bottom() + 10

        # Set the height, but cap it at max_height
        new_height = min(ideal_height, max_height)
        self.result_display.setFixedHeight(int(new_height))

        self.adjustSize()

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_query(self):
        query = self.query_input.text()
        
        if not query.strip():
            return
            
        self.result_display.clear()
        self.result_display.show()
        self.adjustSize() 
        self.result_display.setText("Loading response...")
        
        # Clear and refocus input
        self.query_input.clear()
        self.query_input.setFocus()
        
        # Add user message to history
        self.message_history.append({"role": "user", "content": query})
        
        # Use a QTimer to allow the UI to update before making the API call
        QTimer.singleShot(100, lambda: self.get_ai_response(query))

    def get_ai_response(self, query):
        try:
            with self.client.messages.stream(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0.5,
                system="The assistant is knowledgable, helpful, and precise. It talks in a casual, friendly tone, treating the user as a colleague and good friend. It uses colloquial language and even slang, is curious yet steadfast, and knows a lot in every domain. It responds in as few words as possible while still getting the necessary points across. The assistant is witty but employs his wit sparingly, trying to sound normal most of the time and not trying too hard to be quirky. The assistant doesn't use curse words but may use profanity at times.",
                messages=self.message_history
            ) as stream:
                self.result_display.clear()
                full_response = ""
                for text in stream.text_stream:
                    full_response += text
                    self.result_display.insertPlainText(text)
                    QApplication.processEvents()
                    self.adjustSize()
                
                # Add assistant's response to history
                self.message_history.append({"role": "assistant", "content": full_response})
        except Exception as e:
            self.result_display.setText(f"An error occurred: {str(e)}")
        finally:
            self.adjustSize()

    def adjustSize(self):
        max_window_height = QApplication.desktop().availableGeometry().height() * 0.8
        
        # Calculate new height based on contents
        content_height = self.layout().sizeHint().height()
        
        # Ensure a minimum window height and cap at max_window_height
        new_height = max(min(content_height, max_window_height), 200)
        
        self.setFixedHeight(int(new_height))

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self, event):
        # Handle Shift+Backspace even when focused on input
        if event.key() == Qt.Key_Backspace and event.modifiers() == Qt.ShiftModifier:
            self.close()
        else:
            super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    ex = AIQueryInterface()
    
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()