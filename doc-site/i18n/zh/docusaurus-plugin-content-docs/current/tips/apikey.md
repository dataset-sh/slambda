---
title: OpenAI API 密钥
description: "Slambda：如何加载 OpenAI API 密钥"
sidebar_position: 1
---

# OpenAI API 密钥

## 如何获得OpenAI API 密钥

[点击这里](https://platform.openai.com/account/api-keys)

## 如何用python加载OpenAI API 密钥

OpenAI官方有针对此内容的文章 [Best Practices for API Key Safety
](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety).

### 通过环境变量加载

#### 使用 `python-dotenv` 库

python-dotenv 从 .env 文件中读取键值对，并可以将它们设置为环境变量。它有助于开发遵循"12-Factor 原则"的应用程序（"12-Factor 原则" 是一组关于构建现代化、可扩展和可维护的软件应用程序的指导原则。这些原则最初由Heroku平台的创始人提出，并被广泛接受和应用于云原生应用开发。这些原则旨在帮助开发人员构建具有高度可移植性、可维护性和可扩展性的应用程序）[12-factor principles](https://12factor.net/config).

安装 python-dotenv

```shell
pip install python-dotenv
```

现在在当前目录中创建一个名为 `.env.local` 的文件，你应当也确保在 `.gitignore` 文件中包含了它。

```shell title=".env.local"
OPENAI_API_KEY = "sk-ThIsIsAFaKeKEY12345678990...."
```

现在我们可以安全地在 Python 中加载这个值

```python
import os
import openai
from dotenv import load_dotenv

load_dotenv('.env.local')  # 从 `.env` 中加载环境变量。

# 我们强烈建议您通过环境变量加载 OPENAI_API_KEY。
openai.api_key = os.getenv("OPENAI_API_KEY")

```

### 直接通过密钥值加载（不推荐）

直接加载 API 密钥值是提供 API 密钥的最直接方法。然而，重要的是要注意， **此方法强烈不推荐** 因为它有可能引入多个安全漏洞。

例如:

* 存在意外将 API 密钥上传到版本控制平台（如 Github）的风险，从而危及 API 密钥的机密性。

```python
import openai

openai.api_key = "sk-This_may_be_a_____SECURITY_RISK___"
# 我们认为这是一个**安全风险**
```



