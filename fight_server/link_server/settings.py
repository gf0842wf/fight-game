# -*- coding: utf-8 -*-

import platform

TCP_PORT = 6300             # 连接服务器端口，TCP和UDP采用同一个端口
UDP_PORT = 6300
TCP_CONN_TIMEOUT = 30       # TCP连接超时
TCP_DATA_TIMEOUT = 600      # TCP连接，数据超时
UDP_DATA_TIMEOUT = 600      # UDP数据超时

SSH_PORT = 6301             # SSH调试端口
SSH_PASSWD = "etc/passwd"   # SSH 用户名/密码

SERVER_NAME = platform.node()          # 机器名

# redis 服务器
MSG_REDIS = "redis://127.0.0.1:6379/0"
MSG_USER = "fight_link_server:user"
MSG_IN = "fight_link_server:%s:i" % SERVER_NAME
MSG_OUT = "fight_link_server:%s:o" % SERVER_NAME