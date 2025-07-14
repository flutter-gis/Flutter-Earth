import sys
import os
import json
import glob
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QLabel, QLineEdit, QListWidgetItem, QTextEdit, QScrollArea, QFrame, QPushButton, QSizePolicy
)
from PySide6.QtGui import QPixmap, QDesktopServices
from PySide6.QtCore import Qt, QUrl

DATASET_DIR = os.path.join("backend", "crawler_data")
CATALOG_BASE_URL = "https://developers.google.com/earth-engine/datasets/catalog/"

class DatasetViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satellite Info Catalog Viewer")
        self.resize(1200, 800)
        self.datasets = self.load_datasets()
        self.filtered_datasets = self.datasets.copy()
        self.init_ui()

    def load_datasets(self):
        datasets = []
        for file in glob.glob(os.path.join(DATASET_DIR, "dataset_*.json")):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data['__file__'] = file
                    datasets.append(data)
            except Exception as e:
                print(f"[WARN] Could not load {file}: {e}")
        return datasets

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        # Left: Search + List
        left_panel = QVBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by name, tag, or description...")
        self.search_box.textChanged.connect(self.filter_list)
        left_panel.addWidget(self.search_box)
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.show_details)
        left_panel.addWidget(self.list_widget, 1)
        main_layout.addLayout(left_panel, 2)
        # Right: Details
        self.detail_area = QScrollArea()
        self.detail_area.setWidgetResizable(True)
        self.detail_widget = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_widget)
        self.detail_area.setWidget(self.detail_widget)
        main_layout.addWidget(self.detail_area, 5)
        self.populate_list()
        if self.filtered_datasets:
            self.list_widget.setCurrentRow(0)

    def populate_list(self):
        self.list_widget.clear()
        for ds in self.filtered_datasets:
            item = QListWidgetItem(ds.get('name', 'Unnamed Dataset'))
            item.setToolTip(ds.get('description', ''))
            self.list_widget.addItem(item)

    def filter_list(self):
        query = self.search_box.text().lower()
        if not query:
            self.filtered_datasets = self.datasets.copy()
        else:
            self.filtered_datasets = [d for d in self.datasets if query in d.get('name', '').lower() or query in d.get('description', '').lower() or any(query in tag.lower() for tag in d.get('tags', []))]
        self.populate_list()
        if self.filtered_datasets:
            self.list_widget.setCurrentRow(0)
        else:
            self.show_details(-1)

    def show_details(self, idx):
        for i in reversed(range(self.detail_layout.count())):
            widget = self.detail_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        if idx < 0 or idx >= len(self.filtered_datasets):
            self.detail_layout.addWidget(QLabel("No dataset selected."))
            return
        ds = self.filtered_datasets[idx]
        # Title
        title = QLabel(f"<h2>{ds.get('name', 'Unnamed Dataset')}</h2>")
        self.detail_layout.addWidget(title)
        # Tags
        tags = ds.get('tags', [])
        if tags:
            tag_line = QHBoxLayout()
            for tag in tags:
                tag_lbl = QLabel(tag)
                tag_lbl.setStyleSheet("background:#3a6ea5;color:white;padding:2px 8px;border-radius:8px;margin-right:4px;")
                tag_line.addWidget(tag_lbl)
            tag_line.addStretch(1)
            tag_frame = QFrame()
            tag_frame.setLayout(tag_line)
            self.detail_layout.addWidget(tag_frame)
        # Thumbnail
        thumb_path = ds.get('thumbnail', '')
        if thumb_path and os.path.exists(thumb_path):
            pix = QPixmap(thumb_path)
            thumb = QLabel()
            thumb.setPixmap(pix.scaledToWidth(200, Qt.SmoothTransformation))
            self.detail_layout.addWidget(thumb)
        # Description
        desc = QLabel(f"<b>Description:</b><br>{ds.get('description', '').replace(chr(10), '<br>')}")
        desc.setWordWrap(True)
        self.detail_layout.addWidget(desc)
        # Metadata Sections
        meta_sections = [
            ("Temporal", [
                ('Dates', ds.get('dates', '')),
                ('Start Date', ds.get('start_date', '')),
                ('End Date', ds.get('end_date', '')),
                ('Frequency', ds.get('frequency', '')),
            ]),
            ("Spatial", [
                ('Coverage', ds.get('coverage', '')),
                ('Resolution', ds.get('resolution', '')),
            ]),
            ("Source", [
                ('Publisher', ds.get('publisher', '')),
                ('Satellites', ', '.join(ds.get('satellites', []))),
                ('Collection ID', ds.get('collection_id', '')),
                ('Dataset ID', ds.get('dataset_id', '')),
            ]),
            ("Other", [
                ('Bands', ', '.join(ds.get('bands', []))),
                ('Cloud Cover', str(ds.get('cloud_cover', ''))),
                ('Data Type', ds.get('data_type', '')),
                ('Applications', ', '.join(ds.get('applications', []))),
                ('Limitations', ds.get('limitations', '')),
            ]),
        ]
        for section, fields in meta_sections:
            section_text = f"<b>{section}:</b> "
            has_content = False
            for k, v in fields:
                if v:
                    section_text += f"<b>{k}:</b> {v} &nbsp; "
                    has_content = True
            if has_content:
                meta = QLabel(section_text)
                meta.setWordWrap(True)
                self.detail_layout.addWidget(meta)
        # Dataset Page Link (using dataset_id)
        dataset_id = ds.get('dataset_id', '').strip()
        if dataset_id:
            link = CATALOG_BASE_URL + dataset_id
            link_btn = QPushButton("Open Dataset Page")
            link_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(link)))
            self.detail_layout.addWidget(link_btn)
        else:
            self.detail_layout.addWidget(QLabel("No link available."))
        # Code Snippet Parsing
        code_snippet = ds.get('code_snippet', '')
        code_lines = code_snippet.split('\n')
        # Extract sections
        comments = []
        code = []
        export = []
        in_export = False
        for line in code_lines:
            l = line.strip()
            if l.startswith('//') or l.startswith('/*') or l.startswith('*') or l.endswith('*/'):
                comments.append(line)
            elif l.startswith('Export.') or in_export or l.startswith('/*'):
                export.append(line)
                in_export = True
                if l.endswith('*/'):
                    in_export = False
            elif l:
                code.append(line)
        # How to Use / Instructions
        if comments:
            instr_label = QLabel("<b>How to Use:</b>")
            self.detail_layout.addWidget(instr_label)
            instr_box = QTextEdit()
            instr_box.setReadOnly(True)
            instr_box.setPlainText('\n'.join(comments))
            instr_box.setMinimumHeight(60)
            self.detail_layout.addWidget(instr_box)
        # Code
        if code:
            code_label = QLabel("<b>Code:</b>")
            self.detail_layout.addWidget(code_label)
            code_box = QTextEdit()
            code_box.setReadOnly(True)
            code_box.setPlainText('\n'.join(code))
            code_box.setMinimumHeight(100)
            code_box.setFontFamily("Consolas")
            self.detail_layout.addWidget(code_box)
        # Export Example
        if export:
            export_label = QLabel("<b>Export Example:</b>")
            self.detail_layout.addWidget(export_label)
            export_box = QTextEdit()
            export_box.setReadOnly(True)
            export_box.setPlainText('\n'.join(export))
            export_box.setMinimumHeight(80)
            export_box.setFontFamily("Consolas")
            self.detail_layout.addWidget(export_box)
        self.detail_layout.addStretch(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = DatasetViewer()
    viewer.show()
    sys.exit(app.exec()) 