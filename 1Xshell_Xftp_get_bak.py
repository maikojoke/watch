# 1Xshell_Xftp_get_bak.py 连接获取并下载压缩包

import paramiko  # 导入paramiko库，用于SSH和SFTP操作
import os  # 导入os库，用于文件路径操作

############################# 配置信息 #####################################
# 登录参数设置
hostname = "100.2.129.109"  # 远程服务器的IP地址
host_port = 8022  # 远程服务器的端口号
username = "u0_a260"  # 远程服务器的用户名
password = "123456"  # 远程服务器的密码

# 获取桌面路径
def get_desktop_path():
    """根据操作系统获取桌面路径"""
    if os.name == 'nt':  # 如果操作系统是Windows
        return os.path.join(os.environ['USERPROFILE'], 'Desktop')  # Windows平台的桌面路径
    else:  # 如果操作系统是Linux或macOS
        return os.path.join(os.environ['HOME'], 'Desktop')  # Linux/macOS平台的桌面路径


# 获取设备备份路径
def get_device_backup_path():
    """动态获取设备的备份路径"""
    return "/storage/emulated/0/MIUI/backup/AllBackup"  # 设备上的备份文件夹路径

# 获取最新的备份文件夹
def get_latest_backup_folder(ssh_client):
    """
    获取远程设备中最新的备份文件夹路径。
    该方法使用SSH连接，执行命令获取备份文件夹并按修改时间排序，返回最新文件夹的路径。
    """
    backup_path = get_device_backup_path()  # 获取设备的备份路径
    # 执行Shell命令，获取备份路径下按时间排序后的最新文件夹
    command = f"ls -d {backup_path}/*/ | sort -n | tail -n 1"
    stdin, stdout, stderr = ssh_client.exec_command(command)  # 执行Shell命令并获取返回结果
    stdout_info = stdout.read().decode('utf8').strip()  # 读取标准输出，获取最新文件夹路径
    if stderr.read().decode('utf8').strip():  # 如果有错误输出，打印错误信息
        print(f"错误输出: {stderr.read().decode('utf8')}")
    return stdout_info  # 返回最新备份文件夹的路径

########################################################################
def ssh_client_con():
    """
    创建SSH连接并执行命令来获取最新的备份文件夹，生成压缩包。
    """
    try:
        # 1. 创建SSH客户端实例
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加远程主机的SSH密钥

        # 2. 连接远程服务器
        ssh_client.connect(
            port=host_port,
            hostname=hostname,
            username=username,
            password=password
        )

        # 3. 获取最新备份文件夹的路径
        latest_folder = get_latest_backup_folder(ssh_client)
        print(f"最新的备份文件夹是: {latest_folder}")

        if latest_folder:
            # 构造Shell命令来压缩指定文件为.tar.gz格式
            compressed_filename = f"{latest_folder.split('/')[-2]}.tar.gz"  # 使用文件夹名作为压缩包的名称
            shell_command = f"cd {latest_folder} && tar -zcvf {compressed_filename} '小米运动健康(com.mi.health).bak'"  # 压缩命令
            stdin, stdout, stderr = ssh_client.exec_command(shell_command)  # 执行压缩命令

            # 获取命令执行后的标准输出和错误输出
            stdout_info = stdout.read().decode('utf8')
            stderr_info = stderr.read().decode('utf8')
            print("标准输出:")
            print(stdout_info)
            print("错误输出:")
            print(stderr_info)

            return ssh_client, latest_folder, compressed_filename  # 返回SSH连接、备份文件夹路径和压缩文件名
        else:
            print("未找到最新的备份文件夹")
            return None, None, None  # 如果没有找到备份文件夹，返回空值
    except Exception as e:
        print(f"SSH连接或命令执行失败: {e}")
        return None, None, None  # 出现异常时，返回空值

def sftp_client_con(ssh_client, latest_folder, compressed_filename):
    """
    使用SFTP协议下载远程服务器上的压缩包到本地。

    :param ssh_client: 已连接的SSH客户端
    :param latest_folder: 最新的备份文件夹路径
    :param compressed_filename: 压缩包的文件名
    """
    try:
        # 1. 获取SSH连接的Transport通道
        tran = ssh_client.get_transport()
        # 2. 创建SFTP客户端实例
        sftp = paramiko.SFTPClient.from_transport(tran)

        if latest_folder and compressed_filename:
            # 远程文件路径
            remote_path = f"{latest_folder}/{compressed_filename}"
            # 本地保存路径
            save_path = os.path.join(os.getcwd(), compressed_filename)  # 保存到当前工作目录

            # 下载文件
            sftp.get(remotepath=remote_path, localpath=save_path)
            print(f"下载 {save_path} 完成")
        else:
            print("无法获取最新的备份文件夹或压缩文件")
    except Exception as e:
        print(f"SFTP操作失败: {e}")
    finally:
        # 关闭SFTP连接
        tran.close()

# 调用主函数，执行步骤
if __name__ == "__main__":
    ssh_client, latest_folder, compressed_filename = ssh_client_con()  # 获取SSH连接并压缩文件
    if ssh_client and latest_folder and compressed_filename:
        sftp_client_con(ssh_client, latest_folder, compressed_filename)  # 下载压缩文件
        ssh_client.close()  # 关闭SSH连接
