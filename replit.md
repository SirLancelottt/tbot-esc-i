# Telegram Scheduler Bot

A Telegram bot that sends scheduled messages to a Telegram channel.

## Overview

This bot runs as a background worker and sends scheduled messages to a configured Telegram channel at specified times (Turkey timezone).

## Project Structure

- `telegram_bot.py` - Main bot script with scheduler
- `requirements.txt` - Python dependencies

## Required Environment Variables

The bot requires these secrets to be configured:

- `TELEGRAM_TOKEN` - Bot token from BotFather
- `TELEGRAM_CHANNEL` - Channel ID (e.g., @channelname or -100...)

## Default Schedule (Turkey Time)

- 09:00 - Morning greeting
- 12:00 - Lunch break message
- 18:00 - Evening greeting
- 21:00 - Evening news summary

## Customization

Edit the `my_schedules` dictionary in `telegram_bot.py` to change scheduled messages and times.

## Deployment

This bot should be deployed as a "VM" type deployment (always running background worker).
