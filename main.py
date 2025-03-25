#!/usr/bin/env python3
"""
Main entry point for BookClubBot
"""
import os
from bot import BookClubBot

def main():
    """Main function to start the bot"""
    bot = BookClubBot()
    bot.run(bot.config.TOKEN)

if __name__ == "__main__":
    main()