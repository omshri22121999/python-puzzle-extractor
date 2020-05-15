class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def print_blue(self, data):
        return(self.OKBLUE + data + self.ENDC + '\n')

    def print_green(self, data):
        return(self.OKGREEN + data + self.ENDC) + '\n'

    def print_header(self, data):
        return(self.HEADER + data + self.ENDC + '\n')

    def print_warning(self, data):
        return(self.WARNING + data + self.ENDC + '\n')

    def print_fail(self, data):
        return(self.FAIL + data + self.ENDC + '\n')

    def print_bold(self, data):
        return(self.BOLD + data + self.ENDC + '\n')

    def print_underline(self, data):
        return(self.UNDERLINE + data + self.ENDC + '\n')
