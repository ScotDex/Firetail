import logging
from discord.ext import commands

log = logging.getLogger(__name__)

class ExtensionManager(commands.Cog):
    """Manages extensions for the bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def load(self, ctx, extension: str):
        """Loads an extension."""
        try:
            await self.bot.load_extension(extension)
            await ctx.send(f"Loaded extension {extension}")
        except Exception as e:
            await ctx.send(f"Failed to load extension {extension}: {e}")
            log.exception(f"Failed to load extension {extension}")

    @commands.command()
    async def unload(self, ctx, extension: str):
        """Unloads an extension."""
        try:
            await self.bot.unload_extension(extension)
            await ctx.send(f"Unloaded extension {extension}")
        except Exception as e:
            await ctx.send(f"Failed to unload extension {extension}: {e}")
            log.exception(f"Failed to unload extension {extension}")

    @commands.command()
    async def reload(self, ctx, extension: str):
        """Reloads an extension."""
        try:
            await self.bot.unload_extension(extension)
            await self.bot.load_extension(extension)
            await ctx.send(f"Reloaded extension {extension}")
        except Exception as e:
            await ctx.send(f"Failed to reload extension {extension}: {e}")
            log.exception(f"Failed to reload extension {extension}")


async def setup(bot):
    """Setup function for the ExtensionManager cog."""
    await bot.add_cog(ExtensionManager(bot))
