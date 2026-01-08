"""
CardForge PyQt6 GUI Integration for Agent Orchestration
Connects local Ollama agents to the CardForge desktop application

Architecture:
- AIAssistantPanel widget for user interaction
- Background worker threads for async agent calls
- Real-time progress updates
- Integration with existing CardForge services
"""

import asyncio
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QComboBox, QLabel, QProgressBar,
    QGroupBox, QSpinBox, QDoubleSpinBox, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

# Import our agent orchestration system
from cardforge_agent_orchestration import (
    CardForgeOrchestrator,
    AgentTask,
    optimize_deck_with_ai,
    generate_buy_list_with_ai,
    analyze_collection_with_ai
)


# ============================================================================
# WORKER THREAD - Runs async agent calls without blocking GUI
# ============================================================================

class AgentWorker(QThread):
    """
    Background worker for running agent orchestration tasks.
    
    Emits signals to update GUI without blocking main thread.
    """
    
    # Signals
    started = pyqtSignal()
    progress = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(dict)  # Final result
    error = pyqtSignal(str)  # Error message
    
    def __init__(self, task: AgentTask):
        super().__init__()
        self.task = task
        self.orchestrator: Optional[CardForgeOrchestrator] = None
    
    def run(self):
        """Execute agent task in background thread."""
        try:
            self.started.emit()
            self.progress.emit("Initializing Ollama connection...")
            
            # Run async orchestration
            result = asyncio.run(self._execute_task())
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
    
    async def _execute_task(self) -> Dict[str, Any]:
        """Async execution of agent task."""
        async with CardForgeOrchestrator() as orchestrator:
            self.progress.emit(f"Routing task to specialist agent...")
            
            # Route and execute
            specialist_name = await orchestrator.route_task(self.task)
            self.progress.emit(f"Executing with {specialist_name}...")
            
            response = await orchestrator.execute_task(self.task)
            return response.to_dict()


# ============================================================================
# AI ASSISTANT PANEL - Main GUI component
# ============================================================================

