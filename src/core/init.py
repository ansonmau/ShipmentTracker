from dotenv import load_dotenv
from pathlib import Path

from core.log import MyLogger, getLogger
from core.utils import empty_folder, create_folder, create_file, ROOT
from core.settings import Settings 

class Initializer:
    def __init__(self):
        self.logger = getLogger("Initializer")
        self.err_code = ""
    
    def run(self):
        try:
            self.logger.info("Loading keys...")
            self.init_env()

            self.logger.info("Initializing data...")
            self.init_data()

            self.logger.info("Initializing reports...")
            self.init_reports()
            
            self.logger.info("Initializing logs...")
            self.init_logs()

            self.logger.info("Initializing settings...")
            self.init_settings()
        except Exception as e:
            self.err_code = e
            return False

        return True
    
    def init_logs(self):
        create_folder(ROOT / 'logs')
        create_file(MyLogger.log_file_path)
        MyLogger.init_file_handler()
    
    def init_data(self):
        create_folder(ROOT / 'data')
        create_folder(ROOT / 'data' / 'dls')
        create_file(ROOT / 'data' / 'delivery_data.json')
        create_file(ROOT / 'data' / 'keys.env')
        empty_folder(ROOT / 'data' / 'dls')

    def init_reports(self):
        create_folder(ROOT / 'reports')
    
    def init_env(self):
        env_path = ROOT / 'data' / 'keys.env'

        if (Path(env_path).stat().st_size == 0):
            self.logger.critical("Login keys empty. Please populate ./data/keys.env file")
        else:
            load_dotenv(dotenv_path=env_path)

    def init_settings(self):
        if Settings.file_exists():
            Settings.load_from_file() 
        else:
            self.logger.warning("No settings file detected. Creating one with default settings...")
            Settings.write_to_file()
