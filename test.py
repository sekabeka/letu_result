from classes import *

brands_ute = [
    'GARNIER',
    'LADOR',
    'SYOSS',
    'ELSEVE',
    'TAFT',
    'EGG PLANET',
    'KENSUKO',
    'NIVEA',
    'LIKATO',
    'AVOTTE',
    'LA ROCHE-POSAY'
]


async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        parser = Letu(context)
        await parser.go_to_link('https://www.letu.ru')
        await context.request.post('https://www.letu.ru/s/api/geo/v1/city?pushSite=storeMobileRU', data={'cityId' : '8113'})
        p = pd.read_excel('brands.xlsx')
        brands = p.to_dict('list')[0]
        result = []
        tasks = []
        items = []
        for brand in brands:
            if brand in brands_ute:
                prefix = 'UTE-'
            else:
                prefix = 'VB4-'
            brand = quote(brand)
            task = asyncio.create_task(parser.search(brand, prefix))
            tasks.append(task)
            if len (tasks) == 10:
                    print ('Отправляем 30 запросов')
                    items += await asyncio.gather(*tasks)
                    tasks.clear()
        if len(tasks):
            items += await asyncio.gather(*tasks)
            tasks.clear()
        items = [i for j in items for i in j]

        for item in items:
            article, url, prefix, marker = parser.unpack(item) 
            task = asyncio.create_task(parser.get_main_info(url, article, prefix, marker))
            tasks.append(task)
            if len (tasks) == 10:
                print ('Отправляем 30 запросов')
                result += await asyncio.gather(*tasks)
                tasks.clear()
        if len(tasks):
            result += await asyncio.gather(*tasks)
            tasks.clear()
        
        result = [i for j in result if j != None for i in j]

        result_two = []
        tasks.clear()
        while len(parser.errors):
            if len(parser.errors):
                error = parser.errors.pop()
                link = error['url']
                article = error['article']
                prefix = error['prefix']
                marker = error['marker']
                task = asyncio.create_task(parser.get_main_info(link, article, prefix, marker))
                tasks.append(task)
            if len(tasks) == 30:
                print (f'осталось {len(parser.errors)}')
                result_two += await asyncio.gather(*tasks)
                tasks.clear()
        if len(tasks):
            result_two += await asyncio.gather(*tasks)
        result_two = [i for j in result_two if j != None for i in j]
        res = result + result_two
        print(f'Собрано без ошибок {len(result)}\nИсправлено {len(result_two)}\nВсего вышло {len(res)}')
        p = pd.DataFrame(result)
        p.to_excel('test.xlsx', index=False)


asyncio.run(main())
        
                        

        






