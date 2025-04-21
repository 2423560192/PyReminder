# Redis数据导入说明

本文档说明如何将已有的Redis数据导入到Docker环境中的Redis容器中。

## 导入步骤

1. **确保Docker环境已启动**

   在使用导入脚本前，请确保Docker容器已经启动：

   ```bash
   # 启动Docker环境
   docker-compose up -d
   ```

2. **使用导入脚本**

   在项目根目录下，执行以下命令：

   ```bash
   # 赋予脚本执行权限
   chmod +x import_redis_data.sh
   
   # 执行导入脚本
   ./import_redis_data.sh
   ```

3. **验证数据导入**

   执行以下命令查看已导入的数据键：

   ```bash
   # 列出所有键
   docker-compose exec redis redis-cli -a 5201314 keys '*'
   
   # 查看某个具体的数据
   docker-compose exec redis redis-cli -a 5201314 HGETALL tokens
   ```

## 导入数据说明

本脚本将导入以下数据：

- **用户数据**：包含一个名为`diaomao`的用户账号
- **任务数据**：包含多个任务记录和对应的触发状态
- **通知账号配置**：包含"默认"、"涵涵"和"测试"三个通知账号
- **系统计数器**：设置任务ID计数器等

## 注意事项

1. 脚本会执行`FLUSHALL`命令，这将清空Redis中所有现有数据，请确保在导入前已备份重要数据。

2. 脚本中使用的Redis密码为环境变量文件中设置的密码（默认为`5201314`）。如果您修改了Redis密码，请相应更新脚本。

3. 导入完成后，应用程序应能立即使用这些数据，无需重启应用。 