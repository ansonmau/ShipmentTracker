from src.core.tracking.result import Result
from datetime import datetime

from src.core.utils import ROOT

class Report:
    save_path = ROOT / "reports" / f"{datetime.now().strftime("%m-%d_%H-%M")}.txt"

    def __init__(self):
        self.report = {
            "successes": [],
            "fails": [],
            "crashes": [],
        }

    def add_result(self, result):
        if (result.result == Result.SUCCESS):
            self.report["successes"].append(result)
        elif (result.result == Result.FAIL):
            self.report["fails"].append(result)
        elif (result.result == Result.CRASH):
            self.report["crashes"].append(result)

    def get_report(self):
        return self.report

    def get_successes(self):
        return self.report["successes"]
        
    def get_fails(self):
        return self.report["fails"]
        
    def get_crashes(self):
        return self.report["crashes"]

    def get_all(self):
        all_results = []
        for result_list in self.report.values():
            all_results.extend(result_list)
        return all_results
        
    def save_to_file(self):
        fh = open(str(Report.save_path), 'w')
        for result in self.get_all():
            line = "".join([result.to_csv(), '\n'])
            fh.write(line)
        fh.close()

    def import_previous_reports(self):
        for report_file in self._get_files():
            with open(report_file, 'r') as fh:
                for line in fh:
                    r = Result.from_csv(line)
                    if r in self.get_all():
                        continue
                    self.add_result(r)

    def _get_files(self) -> list:
        report_dir = ROOT / 'reports'
        report_files = [f for f in report_dir.iterdir() if f.is_file()]

        return report_files
