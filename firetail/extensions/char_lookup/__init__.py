from discord.ext import commands

class Dev(commands.Cog):
    """Development Tools Cog for Firetail."""

    def __init__(self, bot):
        self.bot = bot

    # Add commands and methods for Dev here

async def setup(bot):
    """Setup function for the Dev cog."""
    await bot.add_cog(Dev(bot))
