import asyncio

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
import os
import textwrap
from colorama import Fore, Style, init

import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

init(autoreset=True)

def format_response(response):
    """Wrap assistant response neatly for display."""
    return "\n".join(textwrap.wrap(response, width=80))

async def run_memory_chat():
    """Run a chat using MCPAgent's built-in conversation memory."""

    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

    config_file = "src/config.json"

    print(f"{Fore.YELLOW}Initializing MCP Chat Agent...")

    client = MCPClient.from_config_file(config_file)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    system_prompt = """
    You are an intelligent assistant connected to a set of Python functions and APIs.
    Your job is to help the user by interpreting their commands, searching for the most relevant function to fulfill their request, calling that function with the appropriate arguments, and then displaying all results from the action in a clear and user-friendly way.

    Instructions:
    - When the user gives a command or asks a question, analyze their intent and determine which available function is most relevant.
    - If the command requires arguments (such as a symbol or date), extract them from the user's input or ask the user for clarification if needed.
    - Call the selected function with the correct arguments.
    - Display the results of the function call to the user in a clear, concise, and readable format.
    - If the command is ambiguous or you are unsure which function to use, ask the user for clarification.
    - If the user asks for help, provide a list of available commands and their descriptions.
    - If you cannot find the information directly, do not immediately ask the user. First, try to figure out if there is a function you can call to get that information.
    - Always prioritize accuracy and helpfulness in your responses.
    - After performing any action (such as placing an order), always verify the result by checking for confirmation (e.g., by querying open positions, order status, or receiving a success response). Only inform the user that the action was successful if you have received clear confirmation. If confirmation is not received, inform the user that the action may not have completed and provide any available details or troubleshooting steps.

    Example:
    - User: "Get my account balance"
    - Assistant: (Calls the function to fetch account balance and displays the result)

    - User: "Place a buy order for 0.1 lots on XAUUSD with a stop loss of 3200 and take profit of 3300"
    - Assistant: (Calls the function to place a buy order for 0.1 lots on XAUUSD with a stop loss of 3200 and take profit of 3300 and displays the result)
    """

    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True, 
        system_prompt=system_prompt
    )

    print(f"""
    {Fore.CYAN}
    ==============================================
        🤖  TradePilot MCP Trading Assistant
    ==============================================
    {Style.RESET_ALL}
    Type your questions or commands below.
    - Type '{Fore.GREEN}exit{Style.RESET_ALL}' to quit.
    - Type '{Fore.GREEN}clear{Style.RESET_ALL}' to clear conversation history.
    - Type '{Fore.GREEN}help{Style.RESET_ALL}' to see available commands.
    """)
    try:
        while True:
            user_input = input(f"{Fore.BLUE}You: {Style.RESET_ALL}")

            if user_input.lower() in ["exit", "quit"]:
                print(f"{Fore.YELLOW}Exiting... See you next time!")
                break

            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print(f"{Fore.GREEN}Conversation history cleared.")
                continue
            
            if user_input.strip().lower() == "help":
                print(f"""
                {Fore.YELLOW}Available Commands:
                - {Fore.GREEN}exit{Fore.RESET}: End the chat session
                - {Fore.GREEN}clear{Fore.RESET}: Clear chat memory
                - {Fore.GREEN}help{Fore.RESET}: Show this help menu
                - Ask anything related to trading, MetaTrader 5, orders, etc.
                """)
                continue

            print(f"{Fore.MAGENTA}\nAssistant: ", end="", flush=True)

            try:
                response = await agent.run(user_input)
                print(response)

            except Exception as e:
                print(f"{Fore.RED}\n[ERROR] {e}")

    finally:
        if client and client.sessions:
            await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(run_memory_chat())