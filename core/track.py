from core.driver import WebDriverSession
from core.log import getLogger

logger = getLogger(__name__)

SUCCESS = 0
FAIL = 1
CRASH = 2

def track(sesh: WebDriverSession, tracking_nums, executeScript):
        report = {
                "success": [],
                "fail": [],
                "crash": []
        }

        total_count = len(tracking_nums)
        counter = 0

        for tracking_num in tracking_nums:
                counter += 1
                logger.info(f"Attempting tracking for #{tracking_num} ({counter}/{total_count})")
                try:
                        curr_result = executeScript(sesh, tracking_num)
                        if curr_result == SUCCESS:
                                report['success'].append((tracking_num, curr_result))
                        else:
                                report['fail'].append((tracking_num, curr_result))
                except Exception as e:
                        curr_result = result(CRASH, "Unknown error occured")
                        logger.warning("(#{}) Unknown error: {}".format(tracking_num, e))
                        report['crash'].append((tracking_num, curr_result))

        return report

class result:
        def __init__(self, result, reason = ""):
                self.result = result
                self.reason = reason
        
        def __str__(self):
                return f"{self.result}: {self.reason}"
        
        def __eq__(self, other):
                return self.result == other