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
    outputReceived = pyqtSignal(str)
    processFinished = pyqtSignal(int)
    
    def __init__(self, process):
        super().__init__()
        self.process = process
        
    def startReading(self):
        threading.Thread(target=self._readOutput, daemon=True).start()
        
    def _readOutput(self):
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.outputReceived.emit(line.strip())
                else:
                    break
            
            self.process.wait()
            self.processFinished.emit(self.process.returncode)
        except Exception as e:
            self.outputReceived.emit(f"❌ Error reading output: {str(e)}")
            self.processFinished.emit(-1)

def LoadConfigSync():
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

def SaveConfigSync(config):
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
        self.config = LoadConfigSync()
        self.realToken = self.config.get("BotToken", "")
        self.realWebhook = self.config.get("LogWebhook", "")
        self.botProcess = None
        self.processReader = None
        self.guilds = []
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle("EclipseX")
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

        mainLayout = QVBoxLayout()
        
        topLayout = QVBoxLayout()
        
        configGroup = QGroupBox("Bot Settings")
        configLayout = QVBoxLayout()

        tokenLayout = QHBoxLayout()
        tokenLabel = QLabel("Bot Token:")
        tokenLabel.setStyleSheet("color: #dcddde;")
        tokenLabel.setFixedWidth(80)
        tokenLayout.addWidget(tokenLabel)
        
        self.botToken = QLineEdit(self)
        self.botToken.setText(self.realToken)
        self.botToken.setEchoMode(QLineEdit.Password)
        self.botToken.textChanged.connect(self.UpdateRealToken)
        self.botToken.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        tokenLayout.addWidget(self.botToken)
        
        self.showTokenBtn = QPushButton("Show")
        self.showTokenBtn.clicked.connect(self.ToggleTokenVisibility)
        self.showTokenBtn.setFixedWidth(80)
        tokenLayout.addWidget(self.showTokenBtn)
        configLayout.addLayout(tokenLayout)

        activityLayout = QHBoxLayout()
        activityLabel = QLabel("Bot Activity:")
        activityLabel.setStyleSheet("color: #dcddde;")
        activityLabel.setFixedWidth(80)
        activityLayout.addWidget(activityLabel)
        
        self.botActivity = QLineEdit(self)
        self.botActivity.setText(self.config.get("BotActivity", ""))
        self.botActivity.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        activityLayout.addWidget(self.botActivity)
        
        self.sendEveryoneCheck = QPushButton("@everyone")
        self.sendEveryoneCheck.setCheckable(True)
        self.sendEveryoneCheck.setChecked(self.config.get("SendEveryone", True))
        self.sendEveryoneCheck.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:checked { background-color: #3ba55c; }
            QPushButton:!checked { background-color: #72767d; }
        """)
        self.sendEveryoneCheck.setFixedWidth(120)
        activityLayout.addWidget(self.sendEveryoneCheck)
        configLayout.addLayout(activityLayout)

        userIdLayout = QHBoxLayout()
        userIdLabel = QLabel("User ID:")
        userIdLabel.setStyleSheet("color: #dcddde;")
        userIdLabel.setFixedWidth(80)
        userIdLayout.addWidget(userIdLabel)
        
        self.userId = QLineEdit(self)
        self.userId.setText(self.config.get("UserId", ""))
        self.userId.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        userIdLayout.addWidget(self.userId)
        
        self.sendLogsCheck = QPushButton("Send Logs")
        self.sendLogsCheck.setCheckable(True)
        self.sendLogsCheck.setChecked(self.config.get("SendLogs", False))
        self.sendLogsCheck.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:checked { background-color: #3ba55c; }
            QPushButton:!checked { background-color: #72767d; }
        """)
        self.sendLogsCheck.clicked.connect(self.ToggleWebhookVisibility)
        self.sendLogsCheck.setFixedWidth(120)
        userIdLayout.addWidget(self.sendLogsCheck)
        configLayout.addLayout(userIdLayout)

        self.webhookGroup = QGroupBox()
        self.webhookGroup.setStyleSheet("""
            QGroupBox {
                border: none;
                margin-top: 0px;
            }
        """)
        webhookLayout = QHBoxLayout()
        webhookLabel = QLabel("Log Webhook:")
        webhookLabel.setStyleSheet("color: #dcddde;")
        webhookLabel.setFixedWidth(80)
        webhookLayout.addWidget(webhookLabel)
        
        self.logWebhook = QLineEdit(self)
        self.logWebhook.setText(self.realWebhook)
        self.logWebhook.setEchoMode(QLineEdit.Password)
        self.logWebhook.textChanged.connect(self.UpdateRealWebhook)
        self.logWebhook.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        webhookLayout.addWidget(self.logWebhook)

        self.showWebhookBtn = QPushButton("Show")
        self.showWebhookBtn.clicked.connect(self.ToggleWebhookVisibilityContent)
        self.showWebhookBtn.setFixedWidth(80)
        webhookLayout.addWidget(self.showWebhookBtn)
        self.webhookGroup.setLayout(webhookLayout)
        configLayout.addWidget(self.webhookGroup)
        self.webhookGroup.setVisible(self.config.get("SendLogs", False))

        guildLayout = QHBoxLayout()
        guildLabel = QLabel("Guild Name:")
        guildLabel.setStyleSheet("color: #dcddde;")
        guildLabel.setFixedWidth(80)
        guildLayout.addWidget(guildLabel)
        
        self.guildName = QLineEdit(self)
        self.guildName.setText(self.config.get("GuildName", "No1JJ"))
        self.guildName.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                background-color: #40444b;
            }
        """)
        guildLayout.addWidget(self.guildName)
        configLayout.addLayout(guildLayout)

        configGroup.setLayout(configLayout)
        topLayout.addWidget(configGroup)

        listsLayout = QHBoxLayout()

        msgGroup = QGroupBox("Messages")
        msgLayout = QVBoxLayout()

        self.messageList = QListWidget()
        self.messageList.addItems(self.config.get("Messages", []))
        self.messageList.setFixedHeight(120)
        msgLayout.addWidget(self.messageList)

        msgInputLayout = QHBoxLayout()
        self.msgInput = QLineEdit(self)
        self.msgInput.setPlaceholderText("Enter message")
        self.msgInput.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
            }
        """)
        msgInputLayout.addWidget(self.msgInput)

        self.addMsgBtn = QPushButton("Add")
        self.addMsgBtn.clicked.connect(self.AddMessage)
        self.addMsgBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.addMsgBtn.setFixedWidth(120)
        msgInputLayout.addWidget(self.addMsgBtn)

        msgLayout.addLayout(msgInputLayout)

        self.delMsgBtn = QPushButton("Delete Selected")
        self.delMsgBtn.clicked.connect(self.DeleteMessage)
        self.delMsgBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.delMsgBtn.setFixedWidth(120)
        msgLayout.addWidget(self.delMsgBtn)

        msgGroup.setLayout(msgLayout)
        listsLayout.addWidget(msgGroup)

        channelGroup = QGroupBox("Channel Names")
        channelLayout = QVBoxLayout()

        self.channelList = QListWidget()
        self.channelList.addItems(self.config.get("ChannelName", []))
        self.channelList.setFixedHeight(120)
        channelLayout.addWidget(self.channelList)

        channelInputLayout = QHBoxLayout()
        self.channelInput = QLineEdit(self)
        self.channelInput.setPlaceholderText("Enter channel name")
        self.channelInput.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
            }
        """)
        channelInputLayout.addWidget(self.channelInput)

        self.addChannelBtn = QPushButton("Add")
        self.addChannelBtn.clicked.connect(self.AddChannel)
        self.addChannelBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.addChannelBtn.setFixedWidth(120)
        channelInputLayout.addWidget(self.addChannelBtn)

        channelLayout.addLayout(channelInputLayout)

        self.delChannelBtn = QPushButton("Delete Selected")
        self.delChannelBtn.clicked.connect(self.DeleteChannel)
        self.delChannelBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.delChannelBtn.setFixedWidth(120)
        channelLayout.addWidget(self.delChannelBtn)

        channelGroup.setLayout(channelLayout)
        listsLayout.addWidget(channelGroup)

        categoryGroup = QGroupBox("Category Names")
        categoryLayout = QVBoxLayout()

        self.categoryList = QListWidget()
        self.categoryList.addItems(self.config.get("CategoryName", []))
        self.categoryList.setFixedHeight(120)
        categoryLayout.addWidget(self.categoryList)

        categoryInputLayout = QHBoxLayout()
        self.categoryInput = QLineEdit(self)
        self.categoryInput.setPlaceholderText("Enter category name")
        self.categoryInput.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
            }
        """)
        categoryInputLayout.addWidget(self.categoryInput)

        self.addCategoryBtn = QPushButton("Add")
        self.addCategoryBtn.clicked.connect(self.AddCategory)
        self.addCategoryBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.addCategoryBtn.setFixedWidth(120)
        categoryInputLayout.addWidget(self.addCategoryBtn)

        categoryLayout.addLayout(categoryInputLayout)

        self.delCategoryBtn = QPushButton("Delete Selected")
        self.delCategoryBtn.clicked.connect(self.DeleteCategory)
        self.delCategoryBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.delCategoryBtn.setFixedWidth(120)
        categoryLayout.addWidget(self.delCategoryBtn)

        categoryGroup.setLayout(categoryLayout)
        listsLayout.addWidget(categoryGroup)

        roleGroup = QGroupBox("Role Names")
        roleLayout = QVBoxLayout()

        self.roleList = QListWidget()
        self.roleList.addItems(self.config.get("RoleName", []))
        self.roleList.setFixedHeight(120)
        roleLayout.addWidget(self.roleList)

        roleInputLayout = QHBoxLayout()
        self.roleInput = QLineEdit(self)
        self.roleInput.setPlaceholderText("Enter role name")
        self.roleInput.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
            }
        """)
        roleInputLayout.addWidget(self.roleInput)

        self.addRoleBtn = QPushButton("Add")
        self.addRoleBtn.clicked.connect(self.AddRole)
        self.addRoleBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.addRoleBtn.setFixedWidth(120)
        roleInputLayout.addWidget(self.addRoleBtn)

        roleLayout.addLayout(roleInputLayout)

        self.delRoleBtn = QPushButton("Delete Selected")
        self.delRoleBtn.clicked.connect(self.DeleteRole)
        self.delRoleBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.delRoleBtn.setFixedWidth(120)
        roleLayout.addWidget(self.delRoleBtn)

        roleGroup.setLayout(roleLayout)
        listsLayout.addWidget(roleGroup)

        topLayout.addLayout(listsLayout)
        
        mainLayout.addLayout(topLayout)
        
        bottomLayout = QHBoxLayout()
        
        buttonGroup = QGroupBox("Controls")
        buttonLayout = QVBoxLayout()  

        self.saveBtn = QPushButton("Save Config")
        self.saveBtn.clicked.connect(self.SaveConfig)
        self.saveBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.saveBtn.setFixedWidth(120)
        buttonLayout.addWidget(self.saveBtn)

        self.runBotBtn = QPushButton("Run bot.py")
        self.runBotBtn.clicked.connect(self.RunBot)
        self.runBotBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.runBotBtn.setFixedWidth(120)
        buttonLayout.addWidget(self.runBotBtn)

        self.stopBotBtn = QPushButton("Stop Bot")
        self.stopBotBtn.clicked.connect(self.StopBot)
        self.stopBotBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
            }
        """)
        self.stopBotBtn.setFixedWidth(120)
        self.stopBotBtn.setEnabled(False)
        buttonLayout.addWidget(self.stopBotBtn)

        self.closeGuiBtn = QPushButton("Close GUI")
        self.closeGuiBtn.clicked.connect(self.close)
        self.closeGuiBtn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
                background-color: #ed4245;
            }
        """)
        self.closeGuiBtn.setFixedWidth(120)
        buttonLayout.addWidget(self.closeGuiBtn)

        buttonGroup.setLayout(buttonLayout)
        bottomLayout.addWidget(buttonGroup)

        termGroup = QGroupBox("Terminal Output")
        termLayout = QVBoxLayout()
        self.terminalOutput = QTextEdit()
        self.terminalOutput.setReadOnly(True)
        self.terminalOutput.setStyleSheet("background-color: black; color: lime; font-family: monospace;")
        self.terminalOutput.setFixedHeight(200)
        termLayout.addWidget(self.terminalOutput)
        termGroup.setLayout(termLayout)
        bottomLayout.addWidget(termGroup, stretch=2)  
        
        mainLayout.addLayout(bottomLayout)

        self.setLayout(mainLayout)

    def UpdateRealToken(self, text):
        self.realToken = text
    
    def ToggleTokenVisibility(self):
        if self.botToken.echoMode() == QLineEdit.Password:
            self.botToken.setEchoMode(QLineEdit.Normal)
            self.showTokenBtn.setText("Hide")
        else:
            self.botToken.setEchoMode(QLineEdit.Password)
            self.showTokenBtn.setText("Show")
    
    def AddMessage(self):
        msg = self.msgInput.text().strip()
        if msg:
            self.messageList.addItem(msg)
            self.msgInput.clear()
    
    def DeleteMessage(self):
        selectedItem = self.messageList.currentRow()
        if selectedItem >= 0:
            self.messageList.takeItem(selectedItem)
        else:
            QMessageBox.warning(self, "Warning", "No message selected to delete.")
    
    def AddChannel(self):
        name = self.channelInput.text().strip()
        if name:
            self.channelList.addItem(name)
            self.channelInput.clear()
    
    def DeleteChannel(self):
        selectedItem = self.channelList.currentRow()
        if selectedItem >= 0:
            self.channelList.takeItem(selectedItem)
        else:
            QMessageBox.warning(self, "Warning", "No channel name selected to delete.")

    def AddCategory(self):
        name = self.categoryInput.text().strip()
        if name:
            self.categoryList.addItem(name)
            self.categoryInput.clear()
    
    def DeleteCategory(self):
        selectedItem = self.categoryList.currentRow()
        if selectedItem >= 0:
            self.categoryList.takeItem(selectedItem)
        else:
            QMessageBox.warning(self, "Warning", "No category name selected to delete.")

    def AddRole(self):
        name = self.roleInput.text().strip()
        if name:
            self.roleList.addItem(name)
            self.roleInput.clear()
    
    def DeleteRole(self):
        selectedItem = self.roleList.currentRow()
        if selectedItem >= 0:
            self.roleList.takeItem(selectedItem)
        else:
            QMessageBox.warning(self, "Warning", "No role name selected to delete.")
    
    def SaveConfig(self):
        self.config["BotToken"] = self.realToken
        self.config["BotActivity"] = self.botActivity.text()
        self.config["UserId"] = self.userId.text()
        self.config["GuildName"] = self.guildName.text()
        self.config["Messages"] = [self.messageList.item(i).text() for i in range(self.messageList.count())]
        self.config["ChannelName"] = [self.channelList.item(i).text() for i in range(self.channelList.count())]
        self.config["CategoryName"] = [self.categoryList.item(i).text() for i in range(self.categoryList.count())]
        self.config["RoleName"] = [self.roleList.item(i).text() for i in range(self.roleList.count())]
        self.config["SendEveryone"] = self.sendEveryoneCheck.isChecked()
        self.config["SendLogs"] = self.sendLogsCheck.isChecked()
        self.config["LogWebhook"] = self.realWebhook
        
        if SaveConfigSync(self.config):
            self.terminalOutput.append("✅ Settings have been saved successfully!")
        else:
            self.terminalOutput.append("❌ An error occurred while saving the settings.")
    
    def RunBot(self):
        if self.botProcess is not None and self.botProcess.poll() is None:
            QMessageBox.information(self, "Info", "Bot is already running.")
            return
            
        if not os.path.exists("bot.py"):
            self.terminalOutput.append("❌ bot.py file not found!")
            QMessageBox.critical(self, "Error", "bot.py file does not exist in the current directory.")
            return
            
        try:
            self.terminalOutput.append("🚀 Attempting to run bot.py...")

            if not os.path.exists(CONFIG_FILE):
                self.terminalOutput.append("⚠️ No configuration file found. Please save settings first.")
                self.SaveConfig()
            
            self.botProcess = subprocess.Popen(
                ["python", "bot.py"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processReader = ProcessOutputReader(self.botProcess)
            self.processReader.outputReceived.connect(self.AppendOutput)
            self.processReader.processFinished.connect(self.HandleProcessFinished)
            self.processReader.startReading()
            
            self.terminalOutput.append("✅ bot.py execution process has started!")
            self.runBotBtn.setEnabled(False)
            self.stopBotBtn.setEnabled(True)
            
        except Exception as e:
            error_msg = f"❌ Error occurred while running bot.py: {str(e)}"
            self.terminalOutput.append(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def AppendOutput(self, text):
        self.terminalOutput.append(text)
        self.terminalOutput.verticalScrollBar().setValue(
            self.terminalOutput.verticalScrollBar().maximum()
        )
    
    def HandleProcessFinished(self, exit_code):
        if exit_code == 0:
            self.terminalOutput.append("✅ bot.py has terminated successfully.")
        else:
            self.terminalOutput.append(f"⚠️ bot.py has stopped (Exit code: {exit_code})")
        
        self.runBotBtn.setEnabled(True)
        self.stopBotBtn.setEnabled(False)
        self.botProcess = None
    
    def StopBot(self):
        if self.botProcess is not None and self.botProcess.poll() is None:
            self.terminalOutput.append("⏹️ Attempting to stop bot...")
            try:
                self.botProcess.terminate()
                
                def check_and_kill():
                    if self.botProcess and self.botProcess.poll() is None:
                        self.terminalOutput.append("⚠️ Bot is not responding. Forcibly terminating...")
                        self.botProcess.kill()
                
                QTimer.singleShot(5000, check_and_kill)
                
            except Exception as e:
                self.terminalOutput.append(f"❌ Error occurred while stopping bot: {str(e)}")
        else:
            self.terminalOutput.append("ℹ️ No bot is currently running.")
            self.runBotBtn.setEnabled(True)
            self.stopBotBtn.setEnabled(False)

    def ToggleWebhookVisibility(self):
        self.webhookGroup.setVisible(self.sendLogsCheck.isChecked())

    def UpdateRealWebhook(self, text):
        self.realWebhook = text

    def ToggleWebhookVisibilityContent(self):
        if self.logWebhook.echoMode() == QLineEdit.Password:
            self.logWebhook.setEchoMode(QLineEdit.Normal)
            self.showWebhookBtn.setText("Hide")
        else:
            self.logWebhook.setEchoMode(QLineEdit.Password)
            self.showWebhookBtn.setText("Show")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = No1jj()
    editor.show()
    sys.exit(app.exec_())

# Made by no.1_jj
# v1.0.4