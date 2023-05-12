import sys
import re
import openai
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextBrowser, QFileDialog, QLabel, QMessageBox as messagebox 



# OpenAI API key
openai.api_key ="YOUR_API_KEY"




def parse_nvidia_bug_report(file_path):
    issues = []
    gpu_info = ""

    # Define patterns for issue severity levels
    critical_pattern = re.compile("NVRM:.*(Critical|Error|Failed)")
    warning_pattern = re.compile("NVRM:.*(Warning)")
    info_pattern = re.compile("NVRM:.*(Notice)")

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if "NVRM:" in line:
            severity = "info"
            if critical_pattern.search(line):
                severity = "critical"
            elif warning_pattern.search(line):
                severity = "warning"

            issues.append((severity, line.strip()))

        if "NVIDIA-SMI" in line:
            gpu_info = lines[i + 1].strip()

    return issues, gpu_info


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.open_file_button = QPushButton('Open NVIDIA Bug Report File', self)
        self.open_file_button.clicked.connect(self.open_file)

        self.gpu_info_label = QLabel("GPU Info:")
        self.issues_text_browser = QTextBrowser()

        self.ai_solutions_button = QPushButton('AI Solutions', self)
        self.ai_solutions_button.clicked.connect(self.generate_ai_solutions)

        layout.addWidget(self.open_file_button)
        layout.addWidget(self.gpu_info_label)
        layout.addWidget(self.issues_text_browser)
        layout.addWidget(self.ai_solutions_button)

        self.setLayout(layout)
        self.setWindowTitle('NVIDIA Bug Report Analyzer')

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Open NVIDIA Bug Report File", "", "Text Files (*.txt);;All Files (*)", options=options)

        if file_path:
            self.issues, gpu_info = parse_nvidia_bug_report(file_path)
            self.gpu_info_label.setText(f"GPU Info: {gpu_info}")
            self.issues_text_browser.clear()
            for severity, issue in self.issues:
                color = "green"
                if severity == "critical":
                    color = "red"
                elif severity == "warning":
                    color = "yellow"
                self.issues_text_browser.append(f'<font color="{color}">{issue}</font>')

    def generate_ai_solutions(self):

        if not openai.api_key:
            QMessageBox.warning(self, 'API Key Not Found', 'Please add your OpenAI API key to the app.')
            return
    
        prompt = "How to fix the following GPU issues:\n\n"
        prompt += "\n".join(issue for _, issue in self.issues)
        prompt += "\n\nPlease provide step-by-step solutions."

    # Truncate the prompt if it's too long
        max_tokens = 4096 - 150  # Reserve 150 tokens for the response
        tokens = openai.Completion.create(  # Use OpenAI's tokenizer
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=1,  # We only need the token count
            n=1,
            echo=True,
            stop=None,
        )
        token_count = tokens["choices"][0]["text"].count("\n")

        if token_count > max_tokens:
            prompt = prompt[:-(token_count - max_tokens)]  # Truncate the prompt

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.8,
        )

        solutions = response.choices[0].text.strip()
        self.issues_text_browser.append(f'\n<font color="blue">Suggested Solutions:</font>\n{solutions}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

