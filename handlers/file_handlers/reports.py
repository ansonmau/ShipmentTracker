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
    @staticmethod
    def _get_report_file_date(report_file) -> datetime:
        report_date_fmt = "%m-%d_%H-%M.txt"
        return datetime.strptime(report_file.name.split('+')[1], report_date_fmt)

    @staticmethod
    def _get_reports() -> list:
        report_dir = Path("./reports")
        report_files = [f for f in report_dir.iterdir() if f.is_file()]

        return report_files

    @staticmethod
    def _parse_report(report: Path) -> dict:
        parsed = {"success":[], "fail":[], "crash":[]}
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
                parsed['crash'].append(r)
            elif "FAIL" in cols[0]:
                curr_reason = cols[3].split("reason: ")[1]
                r.set_result(result.FAIL)
                r.set_reason(curr_reason)
                parsed['fail'].append(r)
            elif "SUCCESS" in cols[0]:
                parsed['success'].append(r)

        return parsed

    @staticmethod
    def successes() -> list[result]:
        report_files = read._get_reports()
        successes = []
        for report in report_files:
            for result in read._parse_report(report)['success']:
                successes.append(result)
        
        return successes

    @staticmethod
    def get_crashed():
        pass

    @staticmethod
    def fails():
        report_files = read._get_reports()
        fail = []
        for report in report_files:
            for result in read._parse_report(report)['fail']:
                fail.append(result)
        
        return fail

        


