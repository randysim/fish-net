from core import ConfigLoader
from io import BytesIO
from threading import Thread, Event
import discord
import asyncio

class DiscordAPI:
    def __init__(self, event_handler):
        self.config = ConfigLoader().config['discord']
        self.intents = discord.Intents.default()
        self.intents.message_content = True

        self.client = discord.Client(intents=self.intents)
        self.loop = asyncio.new_event_loop()

        self.thread = Thread(target=self._start_background_loop, daemon=True)
        self.thread.start()
        self.ready_event = Event()

        # Register event handlers
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

        # FISHING CLIENT COPMMANDS
        self.event_handler = event_handler

    # API
    def log_action(self, action, img=None):
        asyncio.run_coroutine_threadsafe(self._log_action(action, img), self.loop)

    def log_error(self, error, img=None):
        asyncio.run_coroutine_threadsafe(self._log_error(error, img), self.loop)

    def log_fish(self, description, img=None):
        asyncio.run_coroutine_threadsafe(self._log_fish(description, img), self.loop)
    
    # COMMAND HANDLER
    async def on_message(self, message : discord.Message):
        if message.author.id != self.config["user_id"]:
            return
        msg_prefix, args = message.content[0], message.content[1:].split(" ")

        if msg_prefix != self.config["prefix"]:
            return

        command = args[0].lower()
        args = args[1:]

        if command == 'help':
            await message.channel.send(embed=self._create_help_embed())
            return
        
        print("[Command]", command, args)

        command_data = None
        for c_data in self.config['commands']:
            if c_data['name'] == command:
                command_data = c_data
        
        if not command_data:
            await message.channel.send(content="Invalid Command.") 

        if command_data['args'] and command_data['args'][0].startswith("..."):
            self.event_handler.emit(command, message=message.content)
        else:
            self.event_handler.emit(command, *args, message=message.content)

    # ASYNC
    def _start_background_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.client.start(self.config['token']))
    
    def _create_help_embed(self):
        embed = self._generate_default_embed()
        help_str = ""

        for command in self.config["commands"]:
            help_str += f"**{self.config['prefix']}{command['name']}**"

            if command['args']:
                help_str += " "
                for arg in command['args']:
                    help_str += f"``{arg}``" + " "
            
            help_str += "\n"
            help_str += command['description']
            help_str += "\n\n"
        
        embed.description = help_str
        return embed

    async def on_ready(self):
        print(f"Logged in as {self.client.user} (ID: {self.client.user.id})")
        await self._log_action(f"{self.client.user} has connected to Discord!")
        self.ready_event.set()

    async def _log_action(self, action, img=None):
        await self.client.wait_until_ready()

        channel = self.client.get_channel(self.config["channel_ids"]["action"])

        embed = self._generate_default_embed()
        embed.description = action

        if img:
            embed.set_image(url="attachment://image.png")
            await channel.send(
                file=self._convert_img_to_file(img),
                embed=embed
            )
        else:
            await channel.send(embed=embed)
    
    async def _log_error(self, error, img=None):
        await self.client.wait_until_ready()

        channel = self.client.get_channel(self.config["channel_ids"]["error"])

        embed = self._generate_default_embed()
        embed.title = "Error"
        embed.description = error
        embed.color = discord.Color.from_rgb(*self.config["error_color"])

        if img:
            embed.set_image(url="attachment://image.png")
            await channel.send(
                file=self._convert_img_to_file(img),
                embed=embed
            )
        else:
            await channel.send(embed=embed)
    
    async def _log_fish(self, description, img):
        await self.client.wait_until_ready()
        
        channel = self.client.get_channel(self.config["channel_ids"]["fishing"])

        embed = self._generate_default_embed()
        embed.title = "Item Caught!"
        embed.description = description
        embed.set_image(url="attachment://image.png")

        if img:
            embed.set_image(url="attachment://image.png")
            await channel.send(
                file=self._convert_img_to_file(img),
                embed=embed
            )
        else:
            await channel.send(embed=embed)
    
    def _convert_img_to_file(self, img):
        byte_array = BytesIO()
        img.save(byte_array, format='PNG')
        byte_array.seek(0)
        return discord.File(byte_array, filename="image.png")
    
    def _generate_default_embed(self):
        embed = discord.Embed(color=discord.Color.from_rgb(*self.config["color"]))
        embed.set_author(
            name=self.config['player_username'],
            icon_url=self.client.user.avatar.url
        )

        return embed
