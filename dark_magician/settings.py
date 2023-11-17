import logging


APP_RUNTIME_SETTINGS = {
    "log_level"     : logging.DEBUG,
    "log_format"    : "[%(asctime)s][%(levelname)s]:%(message)s",
    "log_console"   : True,
    "log_file"      : "log.txt",
    "settings_file" : "settings.json",
}