class AIAssistantPanel(QWidget):
    """
    AI Assistant Panel for CardForge.
    
    Features:
    - Task selection dropdown
    - Context input fields
    - Execute button
    - Real-time progress display
    - Results viewer
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker: Optional[AgentWorker] = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("🤖 AI Assistant (Local Ollama)")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Status indicator
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Task selection
        task_group = QGroupBox("Select Task")
        task_layout = QVBoxLayout()
        
        self.task_combo = QComboBox()
        self.task_combo.addItems([
            "Optimize Deck",
            "Generate Buy List",
            "Analyze Collection",
            "Find Synergies",
            "Analyze Meta",
            "Price Analysis"
        ])
        self.task_combo.currentTextChanged.connect(self._on_task_changed)
        task_layout.addWidget(self.task_combo)
        
        task_group.setLayout(task_layout)
        layout.addWidget(task_group)
        
        # Dynamic input fields (change based on task)
        self.input_group = QGroupBox("Task Parameters")
        self.input_layout = QVBoxLayout()
        self.input_group.setLayout(self.input_layout)
        layout.addWidget(self.input_group)
        
        # Initialize with default task inputs
        self._update_input_fields()
        
        # Execute button
        button_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("🚀 Execute")
        self.execute_btn.clicked.connect(self._execute_task)
        self.execute_btn.setMinimumHeight(40)
        button_layout.addWidget(self.execute_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self._cancel_task)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_text = QLabel("")
        self.progress_text.setWordWrap(True)
        layout.addWidget(self.progress_text)
        
        # Results display
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(300)
        results_layout.addWidget(self.results_text)
        
        # Action buttons for results
        result_actions = QHBoxLayout()
        
        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.copy_btn.clicked.connect(self._copy_results)
        result_actions.addWidget(self.copy_btn)
        
        self.export_btn = QPushButton("💾 Export Results")
        self.export_btn.clicked.connect(self._export_results)
        result_actions.addWidget(self.export_btn)
        
        results_layout.addLayout(result_actions)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
    
    def _on_task_changed(self, task_name: str):
        """Update input fields when task changes."""
        self._update_input_fields()
    
    def _update_input_fields(self):
        """Dynamically update input fields based on selected task."""
        # Clear existing inputs
        while self.input_layout.count():
            item = self.input_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        task_name = self.task_combo.currentText()
        
        if task_name == "Optimize Deck":
            self._create_deck_optimization_inputs()
        elif task_name == "Generate Buy List":
            self._create_buy_list_inputs()
        elif task_name == "Analyze Collection":
            self._create_collection_inputs()
        elif task_name == "Find Synergies":
            self._create_synergy_inputs()
        elif task_name == "Analyze Meta":
            self._create_meta_inputs()
        elif task_name == "Price Analysis":
            self._create_price_inputs()
    
    def _create_deck_optimization_inputs(self):
        """Input fields for deck optimization."""
        # Deck selection
        deck_label = QLabel("Select Deck:")
        self.input_layout.addWidget(deck_label)
        
        self.deck_combo = QComboBox()
        # TODO: Populate from CardForge deck service
        self.deck_combo.addItems([
            "Kaalia Voltron",
            "Cloud, Ex-SOLDIER (FF Only)",
            "Grixis Control",
            "Naya Tokens"
        ])
        self.input_layout.addWidget(self.deck_combo)
        
        # Budget constraint
        budget_label = QLabel("Budget for Upgrades ($):")
        self.input_layout.addWidget(budget_label)
        
        self.budget_spin = QDoubleSpinBox()
        self.budget_spin.setRange(0, 10000)
        self.budget_spin.setValue(200.0)
        self.budget_spin.setSuffix(" USD")
        self.input_layout.addWidget(self.budget_spin)
        
        # Optimization goal
        goal_label = QLabel("Optimization Goal:")
        self.input_layout.addWidget(goal_label)
        
        self.goal_combo = QComboBox()
        self.goal_combo.addItems([
            "Turn 3 Commander Consistency",
            "Improve Win Rate",
            "Budget Optimization",
            "Better Mana Base",
            "More Interaction",
            "Stronger Finishers"
        ])
        self.input_layout.addWidget(self.goal_combo)
    
    def _create_buy_list_inputs(self):
        """Input fields for buy list generation."""
        deck_label = QLabel("Deck Name:")
        self.input_layout.addWidget(deck_label)
        
        self.deck_combo = QComboBox()
        self.deck_combo.addItems([
            "Kaalia Voltron",
            "Cloud, Ex-SOLDIER (FF Only)",
            "Grixis Control",
            "Naya Tokens"
        ])
        self.input_layout.addWidget(self.deck_combo)
        
        budget_label = QLabel("Total Budget ($):")
        self.input_layout.addWidget(budget_label)
        
        self.budget_spin = QDoubleSpinBox()
        self.budget_spin.setRange(0, 10000)
        self.budget_spin.setValue(100.0)
        self.budget_spin.setSuffix(" USD")
        self.input_layout.addWidget(self.budget_spin)
        
        priority_label = QLabel("Priority Categories:")
        self.input_layout.addWidget(priority_label)
        
        note = QLabel("(Select categories to prioritize in buy list)")
        note.setStyleSheet("color: gray; font-size: 10pt;")
        self.input_layout.addWidget(note)
    
    def _create_collection_inputs(self):
        """Input fields for collection analysis."""
        info = QLabel("Collection analysis will examine your entire collection for:")
        self.input_layout.addWidget(info)
        
        bullets = QLabel("""
        • Duplicate cards (excess inventory)
        • Missing cards for active decks
        • Organization recommendations
        • Trade fodder identification
        • High-value cards for protection
        """)
        bullets.setStyleSheet("margin-left: 20px;")
        self.input_layout.addWidget(bullets)
    
    def _create_synergy_inputs(self):
        """Input fields for synergy finding."""
        deck_label = QLabel("Analyze Synergies for Deck:")
        self.input_layout.addWidget(deck_label)
        
        self.deck_combo = QComboBox()
        self.deck_combo.addItems([
            "Kaalia Voltron",
            "Cloud, Ex-SOLDIER (FF Only)",
            "Grixis Control",
            "Naya Tokens"
        ])
        self.input_layout.addWidget(self.deck_combo)
    
    def _create_meta_inputs(self):
        """Input fields for meta analysis."""
        info = QLabel("Meta analysis will examine:")
        self.input_layout.addWidget(info)
        
        bullets = QLabel("""
        • Top Commander archetypes
        • Win rate trends
        • Popular commanders
        • Tech card recommendations
        • Budget meta alternatives
        """)
        bullets.setStyleSheet("margin-left: 20px;")
        self.input_layout.addWidget(bullets)
    
    def _create_price_inputs(self):
        """Input fields for price analysis."""
        scope_label = QLabel("Analysis Scope:")
        self.input_layout.addWidget(scope_label)
        
        self.scope_combo = QComboBox()
        self.scope_combo.addItems([
            "Entire Collection",
            "Specific Deck",
            "High-Value Cards Only (>$20)",
            "Recent Purchases"
        ])
        self.input_layout.addWidget(self.scope_combo)
    
    def _execute_task(self):
        """Execute the selected task with agent orchestration."""
        # Build task from inputs
        task = self._build_task_from_inputs()
        
        if not task:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please fill in all required fields."
            )
            return
        
        # Update UI state
        self.execute_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Status: Executing...")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        self.results_text.clear()
        
        # Create and start worker thread
        self.worker = AgentWorker(task)
        self.worker.started.connect(self._on_task_started)
        self.worker.progress.connect(self._on_task_progress)
        self.worker.finished.connect(self._on_task_finished)
        self.worker.error.connect(self._on_task_error)
        self.worker.start()
    
    def _build_task_from_inputs(self) -> Optional[AgentTask]:
        """Build AgentTask from current input values."""
        task_name = self.task_combo.currentText()
        
        try:
            if task_name == "Optimize Deck":
                return AgentTask(
                    task_type="deck_optimization",
                    complexity="complex",
                    context={
                        "deck_name": self.deck_combo.currentText(),
                        "budget": self.budget_spin.value(),
                        "goal": self.goal_combo.currentText()
                    }
                )
            
            elif task_name == "Generate Buy List":
                return AgentTask(
                    task_type="buy_list_generation",
                    complexity="medium",
                    context={
                        "deck_name": self.deck_combo.currentText(),
                        "budget": self.budget_spin.value()
                    }
                )
            
            elif task_name == "Analyze Collection":
                return AgentTask(
                    task_type="collection_analysis",
                    complexity="medium",
                    context={}
                )
            
            elif task_name == "Find Synergies":
                return AgentTask(
                    task_type="synergy_finding",
                    complexity="complex",
                    context={
                        "deck_name": self.deck_combo.currentText()
                    }
                )
            
            elif task_name == "Analyze Meta":
                return AgentTask(
                    task_type="meta_analysis",
                    complexity="complex",
                    context={}
                )
            
            elif task_name == "Price Analysis":
                return AgentTask(
                    task_type="price_analysis",
                    complexity="fast",
                    context={
                        "scope": self.scope_combo.currentText()
                    }
                )
            
        except Exception as e:
            print(f"Error building task: {e}")
            return None
    
    def _cancel_task(self):
        """Cancel running task."""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self._reset_ui_state()
            self.results_text.setPlainText("Task cancelled by user.")
    
    def _on_task_started(self):
        """Handle task start signal."""
        self.progress_text.setText("Task started...")
    
    def _on_task_progress(self, message: str):
        """Handle progress update signal."""
        self.progress_text.setText(message)
    
    def _on_task_finished(self, result: Dict[str, Any]):
        """Handle task completion signal."""
        self._reset_ui_state()
        
        # Format results for display
        formatted_results = self._format_results(result)
        self.results_text.setPlainText(formatted_results)
        
        self.status_label.setText("Status: Complete ✓")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def _on_task_error(self, error_msg: str):
        """Handle task error signal."""
        self._reset_ui_state()
        
        self.results_text.setPlainText(f"Error: {error_msg}")
        self.status_label.setText("Status: Error ✗")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        QMessageBox.critical(
            self,
            "Task Failed",
            f"An error occurred:\n\n{error_msg}"
        )
    
    def _reset_ui_state(self):
        """Reset UI to ready state."""
        self.execute_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_text.clear()
    
    def _format_results(self, result: Dict[str, Any]) -> str:
        """Format agent response for display."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"Agent: {result.get('agent_name', 'Unknown')}")
        lines.append(f"Model: {result.get('model_used', 'Unknown')}")
        lines.append(f"Execution Time: {result.get('execution_time', 0):.2f}s")
        lines.append(f"Confidence: {result.get('confidence', 0):.2%}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(result.get('content', 'No content'))
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _copy_results(self):
        """Copy results to clipboard."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.results_text.toPlainText())
        
        self.status_label.setText("Results copied to clipboard!")
    
    def _export_results(self):
        """Export results to file."""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            f"cardforge_ai_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.results_text.toPlainText())
            
            self.status_label.setText(f"Results exported to {filename}")


# ============================================================================
# INTEGRATION WITH MAIN CARDFORGE WINDOW
# ============================================================================

def add_ai_panel_to_cardforge(main_window):
    """
    Add AI Assistant panel to existing CardForge main window.
    
    Usage in CardForge main GUI:
        from cardforge_gui_integration import add_ai_panel_to_cardforge
        add_ai_panel_to_cardforge(self)
    """
    # Create AI panel
    ai_panel = AIAssistantPanel()
    
    # Add to main window (assuming tab widget structure)
    if hasattr(main_window, 'tab_widget'):
        main_window.tab_widget.addTab(ai_panel, "🤖 AI Assistant")
    else:
        # Fallback: add as dock widget
        from PyQt6.QtWidgets import QDockWidget
        dock = QDockWidget("AI Assistant", main_window)
        dock.setWidget(ai_panel)
        main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    
    return ai_panel


# ============================================================================
# STANDALONE DEMO
# ============================================================================

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Demo window
    demo_window = AIAssistantPanel()
    demo_window.setWindowTitle("CardForge AI Assistant Demo")
    demo_window.resize(800, 900)
    demo_window.show()
    
    sys.exit(app.exec())
