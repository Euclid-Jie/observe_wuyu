from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Literal, List
import requests
import re
import urllib.parse
import json
import uuid
from typing import List
from pyecharts.charts import Line
from pyecharts import options as opts


def now_time():
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")


def load_bais(type=Literal["IF", "IC", "IM", "IH"]) -> pd.DataFrame:
    if type == "IF":
        data = "params=%7B%22head%22%3A%22IF%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    elif type == "IC":
        data = "params=%7B%22head%22%3A%22IC%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    elif type == "IM":
        data = "params=%7B%22head%22%3A%22IM%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    elif type == "IH":
        data = "params=%7B%22head%22%3A%22IH%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    else:
        raise ValueError("type must be one of 'IF', 'IC', 'IM', 'IH'")
    decoded_data = urllib.parse.unquote(data)
    # 解析为字典格式
    parsed_params = urllib.parse.parse_qs(decoded_data)
    parsed_params["g_randomid"] = "randomid_" + str(uuid.uuid4().int)[:-11]
    updated_data = urllib.parse.urlencode(parsed_params, doseq=True)
    response = requests.post(
        "https://web.tinysoft.com.cn/website/loadContentDataAjax.tsl?ref=js",
        updated_data,
    )

    data = response.content.decode("utf-8", "ignore")
    data = json.loads(data)
    soup = BeautifulSoup(data["content"][0]["html"], "html.parser")
    script_content = soup.find("script").string
    match = re.search(r"var\s+SrcData\s*=\s*(\[.*?\]);", script_content, re.DOTALL)
    src_data_raw = match.group(1)
    # 将转义字符转换为实际字符
    src_data = json.loads(src_data_raw.encode().decode("unicode_escape"))
    data_df = pd.DataFrame(src_data)[
        [
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
    ]
    return data_df


# Function to generate a line chart with multiple lines
def plot_lines_chart(
    x_data: np.ndarray,
    ys_data: List[np.ndarray],
    names: List[str],
    range_start: int = 0,
    range_end: int = 100,
    lower_bound: float = None,
    up_bound: float = None,
):
    assert len(ys_data) == len(names), "Length of ys_data and names should be the same"
    line = Line(
        init_opts={
            "width": "1560px",
            "height": "600px",
            "is_horizontal_center": True,
        }
    ).add_xaxis(list(x_data))
    for i, y_data in enumerate(ys_data):
        line.add_yaxis(names[i], list(y_data), is_symbol_show=False)

    line.set_global_opts(
        xaxis_opts=opts.AxisOpts(type_="category"),
        yaxis_opts=opts.AxisOpts(type_="value", min_=lower_bound, max_=up_bound),
        legend_opts=opts.LegendOpts(
            textstyle_opts=opts.TextStyleOpts(font_weight="bold", font_size=20)
        ),
        datazoom_opts=[
            opts.DataZoomOpts(
                range_start=range_start, range_end=range_end, orient="horizontal"
            )
        ],
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        graphic_opts=[
            opts.GraphicImage(
                graphic_item=opts.GraphicItem(
                    right=200,
                    top=10,
                    z=1,
                ),
                graphic_imagestyle_opts=opts.GraphicImageStyleOpts(
                    image="无鱼透明.png",  # Logo 路径
                    width=80,  # 宽度
                    height=30,  # 高度
                ),
            )
        ],
    ).set_series_opts(
        linestyle_opts=opts.LineStyleOpts(width=2),
    )
    return line


def plot_stacked_area_with_right_line(
    x_data: np.ndarray,
    ys_data: List[np.ndarray],
    names: List[str],
    right_y_data: np.ndarray = None,
    right_y_name: str = "Right Axis",
    range_start: int = 0,
    range_end: int = 100,
    lower_bound: float = None,
    up_bound: float = None,
    right_lower_bound: float = None,
    right_up_bound: float = None,
):
    # 创建折线图实例
    line = Line(
        init_opts=opts.InitOpts(
            width="1560px",
            height="600px",
            theme="white",
            is_horizontal_center=True,
        )
    ).add_xaxis(list(x_data))

    # 左轴颜色系
    color_series = [
        "#FF6F61",  # Bright Coral
        "#FFB74D",  # Bright Orange
        "#4FC3F7",  # Bright Sky Blue
        "#BA68C8",  # Bright Purple
        "#B0BEC5",  # Bright Grey
    ]

    # 1. 绘制左轴堆叠面积图
    for i, y_data in enumerate(ys_data):
        line.add_yaxis(
            series_name=names[i],
            y_axis=list(y_data),
            stack="stack_group",
            is_symbol_show=False,
            areastyle_opts=opts.AreaStyleOpts(
                opacity=0.3, color=color_series[i % len(color_series)]
            ),
            color=color_series[i % len(color_series)],
            linestyle_opts=opts.LineStyleOpts(width=0),
            label_opts=opts.LabelOpts(is_show=False),
            yaxis_index=0,
        )

    # 2. 处理右轴（关键修改部分）
    if right_y_data is not None:
        # 必须先添加右轴系列再设置全局配置
        line.extend_axis(
            yaxis=opts.AxisOpts(
                name=right_y_name,
                type_="value",
                position="right",
                splitline_opts=opts.SplitLineOpts(is_show=False),  # 网格线不显示
                min_=right_lower_bound,
                max_=right_up_bound,
            )
        )
        line.add_yaxis(
            series_name=right_y_name,
            y_axis=list(right_y_data),
            symbol="diamond",
            label_opts=opts.LabelOpts(is_show=False),
            z_level=3,
            yaxis_index=1,
            linestyle_opts=opts.LineStyleOpts(
                width=2,
                color="#00B050",
            ),
        )

    # 全局配置（确保在右轴添加后设置）
    line.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category", axispointer_opts=opts.AxisPointerOpts(is_show=True)
        ),
        yaxis_opts=opts.AxisOpts(type_="value", min_=lower_bound, max_=up_bound),
        datazoom_opts=[opts.DataZoomOpts(range_start=range_start, range_end=range_end)],
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        graphic_opts=[
            opts.GraphicImage(
                graphic_item=opts.GraphicItem(
                    right=200,
                    top=10,
                    z=1,
                ),
                graphic_imagestyle_opts=opts.GraphicImageStyleOpts(
                    image="无鱼透明.png",  # Logo 路径
                    width=80,  # 宽度
                    height=30,  # 高度
                ),
            )
        ],
    )

    return line


