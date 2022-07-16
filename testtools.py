from logging import getLogger, INFO, FileHandler, Formatter

loggertest = getLogger('testing')

fmt = Formatter('%(name)s - %(levelname)s : %(message)s')
testhandler = FileHandler('admintest.txt')

testhandler.setLevel(INFO)
testhandler.setFormatter(fmt)


loggertest.setLevel(INFO)
loggertest.addHandler(testhandler)