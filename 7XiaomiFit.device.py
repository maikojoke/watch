# 7XiaomiFit.device.py 创建每天日期的设备数据

# 导入需要的模块
import re  # 引入正则表达式模块
import json  # 引入 JSON 模块，用于解析日志中的 JSON 数据
import pandas as pd  # 引入 pandas 模块，用于处理数据
import mysql.connector  # 引入 MySQL 连接模块
from datetime import datetime  # 引入 datetime 模块，处理时间相关操作
import os  # 引入 os 模块，用于文件和目录操作

# 设置日志文件路径和 Excel 输出路径
log_file_path = r'C:\Users\maikojoke\Desktop\小米手环数据自动化导出代码\health\apps\com.mi.health\ef\log\XiaomiFit.device.log'  # 日志文件路径
excel_output_dir = r'C:\Users\maikojoke\Desktop\小米手环数据自动化导出代码\craw file'  # Excel 输出文件夹路径

# 确保输出目录存在
if not os.path.exists(excel_output_dir):  # 如果输出目录不存在
    os.makedirs(excel_output_dir)  # 创建输出目录
    print(f"创建输出目录: {excel_output_dir}")  # 输出目录创建信息

# 设置 MySQL 数据库连接配置
db_host = "localhost"  # 数据库主机地址
db_user = "root"  # 数据库用户名
db_password = "123456"  # 数据库密码
db_name = "daily_data"  # 数据库名称

# 定义正则表达式模式以匹配日志中的时间戳和 dailyDataReport 部分
timestamp_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')  # 匹配时间戳的正则表达式
daily_report_pattern = re.compile(r'dailyDataReport\((\{.*?\})\)')  # 匹配 dailyDataReport 的正则表达式

# 解析每一行日志
def parse_log_line(line):
    timestamp_match = timestamp_pattern.search(line)  # 查找时间戳
    if not timestamp_match:  # 如果没有找到时间戳，返回 None
        return None

    timestamp_str = timestamp_match.group(1)  # 获取时间戳字符串
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')  # 转换时间戳字符串为 datetime 对象

    match = daily_report_pattern.search(line)  # 查找 dailyDataReport 部分
    if not match:  # 如果没有找到，返回 None
        return None

    try:
        data = json.loads(match.group(1))  # 解析 JSON 数据
        return {  # 返回一个字典，包含日志中提取的数据
            'timestamp': timestamp_str,  # 时间戳
            'avgHr': data.get('avgHr'),  # 平均心率
            'avgSpo2': data.get('avgSpo2'),  # 平均血氧
            'avgStress': data.get('avgStress'),  # 平均压力
            'calories': data.get('calories'),  # 消耗的卡路里
            'dayMediumIntensityVitality': data.get('dayMediumIntensityVitality'),  # 日均中等强度活力
            'hr': data.get('hr'),  # 心率数据
            'maxHr': data.get('maxHr'),  # 最大心率
            'maxHrTime': datetime.fromtimestamp(data.get('maxHrTime', 0)) if data.get('maxHrTime') else None,  # 最大心率时间
            'maxSpo2': data.get('maxSpo2'),  # 最大血氧
            'maxSpo2Time': datetime.fromtimestamp(data.get('maxSpo2Time', 0)) if data.get('maxSpo2Time') else None,  # 最大血氧时间
            'maxStress': data.get('maxStress'),  # 最大压力
            'minHr': data.get('minHr'),  # 最小心率
            'minHrTime': datetime.fromtimestamp(data.get('minHrTime', 0)) if data.get('minHrTime') else None,  # 最小心率时间
            'minSpo2': data.get('minSpo2'),  # 最小血氧
            'minSpo2Time': datetime.fromtimestamp(data.get('minSpo2Time', 0)) if data.get('minSpo2Time') else None,  # 最小血氧时间
            'minStress': data.get('minStress'),  # 最小压力
            'restHr': data.get('restHr'),  # 静息心率
            'steps': data.get('steps'),  # 步数
            'suggestActivityDuration': data.get('suggestActivityDuration'),  # 推荐活动时长
            'suggestActivityType': data.get('suggestActivityType'),  # 推荐活动类型
            'time': datetime.fromtimestamp(data.get('time', 0)) if data.get('time') else None,  # 活动时间
            'total7daysVitality': data.get('total7daysVitality'),  # 过去7天的活力总和
            'totalCal': data.get('totalCal'),  # 总卡路里
            'trainingLoadLevel': data.get('trainingLoadLevel'),  # 训练负荷等级
            'validStand': str(data.get('validStand')) if data.get('validStand') is not None else None,  # 转换为字符串或 NULL
            'zoneOffsetInSec': data.get('zoneOffsetInSec')  # 时区偏移
        }
    except json.JSONDecodeError:  # 如果 JSON 解码失败
        print(f"Failed to decode JSON in line: {line}")  # 输出错误信息
        return None  # 返回 None

