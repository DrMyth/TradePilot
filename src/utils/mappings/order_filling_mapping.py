from utils.mt5_client import mt5

ORDER_FILLING_MAP = {
    "FOK": mt5.ORDER_FILLING_FOK,  
    "IOC": mt5.ORDER_FILLING_IOC,
    "BOC": mt5.ORDER_FILLING_BOC,
    "RETURN": mt5.ORDER_FILLING_RETURN
}
