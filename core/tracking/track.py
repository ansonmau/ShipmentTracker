from core.driver.driver import WebDriverSession
from core.tracking.result import Result
from core.log import getLogger
from time import sleep

logger = getLogger(__name__)
                


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
                    f"({counter}/{total_count}) Starting tracking... | {carrier} | {tracking_num} | attempt {attempt_count}/3"
            )
            try:
                curr_result = executeScript(sesh, tracking_num)
                if curr_result.result == Result.RETRY:
                    if not attempt_count == 3:
                        continue
                    curr_result.set_result(Result.FAIL)
                    curr_result.set_reason("Failed after 3 attempts")
                    report['fail'].append(curr_result)
                elif curr_result.result == Result.SUCCESS:
                    logger.info(str(curr_result))
                    report["success"].append(curr_result)
                    break
                else:
                    logger.info(str(curr_result))
                    report["fail"].append(curr_result)
                    break
            except Exception as e:
                curr_result = Result(Result.CRASH, carrier=carrier, reason="Unknown error occured", tracking_number=tracking_num)
                logger.debug("(#{}) Unknown error: {}".format(tracking_num, e))
                logger.info(str(curr_result))
                if attempt_count == 3:
                    report["crash"].append(curr_result)
            sleep(2)
        sleep(3)
    return report
