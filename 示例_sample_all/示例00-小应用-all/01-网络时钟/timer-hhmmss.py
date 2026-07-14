import time
import datetime
import ntplib

NTP_SERVER = "time1.aliyun.com"


def get_net_time():
    try:
        client = ntplib.NTPClient()
        response = client.request(NTP_SERVER, timeout=3)
        return datetime.datetime.fromtimestamp(response.tx_time)
    except:
        return datetime.datetime.now()


if __name__ == "__main__":
    net_base = get_net_time()
    local_base = datetime.datetime.now()

    while True:
        now_local = datetime.datetime.now()
        delta = now_local - local_base
        now = net_base + delta

        # 格式化到 0.1 秒：截取到小数点后1位
        time_str = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-5]
        print("\r                                                                                                                 当前网络时间：" + time_str, end="", flush=True)

        # 0.1秒刷新一次
        time.sleep(0.1)