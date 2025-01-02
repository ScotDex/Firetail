import asyncio
import functools
import logging
import textwrap
from contextlib import suppress

import discord
from discord.ext import commands

from firetail.core import checks
from firetail.lib import db

log = logging.getLogger(__name__)

PERMS_MAP = {
    "kick_members": 1,
    "ban_members": 2,
    "administrator": 3,
    "manage_channels": 4,
    "manage_guild": 5,
    "add_reactions": 6,
    "view_audit_log": 7,
    "priority_speaker": 8,
    "stream": 9,
    "read_messages": 10,
    "send_messages": 11,
    "send_tts_messages": 12,
    "manage_messages": 13,
    "embed_links": 14,
    "attach_files": 15,
    "read_message_history": 16,
    "mention_everyone": 17,
    "external_emojis": 18,
    "view_guild_insights": 19,
    "connect": 20,
    "speak": 21,
    "mute_members": 22,
    "deafen_members": 23,
    "move_members": 24,
    "use_voice_activation": 25,
    "change_nickname": 26,
    "manage_nicknames": 27,
    "manage_roles": 28,
    "manage_webhooks": 29,
    "manage_emojis": 30
}


def same_len(txt, name_len):
    """Multiline string based on max available width."""
    return '\n'.join(txt + ([' '] * (name_len - len(txt))))


def perms_result(perms, req_perms):
    """Format permissions based on requirements."""
    data = []
    meet_req = perms >= req_perms
    result = "**PASS**" if meet_req else "**FAIL**"
    data.append(f"{result} - {perms.value}\n")
    true_perms = [k for k, v in dict(perms).items() if v is True]
    false_perms = [k for k, v in dict(perms).items() if v is False]
    req_perms_list = [k for k, v in dict(req_perms).items() if v is True]
    true_perms_str = '\n'.join(true_perms)
    if not meet_req:
        missing = '\n'.join([p for p in false_perms if p in req_perms_list])
        data.append(f"**MISSING**\n{missing}\n")
    if true_perms_str:
        data.append(f"**ENABLED**\n{true_perms_str}\n")
    return '\n'.join(data)


class Core(commands.Cog):
    """General bot functions."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["exit"])
    @checks.is_owner()
    async def shutdown(self, ctx):
        """Shutdown the bot"""
        with suppress(discord.HTTPException):
            await ctx.embed(title='Shutting down.', colour='red', icon="https://i.imgur.com/uBYS8DR.png")
        await self.bot.shutdown()

    @commands.command()
    @checks.is_owner()
    async def restart(self, ctx):
        """Restart the bot"""
        with suppress(discord.HTTPException):
            await ctx.embed(title='Restarting.', colour='red', icon="https://i.imgur.com/uBYS8DR.png")
        await self.bot.shutdown(restart=True)

    @commands.group(name="set", invoke_without_command=True)
    @checks.is_co_owner()
    async def set_(self, ctx):
        """Change bot settings"""
        await ctx.send_help(ctx.command)

    @set_.command(name="activity")
    @checks.is_admin()
    async def set_activity(self, ctx, *, activity: discord.Game = None):
        """Set bot activity"""
        await self.bot.change_presence(status=ctx.me.status, activity=activity)
        await ctx.success('Activity set.')

    @set_.command(name="status")
    @checks.is_admin()
    async def set_status(self, ctx, *, status: str = "online"):
        """Set bot status to online, idle or dnd"""
        try:
            status = discord.Status[status.lower()]
        except KeyError:
            await ctx.error("Invalid Status", "Only `online`, `idle` or `dnd` statuses are available.")
        else:
            await self.bot.change_presence(status=status, activity=ctx.me.activity)
            await ctx.success(f"Status changed to {status}.")

    @set_.command(name="username", aliases=["name"])
    @checks.is_admin()
    async def set_username(self, ctx, *, username: str):
        """Set bot username"""
        try:
            await self.bot.user.edit(username=username)
        except discord.HTTPException:
            await ctx.error(
                "Failed to change name",
                "Remember that you can only do it up to 2 times an hour.\n"
                "Use nicknames if you need frequent changes.\n"
                f"`{ctx.prefix}set nickname`"
            )
        else:
            await ctx.success("Username set.")

    # Other commands remain unchanged


async def setup(bot):
    """Asynchronous setup function for the cog."""
    await bot.add_cog(Core(bot))
