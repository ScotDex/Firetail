import os
import sys
import aiohttp
import asyncio
from aiohttp import ClientSession
from collections import Counter
from datetime import datetime
from shutil import copyfile
import discord
from dateutil.relativedelta import relativedelta
from discord.ext import commands

from firetail.lib import ESI, db
from firetail.utils import ExitCodes

# Ensure the config file exists
if os.getenv("CONFIG") is not None:
    if not os.path.exists(os.getenv("CONFIG") + "/config.py"):
        print("Copying example_config.py to " + os.getenv("CONFIG") + "/config.py")
        copyfile("/firetail/firetail/example_config.py", "/config/config.py")
        sys.exit(1)

if os.getenv("CONFIG") is not None:
    sys.path.insert(0, os.getenv("CONFIG"))
    import config
else:
    from firetail import config


async def prefix_manager(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(bot.default_prefix)(bot, message)
    prefix = bot.prefixes.get(message.guild.id) or bot.default_prefix
    return commands.when_mentioned_or(prefix)(bot, message)


class Firetail(commands.Bot):
    def __init__(self, **kwargs):
        self.default_prefix = config.bot_prefix
        self.owner = config.bot_master
        self._shutdown_mode = ExitCodes.CRITICAL
        self.counter = Counter()
        self.core_dir = os.path.dirname(os.path.realpath(__file__))
        self.config = config
        self.default_prefix = config.bot_prefix[0]
        self.prefixes = {}
        self.bot_users = []
        self.repeat_offender = []
        self.last_command = None
        self.token = config.bot_token
        self.req_perms = discord.Permissions(config.bot_permissions)
        self.co_owners = config.bot_coowners
        self.preload_ext = config.preload_extensions

        kwargs["command_prefix"] = prefix_manager
        kwargs["pm_help"] = True
        kwargs["owner_id"] = self.owner
        kwargs["intents"] = discord.Intents.all()  # Full intents for all bot functionalities

        super().__init__(**kwargs)
        self.session = None  # To be initialized asynchronously
        self.esi_data = None
        self.debug = bool(kwargs["debug"])

    async def setup_hook(self):
        """Initialize asynchronous resources and setup the bot."""
        self.session = ClientSession()
        self.esi_data = ESI(self.session)
        await self.load_db()

    async def load_db(self):
        """Load database and prefixes."""
        await db.create_tables()
        data = await db.select("SELECT * FROM prefixes")
        self.prefixes = dict(data)

    async def shutdown(self, *, restart=False):
        """Shutdown the bot cleanly."""
        self._shutdown_mode = ExitCodes.RESTART if restart else ExitCodes.SHUTDOWN
        if self.session:
            await self.session.close()
        await self.logout()

    @discord.utils.cached_property
    def invite_url(self):
        """Generate the bot's invite URL."""
        return discord.utils.oauth_url(self.user.id, permissions=self.req_perms)

    @property
    def uptime(self):
        """Calculate the bot's uptime."""
        return relativedelta(datetime.utcnow(), self.launch_time)

    @property
    def uptime_str(self):
        """Format the uptime as a string."""
        uptime = self.uptime
        components = [
            f"{uptime.years}y" if uptime.years else "",
            f"{uptime.months}m" if uptime.months else "",
            f"{uptime.days}d" if uptime.days else "",
            f"{uptime.hours}h" if uptime.hours else "",
            f"{uptime.minutes}m" if uptime.minutes else "",
            f"{uptime.seconds}s" if not uptime.minutes else "",
        ]
        return " ".join(filter(None, components))

    @property
    def command_count(self):
        return self.counter["processed_commands"]

    @property
    def message_count(self):
        return self.counter["messages_read"]

    @property
    def resumed_count(self):
        return self.counter["sessions_resumed"]
