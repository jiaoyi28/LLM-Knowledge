## 1. 核心概念
- **镜像（Image）**：应用及其运行环境的只读模板。
- **容器（Container）**：镜像运行后的实例，轻量、隔离、启动快。
- **仓库（Registry）**：存放镜像的地方，如 Docker Hub。
- **Docker Engine**：负责镜像、容器、网络、卷的管理。
- **Docker Compose**：用配置文件管理多容器应用。

## 2. 安装 Docker
### Linux
常见做法是通过 Docker 官方仓库安装 Docker Engine，然后用：
```bash
docker --version
docker run hello-world
```
验证安装。

### Windows
通常安装 **Docker Desktop**，并启用 **WSL 2 backend**。安装后用：
```bash
docker version
docker run hello-world
```
验证。

## 3. 下载镜像
```bash
docker pull nginx:latest
docker pull redis:7
docker images
```
建议尽量指定版本号，而不是长期依赖 `latest`。

## 4. `docker run` 创建并运行容器
基本语法：
```bash
docker run [OPTIONS] IMAGE [COMMAND]
```

常用参数：
- `-d`：后台运行
- `--name`：指定容器名
- `-p`：端口映射
- `-it`：交互式终端
- `--rm`：退出后自动删除
- `-e`：环境变量
- `-v`：挂载目录或卷
- `--network`：指定网络
- `--restart`：重启策略

示例：
```bash
docker run -d --name mynginx -p 80:80 nginx:latest
```

## 5. 挂载卷
两种常见方式：

### 绑定挂载（Bind Mount）
把宿主机目录直接挂到容器里：
```bash
docker run -v /host/path:/container/path nginx
```

### 命名卷（Named Volume）
由 Docker 管理，适合数据库数据：
```bash
docker volume create mydata
docker run -v mydata:/var/lib/mysql mysql:8
```

### 一个常见坑

如果你把一个**空的宿主机目录**挂到容器的一个本来有内容的目录上，比如：

-v /empty-dir:/usr/share/nginx/html

那么容器里原本的 `/usr/share/nginx/html` 内容会被遮住，看起来像“没了”。  
这也是很多人第一次挂载静态目录时遇到的现象。
## 6. 进入容器调试
```bash
docker ps # 查看所有容器
docker logs -f 容器名 # 查看容器日志
docker exec -it 容器名 /bin/sh # 进入容器
```
常用来查看日志、检查进程、环境变量和配置文件。

## 7 容器停止与启动

```shell
docker start container_id
docker stop container_id
```
## 8. Docker 网络
### bridge
默认网络模式，适合同机容器互联。

### 自定义 bridge / 子网
```bash
docker network create --driver bridge --subnet 172.18.0.0/16 mynet
docker run -d --name app1 --network mynet nginx
```
适合项目内多个容器通过容器名互相访问。

### host
容器直接使用宿主机网络：
```bash
docker run -d --network host nginx
```
性能高，但隔离弱。

### none
容器无外部网络：
```bash
docker run -it --network none alpine sh
```
适合隔离测试。

## 9. Docker Compose
用 `compose.yaml` 管理多容器服务。

示例：
```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
  redis:
    image: redis:7
```

常用命令：
```bash
docker compose up -d
docker compose ps
docker compose logs -f
docker compose down
```

## 总结
掌握 Docker，先抓住这几件事：
1. 拉镜像：`docker pull`
2. 起容器：`docker run`
3. 看日志：`docker logs`
4. 进容器：`docker exec -it`
5. 挂载数据：`-v`
6. 配网络：`--network`
7. 多容器管理：`docker compose`
