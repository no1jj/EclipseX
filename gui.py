import sys
import json
import subprocess
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidget,
    QPushButton, QHBoxLayout, QMessageBox, QTextEdit, QGroupBox
)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon

CONFIG_FILE = "no1jj/config.json"

class ProcessOutputReader(QObject):
    output_received = pyqtSignal(str)
    process_finished = pyqtSignal(int)
    
    def __init__(self, process):
        super().__init__()
        self.process = process
        
    def start_reading(self):
        threading.Thread(target=self._read_output, daemon=True).start()
        
    def _read_output(self):
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.output_received.emit(line.strip())
                else:
                    break
            
            self.process.wait()
            self.process_finished.emit(self.process.returncode)
        except Exception as e:
            self.output_received.emit(f"❌ Error reading output: {str(e)}")
            self.process_finished.emit(-1)

def load_config_sync():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        return {
            "BotToken": "", 
            "UserId": "", 
            "BotActivity": "", 
            "GuildName": "No1JJ", 
            "Messages": [], 
            "ChannelName": [], 
            "CategoryName": [], 
            "RoleName": [],
            "SendEveryone": True,
            "SendLogs": False,
            "LogWebhook": ""
        }
    except Exception as e:
        return {}

def save_config_sync(config):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        return False

class No1jj(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config_sync()
        self.real_token = self.config.get("BotToken", "")
        self.real_webhook = self.config.get("LogWebhook", "")
        self.bot_process = None
        self.process_reader = None
        self.guilds = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("no1jj")
        self.setWindowIcon(QIcon("no1jj/icon.png"))
        self.setGeometry(100, 100, 1200, 700)
    
        self.setStyleSheet("""
        QWidget {
            font-size: 14px;
            background-color: #36393f;
            color: #dcddde;
        }
        QPushButton {
            background-color: #5865f2;
            color: white;
            border-radius: 10px;
            padding: 8px;
            font-size: 14px;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #4752c4;
        }
        QPushButton:disabled {
            background-color: #3c3f44;
            color: #72767d;
        }
        QLineEdit {
            border: 2px solid #202225;
            border-radius: 10px;
            padding: 5px;
            background-color: #40444b;
            color: #dcddde;
        }
        QGroupBox {
            border: 2px solid #202225;
            border-radius: 10px;
            padding: 8px;
            margin-top: 5px;
            background-color: #2f3136;
            color: #dcddde;
        }
        QTextEdit {
            background-color: #2f3136;
            color: #dcddde;
            font-family: monospace;
            border-radius: 10px;
            padding: 5px;
            border: 2px solid #202225;
        }
        QListWidget {
            border: 1px solid #202225;
            border-radius: 5px;
            padding: 2px;
            background-color: #40444b;
            color: #dcddde;
        }
        QLabel {
            color: #dcddde;
        }
    """)

        main_layout = QVBoxLayout()
        
        top_layout = QVBoxLayout()
        
        config_group = QGroupBox("Bot Settings")
        config_layout = QVBoxLayout()

        token_layout = QHBoxLayout()
        token_label = QLabel("Bot Token:")
        token_label.setStyleSheet("color: #dcddde;")
        token_label.setFixedWidth(80)
        token_layout.addWidget(token_label)
        
        self.bot_token = QLineEdit(self)
        self.bot_token.setText(self.real_token)
        self.bot_token.setEchoMode(QLineEdit.Password)
        self.bot_token.textChanged.connect(self.update_real_token)
        self.bot_token.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        token_layout.addWidget(self.bot_token)
        
        self.show_token_btn = QPushButton("Show")
        self.show_token_btn.clicked.connect(self.toggle_token_visibility)
        self.show_token_btn.setFixedWidth(80)
        token_layout.addWidget(self.show_token_btn)
        config_layout.addLayout(token_layout)

        activity_layout = QHBoxLayout()
        activity_label = QLabel("Bot Activity:")
        activity_label.setStyleSheet("color: #dcddde;")
        activity_label.setFixedWidth(80)
        activity_layout.addWidget(activity_label)
        
        self.bot_activity = QLineEdit(self)
        self.bot_activity.setText(self.config.get("BotActivity", ""))
        self.bot_activity.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        activity_layout.addWidget(self.bot_activity)
        
        self.send_everyone_check = QPushButton("@everyone")
        self.send_everyone_check.setCheckable(True)
        self.send_everyone_check.setChecked(self.config.get("SendEveryone", True))
        self.send_everyone_check.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:checked { background-color: #3ba55c; }
            QPushButton:!checked { background-color: #72767d; }
        """)
        self.send_everyone_check.setFixedWidth(120)
        activity_layout.addWidget(self.send_everyone_check)
        config_layout.addLayout(activity_layout)

        userid_layout = QHBoxLayout()
        userid_label = QLabel("User ID:")
        userid_label.setStyleSheet("color: #dcddde;")
        userid_label.setFixedWidth(80)
        userid_layout.addWidget(userid_label)
        
        self.user_id = QLineEdit(self)
        self.user_id.setText(self.config.get("UserId", ""))
        self.user_id.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        userid_layout.addWidget(self.user_id)
        
        self.send_logs_check = QPushButton("Send Logs")
        self.send_logs_check.setCheckable(True)
        self.send_logs_check.setChecked(self.config.get("SendLogs", False))
        self.send_logs_check.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:checked { background-color: #3ba55c; }
            QPushButton:!checked { background-color: #72767d; }
        """)
        self.send_logs_check.clicked.connect(self.toggle_webhook_visibility)
        self.send_logs_check.setFixedWidth(120)
        userid_layout.addWidget(self.send_logs_check)
        config_layout.addLayout(userid_layout)

        self.webhook_group = QGroupBox()
        self.webhook_group.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
            }
        """)
        webhook_layout = QHBoxLayout()
        webhook_label = QLabel("Log Webhook:")
        webhook_label.setStyleSheet("color: #dcddde;")
        webhook_label.setFixedWidth(80)
        webhook_layout.addWidget(webhook_label)
        
        self.log_webhook = QLineEdit(self)
        self.log_webhook.setText(self.real_webhook)
        self.log_webhook.setEchoMode(QLineEdit.Password)
        self.log_webhook.textChanged.connect(self.update_real_webhook)
        self.log_webhook.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        webhook_layout.addWidget(self.log_webhook)

        self.show_webhook_btn = QPushButton("Show")
        self.show_webhook_btn.clicked.connect(self.toggle_webhook_visibility_content)
        self.show_webhook_btn.setFixedWidth(80)
        webhook_layout.addWidget(self.show_webhook_btn)
        self.webhook_group.setLayout(webhook_layout)
        config_layout.addWidget(self.webhook_group)
        self.webhook_group.setVisible(self.config.get("SendLogs", False))

        guild_layout = QHBoxLayout()
        guild_label = QLabel("Guild Name:")
        guild_label.setStyleSheet("color: #dcddde;")
        guild_label.setFixedWidth(80)
        guild_layout.addWidget(guild_label)
        
        self.guild_name = QLineEdit(self)
        self.guild_name.setText(self.config.get("GuildName", "No1JJ"))
        self.guild_name.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        guild_layout.addWidget(self.guild_name)
        config_layout.addLayout(guild_layout)

        config_group.setLayout(config_layout)
        top_layout.addWidget(config_group)

        lists_layout = QHBoxLayout()

        msg_group = QGroupBox("Messages")
        msg_layout = QVBoxLayout()

        self.message_list = QListWidget()
        self.message_list.addItems(self.config.get("Messages", []))
        self.message_list.setFixedHeight(120)
        msg_layout.addWidget(self.message_list)

        msg_input_layout = QHBoxLayout()
        self.msg_input = QLineEdit(self)
        self.msg_input.setPlaceholderText("Enter message")
        self.msg_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
            }
        """)
        msg_input_layout.addWidget(self.msg_input)

        self.add_msg_btn = QPushButton("Add")
        self.add_msg_btn.clicked.connect(self.add_message)
        self.add_msg_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.add_msg_btn.setFixedWidth(120)
        msg_input_layout.addWidget(self.add_msg_btn)

        msg_layout.addLayout(msg_input_layout)

        self.del_msg_btn = QPushButton("Delete Selected")
        self.del_msg_btn.clicked.connect(self.delete_message)
        self.del_msg_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.del_msg_btn.setFixedWidth(120)
        msg_layout.addWidget(self.del_msg_btn)

        msg_group.setLayout(msg_layout)
        lists_layout.addWidget(msg_group)

        channel_group = QGroupBox("Channel Names")
        channel_layout = QVBoxLayout()

        self.channel_list = QListWidget()
        self.channel_list.addItems(self.config.get("ChannelName", []))
        self.channel_list.setFixedHeight(120)
        channel_layout.addWidget(self.channel_list)

        channel_input_layout = QHBoxLayout()
        self.channel_input = QLineEdit(self)
        self.channel_input.setPlaceholderText("Enter channel name")
        self.channel_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
            }
        """)
        channel_input_layout.addWidget(self.channel_input)

        self.add_channel_btn = QPushButton("Add")
        self.add_channel_btn.clicked.connect(self.add_channel)
        self.add_channel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.add_channel_btn.setFixedWidth(120)
        channel_input_layout.addWidget(self.add_channel_btn)

        channel_layout.addLayout(channel_input_layout)

        self.del_channel_btn = QPushButton("Delete Selected")
        self.del_channel_btn.clicked.connect(self.delete_channel)
        self.del_channel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.del_channel_btn.setFixedWidth(120)
        channel_layout.addWidget(self.del_channel_btn)

        channel_group.setLayout(channel_layout)
        lists_layout.addWidget(channel_group)

        category_group = QGroupBox("Category Names")
        category_layout = QVBoxLayout()

        self.category_list = QListWidget()
        self.category_list.addItems(self.config.get("CategoryName", []))
        self.category_list.setFixedHeight(120)
        category_layout.addWidget(self.category_list)

        category_input_layout = QHBoxLayout()
        self.category_input = QLineEdit(self)
        self.category_input.setPlaceholderText("Enter category name")
        self.category_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
            }
        """)
        category_input_layout.addWidget(self.category_input)

        self.add_category_btn = QPushButton("Add")
        self.add_category_btn.clicked.connect(self.add_category)
        self.add_category_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.add_category_btn.setFixedWidth(120)
        category_input_layout.addWidget(self.add_category_btn)

        category_layout.addLayout(category_input_layout)

        self.del_category_btn = QPushButton("Delete Selected")
        self.del_category_btn.clicked.connect(self.delete_category)
        self.del_category_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.del_category_btn.setFixedWidth(120)
        category_layout.addWidget(self.del_category_btn)

        category_group.setLayout(category_layout)
        lists_layout.addWidget(category_group)

        role_group = QGroupBox("Role Names")
        role_layout = QVBoxLayout()

        self.role_list = QListWidget()
        self.role_list.addItems(self.config.get("RoleName", []))
        self.role_list.setFixedHeight(120)
        role_layout.addWidget(self.role_list)

        role_input_layout = QHBoxLayout()
        self.role_input = QLineEdit(self)
        self.role_input.setPlaceholderText("Enter role name")
        self.role_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
            }
        """)
        role_input_layout.addWidget(self.role_input)

        self.add_role_btn = QPushButton("Add")
        self.add_role_btn.clicked.connect(self.add_role)
        self.add_role_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.add_role_btn.setFixedWidth(120)
        role_input_layout.addWidget(self.add_role_btn)

        role_layout.addLayout(role_input_layout)

        self.del_role_btn = QPushButton("Delete Selected")
        self.del_role_btn.clicked.connect(self.delete_role)
        self.del_role_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.del_role_btn.setFixedWidth(120)
        role_layout.addWidget(self.del_role_btn)

        role_group.setLayout(role_layout)
        lists_layout.addWidget(role_group)

        top_layout.addLayout(lists_layout)
        
        main_layout.addLayout(top_layout)
        
        bottom_layout = QHBoxLayout()
        
        button_group = QGroupBox("Controls")
        button_layout = QVBoxLayout()  

        self.save_btn = QPushButton("Save Config")
        self.save_btn.clicked.connect(self.save_config)
        self.save_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.save_btn.setFixedWidth(120)
        button_layout.addWidget(self.save_btn)

        self.run_bot_btn = QPushButton("Run bot.py")
        self.run_bot_btn.clicked.connect(self.run_bot)
        self.run_bot_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.run_bot_btn.setFixedWidth(120)
        button_layout.addWidget(self.run_bot_btn)

        self.stop_bot_btn = QPushButton("Stop Bot")
        self.stop_bot_btn.clicked.connect(self.stop_bot)
        self.stop_bot_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.stop_bot_btn.setFixedWidth(120)
        self.stop_bot_btn.setEnabled(False)
        button_layout.addWidget(self.stop_bot_btn)

        self.close_gui_btn = QPushButton("Close GUI")
        self.close_gui_btn.clicked.connect(self.close)
        self.close_gui_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
                background-color: #ed4245;
            }
        """)
        self.close_gui_btn.setFixedWidth(120)
        button_layout.addWidget(self.close_gui_btn)

        button_group.setLayout(button_layout)
        bottom_layout.addWidget(button_group)

        term_group = QGroupBox("Terminal Output")
        term_layout = QVBoxLayout()
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("background-color: black; color: lime; font-family: monospace;")
        self.terminal_output.setFixedHeight(200)
        term_layout.addWidget(self.terminal_output)
        term_group.setLayout(term_layout)
        bottom_layout.addWidget(term_group, stretch=2)  
        
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def update_real_token(self, text):
        self.real_token = text
    
    def toggle_token_visibility(self):
        if self.bot_token.echoMode() == QLineEdit.Password:
            self.bot_token.setEchoMode(QLineEdit.Normal)
            self.show_token_btn.setText("Hide")
        else:
            self.bot_token.setEchoMode(QLineEdit.Password)
            self.show_token_btn.setText("Show")
    
    def add_message(self):
        msg = self.msg_input.text().strip()
        if msg:
            self.message_list.addItem(msg)
            self.msg_input.clear()
    
    def delete_message(self):
        selected_item = self.message_list.currentRow()
        if selected_item >= 0:
            self.message_list.takeItem(selected_item)
        else:
            QMessageBox.warning(self, "Warning", "No message selected to delete.")
    
    def add_channel(self):
        name = self.channel_input.text().strip()
        if name:
            self.channel_list.addItem(name)
            self.channel_input.clear()
    
    def delete_channel(self):
        selected_item = self.channel_list.currentRow()
        if selected_item >= 0:
            self.channel_list.takeItem(selected_item)
        else:
            QMessageBox.warning(self, "Warning", "No channel name selected to delete.")

    def add_category(self):
        name = self.category_input.text().strip()
        if name:
            self.category_list.addItem(name)
            self.category_input.clear()
    
    def delete_category(self):
        selected_item = self.category_list.currentRow()
        if selected_item >= 0:
            self.category_list.takeItem(selected_item)
        else:
            QMessageBox.warning(self, "Warning", "No category name selected to delete.")

    def add_role(self):
        name = self.role_input.text().strip()
        if name:
            self.role_list.addItem(name)
            self.role_input.clear()
    
    def delete_role(self):
        selected_item = self.role_list.currentRow()
        if selected_item >= 0:
            self.role_list.takeItem(selected_item)
        else:
            QMessageBox.warning(self, "Warning", "No role name selected to delete.")
    
    def save_config(self):
        self.config["BotToken"] = self.real_token
        self.config["BotActivity"] = self.bot_activity.text()
        self.config["UserId"] = self.user_id.text()
        self.config["GuildName"] = self.guild_name.text()
        self.config["Messages"] = [self.message_list.item(i).text() for i in range(self.message_list.count())]
        self.config["ChannelName"] = [self.channel_list.item(i).text() for i in range(self.channel_list.count())]
        self.config["CategoryName"] = [self.category_list.item(i).text() for i in range(self.category_list.count())]
        self.config["RoleName"] = [self.role_list.item(i).text() for i in range(self.role_list.count())]
        self.config["SendEveryone"] = self.send_everyone_check.isChecked()
        self.config["SendLogs"] = self.send_logs_check.isChecked()
        self.config["LogWebhook"] = self.real_webhook
        
        if save_config_sync(self.config):
            self.terminal_output.append("✅ Settings have been saved successfully!")
        else:
            self.terminal_output.append("❌ An error occurred while saving the settings.")
    
    def run_bot(self):
        if self.bot_process is not None and self.bot_process.poll() is None:
            QMessageBox.information(self, "Info", "Bot is already running.")
            return
            
        if not os.path.exists("bot.py"):
            self.terminal_output.append("❌ bot.py file not found!")
            QMessageBox.critical(self, "Error", "bot.py file does not exist in the current directory.")
            return
            
        try:
            self.terminal_output.append("🚀 Attempting to run bot.py...")

            if not os.path.exists(CONFIG_FILE):
                self.terminal_output.append("⚠️ No configuration file found. Please save settings first.")
                self.save_config()
            
            self.bot_process = subprocess.Popen(
                ["python", "bot.py"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.process_reader = ProcessOutputReader(self.bot_process)
            self.process_reader.output_received.connect(self.append_output)
            self.process_reader.process_finished.connect(self.handle_process_finished)
            self.process_reader.start_reading()
            
            self.terminal_output.append("✅ bot.py execution process has started!")
            self.run_bot_btn.setEnabled(False)
            self.stop_bot_btn.setEnabled(True)
            
        except Exception as e:
            error_msg = f"❌ Error occurred while running bot.py: {str(e)}"
            self.terminal_output.append(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def append_output(self, text):
        self.terminal_output.append(text)
        self.terminal_output.verticalScrollBar().setValue(
            self.terminal_output.verticalScrollBar().maximum()
        )
    
    def handle_process_finished(self, exit_code):
        if exit_code == 0:
            self.terminal_output.append("✅ bot.py has terminated successfully.")
        else:
            self.terminal_output.append(f"⚠️ bot.py has stopped (Exit code: {exit_code})")
        
        self.run_bot_btn.setEnabled(True)
        self.stop_bot_btn.setEnabled(False)
        self.bot_process = None
    
    def stop_bot(self):
        if self.bot_process is not None and self.bot_process.poll() is None:
            self.terminal_output.append("⏹️ Attempting to stop bot...")
            try:
                self.bot_process.terminate()
                
                def check_and_kill():
                    if self.bot_process and self.bot_process.poll() is None:
                        self.terminal_output.append("⚠️ Bot is not responding. Forcibly terminating...")
                        self.bot_process.kill()
                
                QTimer.singleShot(5000, check_and_kill)
                
            except Exception as e:
                self.terminal_output.append(f"❌ Error occurred while stopping bot: {str(e)}")
        else:
            self.terminal_output.append("ℹ️ No bot is currently running.")
            self.run_bot_btn.setEnabled(True)
            self.stop_bot_btn.setEnabled(False)

    def toggle_webhook_visibility(self):
        self.webhook_group.setVisible(self.send_logs_check.isChecked())

    def update_real_webhook(self, text):
        self.real_webhook = text

    def toggle_webhook_visibility_content(self):
        if self.log_webhook.echoMode() == QLineEdit.Password:
            self.log_webhook.setEchoMode(QLineEdit.Normal)
            self.show_webhook_btn.setText("Hide")
        else:
            self.log_webhook.setEchoMode(QLineEdit.Password)
            self.show_webhook_btn.setText("Show")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = No1jj()
    editor.show()
    sys.exit(app.exec_())

#Made by no.1_jj
