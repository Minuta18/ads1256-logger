import sys

import web
import seismo

if __name__ == "__main__":
    if "--start-web-server" in sys.argv:
        web.main()
    else:
        seismo.main()