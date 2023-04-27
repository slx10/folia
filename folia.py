import interactions, json, os, time,sys
from interactions.ext.persistence import keygen,PersistentCustomID

if len(sys.argv) > 1 and sys.argv[1] == "--gen_ck":
    keygen()
    input("")

class Configuration:
    def __init__(self):
        self.config = json.load(open("config.config","r",encoding="utf-8"))
        
    def getConfig(self):
        return self.config

class Stock:
    def __init__(self,name:str,description=None,amount=None,price=None):
        self.name = name
        self.description = description
        self.amount = amount
        self.price = price
        self.file = config.getConfig()["stockPath"]+self.name.lower()+".json"

    @property
    def exist(self) -> bool:
        return os.path.isfile(self.file)

    def create(self) -> dict:
        if not self.exist:
            try:
                stockDict = {"name":self.name,"description":self.description,"amount":self.amount,"price":self.price}
                with open(self.file,"w") as f:
                    f.write(json.dumps(stockDict))
                return {"Message":"✔ Created","Status":True,"stock":stockDict}
            except Exception as e:
                return {"Message":f"❌ Error {e}","Status":False}
        return {"Message":"❌ Already Exist","Status":False}
    
    def display(self) -> dict:
        if self.exist:
            try:
                with open(self.file,"r",encoding="utf8") as f:
                    jsonF = json.load(f)
                    stockDict = {"name":jsonF["name"],"description":jsonF["description"],"amount":jsonF["amount"],"price":jsonF["price"]}
                    return {"Message":"🔎 Stock found","Name":self.name,"Status":True,"stock":stockDict}
            except Exception as e:
                return {"Message":f"❌ Error {e}","Status":False}
        return {"Message":"❌ Stock does not exist","Status":False}

    def remove(self) -> dict:
        if self.exist:
            try:
                with open(self.file,"r",encoding="utf8") as f:
                    jsonF = json.load(f)
                    stockDict = {"name":jsonF["name"],"description":jsonF["description"],"amount":jsonF["amount"],"price":jsonF["price"]}
                os.remove(self.file)
                return {"Message":"❌ Stock removed","Status":True,"stock":stockDict}
            except Exception as e:
                return {"Message":f"❌ Error {e}","Status":False}
        return {"Message":"❌ Stock does not exist","Status":False}

    def edit(self,name,description,amount,price) -> dict:
        if self.exist:
            try:
                with open(self.file,"w") as f:
                    stockDict = {"name":name,"description":description,"amount":amount,"price":price}
                    f.write(json.dumps(stockDict))
                os.rename(self.file,config.getConfig()["stockPath"]+name.lower()+".json")
                return {"Message":"✔ Edited","Status":True,"stock":stockDict}
            except Exception as e:
                return {"Message":f"❌ Error {e}","Status":False}
        return {"Message":"❌ Stock does not exist","Status":False}

config = Configuration()
bot = interactions.Client(token=config.getConfig()["token"])
bot.load("interactions.ext.persistence",cipher_key=config.getConfig()["cipher_key"])

@bot.command(
    name="help"
)
async def help(ctx,):
    help_embed = interactions.Embed(
        title="Help | 🍃",
        description="Avaliable commands\n```/stock create -> Allows you to create stocks\n/stock edit [stock name] -> Allows you to edit existing stocks\n/stock remove [stock name] -> Allows you to delete stocks\n/stock announce -> Allows you to create stock listings and automate the sales process\n/stock display [stock name] -> Allows you to view stock```",
        color = 5570422
    )
    await ctx.send(embeds=help_embed,ephemeral=True)

@bot.command(
    name="stock",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
)
async def stock(ctx):
    pass

@stock.subcommand(

)
async def create(ctx):
    stock = interactions.Modal(
        title="Stock",
        custom_id="stock_modal",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Stock name",
                custom_id="name",
                min_length=1,
                max_length=20,
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.PARAGRAPH,
                label="Stock description",
                placeholder="",
                custom_id="description",
                min_length=1,
                max_length=500,
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Stock amount",
                custom_id="amount",
                min_length=1,
                max_length=10,
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Stock price",
                custom_id="price",
                min_length=1,
                max_length=10,
            )
        ],
    )
    await ctx.popup(stock)

