# 护工预约平台

这是一个使用 Python (Flask) 和纯 HTML/CSS/JS 构建的简单护工预约平台。

## 功能

- **用户端**: 注册、登录、查看已批准的护工列表。
- **护工端**: 注册时上传身份信息和资质证书以供审核。
- **管理端**: 登录、查看待审核的护工列表、查看护工上传的文件，并批准或拒绝其申请。

## 如何运行

### 1. 准备工作

- 确保您的电脑上已经安装了 [Python 3](https://www.python.org/downloads/)。

### 2. 下载项目

- 将整个 `CaregivingApp` 文件夹下载到您的电脑上。

### 3. 安装依赖

打开您的终端（在 Windows 上是命令提示符或 PowerShell，在 macOS 或 Linux 上是终端），然后进入 `CaregivingApp` 文件夹：

```bash
cd path/to/CaregivingApp
```

接着，创建一个虚拟环境来安装项目所需的库：

```bash
python3 -m venv venv
```

激活虚拟环境：

- **在 macOS 或 Linux 上:**
  ```bash
  source venv/bin/activate
  ```
- **在 Windows 上:**
  ```bash
  venv\Scripts\activate
  ```

最后，安装所有依赖：

```bash
pip install -r backend/requirements.txt
```

### 4. 运行服务器

在同一个激活了虚拟环境的终端中，运行以下命令来启动后端服务器：

```bash
python backend/app.py
```

### 5. 访问应用

服务器启动后，您会看到类似以下的输出：

```
 * Running on http://127.0.0.1:8080
```

现在，打开您的网络浏览器，访问 **http://127.0.0.1:8080** 或 **http://localhost:8080**，即可开始使用该应用程序。

### 管理员账号

- **用户名**: `admin`
- **密码**: `password`
