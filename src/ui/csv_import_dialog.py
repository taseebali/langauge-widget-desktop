"""CSV import dialog for vocabulary."""

import csv
import json
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QTextEdit, QMessageBox,
                             QLineEdit, QGroupBox)
from PyQt5.QtCore import Qt


class CSVImportDialog(QDialog):
    """Dialog for importing vocabulary from CSV files."""
    
    def __init__(self, vocab_dir, parent=None):
        super().__init__(parent)
        self.vocab_dir = Path(vocab_dir)
        self.csv_file = None
        self.setWindowTitle("Import Vocabulary from CSV")
        self.setMinimumSize(600, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "CSV Format: German,English,Gender,Category,Difficulty,Pronunciation,Example_German,Example_English\n"
            "Gender: masculine/feminine/neuter (or leave empty for verbs/adjectives)\n"
            "Difficulty: A1, A2, B1, B2, C1, C2\n"
            "Example: \"der Hund\",dog,masculine,animals,A1,\"dair HOONT\",\"Der Hund bellt.\",\"The dog barks.\""
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # File selection
        file_group = QGroupBox("CSV File")
        file_layout = QVBoxLayout(file_group)
        
        select_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        select_layout.addWidget(self.file_label)
        select_layout.addStretch()
        
        select_button = QPushButton("Browse...")
        select_button.clicked.connect(self._select_file)
        select_layout.addWidget(select_button)
        
        file_layout.addLayout(select_layout)
        layout.addWidget(file_group)
        
        # Output filename
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("Save as:"))
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("custom_vocabulary.json")
        filename_layout.addWidget(self.filename_input)
        output_layout.addLayout(filename_layout)
        
        layout.addWidget(output_group)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Select a CSV file to see preview...")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        import_button = QPushButton("Import")
        import_button.clicked.connect(self._import_csv)
        button_layout.addWidget(import_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _select_file(self):
        """Open file dialog to select CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if file_path:
            self.csv_file = Path(file_path)
            self.file_label.setText(self.csv_file.name)
            
            # Auto-fill output filename
            if not self.filename_input.text():
                output_name = self.csv_file.stem + ".json"
                self.filename_input.setText(output_name)
            
            self._preview_csv()
    
    def _preview_csv(self):
        """Preview CSV contents."""
        if not self.csv_file or not self.csv_file.exists():
            return
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                lines = list(reader)
                
                preview = f"Total rows: {len(lines)}\n\n"
                preview += "First 5 rows:\n"
                preview += "-" * 60 + "\n"
                
                for i, row in enumerate(lines[:5]):
                    preview += f"{i+1}. {' | '.join(row)}\n"
                
                self.preview_text.setText(preview)
        
        except Exception as e:
            self.preview_text.setText(f"Error reading file: {str(e)}")
    
    def _import_csv(self):
        """Import CSV and convert to JSON."""
        if not self.csv_file or not self.csv_file.exists():
            QMessageBox.warning(self, "No File", "Please select a CSV file first.")
            return
        
        output_filename = self.filename_input.text().strip()
        if not output_filename:
            QMessageBox.warning(self, "No Filename", "Please enter an output filename.")
            return
        
        if not output_filename.endswith('.json'):
            output_filename += '.json'
        
        try:
            words = []
            word_id = 1000  # Start IDs at 1000 for custom imports
            
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                
                # Skip header if present
                first_row = next(reader, None)
                if first_row and first_row[0].lower() in ['german', 'word']:
                    # Header row, skip it
                    pass
                else:
                    # No header, process first row
                    if first_row:
                        word = self._parse_row(first_row, word_id)
                        if word:
                            words.append(word)
                            word_id += 1
                
                # Process remaining rows
                for row in reader:
                    if not row or len(row) < 2:
                        continue
                    
                    word = self._parse_row(row, word_id)
                    if word:
                        words.append(word)
                        word_id += 1
            
            if not words:
                QMessageBox.warning(self, "No Data", "No valid words found in CSV file.")
                return
            
            # Save to JSON
            output_path = self.vocab_dir / output_filename
            data = {"words": words}
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(
                self,
                "Success",
                f"Imported {len(words)} words to {output_filename}\n\n"
                f"Restart the application to load new vocabulary."
            )
            
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import CSV:\n{str(e)}")
    
    def _parse_row(self, row, word_id):
        """Parse CSV row into word dictionary."""
        try:
            # Required fields
            german = row[0].strip() if len(row) > 0 else ""
            english = row[1].strip() if len(row) > 1 else ""
            
            if not german or not english:
                return None
            
            # Optional fields
            gender = row[2].strip().lower() if len(row) > 2 and row[2].strip() else None
            category = row[3].strip().lower() if len(row) > 3 and row[3].strip() else "custom"
            difficulty = row[4].strip().upper() if len(row) > 4 and row[4].strip() else "A1"
            pronunciation = row[5].strip() if len(row) > 5 and row[5].strip() else ""
            example_german = row[6].strip() if len(row) > 6 and row[6].strip() else ""
            example_english = row[7].strip() if len(row) > 7 and row[7].strip() else ""
            
            # Validate gender
            if gender and gender not in ['masculine', 'feminine', 'neuter']:
                gender = None
            
            # Build word object
            word = {
                "id": word_id,
                "german": german,
                "english": english,
                "gender": gender,
                "pronunciation": pronunciation,
                "category": category,
                "difficulty": difficulty,
                "examples": []
            }
            
            # Add example if provided
            if example_german and example_english:
                word["examples"].append({
                    "german": example_german,
                    "english": example_english
                })
            
            return word
        
        except Exception as e:
            print(f"Error parsing row {row}: {e}")
            return None
