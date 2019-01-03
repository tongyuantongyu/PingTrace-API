import socket
import time
import re
from timeit import default_timer as timer
import aiohttp
from aiohttp import web
import subprocess
import json
import asyncio

MAX_TIME = 10
TIME_OUT = 1
geo_lookup_timeout = 20
FORCE_V4 = True
LISTENING_PORT = 4096
hd = {'User-Agent': 'BestTrace/Windows V3.6.5'}
start = 2
api_key = 'example'

routes = web.RouteTableDef()


class NoConnection(Exception):
    pass


class ConnectTypeUnavailableError(Exception):
    pass


class SelfCheckFail(Exception):
    pass


def connector(ping_host, ping_port, con_type=4):
    if con_type == 4:
        sock = socket.AF_INET
    elif con_type == 6:
        sock = socket.AF_INET6
    else:
        raise AttributeError('Not defined connection type.')
    s = socket.socket(sock, socket.SOCK_STREAM)
    s.settimeout(TIME_OUT)
    t0 = timer()
    try:
        s.connect((ping_host, int(ping_port)))
        s.shutdown(socket.SHUT_RD)
        t1 = timer()
        return True, t1 - t0
    except socket.timeout:
        return False, 0
    except (socket.gaierror, OSError):
        raise ConnectTypeUnavailableError


def pinger(ping_host, ping_port, times, con_type=4):
    results = []
    for i in range(min(times, MAX_TIME)):
        result, timespan = connector(ping_host, ping_port, con_type)
        if result:
            results.append(timespan)
    results.pop(0)
    if results:
        return sum(results) * 1000 / len(results)
    return -1


def handler(ping_host, ping_port, con_type=4):
    try:
        result = pinger(ping_host, ping_port, 4, con_type)
    except ConnectTypeUnavailableError:
        result = '不支持'
    except:
        result = '未知错误'
    else:
        if result == -1:
            result = '超时'
        else:
            result = '{:.2f}ms'.format(result)
    try:
        print('[{0}] IPv{1} {2}:{3} -> {4}'.format(time.strftime("%H:%M:%S", time.localtime()), con_type, ping_host, ping_port, result))
    except UnicodeEncodeError:
        print('[{0}] IPv{1} {2}:{3} -> FAIL'.format(time.strftime("%H:%M:%S", time.localtime()), worker.__name__, ping_host, ping_port))
    return result


async def get_url(url, session):
    async with session.get(url) as response:
        content = await response.read()
    return content


async def get_info(ip, session):
    result = await get_url('https://btapi.ipip.net/host/info?ip={}&lang=CN'.format(ip), session)
    j = json.loads(result)
    asn = j['as']
    location = []
    for item in j['area'].split('\t')[:-2]:
        if item != '' and item not in location:
            location.append(item)
    location = ' '.join(location).replace('.', ':')
    return asn + ' ' + location


async def gen_return(result, reverse=True):
    async with aiohttp.ClientSession(headers=hd) as session:
        tasks = []
        output = []
        for line in result:
            if reverse:
                ip_r = line[1].split(' (')
                ip = ip_r[1][:-1]
                if ip == ip_r[0]:
                    ip_view = ip
                else:
                    ip_view = '{}({})'.format(ip, ip_r[0])
            else:
                ip = line[1]
                ip_view = line[1]
            output.append((line[0], ip_view.replace('.', ':'), line[2]))
            task = asyncio.ensure_future(get_info(ip, session))
            tasks.append(task)
        scheduled = asyncio.gather(*tasks)
        got_info = await scheduled
        final = '\n'.join(['{} {} {} {}'.format(*line, info) for line, info in zip(output, got_info)])
        return final


def gen_return_fast(result, reverse=True):
    output = []
    for line in result:
        if reverse:
            ip_r = line[1].split(' (')
            ip = ip_r[1][:-1]
            if ip == ip_r[0]:
                ip_view = ip
            else:
                ip_view = '{}({})'.format(ip, ip_r[0])
        else:
            ip_view = line[1]
        output.append((line[0], line[2].replace(' ', ''), ip_view.replace('.', ':')))
    final = '\n'.join(['{} {} {}'.format(*line) for line in output])
    return final


