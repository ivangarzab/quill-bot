"""
Session-related commands (book, duedate, session, discussions)
"""
import discord
from discord import app_commands

from utils.embeds import create_embed

def setup_session_commands(bot):
    """
    Setup session-related commands for the bot
    
    Args:
        bot: The bot instance
    """
    @bot.tree.command(name="book", description="Show current book details")
    async def book_command(interaction: discord.Interaction):
        embed = create_embed(
            title="📚 Current Book",
            description=f"**{bot.club['activeSession']['book']['title']}**",
            color_key="info",
            fields=[
                {"name": "Author", "value": f"{bot.club['activeSession']['book']['author']}"}
            ],
            footer="Happy reading! 📖"
        )
        await interaction.response.send_message(embed=embed)
        print("Sent book command response.")

    @bot.tree.command(name="duedate", description="Show the session's due date")
    async def duedate_command(interaction: discord.Interaction):
        embed = create_embed(
            title="📅 Due Date",
            description=f"Session due date: **{bot.club['activeSession']['dueDate']}**",
            color_key="warning"
        )
        await interaction.response.send_message(embed=embed)
        print("Sent duedate command response.")

    @bot.tree.command(name="session", description="Show current session details")
    async def session_command(interaction: discord.Interaction):
        embed = create_embed(
            title="📚 Current Session Details",
            color_key="info",
            fields=[
                {
                    "name": "Book",
                    "value": f"{bot.club['activeSession']['book']['title']}",
                    "inline": True
                },
                {
                    "name": "Author",
                    "value": f"{bot.club['activeSession']['book']['author']}",
                    "inline": True
                },
                {
                    "name": "Due Date",
                    "value": f"{bot.club['activeSession']['dueDate']}",
                    "inline": False
                }
            ],
            footer="Keep reading! 📖"
        )
        await interaction.response.send_message(embed=embed)
        print("Sent session command response.")

    @bot.tree.command(name="discussions", description="Show the session's discussion details")
    async def discussions_command(interaction: discord.Interaction):
        embed = create_embed(
            title="📚 Book Discussion Details",
            color_key="info",
            fields=[
                {
                    "name": "Number of Discussions",
                    "value": f"#{len(bot.club['activeSession']['discussions'])}",
                    "inline": False
                },
                {
                    "name": "Next discussion",
                    "value": f"{bot.club['activeSession']['discussions'][0]['date']}",
                    "inline": False
                }
            ],
            footer="Don't stop reading! 📖"
        )
        await interaction.response.send_message(embed=embed)
        print("Sent discussions command response.")
    
    @bot.tree.command(name="book_summary", description="Let me provide a summary of the active book")
    async def booksummary_command(interaction: discord.Interaction):
        """Ask OpenAI for a summary of the active book."""
        response = await bot.openai_service.get_response(
            f"What is {bot.club['activeSession']['book']['title']} about?"
        )
        embed = create_embed(
            title="🤖 Book Summary",
            description=response,
            color_key="info"
        )
        await interaction.response.send_message(embed=embed)
        print("Sent book summary command response.")