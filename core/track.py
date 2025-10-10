from core.driver import WebDriverSession, random_wait
from core.log import getLogger
from time import sleep

logger = getLogger(__name__)


class result:

    SUCCESS = 1
    FAIL = 0
    CRASH = 2
    RETRY = 3

    def __init__(self, result, reason=""):
        assert result in [self.SUCCESS, self.FAIL, self.CRASH]
        self.result = result
        self.reason = reason

    def __str__(self):
        return f"{self.result}: {self.reason}"

    def __eq__(self, other):
        return self.result == other


def track(sesh: WebDriverSession, tracking_nums, executeScript):
    report = {"success": [], "fail": [], "crash": []}

    total_count = len(tracking_nums)
    counter = 0

    for tracking_num in tracking_nums:
        counter += 1
        attempt_count = 0 
        while attempt_count <= 3:
            attempt_count += 1
            logger.info(
                    f"Starting tracking... ({counter}/{total_count}) | tracking number: {tracking_num} | attempt {attempt_count}/3"
            )
            try:
                curr_result = executeScript(sesh, tracking_num)
                if curr_result == result.RETRY:
                    continue
                elif curr_result == result.SUCCESS:
                    report["success"].append((tracking_num, curr_result))
                    logger.info("success")
                    break
                else:
                    report["fail"].append((tracking_num, curr_result))
                    logger.info("failed")
                    break
            except Exception as e:
                curr_result = result(result.CRASH, "Unknown error occured")
                logger.debug("(#{}) Unknown error: {}".format(tracking_num, e))
                logger.info("unknown error encountered, retrying")
                report["crash"].append((tracking_num, curr_result))
            sleep(1)
        sleep(2)
    return report
