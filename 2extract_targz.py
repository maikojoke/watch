# 2extract_targz.py 获取文件并解压

import tarfile  # 导入tarfile库，用于处理tar文件，解压tar.gz格式的压缩文件
import os  # 导入os库，用于处理文件和目录操作

# 获得目录下的所有文件
def get_file_name(file_dir):
    L = []   # 用于存储目录中的所有文件名
    for root, dirs, files in os.walk(file_dir):  # root是当前目录路径，dirs是目录名，files是文件名
        for file in files:   # 遍历每个文件
            L.append(os.path.join(root, file))   # 将文件的完整路径添加到列表L中
    return L  # 返回包含所有文件名的列表L

# 获取最新的tar.gz文件
def get_latest_tar_gz(files):
    tar_files = [file for file in files if file.endswith(".tar.gz")]  # 过滤出所有.tar.gz文件
    if not tar_files:
        return None  # 如果没有.tar.gz文件，返回None

    # 按照文件的修改时间进行排序，获取最新的文件
    latest_file = max(tar_files, key=os.path.getmtime)
    return latest_file  # 返回最新的.tar.gz文件

# 解压缩模块
def un_tar(file_path):
    try:
        # 获取压缩文件名和文件夹路径
        file_name = os.path.basename(file_path)
        folder_name = file_name.replace(".tar.gz", "")  # 去掉.tar.gz后缀
        extract_path = os.path.join(os.path.dirname(file_path), folder_name)  # 定义解压文件的路径

        # 判断解压目标文件夹是否存在，若不存在则创建
        if not os.path.isdir(extract_path):  # 如果目标文件夹不存在
            print(f"创建解压目标文件夹: {extract_path}")
            os.mkdir(extract_path)  # 创建文件夹
        else:
            print(f"解压目标文件夹已存在: {extract_path}")

        # 打开tar.gz压缩文件
        with tarfile.open(file_path, "r:gz") as tar:
            # 解压缩文件到目标路径
            tar.extractall(path=extract_path)  # 将压缩文件中的所有内容解压到目标路径
            print(f"解压完成，所有文件已解压到: {extract_path}")

    except tarfile.TarError as e:  # 捕获tar文件解压错误
        print(f"tar文件解压错误: {e}")
    except FileNotFoundError as e:  # 捕获文件未找到的错误
        print(f"文件未找到: {e}")
    except Exception as e:  # 捕获其他未知的错误
        print(f"发生了未知错误: {e}")

# 获得当前的文件目录
file_dir = os.getcwd()  # 获取当前工作目录，返回当前脚本运行的文件夹路径
# 获取当前目录下的所有文件名
files = get_file_name(file_dir)  # 调用get_file_name函数，获取所有文件名

# 获取最新的.tar.gz文件
latest_tar_gz = get_latest_tar_gz(files)

# 如果找到了最新的.tar.gz文件，进行解压
if latest_tar_gz:
    print(f"正在解压最新的文件: {latest_tar_gz}")
    un_tar(latest_tar_gz)  # 调用un_tar函数，解压最新的文件
else:
    print("没有找到.tar.gz文件，无法解压")
