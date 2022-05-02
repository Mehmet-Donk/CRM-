
#Data Understanding

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

#1. Reading the "...".csv data and making a copy of the Dataframe

df_ = pd.read_csv('....csv')
df=df_.copy()


#2. In the dataset
        # a. first 10 observations,
        # b. variable names,
        # c. Dimension,
        # D. descriptive statistics,
        # e. null value,
        # f. Variable types, review.

df.head(10)
df.columns
df.describe().T
df.isnull().sum()
df.dtypes
df.shape

# 3. Omnichannel means that customers shop from both online and offline platforms.
# New variables have been created for the total number of purchases and spending of each customer.

df["TotalValue"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]
df["TotalOrder"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]

# 4.Variable types were examined. Changed the type of variables that express date to date.

df["first_order_date"]=pd.to_datetime(df["first_order_date"])
df["last_order_date"]=pd.to_datetime(df["last_order_date"])

#5.The distribution of the number of customers in the shopping channels, the total number of products purchased and the total expenditures were examined.

df["order_channel"].value_counts()

df.groupby("order_channel").agg({"TotalValue": ["sum","mean","count"],
                             "TotalOrder": ["sum","mean","count"],
                                 "master_id": ["count"]})

#6. Listed the top 10 customers with the most revenue

df2 = df.sort_values("TotalValue", ascending=False)
df2["TotalValue"].head(10)


#7. Listed the top 10 customers with the most orders.

df2 = df.sort_values("TotalOrder", ascending=False)
df2["TotalOrder"].head(10)

df.sort_values("TotalValue", ascending=False).iloc[0:10,12:13]


# 8. Data preparation process functionalized

def on_hazırlık(dataframe):
    dataframe.columns
    dataframe.describe().T
    dataframe.isnull().sum()
    dataframe.dtypes
    dataframe.shape
    dataframe["TotalValue"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    dataframe["TotalOrder"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["order_channel"].value_counts()
    dataframe["first_order_date"] = pd.to_datetime(dataframe["first_order_date"])
    dataframe["last_order_date"] = pd.to_datetime(dataframe["last_order_date"])
    df3=dataframe.groupby("order_channel").agg({"TotalValue": ["sum", "mean", "count"],
                                     "TotalOrder": ["sum", "mean", "count"],
                                     "master_id": ["count"]})
    df2=dataframe.sort_values("TotalValue", ascending=False)["TotalValue"].loc[:10]
    df4=dataframe.sort_values("TotalOrder", ascending=False).loc[:10,"TotalOrder"]

    return df3,df2,df4

df=df_.copy()
on_hazırlık(df)


#  CALCULATING RFM METRICS

# 1.Analysis date 2 days after the last shopping date in the data set
# 2021-05-30 found

df["last_order_date"].max()
df["TotalOrder"].values
today_date = dt.datetime(2021, 6, 1) #2 days after the last shopping date



# 2.A new rfm dataframe with customer_id, recency, frequnecy and monetary values

rfm = df.groupby('master_id').agg({'last_order_date': lambda last_order_date: (today_date - last_order_date.max()).days,
                                                'TotalOrder': lambda TotalOrder: TotalOrder.values,
                                                "TotalValue": lambda TotalValue: TotalValue.values})

rfm.columns = ['recency', 'frequency', 'monetary']

rfm.describe().T

#CALCULATING RF AND RFM SCORES


# 1. Converting Recency, Frequency and Monetary metrics to scores between 1-5 with the help of qcut and
# 2. Saving these scores as recency_score, frequency_score and monetary_score

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])

rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])


# 3. Express recency_score and frequency_score as a single variable and save it as RF_SCORE

rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))


#DEFINITION OF RF SCORES AS SEGMENTS

#1. Segment definition and conversion of RF_SCORE to segments with the help of defined seg_map so that the generated RFM scores can be explained more clearly.
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

#SOME ACTIONS

#1. The recency, frequency and monetary averages of the segments were examined.

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#                          recency       frequency       monetary
#                        mean count      mean count     mean count
# segment
# about_to_sleep       113.79  1629      2.40  1629   359.01  1629
# at_Risk              241.61  3131      4.47  3131   646.61  3131
# cant_loose           235.44  1200     10.70  1200  1474.47  1200
# champions             17.11  1932      8.93  1932  1406.63  1932
# hibernating          247.95  3604      2.39  3604   366.27  3604
# loyal_customers       82.59  3361      8.37  3361  1216.82  3361
# need_attention       113.83   823      3.73   823   562.14   823
# new_customers         17.92   680      2.00   680   339.96   680
# potential_loyalists   37.16  2938      3.30  2938   533.18  2938
# promising             58.92   647      2.00   647   335.67   647


# 2. With the help of RFM analysis, find the customers in the relevant profile for 2 cases and save the customer IDs to the csv.

# a. Company includes a new women's shoe brand. The product prices of the included brand are above the general customer preferences. Therefore, the brand
#It is desired to contact the customers in the profile that will be interested in # promotion and product sales. These customers are loyal, on average over 250 TL and
# is planned to be shoppers from the women category. Add the id numbers of the customers to the csv file with the new_brand_target_customer_id.cvs

new_df = pd.DataFrame()

rfm_final = df.merge(rfm, on="master_id", how="left")
new_df["new_customer"]=rfm_final[((df["customer_value_total"] / df["order_num_total"] > 250) & (rfm_final.segment == "loyal_customers"))&(rfm_final.interested_in_categories_12.str.contains("KADIN"))].index
