import sys

import web

if __name__ == "__main__":
    if "--start-web-server" in sys.argv:
        web.main()