from core.driver import WebDriverSession, random_wait
from core.log import getLogger
from time import sleep

logger = getLogger(__name__)


class result:

    SUCCESS = 1
    FAIL = 0
    CRASH = 2
    RETRY = 3

    def __init__(self, result=FAIL, carrier="", tracking_number="", reason=""):
        assert result in [self.SUCCESS, self.FAIL, self.CRASH, self.RETRY]
        self.carrier = carrier
        self.result = result
        self.reason = reason
        self.tracking_number = tracking_number

    def __str__(self):
        text_converter = {
                self.SUCCESS: "Success",
                self.FAIL: "Fail",
                self.RETRY: "Retry",
                self.CRASH: "Crash",
                }
        result = text_converter[self.result]
        return f"{result}: {self.reason}"

    def __eq__(self, other):
        return self.result == other

    def set_reason(self, reason):
        self.reason = reason

    def set_result(self, result):
        self.result = result

    def set_tracking_number(self, tracking_number):
        self.tracking_number = tracking_number

    def set_carrier(self, carrier):
        self.carrier = carrier
    
    def detail(self):
        info_dict = {
                'result': self.result,
                'carrier': self.carrier,
                'tracking_number': self.tracking_number,
                'reason': self.reason,
                }
        return info_dict
                


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
                    logger.info(str(curr_result))
                    report["success"].append(curr_result)
                    break
                else:
                    logger.info(str(curr_result))
                    report["fail"].append(curr_result)
                    break
            except Exception as e:
                curr_result = result(result.CRASH, reason="Unknown error occured")
                logger.debug("(#{}) Unknown error: {}".format(tracking_num, e))
                logger.info(str(curr_result))
                report["crash"].append((carrier, tracking_num))
            sleep(2)
        sleep(3)
    return report
