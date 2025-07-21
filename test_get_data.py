import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
from config import os, name_path, data_file_name

def get_url(name):
    """
    :param name: 玩法名称
    :return: (url, path)
    """
    url = "https://datachart.500.com/{}/history/".format(name)
    path = "newinc/history.php?start={}&end="
    return url, path

def get_current_number(name):
    """ 获取最新一期数字
    :param name: 玩法名称
    :return: int
    """
    url, _ = get_url(name)
    try:
        r = requests.get("{}{}".format(url, "history.shtml"), verify=True)  # 使用 SSL 验证
        r.raise_for_status()  # 检查请求是否成功
        print(r.url)
        r.encoding = r.apparent_encoding  # 自动检测编码
        soup = BeautifulSoup(r.text, "lxml")
        current_num = soup.find("div", class_="wrap_datachart").find("input", id="end")["value"]
        return current_num
    except requests.RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"解析错误: {e}")
    return None


def spider(name, start, end, mode):
    """ 爬取历史数据
    :param name 玩法
    :param start 开始一期
    :param end 最近一期
    :param mode 模式，train：训练模式，predict：预测模式（训练模式会保持文件）
    :return:
    """
    try:
        url, path = get_url(name)
        url = "{}{}{}".format(url, path.format(start), end)
        r = requests.get(url=url, verify=True)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "lxml")
        trs = soup.find("tbody", attrs={"id": "tdata"}).find_all("tr")
        data = []
        for tr in trs:
            item = dict()
            if name == "ssq":
                item[u"期数"] = tr.find_all("td")[0].get_text().strip()
                for i in range(6):
                    item[u"红球_{}".format(i+1)] = tr.find_all("td")[i+1].get_text().strip()
                item[u"蓝球"] = tr.find_all("td")[7].get_text().strip()
                data.append(item)
            # elif name == "dlt":
            #     item[u"期数"] = tr.find_all("td")[0].get_text().strip()
            #     for i in range(5):
            #         item[u"红球_{}".format(i+1)] = tr.find_all("td")[i+1].get_text().strip()
            #     for j in range(2):
            #         item[u"蓝球_{}".format(j+1)] = tr.find_all("td")[6+j].get_text().strip()
            #     data.append(item)
            else:
                logger.warning("抱歉，没有找到数据源！")
    except requests.RequestException as e:
        print(f"请求错误：{e}")
    except Exception as e:
        print(f"解析错误：{e}")

    if mode == "train":
        df = pd.DataFrame(data)
        df.to_csv("{}{}".format(name_path[name]["path"], data_file_name), encoding="utf-8")
        return pd.DataFrame(data)
    elif mode == "predict":
        return pd.DataFrame(data)
    

# 示例调用
if __name__ == "__main__":
    name = "ssq"  # 示例玩法名称
    current_number = get_current_number(name)
    if current_number:
        print(f"最新一期数字: {current_number}")
