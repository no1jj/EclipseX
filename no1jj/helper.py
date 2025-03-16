import json
import random

CONFIG = "no1jj/config.json"

def IsUserInAdmin(userid: str):
    config = LoadConfig()
    User = config.get("UserId")
    if userid == User:
        return True
    else:
        return False

def LoadConfig():
    try:
        with open(CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("❌ config.json file not found!")
    except json.JSONDecodeError:
        print("❌ Error occurred while reading JSON file!")
    except Exception as e:
        print(f"❌ Unknown error occurred: {e}")
    
    return {}  

def SaveConfig(config):
    try:
        with open(CONFIG, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False) 
        print("✅ Settings have been saved!")
    except Exception as e:
        print(f"❌ Error occurred while saving settings: {e}")

def RandomMessage(messages):
    return random.choice(messages)

def RandomCategoryName(name):
    return random.choice(name)

def RandomChannelName(name):
    return random.choice(name)

def RandomRoleName(name):
    return random.choice(name)

# Made by no.1_jj
# v1.0.2