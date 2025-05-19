from utils.mcp_client import mcp

@mcp.resource("mt5://getting_started")
def getting_started() -> str:
    """
    Resource providing getting started information for the MetaTrader 5 API.
    """
    return """
    # Getting Started with MetaTrader 5 API

    This MCP server provides access to the MetaTrader 5 API for trading and market data analysis.

    ## Basic Workflow

    1. **Initialize the MT5 terminal**
    2. **Log in to your trading account**
    3. **Access market data**
    4. **Place trades**
    5. **Manage positions**
    6. **Analyze trading history**
    7. **Shut down the connection**

    See the other resources for detailed guides on each step.
    """

@mcp.resource("mt5://full_trading_workflow")
def full_trading_workflow() -> str:
    """
    Resource providing a full trading workflow from login to shutdown.
    """
    return """
    # Full Trading Workflow Example

    ```python
    # 1. Initialize MT5
    initialize()

    # 2. Log in
    token = login(account=896254754, password="your_password", server="your_server")

    # 3. Get symbols
    symbols = get_symbols()

    # 4. Get price data
    rates = copy_rates_from_pos(symbol="EURUSD", timeframe=15, start_pos=0, count=10)

    # 5. Place a trade
    result = order_send(...)

    # 6. Manage positions
    positions = positions_get()

    # 7. Analyze history
    orders = history_orders_get(...)

    # 8. Shutdown
    shutdown()
    ```
    """
    
@mcp.resource("mt5://tradingview_chart_trade_guide")
def tradingview_chart_trade_guide() -> str:
    """
    Guide for using screenshot-based trade analysis and execution.
    """
    return """
    # Screenshot Trade Analysis & Execution Guide

    You can upload a TradingView chart screenshot with green and red lines marking your Take Profit (TP) and Stop Loss (SL) levels.

    **How it works:**
    - The system analyzes the screenshot to detect the green (TP) and red (SL) price levels.
    - It determines the trade direction:
    - If the green line (TP) is above and the red line (SL) is below the entry: **Buy order**
    - If the green line (TP) is below and the red line (SL) is above the entry: **Sell order**
    - If an entry price is marked, it will be used for a pending order; otherwise, a market order is placed at the current price.
    - The trade is sent to MetaTrader 5 with the detected parameters.

    **Screenshot requirements:**
    - Use clear, horizontal green and red lines for TP and SL.
    - If possible, mark the entry price with a label or line.
    - The price scale must be visible and readable.

    **Example workflow:**
    1. Upload your TradingView screenshot.
    2. The system will analyze the image, extract TP, SL, and entry.
    3. It will determine the order type and direction.
    4. The trade will be placed automatically.
    """

@mcp.resource("mt5://order_types_reference")
def order_types_reference() -> str:
    """
    Resource providing a reference for all order types and trade actions.
    """
    return """
    # Order Types and Trade Actions Reference

    ## Market Orders
    - `ORDER_TYPE_BUY`: Buy at market price
    - `ORDER_TYPE_SELL`: Sell at market price

    ## Pending Orders
    - `ORDER_TYPE_BUY_LIMIT`: Buy at specified price (lower than current)
    - `ORDER_TYPE_SELL_LIMIT`: Sell at specified price (higher than current)
    - `ORDER_TYPE_BUY_STOP`: Buy at specified price (higher than current)
    - `ORDER_TYPE_SELL_STOP`: Sell at specified price (lower than current)
    - `ORDER_TYPE_BUY_STOP_LIMIT`: Buy stop limit order
    - `ORDER_TYPE_SELL_STOP_LIMIT`: Sell stop limit order

    ## Trade Actions
    - `TRADE_ACTION_DEAL`: Place a market order
    - `TRADE_ACTION_PENDING`: Place a pending order
    - `TRADE_ACTION_SLTP`: Modify SL/TP
    - `TRADE_ACTION_MODIFY`: Modify an order
    - `TRADE_ACTION_REMOVE`: Remove a pending order
    - `TRADE_ACTION_CLOSE_BY`: Close a position by an opposite one
    """

@mcp.resource("mt5://market_data_guide")
def market_data_guide() -> str:
    """
    Resource providing a guide for accessing market data with the MetaTrader 5 API.
    """
    return """
    # Market Data Guide

    ## Timeframes
    - `M1`, `M5`, `M15`, `M30`, `H1`, `H4`, `D1`, `W1`, `MN1`

    ## Getting Bars (Candlesticks)
    ```python
    rates = copy_rates_from_pos(symbol="EURUSD", timeframe=60, start_pos=0, count=10)
    ```

    ## Getting Ticks
    ```python
    ticks = copy_ticks_from_pos(symbol="EURUSD", start_pos=0, count=10)
    ```
    """

@mcp.resource("mt5://risk_management_guide")
def risk_management_guide() -> str:
    """
    Resource providing a comprehensive guide to risk management in MT5.
    """
    return """
    # Risk Management Guide

    ## Lot Size Calculation
    Use `calculate_lot_size()` to determine optimal lot size based on equity, risk %, and stop-loss.

    ## Margin and Leverage
    Margin is the collateral required to open a position. Leverage amplifies risk and reward.

    ## Stop-Loss and Take-Profit
    Always set a stop-loss. Take-profit helps lock in gains.

    ## Risk/Reward Ratio
    Aim for at least 1:2 risk/reward.
    """

@mcp.resource("mt5://account_info_reference")
def account_info_reference() -> str:
    """
    Resource providing a reference for all account info fields.
    """
    return """
    # Account Info Reference

    - `balance`: Account balance
    - `equity`: Balance + floating P/L
    - `margin`: Margin in use
    - `free_margin`: Available margin
    - `margin_level`: Equity / margin * 100
    - `leverage`: Account leverage
    - `currency`: Deposit currency
    """

