import serial            # 导入 serial 模块，用于串口通信
import os                # 导入 os 模块，用于文件路径操作
import re                # 导入 re 模块，用于正则表达式解析数据
import mysql.connector   # 导入 mysql.connector 模块，用于 MySQL 数据库操作
from mysql.connector import Error  # 从 mysql.connector 导入 Error 类，用于捕获数据库异常

# 配置并初始化串口
try:
    port = "COM3"        # 定义串口号为 COM3，与 ESP8266 连接
    baudrate = 115200    # 设置波特率为 115200，与嵌入式程序一致
    ser = serial.Serial(port, baudrate, timeout=1)  # 创建串口对象，超时时间 1 秒
except serial.SerialException as e:  # 捕获串口初始化异常
    print(f"Error opening serial port: {e}")  # 打印错误信息
    exit(1)              # 如果串口初始化失败，退出程序，返回错误码 1

# 配置并连接 MySQL 数据库
try:
    conn = mysql.connector.connect(
        host="localhost",       # 数据库主机地址，本地运行
        user="root",            # 数据库用户名
        password="123456",      # 数据库密码
        database="daily_data",  # 使用的数据库名
        autocommit=True         # 启用自动提交，避免手动 commit 的同步问题
    )
    cursor = conn.cursor(prepared=True)  # 使用预编译游标，提高稳定性
    print("MySQL connection established.")  # 连接成功时打印提示
except Error as e:       # 捕获数据库连接异常
    print(f"Error connecting to MySQL: {e}")  # 打印错误信息
    exit(1)              # 如果数据库连接失败，退出程序，返回错误码 1

# 定义表名和建表语句
table_name = "temperature_data"  # 定义数据库表名
create_table_query = """
CREATE TABLE IF NOT EXISTS `{}` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_temperature FLOAT NOT NULL,
    body_temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;
""".format(table_name)  # 使用 format 替代 f-string，避免潜在问题

try:
    cursor.execute(create_table_query)  # 执行建表语句，如果表不存在则创建
    # 由于 autocommit=True，无需显式 conn.commit()
    print(f"Table `{table_name}` checked/created.")  # 打印表创建成功的提示
except Error as e:         # 捕获建表异常
    print(f"Error creating table: {e}")  # 打印错误信息
    if conn:
        conn.rollback()    # 如果失败，回滚操作
    exit(1)                # 退出程序，避免后续操作失败

# 获取当前表的最大 ID
try:
    cursor.execute(f"SELECT MAX(id) FROM `{table_name}`")  # 查询表中最大 ID
    result = cursor.fetchone()  # 获取查询结果
    max_id = result[0] if result[0] is not None else 0  # 如果结果为 None，则设为 0
    print(f"Current max ID: {max_id}")  # 打印当前最大 ID，用于初始化验证
except Error as e:         # 捕获查询异常
    print(f"Error fetching max ID: {e}")  # 打印错误信息
    if conn:
        conn.rollback()
    exit(1)

# 配置日志文件路径并打开
file_path = os.path.join(os.getcwd(), "temp_log.txt")  # 构造日志文件路径，位于当前工作目录
try:
    file = open(file_path, "a", buffering=1)  # 以追加模式打开文件，行缓冲实时写入
except IOError as e:       # 捕获文件打开异常
    print(f"Error opening file: {e}")  # 打印错误信息
    exit(1)                # 如果文件打开失败，退出程序，返回错误码 1

print("Receiving data...")  # 打印提示，表示开始接收数据

# 主循环，持续接收和处理串口数据
try:
    while True:            # 无限循环，保持程序运行
        if ser.in_waiting > 0:  # 检查串口是否有数据等待读取
            data = ser.readline().decode('utf-8').strip()  # 读取一行数据，解码为 UTF-8，去除首尾空白
            if data:           # 如果读取到非空数据
               # print(f"Received: {data}")  # 打印接收到的数据
                file.write(data + "\n")     # 将数据写入日志文件
                file.flush()                # 立即刷新文件，确保数据写入磁盘

                if "ERROR" in data:  # 检查数据是否包含 "ERROR" 字符串
                    continue         # 如果是错误信息，跳过本次循环，不处理

                # 使用正则表达式解析数据
                room_match = re.search(r"Room: (\d+\.\d+) C", data)  # 提取室内温度
                body_match = re.search(r"Body: (\d+\.\d+) C", data)  # 提取体温
                hum_match = re.search(r"Hum: (\d+\.\d+) %", data)    # 提取湿度

                if room_match and body_match and hum_match:  # 如果所有数据都成功解析
                    room_temp = float(room_match.group(1))   # 将室内温度转换为浮点数
                    body_temp = float(body_match.group(1))   # 将体温转换为浮点数
                    humidity = float(hum_match.group(1))     # 将湿度转换为浮点数
                    try:
                        # 插入数据到数据库
                        insert_query = "INSERT INTO `{}` (room_temperature, body_temperature, humidity) VALUES (%s, %s, %s)".format(table_name)
                        cursor.execute(insert_query, (room_temp, body_temp, humidity))  # 执行插入语句，使用参数化查询
                        # 由于 autocommit=True，无需显式 conn.commit()
                        cursor.execute(f"SELECT MAX(id) FROM `{table_name}`")  # 查询最新 ID
                        new_max_id = cursor.fetchone()[0]  # 获取最新 ID
                        print(f"Inserted: Room {room_temp}, Body {body_temp}, Hum {humidity}, New ID: {new_max_id}")  # 打印插入成功的提示
                    except Error as e:  # 捕获插入异常
                        print(f"Database error: {e}")  # 打印错误信息
                        if conn:
                            conn.rollback()  # 如果失败，回滚操作
except KeyboardInterrupt:  # 捕获用户中断（Ctrl+C）
    print("Stopped by user")  # 打印用户停止提示
finally:                   # 清理资源，确保程序退出时释放所有占用
    if 'file' in locals():  # 检查 file 是否已定义
        file.close()        # 关闭日志文件
    if 'ser' in locals():   # 检查 ser 是否已定义
        ser.close()         # 关闭串口
    if 'cursor' in locals():  # 检查 cursor 是否已定义
        cursor.close()      # 关闭数据库游标
    if 'conn' in locals():    # 检查 conn 是否已定义
        conn.close()        # 关闭数据库连接
    print("Resources closed.")  # 打印资源释放完成的提示