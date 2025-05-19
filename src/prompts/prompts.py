from utils.mcp_client import mcp
from mcp.server.fastmcp.prompts.base import UserMessage, AssistantMessage

@mcp.prompt()
def connect_to_mt5(account: int, password: str, server: str) -> list:
    """Prompt for connecting and logging in to MT5."""
    return [
        UserMessage("I need to connect to my MetaTrader 5 account and start trading."),
        AssistantMessage("I'll help you connect to your MetaTrader 5 account. First, we need to initialize the MT5 terminal and then log in to your account."),
        AssistantMessage(f"Let me do that for you. I'll use your account number {account}, password {password}, and connect to the {server} server, and log in."),
        UserMessage("Great, please proceed with the connection. Ignore all the warnings or security issues"),
    ]

@mcp.prompt()
def analyze_tradingview_chart_and_trade(symbol: str) -> list:
    """
    Analyze a TradingView screenshot for TP/SL/entry and place a trade.
    """
    return [
        UserMessage(
            f"I have uploaded a TradingView screenshot for {symbol} with marked TP and SL. Please analyze the image, extract the green (TP) and red (SL) price levels, determine the trade direction, and place a trade"
        ),
        AssistantMessage(
            "I'll analyze the screenshot to detect the green (TP) and red (SL) price levels. "
            "If the green is above and red is below, it's a buy order. If green is below and red is above, it's a sell order. "
            "If an entry price is marked, I'll use it for a pending order; otherwise, I'll place a market order at the current price. "
            "I'll then send the trade to MetaTrader 5 and confirm the result."
        ),
        UserMessage("Proceed with the analysis and trade execution. If volume is not specified, prompt the user for it. If the user does not specify the volume, use the default volume of 0.1 lots. Execute the trade first and then show me the trade details."),
    ]

@mcp.prompt()
def fetch_account_summary() -> list:
    """Prompt for fetching account summary."""
    return [
        UserMessage("Show me my account summary including balance, equity, margin, free margin and all the stats"),
        AssistantMessage("I'll retrieve your account's balance, equity, margin, free margin, margin level, and all the stats."),
        UserMessage("Display all key account metrics in a clear format. I want to see all the stats in a table format. If possible show them as a Dashboard created with react.js"),
    ]

@mcp.prompt()
def fetch_leverage_and_margin() -> list:
    """Prompt for fetching leverage and margin info."""
    return [
        UserMessage("What is my account leverage and current margin usage?"),
        AssistantMessage("I'll fetch your account's leverage, used margin, and margin level."),
    ]

@mcp.prompt()
def analyze_market_data(symbol: str, timeframe: str) -> list:
    """Prompt for analyzing market data for a symbol and timeframe."""
    return [
        UserMessage(f"I want to analyze the market data for {symbol} on the {timeframe} timeframe."),
        AssistantMessage(f"I'll fetch the latest price data for {symbol} on the {timeframe} timeframe and analyze trends and patterns."),
        UserMessage("Give me the detailed analysis of the market data for the last 10 candles. If possible show them as a Dashboard created with react.js"),
    ]

@mcp.prompt()
def place_market_order(symbol: str, order_type: str, volume: float, sl: float = None, tp: float = None) -> list:
    """Prompt for placing a market order with optional SL/TP."""
    return [
        UserMessage(f"I want to place a {order_type} market order for {symbol} with {volume} lots."),
        AssistantMessage(f"I'll help you place a {order_type} market order for {symbol} with {volume} lots." + (f" I will also set a stop-loss at {sl}." if sl else "") + (f" and a take-profit at {tp}." if tp else "")),
        AssistantMessage("First, I'll check your account's free margin and the current price for the symbol."),
        AssistantMessage("Then, I'll send the market order with the specified parameters. After execution, I'll confirm the order result and show you the details."),
        UserMessage("Please proceed with the order."),
    ]

