class Result:
    FAIL = 0
    SUCCESS = 1
    CRASH = 2
    RETRY = 3

    def __init__(self, result=FAIL, carrier="", tracking_number="", reason=""):
        assert result in [self.SUCCESS, self.FAIL, self.CRASH, self.RETRY]
        self.result = result
        self.reason = reason
        self.carrier = carrier
        self.tracking_number = tracking_number

    @staticmethod
    def from_csv(line):
        line = line.strip().split(',')
        return Result(result = int(line[0]), reason = line[1], carrier = line[2], tracking_number = line[3])

    def __str__(self):
        text_converter = {
                Result.SUCCESS: "Success",
                Result.FAIL: "Fail",
                Result.CRASH: "Crash",
                Result.RETRY: "Retry",
                }
        result = text_converter[self.result]
        return f"{result}: {self.reason}" if self.reason else f"{result}"

    def __eq__(self, other):
        return self.result == other.result and self.tracking_number == other.tracking_number

    def get_reason(self):
        return self.reason
    
    def get_carrier(self):
        return self.carrier
    
    def get_tracking_number(self):
        return self.tracking_number
    
    def get_result(self):
        return self.result

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

    def to_csv(self):
        line = f"{self.result},{self.reason},{self.carrier},{self.tracking_number}"
        return line
