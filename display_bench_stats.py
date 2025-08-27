import pandas as pd
import numpy as np
import sqlalchemy
from pathlib import Path
from utils import (
    plot_lines_chart,
    plot_stacked_area_with_right_line,
    plot_lines_with_right_area,
)
from datetime import datetime
from zoneinfo import ZoneInfo

from config import SQL_PASSWORDS, SQL_HOST

engine = sqlalchemy.create_engine(
    f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8"
)
combined_fig = []
# 读取数据
bench_basic_data = pd.read_sql_query(
    "SELECT * FROM bench_basic_data WHERE `date` > '2025-01-01' ORDER BY DATE", engine
)
bench_basic_data.drop_duplicates(subset=["date", "code"], keep="last", inplace=True)
bench_info_wind = pd.read_sql_query("SELECT * FROM bench_info_wind", engine)
ys_data = []
names = []
all_volumeRMB_percent = []
all_data = bench_basic_data[bench_basic_data["code"] == "000985.CSI"]
for code in [
    "000300.SH",
    "000905.SH",
    "000852.SH",
    "932000.CSI",
    "868008.WI",
]:
    sub_data = bench_basic_data[bench_basic_data["code"] == code]
    ys_data.append(sub_data["AMT"].values // 1e8)
    all_volumeRMB_percent.append(
        (sub_data["AMT"].values / all_data["AMT"].values) // 0.0001 / 10000
    )
    names.append(bench_info_wind[bench_info_wind["code"] == code]["name"].values[0])
names[-1] = "微盘股"

# 计算小市值
small_amt = all_data["AMT"].values // 1e8 - np.array(ys_data).sum(axis=0)
small_amt_percent = np.round(1 - np.array(all_volumeRMB_percent).sum(axis=0), 2)
# 插入到倒数第二个
ys_data.insert(-1, small_amt)
all_volumeRMB_percent.insert(-1, small_amt_percent)
names.insert(-1, "小市值")

# 成交金额占比
chart1 = plot_lines_with_right_area(
    sub_data["date"].values,
    all_volumeRMB_percent,
    names,
    all_data["AMT"].values // 1e8,
    "全指成交额(亿)",
    up_bound=0.5,
)

# 成交金额(各个宽基) VS 成交金额(微盘)
chart2 = plot_stacked_area_with_right_line(
    sub_data["date"].values,
    ys_data[:-1],
    names[:-1],
    ys_data[-1],
    "微盘成交额(亿)",
)

columns_in_order = [
    "日期",
    "主力合约",
    "期货价格",
    "现货价格",
    "基差",
    "到期日",
    "剩余天数",
    "期内分红",
    "矫正基差",
    "主力年化基差(%)",
    "年化基差(%)",
]
# 将字段名中的 % 替换为 %%
fields = ", ".join([f'`{col.replace("%", "%%")}`' for col in columns_in_order])
IH_data = pd.read_sql_query(f"SELECT {fields} FROM IH_data", engine)
IF_data = pd.read_sql_query(f"SELECT {fields} FROM IF_data", engine)
IC_data = pd.read_sql_query(f"SELECT {fields} FROM IC_data", engine)
IM_data = pd.read_sql_query(f"SELECT {fields} FROM IM_data", engine)
fig = plot_lines_chart(
    x_data=IC_data["日期"],
    ys_data=[
        IH_data["年化基差(%)"],
        IF_data["年化基差(%)"],
        IC_data["年化基差(%)"],
        IM_data["年化基差(%)"],
    ],
    names=[
        "IH年化基差(%)",
        "IF年化基差(%)",
        "IC年化基差(%)",
        "IM年化基差(%)",
    ],
    range_start=75,
)

html = f"""<html>
    <head>
        <meta charset="UTF-8">
        <title>Value over Time</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }}
            table {{
                margin: auto;
                margin-bottom: 20px;
                border-collapse: collapse;
                width: 80%;
            }}
            table, th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #f59e00;
                color: white;
            }}
            #timestamp {{
                position: absolute;
                top: 10px;
                left: 10px;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
    <div style="margin-top: 10px; margin-left: 20px; font-family: 'Calibri', sans-serif;">
        <div>Last Updated: {datetime.now(ZoneInfo('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}</div>
        <div style="margin-top: 20px; font-weight: bold; font-size: 25px;text-align: center;">成交金额占比</div>
        {chart1.render_embed()}
        <div style="margin-top: 20px; font-weight: bold; font-size: 25px;text-align: center;">成交金额</div>
        {chart2.render_embed()}
        <div style="margin-top: 20px; font-weight: bold; font-size: 25px;text-align: center;">基差</div>
        {fig.render_embed()}
        <div style="margin-top: 30px; font-size: 14px; line-height: 1.5;">
            <div style="font-weight: bold; margin-bottom: 10px;">基差计算说明</div>
            <div>年化基差算法: 每一天，针对主力合约计算基差(=期货价格-现货价格)，然后提取当天至该主力合约到期日之间的"期内分红"，进而计算出"矫正基差"(=基差+期内分红)，最后计算出年化基差率，公式如下:</div>
            <div style="margin: 10px 0;">年化基差率 = (矫正基差 ÷ 指数现货收盘价) × (365 ÷ 合约到期剩余天数)</div>
            <div>期内分红算法: 把合约剩余期限内每日的指数分红点位相加，如果是历史合约，指数每日的分红点位直接用对应的股息点指数来计算，如果是当前尚未到期的合约，未来期限内的每日分红点位用预测值计算。</div>
            <div>主力合约是根据昨持仓进行判断，昨持仓最大的即为当日主力合约。</div>
        </div>
    </div>
    </body>
</html>"""
# Write the combined figure to an HTML file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
