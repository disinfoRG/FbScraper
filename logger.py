import sys

class Logger(object):
    def __init__(self, file_io):
        self.file_io = file_io
    def write(self, s):
        sys.stdout.write(s)
        self.file_io.write(str(s))
    def close(self):
        self.file_io.close()

def main():
    f = open('test_logger.log', 'a', buffering=1)
    logger = Logger(f)
    logger.write('asdfb')
    logger.write('1234556')
    logger.close()
        

if __name__ == '__main__':
    main()
