import MetaTrader5 as mt5
from utils.logger import logger

mt5.initialize()

if not mt5.initialize():
    logger.error(f"MT5 initialization failed, error code: {mt5.last_error()}")
    raise Exception("MT5 initialization failed")