async def gen_return_json(result):
    final = [[int(num), ip, float(latency.split(' ')[0])] for num, ip, latency in result]
    return final


async def trace_handler(host, fast=False, con_type=4, start_ttl=start, reverse=True):
    command = ['traceroute', '-q', '1', '-w', '1', '-f', str(start_ttl)]
    if con_type == 6:
        command.append('-6')
    if not reverse:
        command.append('-n')
    command.append(host)
    try:
        print('[{}] traceroute {} -> START'.format(time.strftime("%H:%M:%S", time.localtime()), host))
        result_raw = subprocess.check_output(command)
    except subprocess.CalledProcessError:
        print('[{}] traceroute {} -> FAIL'.format(time.strftime("%H:%M:%S", time.localtime()), host))
        return web.Response(text='无法解析域名。')
    else:
        result_list = [line.split('  ') for line in result_raw.decode().split('\n')[1:-1] if '*' not in line]
        if fast:
            print('[{}] traceroute_fast {} -> SUCCESS'.format(time.strftime("%H:%M:%S", time.localtime()), host))
            return web.Response(text=gen_return_fast(result_list, reverse))
        else:
            try:
                result = await asyncio.wait_for(gen_return(result_list, reverse), geo_lookup_timeout)
                print('[{}] traceroute {} -> SUCCESS'.format(time.strftime("%H:%M:%S", time.localtime()), host))
            except asyncio.TimeoutError:
                result = gen_return_fast(result_list, reverse)
                print('[{}] traceroute_fallback {} -> SUCCESS'.format(time.strftime("%H:%M:%S", time.localtime()), host))
            return web.Response(text=result)


def check(r):
    if r == '不支持' or r == '超时':
        return False
    elif r == '未知错误':
        raise SelfCheckFail
    else:
        return True


def fil_para(coro):
    async def inner(*args):
        try:
            return await coro(*args)
        except KeyError:
            return web.Response(text='错误的请求指令。请检查API调用')
    return inner


print('---- [ SELF CHECK ] ----')
test_list = [
    ('216.218.186.2', '80'),
    ('www.he.net', '80'),
]
test_list_6 = [
    ('2001:470:0:76::2', '80'),
    ('www.he.net', '80')
]
if all(check(handler(*test)) for test in test_list):
    V4_AVAL = True
    print('V4 - OK')
else:
    V4_AVAL = False
    print('V4 - BAD')
if all(check(handler(*test, 6)) for test in test_list_6):
    V6_AVAL = True
    print('V6 - OK')
else:
    V6_AVAL = False
    print('V6 - BAD')
if not (V4_AVAL or V6_AVAL):
    raise NoConnection


def gen_response(ping_host, ping_port):
    res_list = []
    if V4_AVAL and V6_AVAL:
        res_list.append('IPv4:' + handler(ping_host, ping_port))
    else:
        res_list.append(handler(ping_host, ping_port))
    if V6_AVAL:
        res_list.append('IPv6:' + handler(ping_host, ping_port, 6))
    return ', '.join(res_list)


@routes.get('/' + api_key + '/pingapi')
@fil_para
async def processor(request):
    host = request.query['ip']
    port = request.query['port']
    return web.Response(text=gen_response(host, port))


@routes.get('/' + api_key + '/traceapi')
@fil_para
async def processor(request):
    host = request.query['ip']
    return await trace_handler(host)


@routes.get('/' + api_key + '/traceapi_fast')
@fil_para
async def processor(request):
    host = request.query['ip']
    return await trace_handler(host, fast=True)


@routes.get('/' + api_key + '/traceapi_v6')
@fil_para
async def processor(request):
    host = request.query['ip']
    return await trace_handler(host, con_type=6)


@routes.get('/' + api_key + '/traceapi_v6_fast')
@fil_para
async def processor(request):
    host = request.query['ip']
    return await trace_handler(host, fast=True, con_type=6)


@routes.get('')
async def refuser(*a):
    raise web.HTTPForbidden()


app = web.Application()
app.add_routes(routes)
if V6_AVAL and not FORCE_V4:
    web.run_app(app, host='::', port=LISTENING_PORT)
else:
    web.run_app(app, port=4096)
