"""Simple openaq to only depend on json, math, and requests (no dfs/plots)."""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
​
import json
import requests
import math
​
​
class ApiError(Exception):
    pass
​
class API(object):
    """Generic API wrapper object.
    """
    def __init__(self, **kwargs):
        self._key       = kwargs.pop('key', '')
        self._pswd      = kwargs.pop('pswd', '')
        self._version   = kwargs.pop('version', None)
        self._baseurl   = kwargs.pop('baseurl', None)
        self._headers   = {'content-type': 'application/json'}
​
    def _make_url(self, endpoint, **kwargs):
        """Internal method to create a url from an endpoint.
        :param endpoint: Endpoint for an API call
        :type endpoint: string
        :returns: url
        """
        endpoint = "{}/{}/{}".format(self._baseurl, self._version, endpoint)
​
        extra = []
        for key, value in kwargs.items():
            if isinstance(value, list) or isinstance(value, tuple):
                #value = ','.join(value)
                for v in value:
                    extra.append("{}={}".format(key, v))
            else:
                extra.append("{}={}".format(key, value))
​
        if len(extra) > 0:
            endpoint = '?'.join([endpoint, '&'.join(extra)])
​
        return endpoint
​
    def _send(self, endpoint, method='GET', **kwargs):
        """Make an API call of any method
​
        :param endpoint: API endpoint
        :param method: API call type. Options are PUT, POST, GET, DELETE
​
        :type endpoint: string
        :type method: string
​
        :returns: (status_code, json_response)
​
        :raises ApiError: raises an exception
        """
        auth = (self._key, self._pswd)
        url  = self._make_url(endpoint, **kwargs)
​
        if method == 'GET':
            resp = requests.get(url, auth=auth, headers=self._headers)
        else:
            raise ApiError("Invalid Method")
​
        if resp.status_code != 200:
            raise ApiError("A bad request was made: {}".format(resp.status_code))
​
        res = resp.json()
​
        # Add a 'pages' attribute to the meta data
        try:
            res['meta']['pages'] = math.ceil(res['meta']['found'] / res['meta']['limit'])
        except:
            pass
​
        return resp.status_code, res
​
    def _get(self, url, **kwargs):
        return self._send(url, 'GET', **kwargs)
​
class OpenAQ(API):
    """Create an instance of the OpenAQ API
​
    """
    def __init__(self, version='v1', **kwargs):
        """Initialize the OpenAQ instance.
​
        :param version: API version.
        :param kwargs: API options.
​
        :type version: string
        :type kwargs: dictionary
​
        """
        self._baseurl = 'https://api.openaq.org'
​
        super(OpenAQ, self).__init__(version=version, baseurl=self._baseurl)
​
    def cities(self, **kwargs):
        """Returns a listing of cities within the platform.
​
        :param country: limit results by a certain country
        :param limit: limit results in the query. Default is 100. Max is 10000.
        :param page: paginate through the results. Default is 1.
        :param order_by: order by one or more fields (ex. order_by=['country', 'locations']). Default value is 'country'
        :param sort: define the sort order for one or more fields (ex. sort='desc')
​
        :return: dictionary containing the *city*, *country*, *count*, and number of *locations*
​
        :type country: 2-digit ISO code
        :type limit: number
        :type order_by: string or list of strings
        :type sort: string
        :type page: number
        :type country: string or array of strings
        :type df: bool
        :type index: string
​
        :Example:
​
        >>> import openaq
        >>> api = openaq.OpenAQ()
        >>> status, resp = api.cities()
        >>> resp['results']
        [
            {
                "city": "Amsterdam",
                "country": "NL",
                "count": 21301,
                "locations": 14
            },
            {
                "city": "Badhoevedorp",
                "country": "NL",
                "count": 2326,
                "locations": 1
            },
            ...
        ]
        """
        return self._get('cities', **kwargs)
​
    def countries(self, **kwargs):
        """Returns a listing of all countries within the platform
​
        :param order_by: order by one or more fields (ex. order_by=['cities', 'locations']). Default value is 'country'
        :param sort: define the sort order for one or more fields (ex. sort='desc')
        :param limit: change the number of results returned. Max is 10000. Default is 100.
        :param page: paginate through results. Default is 1.
​
        :type order_by: string or list
        :type sort: string
        :type limit: int
        :type page: int
        :type df: bool
        :type index: string
​
        :return: dictionary containing the *code*, *name*, *count*, *cities*, and number of *locations*.
​
        :Example:
​
        >>> import openaq
        >>> api = openaq.OpenAQ()
        >>> status, resp = api.countries()
        >>> resp['results']
        [
            {
                "cities": 174,
                "code": "AT",
                "count": 121987,
                "locations": 174,
                "name": "Austria"
            },
            {
                "cities": 28,
                "code": "AU",
                "count": 1066179,
                "locations": 28,
                "name": "Australia",
            },
            ...
        ]
        """
        return self._get('countries', **kwargs)
