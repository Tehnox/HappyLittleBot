import os
import re
import glob
import logging
import discord
from discord.ext import commands, tasks
from discord.channel import DMChannel
from datetime import time, date, datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True


class HappyLittleBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or('/'),
            intents=intents,
            help_command=None,
            activity=discord.Game('С праздником, дорогие друзья!')
        )

        self._logger = logging.getLogger('happy_little_bot')
        self._default_channel_names = ['chat', 'чат', 'general', 'основной']
        self._re = '(?=.*?(?:какой|что|че|чо))(?=.*?(?:сегодня|седня|сейчас|щас))(?=.*?(?:день|праздник|денек|денечек)).+'
        self.active_channels = {}
        self.channels_cd = {}
        self.img_files = sorted(glob.glob(os.path.join(os.getcwd(), 'days_img', '*.png')),
                                reverse=True, key=lambda x: int(os.path.basename(x)[:-4]))
        self.img_files.reverse()

    @tasks.loop(time=time(21, 30))
    async def celebration_task(self) -> None:
        day = date.today().timetuple().tm_yday
        for guild in self.guilds:
            for channel in guild.channels:
                if channel.name.lower() in self._default_channel_names:
                    await self.send_clb_img(channel, day)
                    self._logger.info(f'Celebrating with {guild.name} in {channel.name}')
                    break
            else:  # default channel not found
                channel = self.active_channels.get(guild.id)
                if channel:
                    await self.send_clb_img(channel, day)
                    self._logger.info(f'Celebrating with {guild.name} in {channel.name}')

    @celebration_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return

        if message.guild and message.guild.id:
            self.active_channels[message.guild.id] = message.channel.id

        ctx = await self.get_context(message)
        if not ctx.valid:
            match = re.match(self._re, message.content.lower())
            last_usage = self.channels_cd.get(message.channel.id)
            if not last_usage:
                last_usage = datetime(1970, 1, 1, 1)

            is_not_on_cd = (datetime.now() - last_usage) > timedelta(hours=3)
            if match and is_not_on_cd:
                day = date.today().timetuple().tm_yday
                await self.send_clb_img(message.channel, day)
                self.channels_cd[message.channel.id] = datetime.now()
                if isinstance(message.channel, DMChannel):
                    log_msg = f'Celebrating with {message.author.name} in DMs'
                else:
                    log_msg = f'Celebrating with {message.guild.name} in {message.channel.name} in response to {message.author.name}'
                self._logger.info(log_msg)
                return

        await self.process_commands(message)

    async def setup_hook(self) -> None:
        self._logger.info(f"Logged in as {self.user.name}")
        self._logger.info(f"discord.py API version: {discord.__version__}")
        self.celebration_task.start()

    async def send_clb_img(self, channel: discord.TextChannel, index: int) -> None:
        fp = self.img_files[index % len(self.img_files)]
        file_attachment = discord.File(fp=fp, filename='the_day.png')
        await channel.send(file=file_attachment)
