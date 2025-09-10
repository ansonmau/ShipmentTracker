from core.driver import WebDriverSession
from core.log import getLogger

logger = getLogger(__name__)

def track(sesh: WebDriverSession, tracking_nums, executeScript):
        report = {
                "success": [],
                "fail": [],
                "crash": []
        }

        for tracking_num in tracking_nums:
                try:
                        if executeScript(sesh, tracking_num):
                                report['success'].append(tracking_num)
                        else:
                                report['fail'].append(tracking_num)
                except Exception as e:
                        logger.warning("(#{}) Unknown error: {}".format(tracking_num, e))
                        report['crash'].append(tracking_num)

        return report