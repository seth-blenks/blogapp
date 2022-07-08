from logging import getLogger, INFO, FileHandler, Formatter

fmt = Formatter('%(name)s - %(levelname)s : %(message)s')
testhandler = FileHandler('admintest.txt')

testhandler.setLevel(INFO)
testhandler.setFormatter(fmt)

testlogger = getLogger(__name__)
testlogger.setLevel(INFO)
testlogger.addHandler(testhandler)