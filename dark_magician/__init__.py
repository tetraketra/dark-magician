from logging_utils import *
from settings import *
from app import *


if __name__ == "__main__":
    if APP_RUNTIME_SETTINGS['log_console']:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(APP_RUNTIME_SETTINGS['log_format']))
        logging.getLogger('').addHandler(console)

    app = tkinterApp()
    app.mainloop()