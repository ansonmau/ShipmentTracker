from core.driver import WebDriverSession
from core.log import getLogger

logger = getLogger(__name__)

class result:

        SUCCESS = 1
        FAIL = 0
        CRASH = 2

        def __init__(self, result, reason = ""):
                assert result in [self.SUCCESS, self.FAIL, self.CRASH]
                self.result = result
                self.reason = reason
        
        def __str__(self):
                return f"{self.result}: {self.reason}"
        
        def __eq__(self, other):
                return self.result == other

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
                        if curr_result == result.SUCCESS:
                                report['success'].append((tracking_num, curr_result))
                                logger.info("success")
                        else:
                                report['fail'].append((tracking_num, curr_result))
                                logger.info("failed")
                except Exception as e:
                        curr_result = result(result.CRASH, "Unknown error occured")
                        logger.warning("(#{}) Unknown error: {}".format(tracking_num, e))
                        report['crash'].append((tracking_num, curr_result))

        return report

