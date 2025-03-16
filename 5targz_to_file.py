# 5targz_to_file.py 先删除现有文件夹再解压tar文件

import tarfile  # 导入tarfile模块，用于处理tar压缩文件
import shutil  # 导入shutil模块，用于删除文件夹
import os     # 导入os库，用于文件和目录操作
# 定义压缩包路径和解压目录
tar_gz_file = "C:/Users/maikojoke/Desktop/小米手环数据自动化导出代码/health.tar"  # 设置待解压的tar压缩包路径
output_dir = "C:/Users/maikojoke/Desktop/小米手环数据自动化导出代码/health/"  # 设置解压到的目录

# 删除已存在的解压文件夹（如果存在）
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)  # 删除文件夹及其内容

# 定义一个过滤函数，根据需要来控制提取的文件
def filter_function(tarinfo, path):
    """
    过滤函数，在提取文件时可以用来控制哪些文件需要被提取。
    :param tarinfo: tar文件的元数据，包括文件类型、文件名等
    :param path: 当前文件的路径
    :return: 返回tarinfo对象表示该文件，或返回None来跳过该文件
    """
    if tarinfo.isfile():  # 检查tar中的项目是否为文件
        return tarinfo  # 如果是文件，则提取它
    else:
        return None  # 如果不是文件（例如目录），则不提取

# 打开tar.gz文件
with tarfile.open(tar_gz_file, "r") as tar:  # 打开指定的tar文件，"r"表示只读模式
    # 提取所有符合条件的文件到指定的目录，使用 filter 参数来过滤文件
    tar.extractall(path=output_dir, filter=filter_function)  # 执行解压操作，将符合条件的文件提取到output_dir目录

print("解压完成！")  # 提示用户解压完成
