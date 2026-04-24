from core.settings import Settings

import core.scraper.scripts.ems as ems
import core.scraper.scripts.eshipper as eshipper
import core.scraper.scripts.freightcom as freightcom


class Handler:
    site_scrapers = {
            "ems":          ems.scrape,
            "eshipper":     eshipper.scrape, 
            "freightcom":   freightcom.scrape,
            }

    def __init__(self, wds, data_handler) -> None:
        """
        params:
            wds             ->  WebDriverSession obj
            data_handler    ->  [out] ref to data handler to populate
        return:
            bool            ->  no errors => 0
        """
        self.wds        =   wds 
        self.driver     =   self.wds.driver 
        self.dh_out     =   data_handler # out list
        self.settings   =   Settings.get_settings()["scrape"]
        self.worker     =   None 

    def set_worker(self, worker):
        self.worker = worker

    def run(self):
        scrape_list = [x for x in self.settings.keys() if self.settings[x] == True]
        
        for site in scrape_list:
            scrape_results = self.site_scrapers[site](self.wds, self.worker)
            for carrier, tracking_number in scrape_results:
                print("out list <- {} {}".format(carrier, tracking_number))
                self.dh_out.add_shipment(carrier, tracking_number)
