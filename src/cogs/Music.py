import discord
from discord.ext import commands
import wavelink
from wavelink.ext import spotify
import asyncio


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.voice_client: discord.VoiceClient = None
        self.spotify_client = spotify.SpotifyClient(
            client_id="0b595b3e9519444193f4c225df6a2462",
            client_secret="4036883f133f4f109b647d5ec9af1d70",
        )
        self.message_channel: discord.abc.Messageable = None
        self.autoplay = True

    async def connect_voice_client(self, ctx: commands.Context):
        if ctx.author.voice == None:
            await ctx.reply("a ver y donde te lo pincho bro", ephemeral=True)
            return
        if not ctx.voice_client:
            self.voice_client: wavelink.Player = await ctx.author.voice.channel.connect(
                cls=wavelink.Player
            )
        else:
            self.voice_client: wavelink.Player = ctx.voice_client

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        """Simple play command."""
        await self.connect_voice_client(ctx)
        self.message_channel = ctx.channel

        tracks: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.reply(
                f"Sorry I could not find any songs with search: `{search}`",
                ephemeral=True,
            )
            return

        track: wavelink.YouTubeTrack = tracks[0]
        if not self.voice_client.is_playing():
            await self.voice_client.play(track)
        else:
            await self.voice_client.queue.put_wait(track)

    @commands.command()
    async def spotify(self, ctx: commands.Context, *, search: str):
        await self.connect_voice_client(ctx)
        decoded = spotify.decode_url(search)
        if not decoded or decoded["type"] is not spotify.SpotifySearchType.track:
            await ctx.reply("esto no es de spotify bro", ephemeral=True)
            return
        tracks: list[spotify.SpotifyTrack] = await self.spotify_client._search(search)
        if not tracks:
            await ctx.reply("url rara", ephemeral=True)
            return
        track: spotify.SpotifyTrack = tracks[0]

        if not self.voice_client.is_playing():
            await self.voice_client.play(track)
        else:
            await self.voice_client.queue.put_wait(track)

    @commands.command()
    async def disconnect(self, ctx: commands.Context) -> None:
        """Simple disconnect command.
        This command assumes there is a currently connected Player.
        """
        vc: wavelink.Player = ctx.voice_client
        await vc.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if (
            self.voice_client != None
            and self.voice_client.channel != None
            and len(self.voice_client.channel.members) == 1
        ):
            await self.voice_client.disconnect()

    @commands.command()
    async def autoplay(self, ctx: commands.Context, *, search: str) -> None:
        """Simple play command."""
        await self.connect_voice_client(ctx)
        self.message_channel = ctx.channel

        tracks: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.reply(
                f"Sorry I could not find any songs with search: `{search}`",
                ephemeral=True,
            )
            return

        track: wavelink.YouTubeTrack = tracks[0]
        if not self.voice_client.is_playing():
            await self.voice_client.play(track, populate=True)
        else:
            await self.voice_client.queue.put_wait(track)
        await asyncio.sleep(10)
        print(list(self.voice_client.auto_queue))
        await ctx.send(list(self.voice_client.auto_queue))