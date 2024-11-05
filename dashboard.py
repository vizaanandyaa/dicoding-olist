import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

## Membuat fungsi pembantu

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_byreview_df(df):
    byreview_df = df.groupby(by="review_score").customer_id.nunique().reset_index()
    byreview_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return byreview_df

def create_bydelivorder_df(df):
    bydeliv_df = df[df["order_status"] == "delivered"]
    bydeliv_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bydeliv_df
def show_pie_chart(df):
    review_counts = df['review_score'].value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(review_counts, labels=review_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Rating')
    plt.axis('equal')
    st.pyplot(plt)

def show_line_chart(df):
    plt.figure(figsize=(10, 6)) 
    plt.plot(df.index.astype(str), df, marker='o', linestyle='-', color='b', label='Revenue per Month')

    plt.title('Total Revenue per Month', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Revenue', fontsize=12)

    plt.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

def show_on_time_chart(df):
    plt.figure(figsize=(8, 6))
    plt.pie(df, labels=df.index, autopct='%1.1f%%', startangle=90)
    plt.title('Perbandingan pesanan berdasarkan ketepatan waktu')
    plt.axis('equal') 
    st.pyplot(plt)
    
## import csv
all_exc_rev_df = pd.read_csv("all_exc_rev.csv")
by_order_df = pd.read_csv("by_order.csv")

## Mengubah tipe data 
datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
add_datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date", "shipping_limit_date"]
by_order_df.sort_values(by="order_purchase_timestamp", inplace=True)
by_order_df.reset_index(inplace=True)

for column in datetime_columns:
    by_order_df[column] = pd.to_datetime(by_order_df[column])
for column in add_datetime_columns:
    all_exc_rev_df[column] = pd.to_datetime(all_exc_rev_df[column])

min_date = by_order_df["order_purchase_timestamp"].min()
max_date = by_order_df["order_purchase_timestamp"].max()
# status_counts = orders_items_df['order_status_limit'].value_counts()

## Membuat judul
st.title('Belajar Analisis Data')
st.header('Pengembangan Dashboard dengan Streamlit')
st.write('Pilih rentang waktu')

## Membuat kolom input
col1, col2 = st.columns(2)

with col1:

    start_date = st.date_input(
        label='Rentang waktu awal',
        min_value=min_date,
        value= min_date
    )

with col2:

    end_date = st.date_input(
        label='Rentang waktu akhir',
        max_value=max_date,
        value= max_date
    )

## Membuat filter
main_df = by_order_df[(by_order_df["order_purchase_timestamp"] >= str(start_date)) & 
                (by_order_df["order_purchase_timestamp"] <= str(end_date))]

addition_df = all_exc_rev_df[(all_exc_rev_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_exc_rev_df["order_purchase_timestamp"] <= str(end_date))]

## Eksekusi fungsi
daily_orders_df = create_daily_orders_df(main_df)
by_review_df = create_byreview_df(main_df)
deliv_order = create_bydelivorder_df(main_df)

## Menambah kolom 'month' dan 'order_status_limit' dalam tabel addition
addition_df['month'] = addition_df['order_purchase_timestamp'].dt.to_period('M')
monthly_revenue = addition_df.groupby('month')['payment_value'].sum()

addition_df['order_status_limit'] = addition_df.apply(
    lambda x: 'on-time' if x['shipping_limit_date'] >= x['order_delivered_customer_date'] else 'late',
    axis=1
)
status_counts = addition_df['order_status_limit'].value_counts()

## Menampilkan hasil filter dengan chart
with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1 :
        total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='es_CO') 
        st.metric("Total Revenue", value=total_revenue)
    with col2 :
        delivered_count = deliv_order.shape[0]
        st.metric("Total Delivered Order", value=delivered_count)

with st.container(border=True):
    show_line_chart(monthly_revenue)

with st.container(border=True):
    col1, col2 = st.columns(2)

    with col1 :
        fig, ax = plt.subplots(figsize=(16, 8))
        show_pie_chart(main_df)
    with col2 :
        show_on_time_chart(status_counts)
   

        