​
    def latest(self, **kwargs):
        """Provides the latest value of each parameter for each location
​
        :param city: limit results by a certain city. Defaults to ``None``.
        :param country: limit results by a certain country. Should be a 2-digit
                        ISO country code. Defaults to ``None``.
        :param location: limit results by a city. Defaults to ``None``.
        :param parameter: limit results by a specific parameter. Options include [
                            pm25, pm10, so2, co, no2, o3, bc]
        :param has_geo: filter items that do or do not have geographic information.
        :param coordinates: center point (`lat`, `long`) used to get measurements within a
                                certain area. (Ex: coordinates=40.23,34.17)
        :param radius: radius (in meters) used to get measurements. Must be used with coordinates.
                        Default value is 2500.
        :param limit: change the number of results returned. Max is 10000. Default is 100.
        :param page: paginate through the results.
​
        :type city: string
        :type country: string
        :type location: string
        :type parameter: string
        :type has_geo: bool
        :type coordinates: string
        :type radius: int
        :type limit: int
        :type page: int
        :type df: bool
        :type index: string
​
        :return: dictionary containing the *location*, *country*, *city*, and number of *measurements*
​
        :Example:
​
        >>> import openaq
        >>> api = openaq.OpenAQ()
        >>> status, resp = api.latest()
        >>> resp['results']
        [
            {
                "location": "Punjabi Bagh",
                "city": "Delhi",
                "country": "IN",
                "measurements": [
                    {
                        "parameter": "so2",
                        "value": 7.8,
                        "unit": "ug/m3",
                        "lastUpdated": "2015-07-24T11:30:00.000Z"
                    },
                    {
                        "parameter": "co",
                        "value": 1.3,
                        "unit": "mg/m3",
                        "lastUpdated": "2015-07-24T11:30:00.000Z"
                    },
                    ...
                ]
                ...
            }
        ]
        """
        return self._get('latest', **kwargs)
​
    def locations(self, **kwargs):
        """Provides metadata about distinct measurement locations
​
        :param city: Limit results by one or more cities. Defaults to ``None``. Can define as a single city
                        (ex. city='Delhi'), a list of cities (ex. city=['Delhi', 'Mumbai']), or as a tuple
                        (ex. city=('Delhi', 'Mumbai')).
        :param country: Limit results by one or more countries. Should be a 2-digit
                        ISO country code as a string, a list, or a tuple. See `city` for details.
        :param location: Limit results by one or more locations.
        :param parameter: Limit results by one or more parameters. Options include [
                            pm25, pm10, so2, co, no2, o3, bc]
        :param has_geo: Filter items that do or do not have geographic information.
        :param coordinates: center point (`lat`, `long`) used to get measurements within a
                                certain area. (Ex: coordinates=40.23,34.17)
        :param nearest: get the X nearest number of locations to `coordinates`. Must be used
                        with coordinates. Wins over `radius` if both are present. Will add the
                        `distance` property to locations.
        :param radius: radius (in meters) used to get measurements. Must be used with coordinates.
                        Default value is 2500.
        :param order_by: order by one or more fields (ex. order_by=['country', 'count']). Default value is 'location'
        :param sort: define the sort order for one or more fields (ex. sort='desc')
        :param limit: change the number of results returned. Max is 10000. Default is 100.
        :param page: paginate through the results.
​
        :type city: string, array, or tuple
        :type country: string, array, or tuple
        :type location: string, array, or tuple
        :type parameter: string, array, or tuple
        :type has_geo: bool
        :type coordinates: string
        :type nearest: int
        :type radius: int
        :type order_by: string or list
        :type sort: string
        :type limit: int
        :type page: int
        :type df: bool
        :type index: string
​
        :return: a dictionary containing the *location*, *country*, *city*, *count*, *distance*,
                    *sourceName*, *sourceNames*, *firstUpdated*, *lastUpdated*, *parameters*, and *coordinates*
​
        :Example:
​
        >>> import openaq
        >>> api = openaq.OpenAQ()
        >>> status, resp = api.locations()
        >>> resp['results']
        [
            {
                "count": 4242,
                "sourceName": "Australia - New South Wales",
                "firstUpdated": "2015-07-24T11:30:00.000Z",
                "lastUpdated": "2015-07-24T11:30:00.000Z",
                "parameters": [
                    "pm25",
                    "pm10",
                    "so2",
                    "co",
                    "no2",
                    "o3"
                ],
                "country": "AU",
                "city": "Central Coast",
                "location": "wyong"
            },
            ...
        ]
        """
        return self...
