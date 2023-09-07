from lib import *


class Letu:
    def __init__(self, context:BrowserContext):
        self.context = context

    async def get_json(self, link):
        page = await self.context.new_page()
        response = await page.goto(link)
        js = await response.json()
        await page.close()
        return js


    async def links_for_item(self, name:str, prefix):
        try:
            link = f'https://www.letu.ru/s/api/product/listing/v1/products?N=0&Nrpp=36&No=0&Ntt={name}&innerPath=mainContent%5B2%5D&resultListPath=%2Fcontent%2FWeb%2FSearch%2FSearch%20RU&pushSite=storeMobileRU'
            page = await self.context.new_page()
            response = await page.goto(link)
            await asyncio.sleep(5)
            response = await page.goto(link)
            js = await response.json()
            count = int(js['totalNumRecs'])

            products = js['products']
            links = [
                {
                    'URL' : f'https://www.letu.ru/s/api/product/v2/product-detail/{item["repositoryId"]}?pushSite=storeMobileRU',
                    'ARTICLE' : item['article'],
                    'PREFIX' : prefix
                }
                for item in products
            ]

            for i in range (36, count + 1, 36):
                link = re.sub(r'No=.*?&', f'No={i}&', link)
            
                response = await page.goto(link)
                js = await response.json()
                products = js['products']

                links += [
                {
                    'URL' : f'https://www.letu.ru/s/api/product/v2/product-detail/{item["repositoryId"]}?pushSite=storeMobileRU',
                    'ARTICLE' : item['article'],
                    'PREFIX' : prefix
                }
                for item in products
                ]
            await page.close()
            return links
        except Exception as e:
            print (e)
            return await self.links_for_item(self.context, name, prefix)