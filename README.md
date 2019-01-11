# rap2-websocket

扩展开源接口管理工具 [RAP2](https://github.com/thx/rap2-delos) 支持 websocket 接口 mock，本工具会为 RAP2 中命名以 `ws` 开头的接口生成测试接口。

## 环境依赖

- Python 2
- [Websocketd](http://websocketd.com/)

## 使用

1. 安装 `websocktd`

2. 创建 websocktd 工作目录 `~/ws`，复制 `rap2-websocket` 下的所有文件到此目录，修改配置文件 `mock.conf`

    ```ini
    [main]
    server=http://127.0.0.1:8088
    ```

    `server` 为 `rap2-delos` 部署地址

3. 命令启动服务

    ```bash
    websocketd --port=9900 --dir=~/ws --devconsole 1>mock.log 2>&1 &
    ```

4. 创建 websocket 接口

    在 RAP2 创建 websocket 接口，要求 **websocket 接口必须命名 以 ws 开头，请求类型必须是 Get ，请求参数必须为非必选**。


5. 使用mock.py

    进入 mock.py 的 websocketd 的开发管理界面，使用命令 `mock`命令生成指定仓库的测试接口

    ```shell
        mock -i 17 -c 'koa.sid=7QC71YKGHTaOZUbeMHirZjicr0MN8-fX; koa.sid.sig=h0Q0zcHLVyJ_qQVxfwD_9pvXSLE'
    ```

## 问题

1. -bash: /root/ws/mock.py: /usr/bin/python2^M: bad interpreter: No such file or directory

    脚本编码转换

    ```shell
    dos2unix mock.py
    ```

2. SSL 支持

    使用 websocketd 启动参数[^1]
    ```ini
    --ssl               Listen for HTTPS socket instead of HTTP.
    --sslcert=FILE      All three options must be used or all of
    --sslkey=FILE       them should be omitted.
    ```

[^1]: https://github.com/joewalnes/websocketd/issues/316
