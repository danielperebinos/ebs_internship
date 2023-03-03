import pycountry
import gettext
from django.core.cache import cache
from django.conf import settings

settings.configure()


class CountryData:
    CACHE_KEY = 'countrydata'

    def __init__(self, languages: list):
        self.languages = languages
        self.__data = []

    def translate_country(self, country):
        names = {}
        for language in self.languages:
            lang = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=[language])
            lang.install()
            _ = lang.gettext
            names[language] = _(country.name)

        return {'name_language': names}

    def get_country_info(self, country):
        return {
            'alpha_2': country.alpha_2,
            'phone_code': country.numeric,
        }

    def __create_dict(self):
        for country in list(pycountry.countries):
            country_info = self.get_country_info(country)
            country_info['name_language'] = self.translate_country(country)
            self.__data.append(country_info)
        return self.__data

    def get_data(self):
        if self.__data == []:
            from_cache = cache.get(self.CACHE_KEY)
            print(from_cache)
            if not from_cache:
                print('Created')
                self.__data = self.__create_dict()
                cache.set(self.CACHE_KEY, self.__data, 60 * 5)
            else:
                print('From cache')
                self.__data = from_cache

        print('Local')
        return self.__data
