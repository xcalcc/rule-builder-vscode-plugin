import pandas as pd
import json


df = pd.read_csv('./rule_info1.csv', usecols=[0], names=None, lineterminator="\n")
df_li = df.values.tolist()
result = []
for s_li in df_li:
    result.append(s_li[0])
print(result)

# # 使用python json模块加载数据
# with open('./dataList.json', 'r') as f:
#     data = json.loads(f.read())

# # 规范化数据
# df = pd.json_normalize(data)
# df.info()


# df = df[['rules.misra_c', 'code', 'rules.name_cn', 'name']]
# # df = df.loc[df['rules.misra_c'].isin(result)]

# df.to_csv("test.csv", mode='w', index=False)

