import sys
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QTextEdit, QPushButton, QMessageBox, QFileDialog, QInputDialog, QLineEdit, QLabel
)
from PySide6.QtCore import Qt


class SearchWorker(QThread):
    results_ready = Signal(list)

    def __init__(self, notes, query):
        super().__init__()
        self.notes = notes
        self.query = query

    def run(self):
        results = []
        for title, content in self.notes.items():
            if self.query.lower() in content.lower() or self.query.lower() in title.lower():
                results.append(title)
        self.results_ready.emit(results)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Приложение заметок")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.note_list = QListWidget()
        self.note_list.currentItemChanged.connect(self.display_note)
        self.layout.addWidget(self.note_list)

        self.note_editor = QTextEdit()
        self.layout.addWidget(self.note_editor)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.add_button = QPushButton("Добавить заметку")
        self.add_button.clicked.connect(self.add_note)
        self.button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Удалить заметку")
        self.delete_button.clicked.connect(self.delete_note)
        self.button_layout.addWidget(self.delete_button)

        self.save_button = QPushButton("Сохранить заметки")
        self.save_button.clicked.connect(self.save_notes)
        self.button_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Загрузить заметки")
        self.load_button.clicked.connect(self.load_notes)
        self.button_layout.addWidget(self.load_button)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.button_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Найти")
        self.search_button.clicked.connect(self.search_notes)
        self.button_layout.addWidget(self.search_button)

        self.search_results_label = QLabel()
        self.layout.addWidget(self.search_results_label)

        self.notes = {}

    def add_note(self):
        note_title, ok = QInputDialog.getText(self, "Добавить заметку", "Название заметки:")
        if ok and note_title:
            self.notes[note_title] = ""
            self.note_list.addItem(note_title)

    def delete_note(self):
        current_item = self.note_list.currentItem()
        if current_item:
            note_title = current_item.text()
            del self.notes[note_title]
            self.note_list.takeItem(self.note_list.row(current_item))
            self.note_editor.clear()

    def display_note(self, current, previous):
        if previous:
            self.notes[previous.text()] = self.note_editor.toPlainText()
        if current:
            self.note_editor.setText(self.notes[current.text()])

    def save_notes(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить заметки", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'w') as file:
                for title, content in self.notes.items():
                    file.write(f"{title}\n{content}\n{'-'*20}\n")

    def load_notes(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить заметки", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                notes = content.split('\n' + '-'*20 + '\n')
                self.notes.clear()
                self.note_list.clear()
                for note in notes:
                    if note:
                        title, body = note.split('\n', 1)
                        self.notes[title] = body
                        self.note_list.addItem(title)

    def search_notes(self):
        query = self.search_input.text()
        if query:
            self.search_thread = SearchWorker(self.notes, query)
            self.search_thread.results_ready.connect(self.display_search_results)
            self.search_thread.start()

    def display_search_results(self, results):
        if results:
            self.search_results_label.setText(f"Найдено: {', '.join(results)}")
        else:
            self.search_results_label.setText("Ничего не найдено.")


app = QApplication()
window = MainWindow()
window.show()
app.exec()

