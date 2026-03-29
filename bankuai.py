import akshare as ak
import pandas as pd
import time

# 你要查的行业
symbols = ["半导体", "银行", "房地产开发", "食品饮料"]

# 获取行业板块名称列表
valid_symbols = ak.stock_board_industry_name_em()["板块名称"].tolist()

# 函数：加 sz./sh.
def get_exchange_prefix(code):
    code = str(code)
    if code.startswith("6") or code.startswith("688"):
        return "sh." + code
    elif code.startswith("0") or code.startswith("3"):
        return "sz." + code
    else:
        return "unknown." + code

# 结果集合
df_list = []

# 加强版：异常处理+超时重试
for symbol in symbols:
    if symbol not in valid_symbols:
        print(f"❌ symbol 不存在: {symbol}")
        continue

    for attempt in range(3):  # 最多重试3次
        try:
            df = ak.stock_board_industry_cons_em(symbol=symbol)
            df["行业"] = symbol
            df["带前缀代码"] = df["代码"].apply(get_exchange_prefix)
            df_list.append(df[["名称", "带前缀代码", "行业"]])
            print(f"✅ 成功拉取: {symbol}")
            break  # 成功拉取就退出重试
        except Exception as e:
            print(f"⚠️ 第 {attempt+1} 次拉取 {symbol} 失败，错误信息: {e}")
            time.sleep(5)  # 等5秒后再重试
    else:
        print(f"❌ 完全拉取失败: {symbol}")

# 合并结果
final_df = pd.concat(df_list, ignore_index=True)
final_df.columns = ["名称", "代码", "行业"]

# 删除 unknown 的行
final_df = final_df[~final_df["代码"].str.startswith("unknown.")]

# 打印
print(final_df)

final_df.to_excel("多行业成分股合并表.xlsx", index=False)
