from jos_a_bank.items import JosABankItem
from scrapy.cmdline import execute
from jos_a_bank import db_config
from typing import Iterable
from scrapy import Request
from urllib import parse
import pymysql
import scrapy
import json


def get_url(store_dict: dict) -> str:
    store_url = f'https://www.josbank.com/store-locator/{store_dict['storeName']}-{store_dict['state_ntk']}-{store_dict['stloc_id']}?address=%20%2C'
    return store_url


def get_store_no(store_dict: dict) -> str:
    store_no = store_dict.get('stloc_id', 'N/A')
    return store_no


def get_store_name(store_dict: dict) -> str:
    store_name = store_dict.get('storeName', 'N/A')
    return store_name


def get_city(store_dict):
    store_city = store_dict.get('city_ntk', 'N/A')
    return store_city


def get_state(store_dict: dict) -> str:
    store_state = store_dict.get('state_ntk', 'N/A')
    return store_state


def get_street(store_dict: dict) -> str:
    street = store_dict.get('address1_ntk', '') + store_dict.get('address2_ntk', '')
    return street


def get_zip_code(store_dict: dict) -> str:
    zip_code = store_dict.get('zip_code', 'N/A')
    return zip_code


def get_latitude(response_dict: dict) -> str:
    latitude = response_dict.get('contextData', {}).get('latitude', 'N/A')
    return latitude


def get_longitude(response_dict: dict) -> str:
    longitude = response_dict.get('contextData', {}).get('longitude', 'N/A')
    return longitude


def get_phone(store_dict: dict) -> str:
    phone = store_dict.get('phone_ntk', 'N/A')
    return phone


def get_direction_url(store_dict):
    direction_url = f"https://www.google.com/maps/dir/{store_dict['latlong']}"
    return direction_url


def get_open_hours(store_dict: dict) -> str:
    working_hours = store_dict.get('working_hours_ntk').split('<br>')
    open_hours_list = [work[:3] + ": " + work[3:] for work in working_hours]
    open_hours = ' | '.join(open_hours_list)
    return open_hours


