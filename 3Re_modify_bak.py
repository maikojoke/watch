# 3Re_modify_bak.py 找到最新文件夹，删除bak文件前面53个字符

import os
from datetime import datetime

def get_latest_folder(path):
    """
    这个函数返回指定路径下最新的文件夹，基于文件夹名称中的时间戳。
    :param path: 要检查的根路径
    :return: 最新的文件夹路径
    """
    # 获取指定路径下所有文件夹的路径，排除掉名为 .idea 的文件夹（一般是 IDE 使用的文件夹，不需要处理）
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

# 动态获取最新的文件夹
base_path = "C:/Users/maikojoke/Desktop/小米手环数据自动化导出代码"
latest_folder = get_latest_folder(base_path)

# 输出最新的文件夹路径，用于调试，确认是否找到了正确的文件夹
print(f"最新文件夹: {latest_folder}")

# 如果找到了最新的文件夹
if latest_folder:
    # 拼接出原始 .bak 文件的路径
    infile_path = os.path.join(latest_folder, "小米运动健康(com.mi.health).bak")

    # 新的健康数据文件路径
    new_bak_path = os.path.join(latest_folder, "health.bak")

    # 打开原始的 .bak 文件，以二进制模式读取
    if os.path.exists(infile_path):  # 确保文件存在
        with open(infile_path, "rb") as infile1:
            # 读取文件的所有内容
            content = infile1.read()

            # 如果文件内容大于53个字节，则进行修改
            if len(content) > 53:
                # 获取从第54个字节开始的内容（也就是去掉前53个字节）
                modified_content = content[53:]

                # 将修改后的内容保存到新的 .bak 文件
                with open(new_bak_path, "wb") as new_bak_file:
                    new_bak_file.write(modified_content)  # 写入修改后的内容

                print(f'文件修改完成，新文件保存为: {new_bak_path}')  # 输出文件修改成功的信息
            else:
                print("文件内容小于53字节，无法进行修改")  # 如果文件小于53字节，输出无法修改的提示
    else:
        print(f"找不到文件：{infile_path}")  # 如果文件路径错误或者文件不存在，输出文件找不到的提示
else:
    print("没有找到最新的文件夹")  # 如果没有找到最新的文件夹，输出提示
