# 6BloodSugar.device.py 创建每天日期的蓝牙数据库

# 导入需要的模块
import re  # 用于正则表达式匹配
import pandas as pd  # 用于数据处理和保存
import os  # 用于文件和路径操作
import mysql.connector  # 用于数据库连接和操作
from datetime import datetime  # 用于获取当前时间

# 设置日志文件路径
log_file_path = r'C:\Users\maikojoke\Desktop\小米手环数据自动化导出代码\health\apps\com.mi.health\ef\log\BloodSugar.device.log'

# 设置输出的Excel文件路径，与数据库表名格式一致
output_dir = r'C:\Users\maikojoke\Desktop\小米手环数据自动化导出代码\craw file'
current_date = datetime.now().strftime('%Y_%m_%d')  # 获取当前日期，格式为 '年_月_日'，如：2025_02_22
output_filename = f"{current_date}_bloodsugar.device.xlsx"
output_path = os.path.join(output_dir, output_filename)

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"创建输出目录: {output_dir}")

# MySQL 数据库连接配置
db_host = "localhost"  # 数据库主机地址
db_user = "root"  # 数据库用户名
db_password = "123456"  # 数据库密码
db_name = "daily_data"  # 数据库名称，指示存储日志数据的数据库

# 定义正则表达式模式，用于从日志行中提取时间戳、状态、消息
pattern = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d+\|.*?\|I\|.*?\|onResultFlowState\(\) called with: "
    r"status = (?P<status>\w+), msg = (?P<message>[^,]+)"
)

# 存储提取数据的列表
extracted_data = []

# 尝试读取日志文件，并从中提取所需的数据
try:
    # 打开日志文件并逐行读取
    with open(log_file_path, 'r', encoding='utf-8-sig') as file:
        # 遍历每一行
        for line in file:
            # 使用正则表达式匹配每一行的数据
            match = pattern.search(line)
            # 如果匹配到数据
            if match:
                # 获取时间戳并确保只保留到秒
                timestamp = match.group("timestamp")
                timestamp = timestamp.split('.')[0]  # 去掉毫秒部分，保留到秒

                # 将提取的数据添加到列表中
                extracted_data.append({
                    "Timestamp": timestamp,  # 精确到秒的时间戳
                    "Status": match.group("status"),  # 提取的状态
                    "Message": match.group("message").strip()  # 提取消息并去除多余的空白字符
                })

    # 将提取的数据转换为 pandas DataFrame 格式，方便后续处理
    new_data_df = pd.DataFrame(extracted_data)

    # 打印 DataFrame 的前几行，确认内容
    print(new_data_df.head())

    # 连接到 MySQL 数据库
    conn = mysql.connector.connect(
        host=db_host,  # 数据库主机地址
        user=db_user,  # 数据库用户名
        password=db_password,  # 数据库密码
        database=db_name  # 使用的数据库名称
    )
    cursor = conn.cursor()  # 创建游标，用于执行SQL命令

    # 创建表格名称，根据当前日期命名
    table_name = f"{current_date}_bloodsugar.device"

    # 检查表格是否存在
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()

    # 如果表格不存在，则创建新的表格
    if not result:
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,  # 自增主键
            timestamp DATETIME NOT NULL,  # 时间戳，非空
            status VARCHAR(50),  # 状态字段，最大长度50字符
            message TEXT,  # 消息字段
            log_type VARCHAR(50)  -- 用于区分不同类型的日志（作为子表格的标识）
        );
        """
        cursor.execute(create_table_sql)  # 执行创建表格的SQL命令

    # 将数据插入到表格中，避免重复插入相同的时间戳
    for _, row in new_data_df.iterrows():
        # 插入时，避免重复插入相同的时间戳
        insert_sql = f"""
        INSERT INTO `{table_name}` (timestamp, status, message, log_type)
        SELECT %s, %s, %s, 'BloodSugar'
        WHERE NOT EXISTS (
            SELECT 1 FROM `{table_name}` WHERE timestamp = %s
        )
        """
        cursor.execute(insert_sql, (row['Timestamp'], row['Status'], row['Message'], row['Timestamp']))  # 执行插入数据的SQL命令

    # 提交事务
    conn.commit()

    print(f"数据成功插入到 `{table_name}` 表格。")

    # 将数据同步到 Excel 文件
    new_data_df.to_excel(output_path, index=False)
    print(f"数据提取并保存到 {output_path} 成功！")

# 捕获文件未找到的错误
except FileNotFoundError as fnf_error:
    print(f"Error: The file {log_file_path} was not found. Please check the path and try again.")
    print(f"Error details: {fnf_error}")  # 输出错误详细信息

# 捕获数据库操作相关的错误
except mysql.connector.Error as db_error:
    print(f"Database error: {db_error}")
    print(f"Error details: {db_error}")  # 输出错误详细信息

# 捕获其他可能发生的错误
except Exception as general_error:
    print(f"An error occurred while processing the log file: {general_error}")

# 最终步骤，确保在完成后关闭数据库连接
finally:
    # 确保数据库连接被关闭
    if 'conn' in locals() and conn.is_connected():
        cursor.close()  # 关闭游标
        conn.close()  # 关闭数据库连接
        print("数据库连接已关闭。")  # 提示数据库连接已关闭