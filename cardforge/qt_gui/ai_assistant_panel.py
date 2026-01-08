"""
CardForge AI Assistant GUI Integration

PyQt6 widget providing AI orchestration capabilities in the CardForge GUI.
Implements background execution, dynamic forms, and real-time feedback.
"""

import asyncio
import json
import os
from typing import Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QProgressBar,
    QMessageBox,
    QScrollArea,
    QFrame,
)
from PyQt6.QtGui import QFont, QColor, QTextCursor


class OrchestrationWorker(QObject):
    """Worker thread for running orchestration tasks asynchronously."""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(str)
    
    def __init__(self, orchestrator, task: str, **kwargs):
        """Initialize worker."""
        super().__init__()
        self.orchestrator = orchestrator
        self.task = task
        self.kwargs = kwargs
    
    def run(self):
        """Execute orchestration task."""
        try:
            self.progress.emit("Initializing orchestration...")
            
            # Run async orchestration in thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.orchestrator.execute(self.task, **self.kwargs)
            )
            loop.close()
            
            self.result.emit(result)
            self.progress.emit("Complete")
            self.finished.emit()
        
        except Exception as e:
            self.error.emit(f"Orchestration error: {str(e)}")
            self.finished.emit()


class TaskParametersForm(QWidget):
    """Dynamic form for task-specific parameters."""
    
    def __init__(self, task_type: str):
        """Initialize form based on task type."""
        super().__init__()
        self.task_type = task_type
        self.fields = {}
        self._build_form()
    
    def _build_form(self):
        """Build form widgets based on task type."""
        layout = QVBoxLayout()
        
        if self.task_type == "deck_optimization":
            layout.addWidget(QLabel("Deck List (one card per line):"))
            self.deck_input = QTextEdit()
            self.deck_input.setMinimumHeight(150)
            self.deck_input.setPlaceholderText(
                "E.g.:\n1x Command Tower\n1x Kaalia of the Vast\n1x Rampant Growth"
            )
            layout.addWidget(self.deck_input)
            self.fields["deck_list"] = self.deck_input
        
        elif self.task_type == "price_analysis":
            layout.addWidget(QLabel("Card Names (comma-separated):"))
            self.cards_input = QLineEdit()
            self.cards_input.setPlaceholderText("E.g.: Kaalia of the Vast, Command Tower, Sol Ring")
            layout.addWidget(self.cards_input)
            self.fields["cards"] = self.cards_input
        
        elif self.task_type == "collection_management":
            layout.addWidget(QLabel("Collection Analysis Task:"))
            self.task_input = QLineEdit()
            self.task_input.setPlaceholderText(
                "E.g.: Find duplicates in my collection, or: What cards should I trade?"
            )
            layout.addWidget(self.task_input)
            self.fields["collection_task"] = self.task_input
        
        elif self.task_type == "buy_list_generation":
            layout.addWidget(QLabel("Missing Cards (comma-separated):"))
            self.cards_input = QLineEdit()
            self.cards_input.setPlaceholderText("E.g.: Cyclonic Rift, Doubling Season, Craterhoof Behemoth")
            layout.addWidget(self.cards_input)
            self.fields["missing_cards"] = self.cards_input
            
            layout.addWidget(QLabel("Budget ($):"))
            self.budget_input = QSpinBox()
            self.budget_input.setMinimum(0)
            self.budget_input.setMaximum(10000)
            self.budget_input.setValue(500)
            layout.addWidget(self.budget_input)
            self.fields["budget"] = self.budget_input
        
        elif self.task_type == "meta_analysis":
            layout.addWidget(QLabel("Format:"))
            self.format_input = QComboBox()
            self.format_input.addItems([
                "Commander (EDH)",
                "Standard",
                "Modern",
                "Pauper",
                "Pioneer",
                "Vintage"
            ])
            layout.addWidget(self.format_input)
            self.fields["format"] = self.format_input
        
        elif self.task_type == "synergy_finding":
            layout.addWidget(QLabel("Cards to Analyze (comma-separated):"))
            self.cards_input = QLineEdit()
            self.cards_input.setPlaceholderText("E.g.: Karmic Guide, Saffi Eriksdotter, Viscera Seer")
            layout.addWidget(self.cards_input)
            self.fields["cards"] = self.cards_input
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_values(self) -> dict:
        """Get form values as dictionary."""
        values = {}
        for key, widget in self.fields.items():
            if isinstance(widget, QTextEdit):
                values[key] = widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                values[key] = widget.text()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                values[key] = widget.value()
            elif isinstance(widget, QComboBox):
                values[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                values[key] = widget.isChecked()
        return values


class AIAssistantPanel(QWidget):
    """Main AI Assistant panel for CardForge GUI."""
    
    def __init__(self, parent=None):
        """Initialize AI Assistant panel."""
        super().__init__(parent)
        self.orchestrator = None
        self.worker_thread = None
        self.worker = None
        self._init_orchestrator()
        self._build_ui()
    
    def _init_orchestrator(self):
        """Initialize CardForge orchestrator."""
        try:
            from cardforge.ai import CardForgeOrchestrator
            
            # Get config path
            current_dir = os.path.dirname(__file__)
            config_path = os.path.join(
                current_dir,
                "..",
                "ai",
                "config.json"
            )
            
            self.orchestrator = CardForgeOrchestrator(config_path)
        except Exception as e:
            print(f"Warning: Failed to initialize orchestrator: {e}")
    
    def _build_ui(self):
        """Build GUI components."""
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel("🤖 AI Assistant")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        main_layout.addWidget(header)
        
        # Task selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Task Type:"))
        
        self.task_combo = QComboBox()
        self.task_combo.addItems([
            "Deck Optimization",
            "Price Analysis",
            "Collection Management",
            "Buy List Generation",
            "Meta Analysis",
            "Synergy Finding",
        ])
        self.task_combo.currentTextChanged.connect(self._on_task_changed)
        selection_layout.addWidget(self.task_combo)
        selection_layout.addStretch()
        main_layout.addLayout(selection_layout)
        
        # Custom task input
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Custom Task:"))
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText(
            "Or describe what you need (e.g., 'Optimize my Kaalia deck for Turn 3')"
        )
        custom_layout.addWidget(self.task_input)
        main_layout.addLayout(custom_layout)
        
        # Parameters form (scrollable)
        params_label = QLabel("Task Parameters:")
        params_font = QFont()
        params_font.setBold(True)
        params_label.setFont(params_font)
        main_layout.addWidget(params_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.params_form = TaskParametersForm("deck_optimization")
        scroll.setWidget(self.params_form)
        main_layout.addWidget(scroll)
        
        # Execute button
        exec_layout = QHBoxLayout()
        self.execute_btn = QPushButton("Execute Task")
        self.execute_btn.setStyleSheet(
            "background-color: #2196F3; color: white; font-weight: bold; padding: 8px;"
        )
        self.execute_btn.clicked.connect(self._execute_task)
        exec_layout.addStretch()
        exec_layout.addWidget(self.execute_btn)
        main_layout.addLayout(exec_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Ready")
        status_font = QFont()
        status_font.setItalic(True)
        self.status_label.setFont(status_font)
        main_layout.addWidget(self.status_label)
        
        # Results area
        results_label = QLabel("Results:")
        results_font = QFont()
        results_font.setBold(True)
        results_label.setFont(results_font)
        main_layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)
        main_layout.addWidget(self.results_text)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy Results")
        copy_btn.clicked.connect(self._copy_results)
        action_layout.addWidget(copy_btn)
        
        export_btn = QPushButton("Export as File")
        export_btn.clicked.connect(self._export_results)
        action_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_results)
        action_layout.addWidget(clear_btn)
        
        action_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        self.setLayout(main_layout)
    
    def _on_task_changed(self, task_name: str):
        """Handle task type change."""
        # Map display names to task types
        task_map = {
            "Deck Optimization": "deck_optimization",
            "Price Analysis": "price_analysis",
            "Collection Management": "collection_management",
            "Buy List Generation": "buy_list_generation",
            "Meta Analysis": "meta_analysis",
            "Synergy Finding": "synergy_finding",
        }
        
        task_type = task_map.get(task_name, "deck_optimization")
        
        # Recreate form
        scroll_parent = self.params_form.parent()
        old_form = self.params_form
        self.params_form = TaskParametersForm(task_type)
        if isinstance(scroll_parent, QScrollArea):
            scroll_parent.setWidget(self.params_form)
        old_form.deleteLater()
    
    def _execute_task(self):
        """Execute orchestration task."""
        if not self.orchestrator:
            self._show_error("Orchestration not initialized. Check Ollama connection.")
            return
        
        # Get task description
        task = self.task_input.text().strip()
        if not task:
            self._show_error("Please enter a task description or select a task type.")
            return
        
        # Disable button during execution
        self.execute_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Executing task...")
        self.results_text.clear()
        
        # Get form parameters
        params = self.params_form.get_values()
        
        # Create and start worker thread
        self.worker_thread = QThread()
        self.worker = OrchestrationWorker(self.orchestrator, task, **params)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.worker.result.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self._on_progress)
        
        self.worker_thread.start()
    
    def _on_result(self, result):
        """Handle orchestration result."""
        self.execute_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if result.success:
            self.status_label.setText(
                f"✓ Complete ({result.execution_time:.2f}s) - "
                f"Agent: {result.agent_name} | Model: {result.model_used}"
            )
            self.status_label.setStyleSheet("color: green;")
            self.results_text.setText(result.result)
        else:
            self._show_error(result.result)
    
    def _on_error(self, error_msg: str):
        """Handle execution error."""
        self.execute_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._show_error(error_msg)
    
    def _on_progress(self, message: str):
        """Update progress message."""
        if self.status_label:
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: blue;")
    
    def _copy_results(self):
        """Copy results to clipboard."""
        from PyQt6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.results_text.toPlainText())
        self._show_info("Results copied to clipboard")
    
    def _export_results(self):
        """Export results to file."""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "",
            "Text Files (*.txt);;Markdown Files (*.md);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.results_text.toPlainText())
                self._show_info(f"Results exported to {file_path}")
            except Exception as e:
                self._show_error(f"Export failed: {str(e)}")
    
    def _clear_results(self):
        """Clear results display."""
        self.results_text.clear()
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("")
    
    def _show_error(self, message: str):
        """Show error message."""
        self.status_label.setText(f"✗ Error: {message}")
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Error", message)
    
    def _show_info(self, message: str):
        """Show info message."""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: blue;")
        QMessageBox.information(self, "Information", message)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication([])
    window = QMainWindow()
    window.setWindowTitle("CardForge AI Assistant - Demo")
    
    panel = AIAssistantPanel()
    window.setCentralWidget(panel)
    window.resize(900, 800)
    window.show()
    
    app.exec()