def plot_lines_with_right_area(
    x_data: np.ndarray,
    ys_data: List[np.ndarray],
    names: List[str],
    right_y_data: np.ndarray = None,
    right_y_name: str = "Right Axis",
    range_start: int = 0,
    range_end: int = 100,
    lower_bound: float = None,
    up_bound: float = None,
    right_lower_bound: float = None,
    right_up_bound: float = None,
):
    # 创建折线图实例
    line = Line(
        init_opts=opts.InitOpts(
            width="1560px",
            height="600px",
            theme="white",
            is_horizontal_center=True,
        )
    ).add_xaxis(list(x_data))
    color_series = [
        # "#FFA3A6",
        # "#F8CBAD",
        # "#99EBFF",
        # "#C299FF",
        # "#ACACAC",
        "#FF6F61",  # Bright Coral
        "#FFB74D",  # Bright Orange
        "#4FC3F7",  # Bright Sky Blue
        "#BA68C8",  # Bright Purple
        "#B0BEC5",  # Bright Grey
        "#00B050",  # Green
    ]
    # 1. 绘制左轴线图
    for i, y_data in enumerate(ys_data):
        line.add_yaxis(
            series_name=names[i],
            y_axis=list(y_data),
            is_symbol_show=False,
            yaxis_index=0,
            color=color_series[i % len(color_series)],
            linestyle_opts=opts.LineStyleOpts(width=2),
        )

    # 2. 处理右轴（关键修改部分）
    if right_y_data is not None:
        # 必须先添加右轴系列再设置全局配置
        line.extend_axis(
            yaxis=opts.AxisOpts(
                name=right_y_name,
                type_="value",
                position="right",
                splitline_opts=opts.SplitLineOpts(is_show=False),  # 网格线不显示
                min_=right_lower_bound,
                max_=right_up_bound,
            )
        )
        line.add_yaxis(
            series_name=right_y_name,
            y_axis=list(right_y_data),
            stack="stack_group",
            is_symbol_show=False,  # 不显示数据点标记
            areastyle_opts=opts.AreaStyleOpts(
                opacity=0.3,  # 透明度
                color="#808080",  # 灰色 (#808080 是标准灰色)
            ),
            linestyle_opts=opts.LineStyleOpts(
                width=0,  # 线宽设为 0（隐藏线条）
                color=None,  # 颜色设为 None（可选）
            ),
            label_opts=opts.LabelOpts(is_show=False),  # 关闭标签
            yaxis_index=1,
        )

    # 全局配置（确保在右轴添加后设置）
    line.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category", axispointer_opts=opts.AxisPointerOpts(is_show=True)
        ),
        yaxis_opts=opts.AxisOpts(type_="value", min_=lower_bound, max_=up_bound),
        datazoom_opts=[opts.DataZoomOpts(range_start=range_start, range_end=range_end)],
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        graphic_opts=[
            opts.GraphicImage(
                graphic_item=opts.GraphicItem(
                    right=200,
                    top=10,
                    z=1,
                ),
                graphic_imagestyle_opts=opts.GraphicImageStyleOpts(
                    image="无鱼透明.png",  # Logo 路径
                    width=80,  # 宽度
                    height=30,  # 高度
                ),
            )
        ],
    )

    return line
