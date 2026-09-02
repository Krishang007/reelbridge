import discord
import config

intents = discord.Intents.default()
client = discord.Client(intents=intents)



@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    print(f"Sending DM to user ID: {config.USER_ID}")

    user = await client.fetch_user(config.USER_ID)
    print(f"Found user: {user}")

    await user.send(
        file=discord.File("downloads/test.mp4")
    )

    print("Video sent successfully")
client.run(config.DISCORD_TOKEN)