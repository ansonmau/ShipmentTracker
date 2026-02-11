from datetime import datetime
from pathlib import Path, Path
from core.utils import PROJ_FOLDER, generate_tracking_link
from core.track import result

def write_report(report) -> None:
    time = datetime.now().strftime("%m-%d_%H-%M")
    report_file = PROJ_FOLDER / "reports" / f"report+{time}.txt"

    with open(str(report_file), "w") as f:
        for result in report["success"]:
            info = result.detail()
            link = generate_tracking_link(info['carrier'], info['tracking_number'])
            f.write(f"[SUCCESS] | {info['carrier']} | #{info['tracking_number']} | {link}" + '\n')
        f.write("\n" +"-"*50 + "\n")
        for result in report["fail"]:
            info = result.detail()
            link = generate_tracking_link(info['carrier'], info['tracking_number'])
            f.write(f"[FAIL] | {info['carrier']} | #{info['tracking_number']} | reason: {info['reason']} | {link}" + '\n')
        f.write("\n" +"-"*50 + "\n")
        for result in report["crash"]:
            info = result.detail()
            link = generate_tracking_link(info['carrier'], info['tracking_number'])
            f.write(f"[CRASH (FAIL)] | {info['carrier']} | #{info['tracking_number']} | reason: {info['reason']} | {link}" + '\n')

class read:
    report = {"success":[], "fail":[], "crash":[]}

    def __init__(self):
        for r in self._get_reports():
            self._parse_report(r)

    def _get_reports(self) -> list:
        report_dir = Path("./reports")
        report_files = [f for f in report_dir.iterdir() if f.is_file()]

        return report_files

    def _parse_report(self, report: Path) -> dict:
        report_txt = report.read_text()
        lines = report_txt.split('\n')
        for line in lines:
            if len(line) < 1:
                continue
            if line[0] == '-':
                # is a separator line (i.e. ----------)
                continue
            cols = line.split(' | ')
            curr_tracking_num = cols[2][1:] # first char is '#'
            curr_carrier = cols[1]
            r = result(result.SUCCESS, carrier=curr_carrier, tracking_number=curr_tracking_num)
            if "CRASH" in cols[0]:
                r.set_result(result.CRASH)
                self.report['crash'].append(r)
            elif "FAIL" in cols[0]:
                curr_reason = cols[3].split("reason: ")[1]
                r.set_result(result.FAIL)
                r.set_reason(curr_reason)
                self.report['fail'].append(r)
            elif "SUCCESS" in cols[0]:
                self.report['success'].append(r)

        return self.report

    def successes(self) -> list[result]:
        return self.report['success']

    def get_crashed(self):
        return self.report['crash']

    def fails(self):
        return self.report['fail']

        


