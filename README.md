# TradePilot MCP Server

A Model Context Protocol (MCP) server built with Python to enable AI LLMs (such as Claude AI) to trade using the MetaTrader 5 platform. This project exposes a comprehensive set of trading and market data functions, allowing natural language and programmatic control over trading operations.


## Features

- **Natural Language Trading:** Integrate with AI LLMs to place, manage, and analyze trades using plain English.
- **MetaTrader 5 Integration:** Direct connection to MT5 for real-time trading, order management, and account monitoring.
- **Gemini-2.0-flash Support:** Leverage Google’s advanced model for richer conversations.
- **Comprehensive API:** Exposes market data, trading, account, and historical functions for advanced automation and analytics.
- **Extensible & Modular:** Easily add new strategies or extend existing functionality.
- **User-Friendly:** Designed for both novice and experienced traders.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/DrMyth/TradePilot.git
cd TradePilot
```

### 2. Create and Activate a Virtual Environment

On Windows:
```powershell
uv venv
source .venv/Scripts/activate
```

On Linux/macOS (assuming bash/zsh):
```bash
uv venv
.venv/Scripts/activate
```

### 3. Install Dependencies

```bash
uv pip install -r pyproject.toml
```

### 4. Running the MCP Client with Gemini-2.0-flash
Interactive CLI Client: Launch a REPL powered by Gemini‑2.0‑flash to execute natural‑language trading commands (e.g. “Place a buy order…” or “Show my open positions”).
1. Edit `src/config.json` to point at your MCP server endpoint and credentials.
2. Obtain a Gemini-2.0-flash API key from [Google AI Studio](https://aistudio.google.com/).
4. Add your API key to your `.env` file (create one if it doesn't exist) in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
3. Run the client:

   ```bash
   uv run src/client.py
   ```

### 5. Running the Server (Debug/Development)

```bash
mcp run src/main.py
```

This command starts the MCP server and makes all trading and market‑data functions available. You can reach the server at https://localhost:6274.

## Integration with Cursor IDE or Claude AI

To integrate this MCP server with AI tools like Cursor IDE or Claude AI, use the following configuration (example):

```json
{
  "mcpServers": {
    "TradePilot": {
      "command": "/absolute/path/to/uv/.local/bin/uv.exe",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/absolute/path/to/TradePilot/src/main.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/TradePilot/src"
      }
    }
  }
}
```

## Function Reference

### Market Data Functions

- `get_symbols()`: Get all available symbols.
- `get_symbols_by_group(group)`: Get symbols by group.
- `get_symbol_info(symbol)`: Get information about a specific symbol.
- `get_symbol_info_tick(symbol)`: Get the latest tick for a symbol.
- `copy_rates_from_pos(symbol, timeframe, start_pos, count)`: Get bars from a specific position.
- `copy_rates_from_date(symbol, timeframe, date_from, count)`: Get bars from a specific date.
- `copy_rates_range(symbol, timeframe, date_from, date_to)`: Get bars within a date range.
- `copy_ticks_from_pos(symbol, start_pos, count)`: Get ticks from a specific position.
- `copy_ticks_from_date(symbol, date_from, count)`: Get ticks from a specific date.
- `copy_ticks_range(symbol, date_from, date_to)`: Get ticks within a date range.

### Trading Functions

- `order_send(request)`: Send an order to the trade server.
- `order_check(request)`: Check if an order can be placed with the specified parameters.
- `positions_get(symbol, group)`: Get open positions.
- `positions_get_by_ticket(ticket)`: Get an open position by its ticket.
- `orders_get(symbol, group)`: Get active orders.
- `orders_get_by_ticket(ticket)`: Get an active order by its ticket.
- `history_orders_get(symbol, group, ticket, position, from_date, to_date)`: Get orders from history.
- `history_deals_get(symbol, group, ticket, position, from_date, to_date)`: Get deals from history.

### Account Functions

- `fetch_account_info()`: Get full account details.
- `fetch_account_balance()`: Get current account balance.
- `fetch_account_equity()`: Get current account equity.
- `fetch_account_currency()`: Get account deposit currency.
- `fetch_account_leverage()`: Get account leverage.
- `fetch_account_type()`: Get account type (real/demo/contest).
- `fetch_trade_stats()`: Get a summary of trading statistics.
- `fetch_margin_level()`: Get margin level percentage.
- `fetch_free_margin()`: Get free margin.
- `fetch_account_used_margin()`: Get used margin.

### Order/Position Management

- `send_market_order()`: Place a market order (buy/sell).
- `send_pending_order()`: Place a pending order (limit/stop/stop-limit).
- `close_position_by_id()`: Close a position by ticket.
- `close_all_positions()`: Close all open positions.
- `close_all_positions_by_symbol(symbol)`: Close all positions for a symbol.
- `close_all_profitable_positions()`: Close all profitable positions.
- `close_all_losing_positions()`: Close all losing positions.
- `cancel_order()`: Cancel a pending order by ticket.
- `cancel_all_pending_orders()`: Cancel all pending orders.
- `cancel_pending_order_by_symbol(symbol)`: Cancel all pending orders for a symbol.
- `update_sltp()`: Update stop-loss/take-profit for a position.
- `modify_position()`: Modify an open position.
- `modify_pending_order()`: Modify a pending order.
- `modify_order()`: Modify an order.

### Calculations

- `calculate_profit()`: Calculate profit for a trade.
- `calculate_price_targets()`: Estimate exit price or stop-loss for a desired profit/loss.
- `calculate_margin()`: Calculate margin required for a trade.
- `calculate_lot_size()`: Calculate lot size based on risk and stop-loss.

### Connection/Terminal Functions

- `initialize()`: Initialize the MetaTrader 5 terminal.
- `login()`: Log in to the MetaTrader 5 terminal.
- `shutdown()`: Shut down the MetaTrader 5 terminal.
- `fetch_terminal_info()`: Get terminal information.
- `check_trading_status()`: Check if trading is allowed.
- `check_connection_status()`: Check if the terminal is connected.

## Disclaimer

This project is for educational and research purposes only. Trading financial instruments such as forex, stocks, or cryptocurrencies involves significant risk and may not be suitable for all investors. The authors and contributors of this project are not responsible for any financial losses or damages incurred as a result of using this software. Always test thoroughly with demo accounts before trading with real money, and consult with a qualified financial advisor if you are unsure. Use at your own risk.

## License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.