from core.driver.driver import WebDriverSession
from core.tracking.result import Result
from core.tracking.report import Report
from core.log import getLogger
from time import sleep

logger = getLogger(__name__)

def track(sesh: WebDriverSession, carrier, tracking_nums, executeScript, report):
    total_shipment_count = len(tracking_nums)
    current_shipment_count = 0

    for tracking_num in tracking_nums:
        current_shipment_count += 1
        attempt_count = 0 
        curr_result = Result()
        while attempt_count < 3:
            attempt_count += 1
            logger.info(
                f"Starting tracking for shipment {carrier} #{tracking_num} | {current_shipment_count}/{total_shipment_count} | attempt {attempt_count}/3"
            )
            try:
                curr_result = executeScript(sesh, tracking_num)
            except Exception as e:
                if (attempt_count == 3):
                    curr_result = Result(Result.CRASH, carrier=carrier, reason="Unknown error occured", tracking_number=tracking_num)
                    logger.debug("(#{}) Unknown error: {}".format(tracking_num, e))
                else:
                    curr_result = Result(Result.RETRY)

            if curr_result.result != Result.RETRY:
                break
            sleep(2)
        if (curr_result.result == Result.RETRY):
            curr_result.set_result(Result.FAIL)
            curr_result.set_reason("Failed after 3 attempts")
        logger.info(str(curr_result))
        report.add_result(curr_result)
        sleep(3)
