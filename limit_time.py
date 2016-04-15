import signal
from bs4 import BeautifulSoup
import sys
sys.path.append("./BeautifulSoup")
import urllib2 # Used to read the html document


def timeout(url, timeout_duration=3, default=None):
    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler) 
    signal.alarm(timeout_duration)
    opener = urllib2.build_opener()
    try:
        if not url.startswith('http'):
            url = '%s%s' % ('http://', url)
        page = opener.open(url)
        result = BeautifulSoup(page)

    except TimeoutError as exc:
        result = default
    finally:
        signal.alarm(0)

    return result