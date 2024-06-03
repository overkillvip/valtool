import json
from inspect import stack

"""
from my disc bot and earlier than that my comp sci project
i might release both but without commit history bot cuz random hotfixes (im lazy and just commit and test on server/prod)
comp sci cuz the one contribution my classmate made to a ui txt file
"""

class Config():
    def __init__(self):
        try:
            # time this
            with open(f"{__file__.replace(__file__.split('\\')[-1], "")}config.json", "r") as self.configFile:
                self.config:dict = json.load(self.configFile)
                self.verify()
                print(f"({stack()[0][3]})[INFO] Loaded config | verify returned {self.verify()} | {self.config}")
        except Exception as e:
            print(f"({stack()[0][3]})[CRITICAL] {e}")
            exit()

    def save(self):
        try:
            if not self.verify(): raise BrokenPipeError
            with open(self.configFile.name, "w") as configFileWrite:
                json.dump(self.config, configFileWrite, ensure_ascii=False)

        except BrokenPipeError:
            print(f"({stack()[0][3]})[CRITICAL] Error saving config verify failed | {e} | {self.config}")
            exit()
        except Exception as e:
            print(f"({stack()[0][3]})[CRITICAL] Error saving config | {e} | {self.config}")
            exit()

    def verify(self):
        try:
            if self.config == None or "valid" not in self.config.keys():
                raise BufferError
            return True
        except Exception as e:
            print(f"({stack()[0][3]})[CRITICAL] Error verifying config | {e if type(e) != BufferError else 'INVALID'} | {self.config}")
            exit()
    
configObj = Config()
config = configObj.config


#================================================================================#
