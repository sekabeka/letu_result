from lib import *


class Letu:

    def __init__(self, context:BrowserContext):
        self.context = context
        self.errors = []


    def unpack (self, item:dict):
        url = item['URL']
        prefix = item['PREFIX']
        article = item['ARTICLE']
        marker = item['MARKER']
        return article, url, prefix, marker

    def image(self, imgs:list, images:list):
        for img in imgs:
            if img['type'] != 'shade':
                images.append(
                    'https://letu.ru' + img['url']
                )


    async def get_json(self, link):
        page = await self.context.new_page()
        response = await page.goto(link)
        await asyncio.sleep(5)
        js = await response.json()
        await page.close()
        return js

    async def go_to_link(self, link):
        page = await self.context.new_page()
        await page.goto(link)
        await asyncio.sleep(5)
        await page.close()
    
    def IsAvailable(self, data:dict):
        if data['article'] == '':
            return False
        else:
            return True




    async def search(self, query:str, prefix:str):
        try:
            link = f'https://www.letu.ru/s/api/product/listing/v1/products?N=0&Nrpp=36&No=0&Ntt={query}&innerPath=mainContent%5B2%5D&resultListPath=%2Fcontent%2FWeb%2FSearch%2FSearch%20RU&pushSite=storeMobileRU'
            try:
                data = await self.get_json(link)
            except TimeoutError:
                print ('ssss')
                return await self.search(query, prefix)
            count = int(data['totalNumRecs'])
            products = data['products']
            items_list = []
            func = lambda item, prefix, marker: {
                items_list.append(
                    {
                        'URL' : f'https://www.letu.ru/s/api/product/v2/product-detail/{item["repositoryId"]}?pushSite=storeMobileRU',
                        'ARTICLE' : item['article'],
                        'PREFIX' : prefix,
                        'MARKER' : marker
                    }
                )
            }
            for prod in products:
                if self.IsAvailable(prod):
                    markers = [item['ui_name'] for item in prod['appliedMarkers']]
                    func(prod, prefix, ' '.join(markers))
                    
                else:
                    continue
            for i in range (36, count + 1, 36):
                link = re.sub(r'No=.*?&', f'No={i}&', link)
                data = await self.get_json(link)
                products = data['products']
                for prod in products:
                    if self.IsAvailable(prod):
                        markers = [item['ui_name'] for item in prod['appliedMarkers']]
                        func(prod, prefix, ' '.join(markers))
                    else:
                        continue
            return items_list
        except Exception as e:
            print (str(e))
            return await self.search(query, prefix)

    async def promo(self, promoid:str, query:str, prefix:str):
        try:
            link = f'https://www.letu.ru/s/api/product/listing/v1/products?N={query}&Nrpp=36&No=0&innerPath=mainContent%5B1%5D&resultListPath=%2Fcontent%2FWeb%2FPromotions%2FPromo%20Detail%20Page%2FPromo%20Detail%20Page&promoId={promoid}&pushSite=storeMobileRU'
            data = await self.get_json(link)
            count = int(data['totalNumRecs'])
            products = data['products']
            items_list = []
            func = lambda item, prefix: {
                items_list.append(
                    {
                        'URL' : f'https://www.letu.ru/s/api/product/v2/product-detail/{item["repositoryId"]}?pushSite=storeMobileRU',
                        'ARTICLE' : item['article'],
                        'PREFIX' : prefix
                    }
                )
            }
            for prod in products:
                if self.IsAvailable(prod):
                    func(prod, prefix)
                else:
                    continue
            for i in range (36, count + 1, 36):
                print (i)
                link = re.sub(r'No=.*?&', f'No={i}&', link)
                data = await self.get_json(link)
                products = data['products']
                for prod in products:
                    if self.IsAvailable(prod):
                        func(prod, prefix)
                    else:
                        continue
            return items_list
        except Exception as e:
            print (str(e))
            
            return await self.promo(promoid=promoid, query=query, prefix=prefix)


    async def get_main_info(self, link:str, article:str, prefix:str, marker:str):
        try:
            error = {
                'url' : link,
                'article' : article,
                'prefix' : prefix,
                'marker' : marker
            }
            data = await self.get_json(link)
            name = data['displayName']
            brand = data['brand']['name']
            id = data['productId']
            for_link = data['sefPath'].split('/')
            url = 'https://www.letu.ru/product' + for_link[-1] + '/' + id
            skuList = data['skuList']
            images = []
            self.image(data['media'], images)
            for el in skuList:
                if article == el['article']:
                    info = skuList.pop(skuList.index(el))
                else:
                    print ('error')
                self.image(el['media'], images)
            weight = info['displayName']
            price = float(info['price']['amount'])
            sale_size = int(info['price']['discountPercent'])

            new_link = f'https://www.letu.ru/s/api/product/v2/product-detail/{id}/tabs?locale=ru-RU&pushSite=storeMobileRU'
            data2 = await self.get_json(new_link)
            definition = re.sub(r'<.*?>','',data2['description']['longDescription'])
            match sale_size:
                case 0:
                    result = { 
                        'Подкатегория 1' : "Косметика",
                        'Подкатегория 2' : 'Для волос',
                        'Подкатегория 3' : brand,
                        'Название товара или услуги' : name,
                        "Размещение на сайте" : 'catalog/' + '/'.join(for_link[1:-1]),
                        'Полное описание' : definition,
                        'Краткое описание' : weight,
                        'Артикул поставщика' : article,
                        'Артикул' : prefix + article,
                        'Цена продажи' : None,
                        'Старая цена' : None,
                        'Цена закупки' : str(price).replace('.', ','),
                        'Остаток' : 100,
                        'Параметр: Бренд' : brand,
                        'Параметр: Производитель' : brand,
                        "Параметр: Размер скидки" : 'Скидки нет',
                        'Параметр: Период скидки' : None,
                        'Параметр: Метки' : marker
                    }
                case _:
                    result = { 
                        'Подкатегория 1' : "Косметика",
                        'Подкатегория 2' : 'Для волос',
                        'Подкатегория 3' : brand,
                        'Название товара или услуги' : name,
                        "Размещение на сайте" : 'catalog/' + '/'.join(for_link[1:-1]),
                        'Полное описание' : definition,
                        'Краткое описание' : weight,
                        'Артикул поставщика' : article,
                        'Артикул' : prefix + article,
                        'Цена продажи' : None,
                        'Старая цена' : str(format(price * 2.0 * (1.0 + sale_size / 100), '.2f')).replace('.', ','),
                        'Цена закупки' : str(price).replace('.', ','),
                        'Остаток' : 100,
                        'Параметр: Бренд' : brand,
                        'Параметр: Производитель' : brand,
                        "Параметр: Размер скидки" : str(sale_size) + '%',
                        'Параметр: Период скидки' : None,
                        'Параметр: Метки' : marker
                    }
            for item in data['topSpecs']:
                result[f'Параметр: {item["name"]}'] = item['value']
           
            result['Изображения'] = ' '.join(images)
            result['Ссылка на товар'] = url
            tmp = []
            if len(skuList):
                for item in skuList:
                    article = item['article']
                    display_name = item['displayName']
                    available = item['isInStock']
                    price = float(item['price']['amount'])
                    sale_size = int(item['price']['discountPercent'])
                    img_prop = 'https://www.letu.ru' + item['media'][1]['url']
                    prop = item['unitOfMeasure'].strip()
                    if available:
                        res = result.copy()
                        res['Артикул поставщика'] = article
                        res['Артикул'] = prefix + article
                        res['Цена закупки'] = str(price).replace('.', ',')
                        if sale_size != 0:
                            res['Старая цена'] = str(format(price * 2.0 * (1.0 + sale_size / 100), '.2f')).replace('.', ',')
                            res['Параметр: Размер скидки'] = str(sale_size) + '%' 
                        else:
                            res['Старая цена'] = None
                            res['Параметр: Размер скидки'] = 'Скидки нет'
                        res[f'Свойство: {prop.lower()}'] = display_name
                        res['Изображение варианта'] = img_prop
                        tmp.append(res)
                    else:
                        continue
            
            return [result, *tmp]
        except Exception as e:
            print (str(e))
            self.errors.append(
                error
            )
