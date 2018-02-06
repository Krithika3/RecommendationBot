class EbayData:
    def get_ebay_data(config, keyword):
        print "hello"
        site_id = config.get('ebay', 'site_id')
        app_id = config.get('ebay', 'app_id')
        max_price = config.get('ebay', 'max_price')
        min_price = config.get('ebay', 'min_price')
        sort_order = config.get('ebay', 'sort_order')

        api = finding(siteid=site_id,appid=app_id, config_file=None)
        response = api.execute('findItemsAdvanced', {
                'keywords': keyword,
                'itemFilter': [
                    {'name': 'Condition', 'value': 'Used'},
                    {'name': 'MinPrice', 'value': min_price, 'paramName': 'Currency', 'paramValue': 'USD'},
                    {'name': 'MaxPrice', 'value': max_price, 'paramName': 'Currency', 'paramValue': 'USD'}
                ],
                'sortOrder': sort_order
            })


        item_response = response.dict()
        return item_response['itemSearchURL']
 
