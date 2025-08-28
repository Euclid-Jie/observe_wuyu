import pandas as pd
import sqlalchemy
from config import SQL_PASSWORDS, SQL_HOST

engine = sqlalchemy.create_engine(
    f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8"
)
query = "SELECT date FROM Chinese_special_holiday"
holidays = pd.read_sql(query, engine)
holidays.to_csv("Chinese_special_holiday.txt", index=False, header=False)
print("成功更新Chinese_special_holiday.txt")