@mcp.resource("mt5://example_market_order")
def example_market_order() -> str:
    """
    Resource providing an example of placing a market order.
    """
    return """
    # Example: Placing a Market Order

    ```python
    request = OrderRequest(
        action=mt5.TRADE_ACTION_DEAL,
        symbol="EURUSD",
        volume=0.1,
        type=mt5.ORDER_TYPE_BUY,
        price=mt5.symbol_info_tick("EURUSD").ask,
        deviation=20,
        magic=123456,
        comment="Buy order",
        type_time=mt5.ORDER_TIME_GTC,
        type_filling=mt5.ORDER_FILLING_IOC
    )
    result = order_send(request)
    ```
    """

@mcp.resource("mt5://example_pending_order")
def example_pending_order() -> str:
    """
    Resource providing an example of placing a pending order.
    """
    return """
    # Example: Placing a Pending Order

    ```python
    request = OrderRequest(
        action=mt5.TRADE_ACTION_PENDING,
        symbol="EURUSD",
        volume=0.1,
        type=mt5.ORDER_TYPE_BUY_LIMIT,
        price=1.08,
        sl=1.07,
        tp=1.09,
        deviation=20,
        magic=123456,
        comment="Buy limit order",
        type_time=mt5.ORDER_TIME_GTC,
        type_filling=mt5.ORDER_FILLING_IOC
    )
    result = order_send(request)
    ```
    """

@mcp.resource("mt5://example_modify_sltp")
def example_modify_sltp() -> str:
    """
    Resource providing an example of modifying SL/TP for a position.
    """
    return """
    # Example: Modifying SL/TP

    ```python
    request = OrderRequest(
        action=mt5.TRADE_ACTION_SLTP,
        symbol=position.symbol,
        sl=1.07,
        tp=1.09,
        position=position.ticket
    )
    result = order_send(request)
    ```
    """

@mcp.resource("mt5://example_close_position")
def example_close_position() -> str:
    """
    Resource providing an example of closing a position.
    """
    return """
    # Example: Closing a Position

    ```python
    request = OrderRequest(
        action=mt5.TRADE_ACTION_DEAL,
        symbol=position.symbol,
        volume=position.volume,
        type=mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
        price=mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
        position=position.ticket,
        deviation=20,
        magic=123456,
        comment="Close position",
        type_time=mt5.ORDER_TIME_GTC,
        type_filling=mt5.ORDER_FILLING_IOC
    )
    result = order_send(request)
    ```
    """

@mcp.resource("mt5://example_account_summary")
def example_account_summary() -> str:
    """
    Resource providing an example of fetching account summary.
    """
    return """
    # Example: Fetching Account Summary

    ```python
    summary = get_account_summary()
    print(summary)
    ```
    """

@mcp.resource("mt5://example_fetch_positions")
def example_fetch_positions() -> str:
    """
    Resource providing an example of fetching open positions.
    """
    return """
    # Example: Fetching Open Positions

    ```python
    positions = positions_get()
    for pos in positions:
        print(pos)
    ```
    """

@mcp.resource("mt5://example_trading_history")
def example_trading_history() -> str:
    """
    Resource providing an example of fetching trading history.
    """
    return """
    # Example: Fetching Trading History

    ```python
    orders = history_orders_get(from_date="2023-01-01", to_date="2023-01-31")
    for order in orders:
        print(order)
    ```
    """

@mcp.resource("mt5://example_calculate_lot_size")
def example_calculate_lot_size() -> str:
    """
    Resource providing an example of calculating lot size.
    """
    return """
    # Example: Calculating Lot Size

    ```python
    result = calculate_lot_size(symbol="EURUSD", account_equity=10000, risk_pct=2, stop_loss_pips=50)
    print(result)
    ```
    """

@mcp.resource("mt5://example_calculate_margin")
def example_calculate_margin() -> str:
    """
    Resource providing an example of calculating margin required for a trade.
    """
    return """
    # Example: Calculating Margin

    ```python
    result = calculate_margin(order_type="BUY", symbol="EURUSD", volume=0.1, price=1.1)
    print(result)
    ```
    """

@mcp.resource("mt5://example_calculate_profit")
def example_calculate_profit() -> str:
    """
    Resource providing an example of calculating profit/loss for a trade.
    """
    return """
    # Example: Calculating Profit/Loss

    ```python
    result = calculate_profit(order_type="BUY", symbol="EURUSD", volume=0.1, price_open=1.1, price_close=1.12)
    print(result)
    ```
    """

@mcp.resource("mt5://example_symbol_info")
def example_symbol_info() -> str:
    """
    Resource providing an example of fetching symbol info.
    """
    return """
    # Example: Fetching Symbol Info

    ```python
    info = get_symbol_info("EURUSD")
    print(info)
    ```
    """

@mcp.resource("mt5://example_market_data")
def example_market_data() -> str:
    """
    Resource providing an example of fetching market data.
    """
    return """
    # Example: Fetching Market Data

    ```python
    rates = copy_rates_from_pos(symbol="EURUSD", timeframe=15, start_pos=0, count=10)
    print(rates)
    ```
    """

@mcp.resource("mt5://example_portfolio_management")
def example_portfolio_management() -> str:
    """
    Resource providing an example of multi-symbol portfolio management.
    """
    return """
    # Example: Portfolio Management

    ```python
    symbols = ["EURUSD", "USDJPY", "GBPUSD"]
    positions = [positions_get(symbol=s) for s in symbols]
    for pos_list in positions:
        for pos in pos_list:
            print(pos)
    ```
    """