import pandas as pd

data = {'Project':[], 'Location':[], 'Site':[]}
df = pd.DataFrame(data)


for i in range(1,51):
    df2 = pd.DataFrame(data)
    for j in range(1,4):
        df2.at[j, 'Project'] = 'TX Shinnery REU'
        df2.at[j, 'Location'] = str(i)
        # df2['Project'] = 'TX Shinnery REU'
        # df2['Location'] = str(i)
        if j == 1:
            df2.at[j, 'Site'] = 'A'
            # df2['Site'] = 'A'
        elif j == 2:
            df2.at[j, 'Site'] = 'B'
        elif j == 3:
            df2.at[j, 'Site'] = 'C'
        df2.append(df2)
        print(df2)
    df = pd.concat([df, df2], sort=False)
print(df)
df.to_csv('shinnery_oak.csv')