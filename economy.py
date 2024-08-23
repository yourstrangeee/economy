import discord
from discord.ext import commands
import json
import os
import datetime
import random
SHOP_ITEMS = {
    "items_name_1": {"price": 100, "description": "items_name_1 description"},
    "items_name_2": {"price": 500, "description": "items_name_2 description"},
    "items_name_3": {"price": 1000, "description": "items_name_3 description"}
    # etc.
    }
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = 'db/economy.json'
        self.load_data()

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.data = json.load(f)
                if not isinstance(self.data.get("users"), dict):
                    self.data["users"] = {}
        else:
            self.data = {"users": {}}

    def save_data(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)
    @commands.command(name="balance",aliases=["bal"],description="Check your current balance.")
    async def balance(self, ctx):
        user_id = str(ctx.author.id)

        if user_id not in self.data["users"]:
            await ctx.send("You need to register first. Use the `register` command.")
            return

        user_data = self.data["users"][user_id]
        coins = user_data.get("coins", 0) 


        await ctx.send(f"{ctx.author.name} you currently have __**{coins}**__ coins")

    @commands.command(name="register", description="Register a new account.")
    async def register(self, ctx):
        user_id = str(ctx.author.id)

        if user_id in self.data["users"]:
            await ctx.send("You already have an account.")
            return

        self.data["users"][user_id] = {
        "username": str(ctx.author),
        "registered_at": str(ctx.message.created_at),
        "last_claimed_daily": str(ctx.message.created_at),
        "last_claimed_weekly": str(ctx.message.created_at),
        "coins": 0
    }
        self.save_data()

        await ctx.send(f"Successfully registered {ctx.author.mention}!")

    @commands.command(name="spend", description="Spend your coins. Use 'all' to spend all your coins.")
    async def spend(self, ctx, option: str):
        user_id = str(ctx.author.id)
    
        if user_id not in self.data["users"]:
            await ctx.send("You need to register first. Use the `register` command.")
            return
    
        user_data = self.data["users"][user_id]
        coins = user_data.get("coins", 0)
    
        if option.lower() == "all":
            amount = coins
        else:
            try:
                amount = int(option)
                if amount <= 0:
                    await ctx.send("Please specify a positive number of coins.")
                    return
            except ValueError:
                await ctx.send("Please provide a valid number of coins or type 'all' to spend all your coins.")
                return
    
        if amount > coins:
            await ctx.send("You don't have enough coins.")
            return

        emojis = ["🍒", "🍋", "🍊"]
        spin = [random.choice(emojis) for _ in range(3)]
    
        result = " | ".join(spin)
        embed = discord.Embed(
        title="Slot Machine",
        description=f"{result}",
        color=discord.Color.gold()
    )
    
        if spin[0] == spin[1] == spin[2]:
            win_amount = amount * 2
            user_data["coins"] += win_amount
            message = f"Congratulations {ctx.author.mention}! You hit the jackpot and doubled your money to **{user_data['coins']}** coins!"
        else:
            user_data["coins"] -= amount
            message = f"Sorry {ctx.author.mention}, you lost. You now have **{user_data['coins']}** coins."
    
        self.save_data()
        embed.add_field(name="Result", value=message)
        await ctx.send(embed=embed)
    @commands.command(name="removecoins", description="Remove a specified amount of coins from your balance.")
    async def removecoins(self, ctx, member: discord.Member, amount: int):
        if ctx.author.id not in [1129092454495289374]:
            return
        user_id = str(member.id)

        if user_id not in self.data["users"]:
            await ctx.send(f"{member.mention} does not have an account. Please have them register first using `register`.")
            return

        user_data = self.data["users"][user_id]

        if amount <= 0:
            await ctx.send("Please specify a positive number of coins to remove.")
            return

        if amount > user_data["coins"]:
            await ctx.send(f"{member.mention} does not have enough coins to remove that amount.")
            return

        user_data["coins"] -= amount
        self.save_data()

        await ctx.send(f"Successfully removed {amount} coins from {member.mention}'s account.")

    @commands.command(name="addcoins", description="Add coins to a user's account.")
    async def addcoins(self, ctx, member: discord.Member, amount: int):
        if ctx.author.id not in [1129092454495289374]:
            return
        if amount <= 0:
            await ctx.send("Please specify a positive number of coins to add.")
            return
    
        user_id = str(member.id)
    
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {"coins": 0, "last_claimed_daily": "", "last_claimed_weekly": ""}
    
        self.data["users"][user_id]["coins"] += amount
        self.save_data()

        await ctx.send(f"Successfully added {amount} coins to {member.mention}'s account.")


    @commands.command(name="daily", description="Claim daily reward.")
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        today_str = datetime.datetime.utcnow().strftime('%Y-%m-%d')

        if user_id not in self.data["users"]:
            await ctx.send("You need to register first. Use the `!register` command.")
            return

        user_data = self.data["users"][user_id]

        if user_data["last_claimed_daily"] == today_str:
            await ctx.send("You have already claimed your daily reward today.")
            return

        user_data["last_claimed_daily"] = today_str
        user_data["coins"] += 50 # adjust according to your choice
        self.save_data()

        await ctx.send(f"You have claimed your daily reward of 100 coins, {ctx.author.mention}!")
    @commands.command(name="weekly", description="Claim weekly reward.")
    async def weekly(self, ctx):
        user_id = str(ctx.author.id)
        current_week = datetime.datetime.utcnow().strftime('%Y-W%U')

        if user_id not in self.data["users"]:
            await ctx.send("You need to register first. Use the `register` command.")
            return

        user_data = self.data["users"][user_id]

        if user_data.get("last_claimed_weekly") == current_week:
            await ctx.send("You have already claimed your weekly reward this week.")
            return

        user_data["last_claimed_weekly"] = current_week
        user_data["coins"] += 100 # adjust according to your choice
        self.save_data()

        await ctx.send(f"You have claimed your weekly reward of 500 coins, {ctx.author.mention}!")

    @commands.command(name="shop", description="View the shop and buy items.")
    async def shop(self, ctx):
        embed = discord.Embed(
        title="Shop",
        description="Welcome to the shop! Here are the items you can buy:",
        color=discord.Color.gold()
    )

        for item, details in SHOP_ITEMS.items():
            embed.add_field(
            name=item.capitalize(),
            value=f"Price: {details['price']} coins\nDescription: {details['description']}",
            inline=False
        )
    
        embed.set_footer(text="Use buy <item> to purchase an item.")

        await ctx.send(embed=embed)

    @commands.command(name="buy", description="Buy an item from the shop.")
    async def buy(self, ctx, item_name: str):
        user_id = str(ctx.author.id)

        if user_id not in self.data["users"]:
            await ctx.send("You need to register first. Use the `register` command.")
            return

        user_data = self.data["users"][user_id]

        item_name = item_name.lower()

        if item_name not in SHOP_ITEMS:
            await ctx.send("That item does not exist in the shop.")
            return

        item_price = SHOP_ITEMS[item_name]["price"]

        if user_data["coins"] < item_price:
            await ctx.send("You do not have enough coins to purchase this item.")
            return

        user_data["coins"] -= item_price
        if "inventory" not in user_data:
            user_data["inventory"] = []

        user_data["inventory"].append(item_name)
        self.save_data()

        await ctx.send(f"You have successfully purchased {item_name.capitalize()} for {item_price} coins!")
    @commands.command(name="inventory", description="Show your inventory of items.")
    async def inventory(self, ctx):
        user_id = str(ctx.author.id)

        if user_id not in self.data["users"]:
            await ctx.send("You need to register first. Use the `register` command.")
            return

        user_data = self.data["users"][user_id]

        inventory = user_data.get("inventory", [])

        if not inventory:
            await ctx.send("Your inventory is empty. Buy some items from the shop!")
            return

        embed = discord.Embed(
        title=f"{ctx.author.display_name}'s Inventory",
        description="Here are the items you currently have:",
        color=discord.Color.gold()
    )

        for item in inventory:
            item_description = SHOP_ITEMS.get(item, {}).get("description", "No description available.")
            embed.add_field(
            name=item.capitalize(),
            value=item_description,
            inline=False
        )

        embed.set_footer(text="Use shop to view available items.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))
