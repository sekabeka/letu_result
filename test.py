from classes import *


async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        parser = Letu(context)
        await parser.go_to_link('https://www.letu.ru')
        result = await parser.get_json('https://www.letu.ru/s/api/product/v2/product-detail/132803574?pushSite=storeMobileRU')
        print (result)

asyncio.run(main())