@bot.modal("stock_modal")
async def createStock(ctx,name:str,description:str,amount,price):
    if not amount.isdigit():
        await ctx.send("❌ The amount must be in numbers",ephemeral=True)
        return
    stock = Stock(name,description,int(amount),price)
    if stock.exist:
        await ctx.send(stock.create()["Message"],ephemeral=True)
        return
    status = stock.create()
    stockDict = status["stock"]
    create_embed = interactions.Embed(
        title="Stock Status | 📦",
        fields=[
            interactions.EmbedField(
                name="Status",
                value=status["Message"],
            ),
            interactions.EmbedField(
                name="Name",
                value=stockDict["name"]
            ),
            interactions.EmbedField(
                name="Command",
                value="If you want to edit something type /stock edit [stock name]"
            )
        ],
        color = 5570422
    )
    await ctx.send(embeds=create_embed,ephemeral=True)

@stock.subcommand(
    options=[
        interactions.Option(
            name="name",
            description="Stock name to be displayed",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def display(ctx,name):
    stock = Stock(name)
    if not stock.exist:
        await ctx.send("❌ No stock found",ephemeral=True)
        return
    stockDict = stock.display()["stock"]
    display_embed = interactions.Embed(
        title="Stock Status | 📦",
        fields=[
            interactions.EmbedField(
                name="Status",
                value=stock.display()["Message"],
            ),
            interactions.EmbedField(
                name="Stock name",
                value=stockDict["name"]
            ),
            interactions.EmbedField(
                name="Stock amount",
                value=stockDict["amount"]
            ),
            interactions.EmbedField(
                name="Stock price",
                value=stockDict["price"]
            )
        ],
        color = 5570422
    )
    await ctx.send(embeds=display_embed,ephemeral=True)

@stock.subcommand(
    options=[
        interactions.Option(
            name="name",
            description="Stock name to remove",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def remove(ctx,name):
    stock = Stock(name)
    remove = stock.remove()
    if not remove["Status"]:
        await ctx.send("❌ Stock not found, not removed",ephemeral=True)
        return
    stockDict = remove["stock"]
    removed_embed = interactions.Embed(
    title="Stock Status | 📦",
    fields=[
        interactions.EmbedField(
            name="Status",
            value=remove["Message"],
        ),
        interactions.EmbedField(
            name="Stock name",
            value=stockDict["name"]
        ),
        interactions.EmbedField(
            name="Stock amount",
            value=stockDict["amount"]
        ),
        interactions.EmbedField(
            name="Stock price",
            value=stockDict["price"]
        )
    ],
        color = 5570422
    )
    await ctx.send(embeds=removed_embed,ephemeral=True)

@stock.subcommand(
    options=[
        interactions.Option(
            name="name",
            description="Stock name to be displayed",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def edit(ctx,name):
    stock = Stock(name).display()
    if not stock["Status"]:
        await ctx.send(stock["Message"],ephemeral=True)
        return
    original_name = stock["stock"]["name"]
    custom_id = PersistentCustomID(bot,"stock_edit",original_name)
    stock_modal = interactions.Modal(
        title="Stock",
        custom_id=str(custom_id),
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Stock name",
                custom_id="name",
                value=stock["stock"]["name"],
                min_length=1,
                max_length=20,
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.PARAGRAPH,
                label="Stock description",
                value=stock["stock"]["description"],
                placeholder="",
                custom_id="description",
                min_length=1,
                max_length=500,
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Stock amount",
                value=stock["stock"]["amount"],
                custom_id="amount",
                min_length=1,
                max_length=10,
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                label="Stock price",
                value=stock["stock"]["price"],
                custom_id="price",
                min_length=1,
                max_length=10,
            )
        ],
    )
    await ctx.popup(stock_modal)

@bot.persistent_modal("stock_edit")
async def editStock(ctx,package,name:str,description:str,amount,price):
    stock = Stock(package)
    stockDict = stock.edit(name,description,int(amount),price)
    if not stock.exist:
        await ctx.send(stockDict["Message"],ephemeral=True)
        return
    edited_embed = interactions.Embed(
    title="Stock Status | 📦",
    fields=[
        interactions.EmbedField(
            name="Status",
            value=stockDict["Message"],
        ),
        interactions.EmbedField(
            name="Stock name",
            value=stockDict["stock"]["name"]
        ),
        interactions.EmbedField(
            name="Stock amount",
            value=stockDict["stock"]["amount"]
        ),
        interactions.EmbedField(
            name="Stock price",
            value=stockDict["stock"]["price"]
        )
    ],
        color = 5570422
    )
    await ctx.send(embeds=edited_embed,ephemeral=True)

inProcess = {}

@stock.subcommand(
    options=[
        interactions.Option(
            name="name",
            description="Stock name to announce",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="channel",
            description="Channel to be announced",
            type=interactions.OptionType.CHANNEL,
            required=True
        ),
        interactions.Option(
            name="mention",
            description="Mention role",
            type=interactions.OptionType.ROLE,
            required=False
        ),
        interactions.Option(
            name="image",
            description="Image url",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def announce(ctx,name,channel,mention="",image=""):
    stock = Stock(name)
    if not stock.exist:
        await ctx.send("This stock does not exist | ❌",ephemeral=True)
    stockDict = stock.display()["stock"]
    price = stockDict["price"]
    amount = stockDict["amount"]
    description = stockDict["description"]
    def embed(image):
        if image != "":
            return interactions.Embed(title=f"{name} | 📦",description=f"```\n{description}\n```\n**🛒 | Name:** __{name}__\n**💵 | Price:** __{price}__\n**📦 | Stock:** __{amount}__",image=interactions.EmbedImageStruct(url=image,height=400,width=900),color = 2)
        if image == "":
            return interactions.Embed(title=f"{name} | 📦",description=f"```\n{description}\n```\n**🛒 | Name:** __{name}__\n**💵 | Price:** __{price}__\n**📦 | Stock:** __{amount}__",color = 2)

    product = {"name":stockDict["name"],"image":image}
    custom_id = PersistentCustomID(bot,"buy",product)
    buy = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="🛒Buy",
        custom_id=str(custom_id),
    )
    #I tried using a lambda function which didn't work very well 
    def checkMention(mention):
        if mention != "":
            return mention.mention
    await channel.send(checkMention(mention),embeds=embed(image),components=buy)

@bot.persistent_component("buy")
async def buy_response(ctx,package):
    stock = Stock(package["name"])
    stockDict = stock.display()["stock"]
    name = stockDict["name"]
    description = stockDict["description"]
    amount = stockDict["amount"]
    price = stockDict["price"]
    channel = await ctx.guild.create_channel(name=str(ctx.author.id),type=0,parent_id=config.getConfig()["categoryID"])
    customer = str(ctx.author.id)
    everyone = 0
    seller = config.getConfig()["sellerRoleID"]
    sellerRole = 0
    def embed(image):
        if image != "":
            return interactions.Embed(title=f"{name} | 📦",description=f"```\n{description}\n```\n**🛒 | Name:** __{name}__\n**💵 | Price:** __{price}__\n**📦 | Stock:** __{amount}__",image=interactions.EmbedImageStruct(url=package["image"],height=400,width=900),color = 2)
        if image == "":
            return interactions.Embed(title=f"{name} | 📦",description=f"```\n{description}\n```\n**🛒 | Name:** __{name}__\n**💵 | Price:** __{price}__\n**📦 | Stock:** __{amount}__",color = 2)
    for i in await ctx.guild.get_all_roles():
        if i.position == 0:
            everyone = i.id
        if int(i.id) == seller:
            sellerRole = i
    permissions = [
        interactions.Overwrite(
            id=str(everyone),
            type=0,
            deny="1024"
        ),
        interactions.Overwrite(
            id=str(seller),
            type=0,
            allow="1024"
        ),
        interactions.Overwrite(
            id=customer,
            type=1,
            allow="1024"
        )
    ]
    confirm_id = PersistentCustomID(bot,"confirm",{"name":name})
    cancel = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="❌ Cancel the purchase",
        custom_id="cancel",
    )
    confirm = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="✔ Purchase made",
        custom_id=str(confirm_id)

    )
    buttons = interactions.ActionRow(components=[confirm,cancel])
    await channel.modify(permission_overwrites=permissions)
    await channel.send(f"{sellerRole.mention}",embeds=embed(package["image"]),components=buttons)
    await ctx.send("Buy process started",ephemeral=True)

@bot.component("cancel")
async def cancel_response(ctx):
    await ctx.channel.delete()
    pass

@bot.persistent_component("confirm")
async def confirm_response(ctx,package):
    stock = Stock(package["name"])
    stockDict = stock.display()["stock"]
    seller = False
    for role in ctx.author.roles:
        if int(role) == config.getConfig()["sellerRoleID"]:
            seller = True

    if seller:
        new = stockDict["amount"] - 1
        edit = stock.edit(stockDict["name"],stockDict["description"],new,stockDict["price"])
        await ctx.send("✔ Purchase made. | Stock automatically edited, if you want to edit something type /stock edit [stock name]",ephemeral=True)
        await ctx.send("✔ Purchase made.\n⚠ Deleting this channel in 3 seconds")
        time.sleep(3)
        await ctx.channel.delete()
    else:
        await ctx.send("❌ Only sellers can do this",ephemeral=True)

@bot.event
async def on_ready():
    os.system("cls||clear")
    line = "-"*20
    print(f"folia Stock Bot\nMade by slx10\nDiscord: SL#5115\n{line}\n/help -> Help with commands")

bot.start()