class JosabankStoreSpider(scrapy.Spider):
    name = "josabank_store"

    def __init__(self, ):
        """Initialize database connection and set file paths."""
        super().__init__()
        self.client = pymysql.connect(host=db_config.db_host, user=db_config.db_user, password=db_config.db_password, database=db_config.db_name, autocommit=True)
        self.cursor = self.client.cursor()  # Create a cursor object to interact with the database

        # self.page_save_path = rf'C:\Project Files Live (using Scrapy)\storeLocator\{self.today_date_time}\{self.name}'
        self.input_table = 'states_abbreviations_latilong'

        self.cookies = {
            '_evga_13f4': '{%22uuid%22:%2291ea64b8af5e567a%22}',
            '_qubitTracker': '2sgxp57y2m4-0m3y5ccb9-5gj6pd8',
            'qb_generic': ':ZNnaWZU:.josbank.com',
            '__ogfpid': 'c37982b4-43f1-4c48-8579-822ea5c161de',
            'OTGPPConsent': 'DBABLA~BAAAAAAAAgA.QA',
            '_sfid_720f': '{%22anonymousId%22:%2291ea64b8af5e567a%22%2C%22consents%22:[]}',
            '_caid': '1e702b04-e7d5-4bc7-b4b0-d331f0c67452',
            '_gid': 'GA1.2.1427507934.1732606782',
            '_gcl_au': '1.1.993264616.1732606782',
            'tracker_device_is_opt_in': 'true',
            'uuid': 'f35e4c86-47b1-41bd-bf79-d60efcce7a32',
            'gbi_visitorId': 'cm3y5cdjt000135k3wutzi6i0',
            '_fbp': 'fb.1.1732606782693.350064536653223749',
            'kampyle_userid': '4181-e0ed-26e1-e40c-294d-2a74-476d-4696',
            '_tt_enable_cookie': '1',
            '_ttp': 'OJ4W8vXDMq2wrChgBEvTJPGEGRc.tt.1',
            'tracker_device': 'fa3a366e-6e8d-4b56-9933-b05550865ff5',
            'JAB_FreeShipping': '30',
            'WC_PERSISTENT': '9w%2FhddB2KpgES7eZN6DY2XL0NOCgAr9MeSNncybxep8%3D%3B2024-11-26+01%3A41%3A16.495_1732606876493-87187_13452_-1002%2C-1%2CUSD_13452',
            'JABCART_COUNT': '0',
            'JABStore': '86%7CBurlington%20Market%20Place%7C42.48657%7C-71.21142%7C01803%7CBurlington%7CMA',
            'xyz_cr_1200_et_111': '=NaN&cr=1200&wegc=&et=111&ap=',
            'OptanonAlertBoxClosed': '2024-11-26T07:39:54.774Z',
            'BVBRANDID': '67a8b136-3193-4191-87bb-fcba529673f4',
            'akacd_JAB': '3910145700~rv=33~id=5694ac1c13b3eb7e8c3908fd6af73c68',
            'ak_bmsc': '71A1A52B141DF19987DC4B896A357C50~000000000000000000000000000000~YAAQzPXSF7O0uDWTAQAAZ4WLbBllrmauLqnRoEzusTWGB9ey9d33Bfb5R9sxGXz5dh2+tiVCQeq4UQUgYSz9ym2lWThVJb6KLUn7Qch3+FkbTlPTvsw+VZd29Z8b0DF+tY5P5u3nq1lMaIxzbtq1t7wS5nHEikHmx5b8i8Rbn4ki4r031v6N9or2WMZttRwN+lR72udrlvKdP4yRkiadQFmPvHVdz9tNZ9/Je8uWHVt5j2gm8H+AcPrYhJRfq6F0KoSKOwxY00ZNuIa1tYxwt9NO+abvPv51f2Un4SeNXY5x9ZOoNCu6HeKV+uaalUOlqGL2Ms/ZzKLT2sbQw0nHFlERuh0W0djJfIIsjMBL21Jeo7wZuX4mg6LCOIy4QF+Ux5CMmvqkbUEUVbBLjlcuuC0bMugjSJqK6UFJnokaHV2BAywK1U7BUvMZBHg6tPiOr0mHQmGgecY8a+mKb5w=',
            'gtm-session-start': '1732692805053',
            'gbi_sessionId': 'cm3zkk6eg000035j5d0kmxcvx',
            '_cavisit': '1936c8a0e79|',
            '_pin_unauth': 'dWlkPVpUbGhNRFF4WVRVdE1tRTNZUzAwTVdNM0xXSXlZakl0TlRJd09UUTRZMkkyTXprMw',
            'JSESSIONID': '0000NI6Mkvo-HVoucTL6CsioQ7q:clone616',
            'JAB_SESSION': '1aH0bQD93sjI%2BM36rjyIakt82xMWuwgby%2FVEHF7qAsrZJ2kxGpffMmCQbJiIHBwYDZtnA%2FCnijZ4ZlsMof4ED38NqzRpjGAq2Ew0zE4ajU2joe73JZc1o6kcSEBVKCQl',
            'WC_SESSION_ESTABLISHED': 'true',
            'WC_AUTHENTICATION_-1002': '-1002%2CAfTzczNoA61Fk0lWGCDqcpqH5bfvdI5jzR12A1HhwvM%3D',
            'WC_ACTIVEPOINTER': '-1%2C13452',
            'WC_USERACTIVITY_-1002': '-1002%2C13452%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C377314561%2C0oR0X%2BVLjrd8ZVPIVmwdr7qKgNLo18oyHECAq%2FvVdeYH6UBZMipgokjHGZWL6Ph0mZdWt7vDXYcVIZDErjAsoyGJjfcwlIxsWN6cxLeEy8w5HycgyWTrUlJE%2FwIevFk3aCrJfUqQ2eFeccsrezLyTQuevJRRbSyU%2BLKyC3Li46btDxpQ7L2LRZzKoNTpFKQTZLw23slMLtx9He6CGp8anCA1EyZe0V%2FmNh%2B0utiSct5ybo4LuB1VvmPEREdxlDNS',
            'WC_GENERIC_ACTIVITYDATA': '[7273191394%3Atrue%3Afalse%3A0%3AFmSau2GTb%2BHLhnlh1Bp0nh6DiHPicelyxhgHzZKsMBo%3D][com.ibm.commerce.context.entitlement.EntitlementContext|15507%2615507%26null%26-2000%26null%26null%26null][com.ibm.commerce.context.audit.AuditContext|1732606876493-87187][com.ibm.commerce.context.globalization.GlobalizationContext|-1%26USD%26-1%26USD][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.ibm.commerce.catalog.businesscontext.CatalogContext|14052%26null%26false%26false%26false][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.context.ExternalCartContext|null][CTXSETNAME|Store][com.ibm.commerce.context.base.BaseContext|13452%26-1002%26-1002%26-1][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null]',
            'bm_ss': 'ab8e18ef4e',
            '_abck': '2B7C8D0F9B380C37F837883A252F5BC2~0~YAAQzPXSFxq3uDWTAQAAAIyLbAy9H+Z87aZBN2lRTKYC7GJo0oPTHaLOZUeEUZSfNntKybwxwuuR+zqMAlbSa7VfgscrAq7ldxq3Eux31uTbUrzx6cUYDXdZ4ZcX6xAsENVi2a+YZAf25BAmtGgXAjKkGr1BZULoRdBVxK+XD++pNv58S4UGWN8bac4ZFz4HXOJanjeV99h4M4rMkJfP0NQsRIcSlQNCN7aoja8Y2Y6+jMpWBpCFCRv/F+bLo5CCrh0oOKwZbFWtTSu0LIAUHqNwKWsEHnxH+znYXeRWjiVhYANRB/5FlIjppVde9vcyKk/1crYd/qnVTtTdNsasVMy+uq4Slreocif0spG5o5ZvptfJtWepNm7L/J1Ww7/A/Ei6lUE4UImJpyd6uhBXy5zJFnXO8hHmkZs5ziprdg5xkiwcQMY3yzRlYXrm/k3rLY9F4svV18RNbQV0q4bPLlQgbLjY5+K6IF/QSRIBxtGqpiPsU9iWPiviCdzs5XGyeoIZkpFPb6Kdf8JGouVzIfgx5ov2pcM9LNfd0RFdjGktTRhfx78bMYykwW2BPtd5IqHU5cz4/CFZon8NFZmD8M9Gc82t5/KCKPhW1lzmQ5rZHpyoc6cns9X1MNV5xIXj7ljTEYZjxkgwIZ9fBg==~-1~-1~-1',
            'bm_s': 'YAAQzPXSFxu3uDWTAQAAAIyLbAK+zpBYqz52oVDiMJ/9mBspGRwPFD1kZ44pCy+9yxRMSm9b7i/+5uH6J/BEv3KIO373yMZEbAtY9d8rYXnGGy91JPXuzvlMP4EmwmeNReZ00Y5uajm9FQBZkEZWW7izRZhTFrdCK7NijMxQ9FQvT9k+XIg62RJZaTpN4DEPDNEqRVUuhAparbECTzuzBB46Yuzk3k5QCrFwGQsrvA846tevbQoMr+9Wbf1m4AUMwpKPsn/PfPR8U72rGSToIfhVBroJjhlFlzP7EI69sNE97mEutgmHOMZEpLTTwCpr4Cw2XXSkcW+xea9kp+6lTqopL7l/8qk=',
            'JABCART_INIT': '1732692808229',
            'JABUSERINFO': 'G%7C%7C%7C%7C%7C%7C%7C%7C',
            'kampyleUserSession': '1732692810097',
            'kampyleUserSessionsCount': '2',
            'JABSHOPSTOREID': '86',
            'JABSHOPSTOREZIPCODE': '01803',
            'BVBRANDSID': '632f8eb3-3012-4d5c-9db3-def1f44053b3',
            'bm_sz': 'E16D268627BA734480ECB3CB91942C5B~YAAQzPXSFwcEuTWTAQAAXF6MbBky4DnZL6UcyoDuMyBe5ZSwfRUYXXCCge2bYTXOe33iwqYONur5hjMQrfen9NHTOJlZB605VWW7QA1JNW2GcNsKPuGEcB5QC0GG1rMztx0lC7t7ieQ8w/iX3fQUByoCJlA0WYJsw+XKeuZGZD/0BPTOwmGiPJMfPk02OaOASQ9Hm9AIddIBXwaiHrP+WDmfByzHJq0jOYKUsP0FOdKD79ghN6gXSzVtyIPJYkrOHguTh2Xxkvyd2+Gwc38avf45qGxaq9Eo11iUepT0EQX4R3sLe65/Z3A/o4WlEtXwNVnNWVciTs5XENaETLchrzV07AAjFAv6GShZ1xOJz4jC5UEkyvxdScnkF/LtE37HVfHW7XkuKMXVu28qkZN1w9XM+Rb5lCZYcenv/Zf8DesVTu9UkQ==~3490629~4535619',
            'qb_session': '4:1:13::0:ZNsigiD:0:0:0:0:.josbank.com',
            'ABTastySession': 'mrasn=&lp=https%253A%252F%252Fwww.josbank.com%252F',
            'ABTasty': 'uid=9b836hz19e9x5351&fst=1732606780469&pst=1732606780469&cst=1732692804851&ns=2&pvt=7&pvis=4&th=',
            'cto_bundle': '5eC3Ql9MY3IxbmZNQnMwZ3YzUHI3JTJCYUhHJTJGYlBuN2padlolMkJDWTMzbEJrRyUyQiUyQko4NVY0RFlXR2lIZmdmYk1haDg1UHF2SjFiR0ZYQ0tqMXo3JTJCM1ZmVjlDNHlVcUJUJTJGeUo5eUYlMkY4Tm1UaUk4bTJhSlFVVU51Z3RTViUyRmpQb1V0RGUzWmtON2RUcSUyRkY1N2JSJTJGajUxS01Wc2FlelplQU5oeGlJR1JNUHNtWXdRc1lkRTdrWVlLbHl2V1pDODRZMWh2cTBFeWlZaGNwTm12dTNxOGZlSk80RGhBWXE2QSUzRCUzRA',
            'qb_permanent': '2sgxp57y2m4-0m3y5ccb9-5gj6pd8:7:4:2:2:0::0:1:0:BnRXs+:BnRst/:A::::27.109.10.106:ahmedabad:148387:india:IN:23.01:72.51:surat%20metropolitan%20region:356008:gujarat:10002:migrated|1732692863469:::ZNsiunt:ZNsigiD:0:0:0::0:0:.josbank.com:0',
            '_ga': 'GA1.2.1007224004.1732606782',
            'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Nov+27+2024+13%3A04%3A24+GMT%2B0530+(India+Standard+Time)&version=202405.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=6d0c8a1c-1e63-4fdf-8e80-514a2108839c&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&GPPCookiesCount=1&groups=TB01%3A1%2CTB03%3A1%2CTB02%3A1%2CTB04%3A1%2CTB05%3A0&AwaitingReconsent=false&intType=3&geolocation=IN%3BGJ',
            '_uetsid': '99962160abc911efab417becd3ee9e03',
            '_uetvid': '99965090abc911ef8c9937294b16a41b',
            '_br_uid_2': 'uid%3D4572450519744%3Av%3D12.0%3Ats%3D1732606782649%3Ahc%3D8',
            'kampyleSessionPageCounter': '3',
            'smtrrmkr': '638682897664272851%5E0193676a-d97a-4ea1-9cd4-ab97db63a36f%5E01936c8b-8d68-49eb-b64d-0aea6bcb61ed%5E0%5E27.109.10.106',
            'akavpau_wwwprd': '1732694090~id=14313bdbdb9898dd92906f9073019e28',
            'bm_sv': '063CFBD74A2EC3D7C0C561C61FC904A1~YAAQPnLBF8l7FzGTAQAAlQ+ZbBnvTRVG2Gi6KcYg/VuEW756FOMBGHBjqyzUqNnn/ntj1peXmgcX8B+gfJV6akcwQEWwZcAeAKb1AuwqcdKCq33c2IbPTwzcv6+rLkSMFTnvYuX9lCvMa8H5n+BDCmSwcAJKeWlyprSDg+Y/pbAMfVfQ/wbFs7x62POqzS+nJ0a5CCswcIgaLBoyikVd6f9qaH7byoQtVcervjsQbxmF3xce/AQO5fonxRVOxV3C3Dk=~1',
            '_ga_T6SWH68K36': 'GS1.1.1732692806.3.1.1732693694.60.0.0',
            '_gat_UA-55155345-1': '1',
            'RT': '"z=1&dm=www.josbank.com&si=5fefb69b-de21-4485-8741-3e72b05217b9&ss=m3zkk3cf&sl=4&tt=ast&bcn=%2F%2F684d0d48.akstat.io%2F&obo=1&nu=32i8k9gw&cl=m6fv"',
        }
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=1, i',
            'referer': 'https://www.josbank.com/store-locator',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

    def start_requests(self) -> Iterable[Request]:
        """Generates initial requests with cookies and headers."""
        fetch = f'''SELECT index_id, state, abbreviation, lat, lon FROM {self.input_table} where status = "pending"'''
        self.cursor.execute(fetch)
        results = self.cursor.fetchall()

        for result in results:
            index_id = result[0]
            state = result[1]
            abbreviation = result[2]
            lat = result[3]
            lon = result[4]

            params = {
                'catalogId': '14052',
                'langId': '-24',
                'radius': '500',
                'zip': state,
                'city': '',
                'state': abbreviation,
                'brand': 'JAB',
                'profileName': 'X_findStoreLocatorWithExtraFields',
                'latLong': f'{lat},{lon}'
            }

            _url = 'https://www.josbank.com/sr/search/resources/store/13452/storelocator/byProximity'
            url = _url + '?' + parse.urlencode(params)
            cb_kwargs = {'state': state, 'index_id': index_id}
            # Sending request on store-locator page
            yield scrapy.Request(url=url, cookies=self.cookies, headers=self.headers,
                                 dont_filter=True, cb_kwargs=cb_kwargs)

    def parse(self, response, **kwargs):
        response_dict = json.loads(response.text)
        stores_list = response_dict['DocumentList']
        print(f'Total stores:, {len(stores_list)}, in {kwargs['state']}')
        for store_dict in stores_list:
            item = JosABankItem()
            item['name'] = get_store_name(store_dict)
            item['city'] = get_city(store_dict)
            item['url'] = get_url(store_dict)
            item['store_no'] = get_store_no(store_dict)
            item['street'] = get_street(store_dict)
            item['state'] = get_state(store_dict)
            item['zip_code'] = get_zip_code(store_dict)
            item['latitude'] = get_latitude(response_dict)
            item['longitude'] = get_longitude(response_dict)
            item['county'] = 'N/A'
            item['phone'] = get_phone(store_dict)

            item['open_hours'] = get_open_hours(store_dict)

            item['provider'] = 'JoS A Bank'
            item['category'] = 'Apparel'
            item['updated_date'] = db_config.delivery_date
            item['country'] = 'USA'
            item['status'] = 'N/A'
            item['direction_url'] = get_direction_url(store_dict)
            print('item', item)
            print('*' * 50)
        #     yield item
        # print('-' * 100)


if __name__ == '__main__':
    execute(f'scrapy crawl {JosabankStoreSpider.name}'.split())
