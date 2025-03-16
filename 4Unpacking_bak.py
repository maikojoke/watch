# 4Unpacking_bak.py 寻找最新文件夹解包bak文件

import os  # 导入os库，用于文件和目录操作
import subprocess  # 导入subprocess库，用于执行外部命令并获取结果
from datetime import datetime  # 导入datetime模块，用于时间的处理

# 获取指定路径下最新的文件夹
def get_latest_folder(path):
    """
    这个函数返回指定路径下最新的文件夹，基于文件夹名称中的时间戳。
    :param path: 要检查的根路径
    :return: 最新的文件夹路径
    """
    # 获取指定路径下所有文件夹的路径，排除掉名为 .idea 的文件夹
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) and f != '.idea']

    # 如果没有文件夹，则返回空
    if not folders:
        return None

    # 定义一个函数将文件夹名称中的时间戳转换为 datetime 对象
    def folder_to_datetime(folder_name):
        try:
            # 假设文件夹名的格式是 "20250222_161028"
            return datetime.strptime(folder_name, "%Y%m%d_%H%M%S")
        except ValueError:
            return None  # 如果转换失败则返回 None

    # 提取每个文件夹的时间戳并将其转换为 datetime 对象
    folder_dates = [(folder, folder_to_datetime(folder)) for folder in folders]

    # 排除掉无法转换时间戳的文件夹
    folder_dates = [f for f in folder_dates if f[1] is not None]

    # 如果没有有效的时间戳，返回空
    if not folder_dates:
        return None

    # 按照时间戳从大到小排序，最新的文件夹在前面
    latest_folder = max(folder_dates, key=lambda x: x[1])[0]

    # 返回最新的文件夹路径
    return os.path.join(path, latest_folder)

# 打开并执行命令，获取执行结果
def subprocess_getoutput(stmt):
    """
    这个函数执行传入的命令，并返回执行的结果。
    :param stmt: 需要执行的命令
    :return: 执行命令后的输出结果
    """
    result = subprocess.getoutput(stmt)  # 执行命令并获取输出
    return result  # 返回命令执行结果

# 主函数
def unpack_bak_file():
    # 设置根目录路径
    base_path = "C:/Users/maikojoke/Desktop/小米手环数据自动化导出代码"

    # 获取根目录下最新的文件夹
    latest_folder = get_latest_folder(base_path)

    # 如果找到了最新的文件夹，执行后续操作
    if latest_folder:
        print(f"最新文件夹: {latest_folder}")  # 打印最新文件夹路径，用于调试

        # 拼接出health.bak文件的完整路径
        infile_path = os.path.join(latest_folder, "health.bak")

        # 检查health.bak文件是否存在
        if os.path.exists(infile_path):
            # 如果文件存在，执行解压命令
            cmd = f'java -jar "C:/Users/maikojoke/Desktop/小米手环数据自动化导出代码/abe.jar" unpack "{infile_path}" health.tar'
            result = subprocess_getoutput(cmd)  # 执行解压命令并获取输出结果
            print(f"解压结果: {result}")  # 输出解压的结果
        else:
            # 如果找不到文件，输出错误信息
            print(f"找不到文件：{infile_path}")
    else:
        # 如果没有找到最新的文件夹，输出提示信息
        print("没有找到最新的文件夹")

# 调用主函数，开始执行解压任务
unpack_bak_file()
