from classes import *
import xlsxwriter
# async def main():
#     async with async_playwright() as p:
#         browser = await p.firefox.launch(headless=True)
#         context = await browser.new_context()
#         parser = Letu(context)
#         pages = [await context.new_page() for _ in range (1, 8)]
#         await parser.go_to_link('https://www.letu.ru', pages[0])
#         await context.request.post('https://www.letu.ru/s/api/geo/v1/city?pushSite=storeMobileRU', data={'cityId' : '8113'})
#         # p = pd.read_excel('letu_result/letu.xlsx', sheet_name=None)
#         # names = list(p.keys())
#         # DataFrames = list(p.values())
#         p = pd.read_excel('letu_result/sex.xlsx')
#         # with pd.ExcelWriter('letu_result/elements_letu.xlsx') as writer:
#         with pd.ExcelWriter('letu_result/sex_elements_letu.xlsx', engine='xlsxwriter') as writer:
#             # with pd.ExcelWriter('letu_result/result.xlsx') as writer2:
#             with pd.ExcelWriter('letu_result/result_sex.xlsx', engine='xlsxwriter') as writer2:

#                 # for df, name in zip(DataFrames, names):
#                     df = p.to_dict('list')
#                     # df = df.to_dict('list')
#                     brands = df['Название Бренда']
#                     prefixs = df['Префикс']
#                     tasks = []
#                     items = []
#                     while len(brands):
#                         for page in pages:
#                             if len(brands):
#                                 task = asyncio.create_task(parser.search(quote(brands.pop()), prefixs.pop(), page))
#                                 tasks.append(task)
#                             else:
#                                 break
#                         if len(tasks):
#                             items += await asyncio.gather(*tasks)
#                             tasks.clear()
#                         else:
#                             break
#                     items = [i for j in items for i in j]
#                     print (f'{len(items)} собрано продуктов')
#                     print('Записываем в таблицу, мало ли понадобятся нам ссылки и прочее, чтобы в дальнейшем не пользоваться функцией search')
#                     p = pd.DataFrame(items)
#                     p.to_excel(writer, sheet_name='sex', index=False)
#                     tasks.clear()
#                     result = []
#                     while len(items):
#                         for page in pages:
#                             if len(items):
#                                 item = items.pop()
#                                 article = item['ARTICLE']
#                                 url = item['URL']
#                                 marker = item['MARKER']
#                                 prefix = item['PREFIX']
#                                 task = asyncio.create_task(parser.get_main_info(url, article, prefix, marker, page))
#                                 tasks.append(task)
#                             else:
#                                 break
#                         if len(tasks):
#                             result += await asyncio.gather(*tasks)
#                             tasks.clear()
#                         else:
#                             break
#                     result = [i for j in result if j != None for i in j]
#                     print (f'{len(result)} собрано продуктов')
#                     tasks.clear()
#                     result_error = []
#                     print ('Приступим к исправлению ошибок....')
#                     while len(parser.errors):
#                         flag = int(input(f'Повторяем? Количество ошибок --{len(parser.errors)}--\n'))
#                         if flag == 0:
#                             break
#                         for page in pages:
#                             if len(parser.errors):
#                                 item = parser.errors.pop()
#                                 article = item['article']
#                                 url = item['url']
#                                 marker = item['marker']
#                                 prefix = item['prefix']
#                                 task = asyncio.create_task(parser.get_main_info(url, article, prefix, marker, page))
#                                 tasks.append(task)
#                             else:
#                                 break
#                         if len(tasks):
#                             result_error += await asyncio.gather(*tasks)
#                             tasks.clear()
#                         else:
#                             break
#                     result_error = [i for j in result_error if j != None for i in j]
#                     result += result_error
#                     p = pd.DataFrame(result)
#                     p.to_excel(writer2, index=False, sheet_name='sex')
#                     print ('Мы прошли одну категорию, поздравляем!!!')
        


        
            
async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        parser = Letu(context)
        pages = [await context.new_page() for _ in range (1, 8)]
        await parser.go_to_link('https://www.letu.ru', pages[0])
        await context.request.post('https://www.letu.ru/s/api/geo/v1/city?pushSite=storeMobileRU', data={'cityId' : '8113'})
        p = pd.read_excel('letu_result/sex_elements_letu.xlsx')
        items = p.to_dict('list')
        with pd.ExcelWriter('letu_result/result_sex.xlsx', engine='xlsxwriter') as writer:
            tasks = []
            tasks.clear()
            result = []
            while len(items['ARTICLE']):
                for page in pages:
                    if len(items['ARTICLE']):
                        article = items['ARTICLE'].pop()
                        url = items['URL'].pop()
                        marker = items['MARKER'].pop()
                        prefix = items['PREFIX'].pop()
                        task = asyncio.create_task(parser.get_main_info(url, article, prefix, marker, page))
                        tasks.append(task)
                    else:
                        break
                if len(tasks):
                    result += await asyncio.gather(*tasks)
                    tasks.clear()
                else:
                    break
            result = [i for j in result if j != None for i in j]
            print (f'{len(result)} собрано продуктов')
            tasks.clear()
            result_error = []
            print ('Приступим к исправлению ошибок....')
            while len(parser.errors):
                flag = int(input(f'Повторяем? Количество ошибок --{len(parser.errors)}--\n'))
                if flag == 0:
                    break
                for page in pages:
                    if len(parser.errors):
                        item = parser.errors.pop()
                        article = item['article']
                        url = item['url']
                        marker = item['marker']
                        prefix = item['prefix']
                        task = asyncio.create_task(parser.get_main_info(url, article, prefix, marker, page))
                        tasks.append(task)
                    else:
                        break
                if len(tasks):
                    result_error += await asyncio.gather(*tasks)
                    tasks.clear()
                else:
                    break
            result_error = [i for j in result_error if j != None for i in j]
            result += result_error
            p = pd.DataFrame(result)
            p.to_excel(writer, index=False, sheet_name='sex')
            print ('Мы прошли одну категорию, поздравляем!!!')            



        
    


asyncio.run(main())
        
                        

        






