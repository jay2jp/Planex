import asyncio
from dotenv import load_dotenv
load_dotenv()
from browser_use import Agent
from browser_use.llm import ChatGoogle

async def main():
    prompt = """
    using this hashtags as a start determine which of them have real tiktok posts underneath them or not return back the list of hashtags that have real tiktok posts underneath them
    if you need to sign in with google use the following credentials:
    email: alfredBot23@gmail.com
    password: aE45mDC63qFUK5g

    #DowntownJerseyCityEats
#DowntownJerseyCityFood
#DowntownJerseyCityBrunch
#DowntownJerseyCityBars
#DowntownJerseyCityCocktails
#DowntownJerseyCityRestaurants
#DowntownJerseyCityCoffee
#DowntownJerseyCityDateSpots
#JournalSquareEats
#JournalSquareFood
#JournalSquareBrunch
#JournalSquareBars
#JournalSquareCocktails
#JournalSquareRestaurants
#JournalSquareCoffee
#JournalSquareDateSpots
#TheHeightsEats
#TheHeightsFood
#TheHeightsBrunch
#TheHeightsBars
#TheHeightsCocktails
#TheHeightsRestaurants
#TheHeightsCoffee
#TheHeightsDateSpots
#BergenLafayetteEats
#BergenLafayetteFood
#BergenLafayetteBrunch
#BergenLafayetteBars
#BergenLafayetteCocktails
#BergenLafayetteRestaurants
#BergenLafayetteCoffee
#BergenLafayetteDateSpots
#GreenvilleEats
#GreenvilleFood
#GreenvilleBrunch
#GreenvilleBars
#GreenvilleCocktails
#GreenvilleRestaurants
#GreenvilleCoffee
#GreenvilleDateSpots
#PaulusHookEats
#PaulusHookFood
#PaulusHookBrunch
#PaulusHookBars
#PaulusHookCocktails
#PaulusHookRestaurants
#PaulusHookCoffee
#PaulusHookDateSpots
#McGinleySquareEats
#McGinleySquareFood


instead of using the UI to complete the search you can use the URL like so https://www.tiktok.com/tag/DowntownJerseyCityEats you can replace DowntownJerseyCityEats with the tag you are looking for and it will show if results are real or not


    """
    agent = Agent(
        task=prompt,
        llm=ChatGoogle(model="gemini-2.0-flash", temperature=1.0),
    )
    await agent.run()

asyncio.run(main())