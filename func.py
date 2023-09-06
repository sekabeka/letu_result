from lib import *


async def promo(context:BrowserContext, name:str, prefix):
    try:
        link = f'https://www.letu.ru/s/api/product/listing/v1/products?N={name}&Nrpp=36&No=0&innerPath=mainContent%5B1%5D&resultListPath=%2Fcontent%2FWeb%2FPromotions%2FPromo%20Detail%20Page%2FPromo%20Detail%20Page&promoId=13020018&pushSite=storeMobileRU'
        page = await context.new_page()
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
                'PREFIX' : prefix,
                'VALUE' : count
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
                'PREFIX' : prefix,
                'VALUE' : count
            }
            for item in products
            ]
        await page.close()
        return links
    except Exception as e:
        print (e)
        return await links_for_item(context, name, prefix)



async def links_for_item(context:BrowserContext, name:str, prefix):
    try:
        link = f'https://www.letu.ru/s/api/product/listing/v1/products?N=0&Nrpp=36&No=0&Ntt={name}&innerPath=mainContent%5B2%5D&resultListPath=%2Fcontent%2FWeb%2FSearch%2FSearch%20RU&pushSite=storeMobileRU'
        page = await context.new_page()
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
        return await links_for_item(context, name, prefix)
      

async def data(context, link:str, article_check, prefix):
    try:
        result = []
        page = await context.new_page()
        response = await page.goto(link, timeout = 0)
        js = await response.json()
        if article_check == '':
            count = 0
        else:
            count = 100
            
        
        name = js['displayName']
        images = []

        for img in js['media']:
            images.append('https://letu.ru' + img['url'])

        info = js['skuList'][0]
        article = info['article']
        weight = info['displayName']
        price = float(info['price']['amount'])
        sale_size = int(info['price']['discountPercent'])
        if sale_size != 0:
            old_price = price * 2.0 * (1.0 + sale_size / 100)
            sale_size = f'{sale_size}' + '%'
        else:
            old_price = None
            sale_size = 'Не указана'
        
        brand = js['brand']['name']
        
        id = js['productId']
        for_link = js['sefPath'].split('/')
        url = 'https://www.letu.ru/product' + for_link[-1] + '/' + id
        tmp = for_link[1:-1]

        new_link = f'https://www.letu.ru/s/api/product/v2/product-detail/{id}/tabs?locale=ru-RU&pushSite=storeMobileRU'
        response = await page.goto(new_link,  timeout = 0)
        js2 = await response.json()
        #
        definition = re.sub(r'<.*?>','',js2['description']['longDescription'])
        #
        match count:
            case 0:
                result.append({ 
                'Подкатегория 1' : "Косметика",
                'Подкатегория 2' : 'Для волос',
                'Подкатегория 3' : brand,
                'Название товара или услуги' : name,
                "Размещение на сайте" : 'catalog/' + '/'.join(tmp),
                'Полное описание' : definition,
                'Краткое описание' : weight,
                'Артикул поставщика' : article,
                'Артикул' : prefix + article,
                'Цена продажи' : None,
                'Старая цена' : None,
                'Цена закупки' : 'Нет в наличии',
                "Размер скидки" : str(sale_size),
                'Период скидки' : None,
                'Остаток' : 0,
                'Параметр: Бренд' : brand,
                'Параметр: Производитель' : brand,
            })
            case 100:
                result.append({ 
                        'Подкатегория 1' : "Косметика",
                        'Подкатегория 2' : 'Для волос',
                        'Подкатегория 3' : brand,
                        'Название товара или услуги' : name,
                        "Размещение на сайте" : 'catalog/' + '/'.join(tmp),
                        'Полное описание' : definition,
                        'Краткое описание' : weight,
                        'Артикул поставщика' : article,
                        'Артикул' : prefix + article,
                        'Цена продажи' : None,
                        'Старая цена' : old_price,
                        'Цена закупки' : re.sub('[.]',',',str(price)),
                        "Размер скидки" : str(sale_size),
                        'Период скидки' : None,
                        'Остаток' : count,
                        'Параметр: Бренд' : brand,
                        'Параметр: Производитель' : brand,
                    })
        
        for var in js['skuList'][1:]:
            article = var['article']
            display_name = var['displayName']
            id = var['id']
            available = bool(var['isInStock'])
            price = float(info['price']['amount'])
            sale_size = int(info['price']['discountPercent'])
            if sale_size != 0:
                old_price = price * 2.0 * (1.0 + sale_size / 100)
                sale_size = f'{sale_size}' + '%'
            else:
                old_price = None
                sale_size = 'Не указана'
            prop = var['unitOfMeasure'].strip()
            img_tovar = 'https://www.letu.ru' + var['media'][0]['url']
            img_prop = 'https://www.letu.ru' + var['media'][1]['url']
            link = url + f'/sku/{id}'
            match available:
                case True:
                    t = { 
                        'Подкатегория 1' : "Косметика",
                        'Подкатегория 2' : 'Для волос',
                        'Подкатегория 3' : brand,
                        'Название товара или услуги' : name,
                        "Размещение на сайте" : 'catalog/' + '/'.join(tmp),
                        'Полное описание' : definition,
                        'Краткое описание' : weight,
                        'Артикул поставщика' : article,
                        'Артикул' : prefix + article,
                        'Цена продажи' : None,
                        'Старая цена' :old_price,
                        'Цена закупки' : re.sub('[.]',',',str(price)),
                        "Размер скидки" : str(sale_size),
                        'Период скидки' : None,
                        'Остаток' : 100,
                        'Параметр: Бренд' : brand,
                        'Параметр: Производитель' : brand,
                    }
        
                case False:
                    t =  { 
                        'Подкатегория 1' : "Косметика",
                        'Подкатегория 2' : 'Для волос',
                        'Подкатегория 3' : brand,
                        'Название товара или услуги' : name,
                        "Размещение на сайте" : 'catalog/' + '/'.join(tmp),
                        'Полное описание' : definition,
                        'Краткое описание' : weight,
                        'Артикул поставщика' : article,
                        'Артикул' : prefix + article,
                        'Цена продажи' : None,
                        'Старая цена' : None,
                        'Цена закупки' : 'Нет в наличии',
                        "Размер скидки" : str(sale_size),
                        'Период скидки' : None,
                        'Остаток' : 0,
                        'Параметр: Бренд' : brand,
                        'Параметр: Производитель' : brand,
                    }
            t['Свойство: название товара'] = display_name
            t['Свойство: ссылка на товар'] = link
            t['Свойство: критерий различия'] = prop
            t['Свойство: фото товара'] = img_tovar
            t['Свойство: фото критерия'] = img_prop
            result.append(t)

        for item in js['topSpecs']:
            for res in result:
                res[f'Параметр: {item["name"]}'] = item['value']
        for res in result:
            res['Изображения'] = ' '.join(images)
            res['Ссылка на товар'] = url
        await page.close()
        return result
    except Exception as e:
        print(e)

        
       


        


            
        




