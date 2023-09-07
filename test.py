from classes import *


async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()

        parser = Letu(context)

        js = await parser.get_json('https://www.letu.ru/s/api/product/v2/product-detail/139100401?pushSite=storeMobileRU')
        await browser.close()
        print (js)

asyncio.run(main())
sdfsd