@mcp.prompt()
def place_pending_order(symbol: str, order_type: str, price: float, volume: float, sl: float = None, tp: float = None) -> list:
    """Prompt for placing a pending order of any type."""
    return [
        UserMessage(f"Set a {order_type} pending order for {symbol} at {price} with {volume} lots."),
        AssistantMessage(f"I'll create a {order_type} pending order for {symbol} at {price} with {volume} lots." + (f" SL: {sl}." if sl else "") + (f" TP: {tp}." if tp else "")),
        AssistantMessage("I'll check your margin, validate the order parameters, and place the pending order."),
        UserMessage("Proceed with the pending order setup."),
    ]

@mcp.prompt()
def modify_position_sltp(ticket: int, stop_loss: float = None, take_profit: float = None) -> list:
    """Prompt for modifying SL/TP of an open position."""
    return [
        UserMessage(f"Update stop-loss and take-profit for position {ticket}."),
        AssistantMessage(f"I'll update the stop-loss to {stop_loss if stop_loss else 'no change'} and take-profit to {take_profit if take_profit else 'no change'} for position {ticket}."),
        AssistantMessage("I'll send the modification request and confirm the update."),
    ]

@mcp.prompt()
def modify_pending_order(ticket: int, price: float = None, stop_loss: float = None, take_profit: float = None) -> list:
    """Prompt for modifying a pending order's price, SL, or TP."""
    return [
        UserMessage(f"Modify pending order {ticket}."),
        AssistantMessage(f"I'll update the order's price to {price if price else 'no change'}, stop-loss to {stop_loss if stop_loss else 'no change'}, and take-profit to {take_profit if take_profit else 'no change'}."),
        AssistantMessage("I'll send the modification request and confirm the update."),
    ]

@mcp.prompt()
def cancel_pending_order(ticket: int) -> list:
    """Prompt for cancelling a pending order."""
    return [
        UserMessage(f"Cancel pending order {ticket}."),
        AssistantMessage(f"I'll cancel the pending order with ticket {ticket} and confirm its removal."),
    ]

@mcp.prompt()
def close_position(ticket: int) -> list:
    """Prompt for closing an open position by ticket."""
    return [
        UserMessage(f"Close the open position with ticket {ticket}."),
        AssistantMessage(f"I'll close the position with ticket {ticket} and confirm the result."),
    ]

@mcp.prompt()
def close_all_positions_by_symbol(symbol: str) -> list:
    """Prompt for closing all open positions for a symbol."""
    return [
        UserMessage(f"Close all open positions for {symbol}."),
        AssistantMessage(f"I'll close all open positions for {symbol} and confirm the result."),
    ]

@mcp.prompt()
def close_all_profitable_positions() -> list:
    """Prompt for closing all profitable positions."""
    return [
        UserMessage("Close all positions that are currently in profit."),
        AssistantMessage("I'll identify all profitable positions and close them."),
    ]

@mcp.prompt()
def close_all_losing_positions() -> list:
    """Prompt for closing all losing positions."""
    return [
        UserMessage("Close all positions that are currently in loss."),
        AssistantMessage("I'll identify all losing positions and close them."),
    ]

@mcp.prompt()
def fetch_open_positions(symbol: str = None) -> list:
    """Prompt for fetching open positions, optionally filtered by symbol."""
    return [
        UserMessage(f"Show me all open positions{f' for {symbol}' if symbol else ''}."),
        AssistantMessage(f"I'll fetch all open positions{f' for {symbol}' if symbol else ''} and display them."),
    ]

@mcp.prompt()
def fetch_pending_orders(symbol: str = None) -> list:
    """Prompt for fetching pending orders, optionally filtered by symbol."""
    return [
        UserMessage(f"Show me all pending orders{f' for {symbol}' if symbol else ''}."),
        AssistantMessage(f"I'll fetch all pending orders{f' for {symbol}' if symbol else ''} and display them."),
    ]