# 主程序
try:
    # 获取当前日期
    current_date = datetime.now().strftime('%Y_%m_%d')  # 当前日期（格式：年_月_日）
    table_name = f"{current_date}_xiaomifit_device"  # 表名格式：当前日期_xiaomifit_device

    # 更新 Excel 输出路径为与数据库表名相同
    excel_output_path = os.path.join(excel_output_dir, f"{table_name}.xlsx")  # Excel 输出文件路径

    # 读取日志文件并解析数据
    data = []
    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parsed_data = parse_log_line(line)  # 调用函数解析每一行日志
            if parsed_data:
                log_date = datetime.strptime(parsed_data['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%Y_%m_%d')
                if log_date == current_date:  # 如果日志日期与当前日期匹配
                    data.append(parsed_data)

    if not data:  # 如果没有符合当天日期的数据
        print("没有符合当天日期的数据可处理。")
        exit()

    # 转换为 DataFrame
    df = pd.DataFrame(data)  # 将数据转为 pandas DataFrame 格式
    print("提取的数据（前5行）：")
    print(df.head())  # 输出前5行数据查看

    # 连接数据库
    conn = mysql.connector.connect(  # 创建数据库连接
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()  # 创建数据库游标

    # 检查表是否存在
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    if cursor.fetchone():  # 如果表已经存在
        # 表存在，检查并修改 validStand 字段类型
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = {row[0]: row[1] for row in cursor.fetchall()}  # 获取表的列信息
        if 'validStand' in columns and 'varchar' not in columns['validStand'].lower():  # 如果 validStand 字段类型不是 VARCHAR
            alter_sql = f"""
            ALTER TABLE `{table_name}`
            MODIFY COLUMN validStand VARCHAR(255);
            """
            cursor.execute(alter_sql)  # 修改字段类型
            print(f"已修改 `{table_name}` 表的 validStand 字段为 VARCHAR(255)。")
    else:  # 如果表不存在，创建新表
        create_table_sql = f"""
        CREATE TABLE `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL UNIQUE,
            avgHr INT,
            avgSpo2 INT,
            avgStress INT,
            calories INT,
            dayMediumIntensityVitality INT,
            hr INT,
            maxHr INT,
            maxHrTime DATETIME,
            maxSpo2 INT,
            maxSpo2Time DATETIME,
            maxStress INT,
            minHr INT,
            minHrTime DATETIME,
            minSpo2 INT,
            minSpo2Time DATETIME,
            minStress INT,
            restHr INT,
            steps INT,
            suggestActivityDuration INT,
            suggestActivityType VARCHAR(50),
            time DATETIME,
            total7daysVitality INT,
            totalCal INT,
            trainingLoadLevel INT,
            validStand VARCHAR(255),
            zoneOffsetInSec INT
        );
        """
        cursor.execute(create_table_sql)  # 创建新表
        print(f"表格 `{table_name}` 创建成功！")

    # 插入数据并避免重复
    insert_sql = f"""
    INSERT INTO `{table_name}` (
        timestamp, avgHr, avgSpo2, avgStress, calories, dayMediumIntensityVitality,
        hr, maxHr, maxHrTime, maxSpo2, maxSpo2Time, maxStress, minHr, minHrTime,
        minSpo2, minSpo2Time, minStress, restHr, steps, suggestActivityDuration,
        suggestActivityType, time, total7daysVitality, totalCal, trainingLoadLevel,
        validStand, zoneOffsetInSec
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE  # 避免重复数据
        avgHr = VALUES(avgHr),
        avgSpo2 = VALUES(avgSpo2),
        avgStress = VALUES(avgStress),
        calories = VALUES(calories),
        dayMediumIntensityVitality = VALUES(dayMediumIntensityVitality),
        hr = VALUES(hr),
        maxHr = VALUES(maxHr),
        maxHrTime = VALUES(maxHrTime),
        maxSpo2 = VALUES(maxSpo2),
        maxSpo2Time = VALUES(maxSpo2Time),
        maxStress = VALUES(maxStress),
        minHr = VALUES(minHr),
        minHrTime = VALUES(minHrTime),
        minSpo2 = VALUES(minSpo2),
        minSpo2Time = VALUES(minSpo2Time),
        minStress = VALUES(minStress),
        restHr = VALUES(restHr),
        steps = VALUES(steps),
        suggestActivityDuration = VALUES(suggestActivityDuration),
        suggestActivityType = VALUES(suggestActivityType),
        time = VALUES(time),
        total7daysVitality = VALUES(total7daysVitality),
        totalCal = VALUES(totalCal),
        trainingLoadLevel = VALUES(trainingLoadLevel),
        validStand = VALUES(validStand),
        zoneOffsetInSec = VALUES(zoneOffsetInSec)
    """

    # 插入每行数据
    for _, row in df.iterrows():
        row = row.where(pd.notnull(row), None)  # 将 NaN 替换为 None
        values = (
            row['timestamp'], row['avgHr'], row['avgSpo2'], row['avgStress'], row['calories'],
            row['dayMediumIntensityVitality'], row['hr'], row['maxHr'], row['maxHrTime'],
            row['maxSpo2'], row['maxSpo2Time'], row['maxStress'], row['minHr'], row['minHrTime'],
            row['minSpo2'], row['minSpo2Time'], row['minStress'], row['restHr'], row['steps'],
            row['suggestActivityDuration'], row['suggestActivityType'], row['time'],
            row['total7daysVitality'], row['totalCal'], row['trainingLoadLevel'],
            row['validStand'], row['zoneOffsetInSec']
        )
        try:
            cursor.execute(insert_sql, values)  # 执行插入操作
        except mysql.connector.Error as db_err:
            print(f"数据库插入错误: {db_err}")
            print(f"出错的数据: {row.to_dict()}")
            raise

    # 提交数据库事务
    conn.commit()
    print(f"数据成功插入到 `{table_name}`。")

    # 保存到 Excel，确保与数据库一致
    df.to_excel(excel_output_path, index=False)  # 保存为 Excel 文件
    print(f"数据已保存到 Excel 文件: {excel_output_path}")

except FileNotFoundError as fnf_error:
    print(f"错误: 日志文件未找到 - {fnf_error}")  # 如果日志文件未找到
except mysql.connector.Error as db_error:
    print(f"数据库错误: {db_error}")  # 数据库错误处理
    if 'conn' in locals() and conn.is_connected():
        conn.rollback()  # 如果有数据库连接，回滚事务
except json.JSONDecodeError as json_error:
    print(f"JSON 解析错误: {json_error}")  # JSON 解析错误
except Exception as general_error:
    print(f"发生未知错误: {general_error}")  # 处理其他未知错误
    if 'conn' in locals() and conn.is_connected():
        conn.rollback()  # 回滚事务
finally:
    if 'conn' in locals() and conn.is_connected():  # 确保数据库连接关闭
        cursor.close()
        conn.close()
        print("数据库连接已关闭。")
