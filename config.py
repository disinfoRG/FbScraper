from facebook import *
from settings import *

## 初始化爬蟲
fb = Facebook(FB_EMAIL, FB_PASSWORD, 'Chrome', CHROMEDRIVER_BIN, True)