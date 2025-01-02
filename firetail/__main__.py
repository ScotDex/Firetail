"""Firetail - An EVE Online Discord Bot"""

import argparse
import asyncio
import sys
import discord
from firetail.core import bot, events
from firetail.utils import ExitCodes, logger


if discord.version_info.major < 1:
    print(
        "You are not running discord.py v1.0.0a or above.\n\n"
        "Firetail requires the new discord.py library to function correctly. "
        "Please install the correct version."
    )
    sys.exit(1)


async def run_firetail(debug=None, launcher=None):
    firetail = bot.Firetail(debug=debug)
    events.init_events(firetail, launcher=launcher)
    firetail.logger = logger.init_logger(debug_flag=debug)

    if firetail.token is None or not firetail.default_prefix:
        firetail.logger.critical("Token and prefix must be set in order to login.")
        sys.exit(1)

    try:
        await firetail.start(firetail.token)
    except discord.PrivilegedIntentsRequired as e:
        firetail.logger.critical(
            f"Privileged intents required but not enabled. "
            f"Visit https://discord.com/developers/applications/ to enable them.\nDetails: {e}"
        )
        sys.exit(1)
    except discord.LoginFailure:
        firetail.logger.critical("Invalid token")
        await firetail.logout()
        firetail._shutdown_mode = ExitCodes.SHUTDOWN
    except KeyboardInterrupt:
        firetail.logger.info("Keyboard interrupt detected. Quitting...")
        await firetail.logout()
        firetail._shutdown_mode = ExitCodes.SHUTDOWN
    except Exception as e:
        firetail.logger.critical("Fatal exception", exc_info=e)
        await firetail.logout()
    finally:
        code = firetail._shutdown_mode
        sys.exit(code.value)


def parse_cli_args():
    parser = argparse.ArgumentParser(description="firetail - An EVE Online Discord Bot")
    parser.add_argument("--debug", "-d", help="Enable debug mode.", action="store_true")
    parser.add_argument("--launcher", "-l", help=argparse.SUPPRESS, action="store_true")
    return parser.parse_args()


def main():
    args = parse_cli_args()
    asyncio.run(run_firetail(debug=args.debug, launcher=args.launcher))  # Use asyncio.run to handle the coroutine

if __name__ == "__main__":
    main()
