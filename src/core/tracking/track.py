from src.core.tracking.result import Result
from src.core.log import getLogger
from time import sleep
from src.core.settings import Settings

import src.core.tracking.scripts.canadapost as cp
import src.core.tracking.scripts.ups as ups
import src.core.tracking.scripts.fedex as fdx
import src.core.tracking.scripts.canpar as cpr
import src.core.tracking.scripts.purolator as pur

logger = getLogger("tracker")

class Handler:
    def __init__(self, wds, data_handler, report) -> None:
        self.wds        =   wds
        self.driver     =   self.wds.driver
        self.dh         =   data_handler 
        self.report     =   report

        self.wait_between_attempts_s     =   2
        self.wait_between_shipments_s    =   3

        self.scripts = {
                "canada post": cp.executeScript,
                "ups": ups.executeScript,
                "fedex": fdx.executeScript,
                "canpar": cpr.executeScript,
                "purolator": pur.executeScript,
                }

    def run(self):
        active_carriers = [x for x in self.dh.get_dict() if (self.dh.get_dict()[x] and Settings.get_settings()["track"][x])]
        logger.info(f"Active carriers: {','.join(active_carriers)}")
        for carrier in active_carriers:
            self.track(carrier)

    def track(self, carrier):
        tracking_nums               =   self.dh.get_dict()[carrier]
        total_shipment_count        =   len(tracking_nums)
        comp_shipment_count         =   0 # completed shipments

        for tracking_num in tracking_nums:
            attempt_count   =   0 
            curr_result     =   None

            while attempt_count < 3:
                attempt_count += 1

                # log msg list that will be joined by \t and then info'd
                # [n]carrier#tracking_number   n%  attempt n/3
                log_msg_l = [f"{carrier}#{tracking_num}", f"{int((comp_shipment_count / total_shipment_count)*100)}%"]
                if (attempt_count > 1):
                    log_msg_l.append(f"attempt {attempt_count} / 3")
                logger.info("  ---  ".join(log_msg_l))

                try:
                    curr_result = self.scripts[carrier](self.wds, tracking_num)
                except Exception as e:
                    if (attempt_count == 3):
                        curr_result = Result(Result.CRASH, carrier=carrier, reason="Unknown error occured", tracking_number=tracking_num)
                        logger.debug("(#{}) Unknown error: {}".format(tracking_num, e))
                    else:
                        curr_result = Result(Result.RETRY)
                if curr_result.result != Result.RETRY:
                    break
                sleep(self.wait_between_attempts_s)

            if (curr_result and curr_result.result == Result.RETRY):
                curr_result.set_result(Result.FAIL)
                curr_result.set_reason("Failed after 3 attempts")

            logger.info(str(curr_result))
            self.report.add_result(curr_result)
            comp_shipment_count += 1
            sleep(self.wait_between_shipments_s)
