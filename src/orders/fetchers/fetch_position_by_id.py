from orders.fetchers.fetch_positions import fetch_positions
from utils.mcp_client import mcp
from utils.logger import logger
from typing import Dict, Any

@mcp.tool()
def fetch_position_by_id(position_id: int) -> Dict[str, Any]:
    """
    Fetch a single open position from MT5 by its ticket ID.

    This tool wraps the lower‑level `fetch_positions` call, filtering
    on a specific position ticket. It ensures a consistent response
    schema and logs successes, failures, and unexpected errors.

    Parameters:
        position_id (int):
            The MT5 ticket ID of the open position to retrieve.

    Returns:
        Dict[str, Any]:
            - status (str):
                "success" if the position was retrieved; otherwise "error".
            - message (str):
                Human‑readable description of the outcome.
            - data (dict):
                - positions (List[Dict[str, Any]]):
                    A list containing the matching position record,
                    or an empty list if none.
    """
    logger.info(f"Getting position with ID: {position_id}")

    if not isinstance(position_id, int) or position_id < 0:
        logger.error(f"Invalid position_id provided: {position_id!r}")
        return {
            "status": "error",
            "message": f"Invalid position_id: {position_id!r}",
            "data": {"positions": []}
        }

    if len(str(position_id)) != 9:
        logger.error(f"Invalid position_id provided: {position_id!r}")
        return {
            "status": "error",
            "message": f"Invalid position_id: {position_id!r}",
            "data": {"positions": []}
        }
    
    try:
        response = fetch_positions(ticket=position_id)
        status = response.get("status")
        message = response.get("message", "")
        positions = response.get("data", {}).get("positions", [])

        if status != "success":
            logger.error(f"fetch_positions() failed for ticket={position_id}: {message}")
            return {
                "status": "error",
                "message": f"Failed to fetch position {position_id}: {message}",
                "data": {"positions": []}
            }

        if not positions:
            logger.info(f"No position found with ticket={position_id}")
            return {
                "status": "error",
                "message": f"No position found with ticket {position_id}",
                "data": {"positions": []}
            }

        logger.info(f"Successfully fetched position: {positions[0]}")
        
        return {
            "status": "success",
            "message": f"Position {position_id} fetched successfully",
            "data": {"positions": positions}
        }

    except Exception as exc:
        logger.error(f"Unexpected error in fetch_position_by_id()")
        return {
            "status": "error",
            "message": f"Unexpected error: {exc}",
            "data": {"positions": []}
        }