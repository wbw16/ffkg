## 水利知识平台
- 基于知识图谱技术的流域防洪知识平台
- 本平台框架为Flask+JinJa2+MySQL+Redis+Neo4j+Dify API
- 配置文件为`config.py`所有配置项均位于此,'DEEPSEEK API'为本地Dify对应的API,本地的哦
- 本平台为本科毕业设计,不可用于真实环境中
## 使用方法
1. 配置环境
```shell
pip install -r requirements.txt
```
2. 初始化数据库
```shell
python init_db.py
```
3. 创建管理员账户
```shell
flask create-admin admin admin123
```
3. 运行项目
```shell
flask run --port=5000
```