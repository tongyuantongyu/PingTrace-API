# PingTrace-API
Simple api let you get ping and route info from your server to some destination.

You may adjust configuration in the program.
Originally write to cooperate with a bot to provide server info.

## Requirement
python(>=3.6.0) aiohttp
## API-Usage:
We recommend you to run this api with screen,because it's a listener,but it can't be daemon.<br>
When the program running,access http://yourIP:yourport/key/?apitype&parameter1=xxx&parameter2=xxx<br><br>
### Parameter Explain
#### yourport:
which you selected listen port,default is 4096.when both ipv4 and ipv6 available,it will listen at both ipv4 and ipv6.<br>
#### key:
your api key.<br><br>
#### apitype:
available value<br>
{pingapi,traceapi,traceapi_fast,traceapi_v6,traceapi_v6_fast}<br>
##### pingapi:
a tcp ping tool.when received the request,the api will tcping with both ipv4 and ipv6,then return both ipv4 and ipv6 latency.essential parameter:ip,port<br>
##### traceapi:
a traceroute tool.when received the request,the api will traceroute to target,then return the result (include the location display).essential parameter:ip<br>
##### traceapi_v6:
the same as traceapi,but force ipv6.<br>
##### traceapi_fast:
the same as traceapi,but no location searching(will not handed any ip to IP to location api)<br>

## Note

This api's default language is zh_CN,you can modify the location display code to let it showing what you want.<br>
Default IP format is 123:45:67:89,because like the xxx.xxx.xxx.xxx will be shown in blue and underline in QQ,so we force it shows with ":" instead "."<br>
