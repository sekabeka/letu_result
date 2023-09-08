from classes import *


async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        parser = Letu(context)
        await parser.go_to_link('https://www.letu.ru')
        await context.request.post('https://www.letu.ru/s/api/geo/v1/city?pushSite=storeMobileRU', data={'cityId' : '8113'})
        p = pd.read_excel('items.xlsx')
        p = p.to_dict('list')
        querys = p['query']
        promoids = p['id']
        names = p['number']
       
        for name, query, id in zip(names[1:2], querys, promoids):
            print (f'Пойду обрабатывать номер 3.3')
            items = await parser.promo(id, "1kzt1a7", 'VB4-')
            tasks = []
            result = []
            for item in items:
                url = item['URL']
                article = item['ARTICLE']
                prefix = item['PREFIX']
                task = asyncio.create_task(parser.get_main_info(url, article, prefix))
                tasks.append(task)
                if len (tasks) == 30:
                    print(f'Отправляю {len(tasks)} запросов')
                    result += await asyncio.gather(*tasks)
                    sec = random.randint(1,5)
                    print(f'Спим {sec} секунд')
                    await asyncio.sleep(sec)
                    tasks.clear()
                else:
                    continue
            if len(tasks):
                print (f'Отправляю {len(tasks)} запросов')
                result += await asyncio.gather(*tasks)
            
            p = pd.DataFrame(result)
            p.to_excel(f'3.3.xlsx', index=False)
                        

        

asyncio.run(main())



