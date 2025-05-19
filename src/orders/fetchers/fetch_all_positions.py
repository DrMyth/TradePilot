from orders.fetchers.fetch_positions import fetch_positions
from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any

@mcp.tool()
def fetch_all_positions() -> Dict[str, Any]:
    """
    Fetch all currently open positions from MT5.

    This tool wraps the lower‐level `fetch_positions` call, handling
    error conditions and ensuring a consistent return schema.

    Returns:
        Dict[str, Any]:
            - status (str):
                "success" if positions were retrieved; otherwise "error".
            - message (str):
                Human‐readable description of the outcome.
            - data (dict):
                - positions (List[Dict[str, Any]]):
                    The list of position records, or an empty list if none.
    """
    logger.info("Fetching all positions")

    try:
        response = fetch_positions()
        status = response.get("status")
        message = response.get("message", "")
        positions = response.get("data", {}).get("positions", [])

        if status != "success":
            logger.error(f"fetch_positions() failed: {message}")
            return {
                "status": "error",
                "message": f"Failed to fetch positions: {message}",
                "data": {"positions": []}
            }

        count = len(positions)
        logger.info(f"Fetched {count} position{'s' if count != 1 else ''}.")
        
        return {
            "status": "success",
            "message": "All positions fetched successfully",
            "data": {"positions": positions}
        }

    except Exception as exc:
        logger.error("Unexpected error in fetch_all_positions()")
        return {
            "status": "error",
            "message": f"Unexpected error: {exc}",
            "data": {"positions": []}
        }