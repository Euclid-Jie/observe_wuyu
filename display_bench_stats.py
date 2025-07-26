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
from utils import load_bais
import os

SQL_PASSWORDS = os.environ["SQL_PASSWORDS"]
SQL_HOST = os.environ["SQL_HOST"]

engine = sqlalchemy.create_engine(
    f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8"
)
combined_fig = []
# 读取数据
bench_basic_data = pd.read_sql_query(
    "SELECT * FROM bench_basic_data WHERE `date` > '2025-01-01'", engine
)
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
        (sub_data["AMT"].values / all_data["AMT"].values) // 0.01 / 100
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

chart1 = plot_stacked_area_with_right_line(
    sub_data["date"].values,
    ys_data,
    names,
    all_data["AMT"].values // 1e8,
    "全指成交额(亿)",
)

chart2 = plot_lines_with_right_area(
    sub_data["date"].values,
    all_volumeRMB_percent,
    names,
    all_data["AMT"].values // 1e8,
    "全指成交额(亿)",
)

IH_data = load_bais("IH")
IH_data.to_csv(Path("data/IH_data.csv"), index=False, encoding="utf-8-sig")
IF_data = load_bais("IF")
IF_data.to_csv(Path("data/IF_data.csv"), index=False, encoding="utf-8-sig")
IC_data = load_bais("IC")
IC_data.to_csv(Path("data/IC_data.csv"), index=False, encoding="utf-8-sig")
IM_data = load_bais("IM")
IM_data.to_csv(Path("data/IM_data.csv"), index=False, encoding="utf-8-sig")
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
        <div style="margin-top: 10px;margin-left: 20px;">
            <div>Last Updated: {datetime.now(ZoneInfo('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}</div>
            {chart1.render_embed()}
            {chart2.render_embed()}
            {fig.render_embed()}
        </div>
    </body>
</html>"""
# Write the combined figure to an HTML file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
