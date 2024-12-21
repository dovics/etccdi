from logging import getLogger, StreamHandler, Formatter

logger = getLogger("main")
logger.setLevel("INFO")

console_handler = StreamHandler()
formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

def info(msg):
    logger.info(msg)
    
def error(msg):
    logger.error(msg)
    
def warn(msg):
    logger.warning(msg)