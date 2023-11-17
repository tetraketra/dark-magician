import logging

from app import tkinterApp
from settings import APP_RUNTIME_SETTINGS


if __name__ == "__main__":
    logging.basicConfig(
        filename = APP_RUNTIME_SETTINGS['log_file'], 
        level = APP_RUNTIME_SETTINGS['log_level'], 
        format = APP_RUNTIME_SETTINGS['log_format']
    )

    if APP_RUNTIME_SETTINGS['log_console']:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(APP_RUNTIME_SETTINGS['log_format']))
        logging.getLogger('').addHandler(console)

    app = tkinterApp()
    app.mainloop()