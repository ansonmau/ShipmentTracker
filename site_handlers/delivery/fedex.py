from core.driver import WebDriverSession, ELEMENT_TYPES
from selenium.common.exceptions import StaleElementReferenceException
from os import getenv
from core.log import getLogger

logger = getLogger(__name__)

paths = {
        "cookies_banner": (ELEMENT_TYPES['id'], 'uc-main-dialog'),
        "deny_cookies_btn": (ELEMENT_TYPES['id'], 'deny'),

}

def track(sesh: WebDriverSession, tracking_nums):
        report = {
                "success": [],
                "fail": []
        }

        for tracking_num in tracking_nums:
                if executeScript(sesh, tracking_num):
                        report['success'].append(tracking_num)
                else:
                        report['fail'].append(tracking_num)

        return report

def executeScript(sesh: WebDriverSession, tracking_num):
        link = ""
        sesh.get(link)

        if sesh.find.path(paths['cookies_banner'], wait = 2):
                sesh.click.path(paths['deny_cookies_btn'])

        
