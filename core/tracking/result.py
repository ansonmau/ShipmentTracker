class Result:

    FAIL = 0
    SUCCESS = 1
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
        return f"{result} {self.reason}"

    def __eq__(self, other):
        return self.result == other.result and self.tracking_number == other.tracking_number

    def set_reason(self, reason):
        reason = "".join([': ', reason])
        self.reason = reason

    def set_result(self, result):
        self.result = result

    def set_tracking_number(self, tracking_number):
        self.tracking_number = tracking_number

    def set_carrier(self, carrier):
        self.carrier = carrier
    
    def get_reason(self):
        return self.reason
    
    def get_carrier(self):
        return self.carrier
    
    def get_tracking_number(self):
        return self.tracking_number
    
    def get_result(self):
        return self.result
    
    def detail(self):
        info_dict = {
                'result': self.result,
                'carrier': self.carrier,
                'tracking_number': self.tracking_number,
                'reason': self.reason,
                }
        return info_dict
