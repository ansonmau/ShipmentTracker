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


def track(sesh: WebDriverSession, carrier, tracking_nums, executeScript):
    report = {"success": [], "fail": [], "crash": []}

    total_count = len(tracking_nums)
    counter = 0

    for tracking_num in tracking_nums:
        counter += 1
        attempt_count = 0 
        while attempt_count < 3:
            attempt_count += 1
            logger.info(
                    f"({counter}/{total_count}) Starting tracking... | {carrier} {tracking_num} | attempt {attempt_count}/3"
            )
            try:
                curr_result = executeScript(sesh, tracking_num)
                if curr_result == result.RETRY:
                    continue
                elif curr_result == result.SUCCESS:
                    report["success"].append((carrier, tracking_num))
                    logger.info("Success")
                    break
                else:
                    report["Fail"].append((carrier, tracking_num))
                    logger.info("failed")
                    break
            except Exception as e:
                curr_result = result(result.CRASH, "Unknown error occured")
                logger.debug("(#{}) Unknown error: {}".format(tracking_num, e))
                logger.info("unknown error encountered, retrying")
                report["crash"].append((carrier, tracking_num))
            sleep(2)
        sleep(3)
    return report
