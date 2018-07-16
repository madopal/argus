#!/usr/bin/env

import os
import sys
import requests
import datetime

from argparse import ArgumentParser

BASE_URL='http://www.ctabustracker.com/bustime/api/v2/'

def parse_cmd_args():
    parser = ArgumentParser()
    parser.add_argument('choices',
                        help='possible actions',
                        choices=['routes', 'stops', 'schedule'])
    parser.add_argument('--api_key',
                        help='API key to use with API',
                        default=os.environ['CTA_API_KEY'])
    parser.add_argument('--dry_run',
                        help='do not commit results',
                        action='store_true')
    parser.add_argument('--stops',
                        help='which stops to return info for',
                        nargs='+')
    parser.add_argument('--routes',
                        help='which routes to return info for',
                        nargs='+')
    parser.add_argument('--direction',
                        help='which direction to use')

    args = parser.parse_args()

    return args


def get_bus_arrivals(api_key=None,
                     stops=None,
                     routes=None,
                     results=5):
    payload = {'key': api_key,
               'format': 'json',
               'stpid': stops,
               'rt': routes,
               'top': results}
    r = requests.get(BASE_URL + "getpredictions",
                     params=payload)

    return r

def get_bus_routes(api_key=None):
    payload = {'key': api_key,
               'format': 'json'}

    route_info = {}
    r = requests.get(BASE_URL + "getroutes",
                     params=payload)

    if r.status_code == 200:
        resp = r.json().get('bustime-response', {})
        route_list = resp.get('routes', [])
        for route in route_list:
            print 'Processing {}:{}'.format(route['rt'], route['rtnm'])
            route_info[route['rt']] = dict(route)
            route_info[route['rt']]['dirs'] = []
            payload['rt'] = route['rt']
            r2 = requests.get(BASE_URL + "getdirections",
                              params=payload)
            resp = r2.json().get('bustime-response', {})
            dirs = resp.get('directions', [])
            for dir_entry in dirs:
                route_info[route['rt']]['dirs'].append(dir_entry['dir'])
    return route_info


def get_bus_stops(api_key=None,
                  route=None,
                  direction=None):
    payload = {'key': api_key,
               'format': 'json',
               'rt': route,
               'dir': direction}
    r = requests.get(BASE_URL + "getstops",
                     params=payload)

    return r

args = parse_cmd_args()
if args.choices == 'schedule':
    cur_time = datetime.datetime.now()
    arrivals = get_bus_arrivals(api_key=args.api_key,
                                routes=args.routes,
                                stops=args.stops)
    for arrival in arrivals.json()['bustime-response']['prd']:
        new_time = datetime.datetime.strptime(arrival['prdtm'], "%Y%m%d %H:%M")
        print '{:2d}: {:.1f} min'.format(int(arrival['rt']),
                (new_time - cur_time).total_seconds() / 60)
elif args.choices == 'routes':
    route_info = get_bus_routes(api_key=args.api_key)
    for route, route_data in route_info.iteritems():
        if route in args.routes:
            print route_data
        
elif args.choices == 'stops':
    for route in args.routes:
        stop_info = get_bus_stops(api_key=args.api_key,
                                  route=route,
                                  direction=args.direction)
        print stop_info.json()