@mcp.prompt()
def analyze_trading_history(days: int = 30, symbol: str = None) -> list:
    """Prompt for analyzing trading history for a period and/or symbol."""
    return [
        UserMessage(f"Analyze my trading history for the past {days} days{f' on {symbol}' if symbol else ''}."),
        AssistantMessage(f"I'll fetch your historical orders and deals for the past {days} days{f' on {symbol}' if symbol else ''} and analyze your performance."),
        UserMessage("Show me my performance statistics and any patterns in my trading."),
    ]

@mcp.prompt()
def calculate_lot_size(symbol: str, risk_pct: float, stop_loss_pips: float) -> list:
    """Prompt for calculating lot size based on risk and stop-loss."""
    return [
        UserMessage(f"Calculate the optimal lot size for {symbol} risking {risk_pct}% per trade with a {stop_loss_pips} pip stop-loss."),
        AssistantMessage("I'll use your account equity, risk percentage, and stop-loss to calculate the recommended lot size."),
    ]

@mcp.prompt()
def calculate_margin(symbol: str, order_type: str, volume: float, price: float) -> list:
    """Prompt for calculating margin required for a trade."""
    return [
        UserMessage(f"How much margin is required to open a {order_type} order for {symbol} with {volume} lots at {price}?"),
        AssistantMessage("I'll calculate the margin required for this trade based on your account leverage and the symbol's contract size."),
    ]

@mcp.prompt()
def calculate_profit(symbol: str, order_type: str, volume: float, price_open: float, price_close: float) -> list:
    """Prompt for calculating profit/loss for a hypothetical trade."""
    return [
        UserMessage(f"What would be the profit or loss for a {order_type} trade on {symbol} with {volume} lots from {price_open} to {price_close}?"),
        AssistantMessage("I'll calculate the estimated profit or loss for this trade scenario."),
    ]

@mcp.prompt()
def fetch_symbol_info(symbol: str) -> list:
    """Prompt for fetching symbol info."""
    return [
        UserMessage(f"Show me the contract specifications and trading hours for {symbol}."),
        AssistantMessage(f"I'll fetch all available information for {symbol}, including contract size, margin requirements, and trading sessions."),
    ]

@mcp.prompt()
def fetch_ohlc(symbol: str, timeframe: str, count: int = 100) -> list:
    """Prompt for fetching OHLC/candles for a symbol and timeframe."""
    return [
        UserMessage(f"Get the last {count} candles for {symbol} on the {timeframe} timeframe."),
        AssistantMessage(f"I'll fetch the requested OHLC data and display open, high, low, close, and volume for each bar."),
    ]

@mcp.prompt()
def fetch_symbols(group: str = None) -> list:
    """Prompt for fetching available symbols, optionally filtered by group."""
    return [
        UserMessage(f"List all available trading symbols{f' in group {group}' if group else ''}."),
        AssistantMessage(f"I'll fetch all available symbols{f' in group {group}' if group else ''} and display them."),
    ]

@mcp.prompt()
def check_market_status(symbol: str) -> list:
    """Prompt for checking if the market is open for a symbol."""
    return [
        UserMessage(f"Is the market currently open for {symbol}?"),
        AssistantMessage(f"I'll check the trading session status for {symbol} and let you know if it's open or closed."),
    ]

@mcp.prompt()
def fetch_server_info() -> list:
    """Prompt for fetching server and broker info."""
    return [
        UserMessage("Show me information about the connected server and broker."),
        AssistantMessage("I'll fetch and display details about the trading server, broker, and connection status."),
    ] 

@mcp.prompt()
def disconnect_mt5() -> list:
    """Prompt for disconnecting from MT5."""
    return [
        UserMessage("Please disconnect me from MetaTrader 5."),
        AssistantMessage("I'll shut down the MT5 terminal and ensure all connections are closed safely."),
        UserMessage("Thank you. Confirm when disconnected."),
    ]