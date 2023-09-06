from func import *






async def main():
    result = []
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context()
        p = pd.read_excel('brands.xlsx')
        p = p.to_dict('list')
        brands = p['brands']
        prefixs = p['articles']
        items = []
        tasks = []
        for brand, prefix in zip(brands, prefixs):
            tasks.append(asyncio.create_task(links_for_item(context, brand, prefix)))
        items = await asyncio.gather(*tasks)
        items = [i for j in items for i in j]
        print (items)
        print('Перехожу к итерации по карточкам товаров')
        tasks = []
        for item in items:
            art = item['ARTICLE']
            link = item['URL']
            prefix = item['PREFIX']
            task = asyncio.create_task(data(context, link, art, prefix))
            tasks.append(task)
            if len(tasks) == 10:
                print(f'Отправляю {len(tasks)}  запросов')
                result += await asyncio.gather(*tasks)
                sec = random.randint(1,4)
                print (f'Количество собранных товаров {len(result)}')
                print (f'Спим {sec} секунд')
                await asyncio.sleep(sec)
                tasks.clear()
            else:
                continue
        if len(tasks):
            print (f'Отправляю {len(tasks)} запросов')
            result += await asyncio.gather(*tasks)
        await browser.close()

        p = pd.DataFrame([item for item in result if item != None])
        p.to_excel('result.xlsx', index=False)



async def test():
    start = time.perf_counter()
    result = []
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context()
        items = []
        tasks = [asyncio.create_task(promo(context, 'p7ubid', 'VB4-'))]
        items = await asyncio.gather(*tasks)
        items = [i for j in items for i in j]
        len(items)
        print('Перехожу к итерации по карточкам товаров')
        tasks = []
        tmp = set()
        for item in items:
            tmp.add(item['VALUE'])
        count = sum(tmp)
        for item in items:
            art = item['ARTICLE']
            link = item['URL']
            prefix = item['PREFIX']
            task = asyncio.create_task(data(context, link, art, prefix))
            tasks.append(task)
            if len(tasks) == 30:
                print(f'Отправляю {len(tasks)}  запросов')
                result += await asyncio.gather(*tasks)
                # print (f'Количество полученных товаров {len([i for j in result for i in j if i != None])} из {count}')
                tasks.clear()
            else:
                continue
        if len(tasks):
            print (f'Отправляю {len(tasks)} запросов')
            result += await asyncio.gather(*tasks)
        
        result = [i for i in result if i != None]
        result = [i for j in result for i in j]
        print(f'Количество гарантированных товаров {len(result)} из {count}')
        await browser.close()
        print(f'Время выполнения : {time.perf_counter() - start}')
        for item in result:
            item['Старая цена'] = re.sub(r'.', ',', str(item['Старая цена']))
            
        p = pd.DataFrame(result)
        p.to_excel('result.xlsx', index=False)


asyncio.run(test())