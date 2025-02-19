import streamlit as st
import pandas as pd
import plotly.express as px

# Load Data


@st.cache_data
def load_data():
    # Gantilah dengan dataset Anda
    return pd.read_csv("dashboard/main_data.csv")


df = load_data()

# Konversi kolom 'order_purchase_timestamp' ke tipe data datetime
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

# Tampilkan dataset
st.subheader("📁 Dataset Preview")
st.write(df.head())

# Analisis 1: Penjualan Tertinggi dan Terendah per Kategori
st.subheader("📈 Top and Bottom Product Categories by Sales")

# Hitung total penjualan per kategori
sales_by_category = df.groupby('product_category')[
    'price'].sum().reset_index()
sales_by_category.columns = ['Category', 'Total Sales']

# Urutkan berdasarkan total penjualan
top_categories = sales_by_category.sort_values(
    by='Total Sales', ascending=False).head(10)
bottom_categories = sales_by_category.sort_values(
    by='Total Sales', ascending=True).head(10)

# Tampilkan penjualan tertinggi
st.write("**Top 10 Categories by Sales:**")
st.write(top_categories)

# Visualisasi penjualan tertinggi
fig_top = px.bar(top_categories, x='Category', y='Total Sales',
                 title='Top 10 Categories by Sales')
st.plotly_chart(fig_top)

# Tampilkan penjualan terendah
st.write("**Bottom 10 Categories by Sales:**")
st.write(bottom_categories)

# Visualisasi penjualan terendah
fig_bottom = px.bar(bottom_categories, x='Category',
                    y='Total Sales', title='Bottom 10 Categories by Sales')
st.plotly_chart(fig_bottom)

# Analisis 2: Tren Jumlah Pesanan dari Waktu ke Waktu
st.subheader("📅 Order Trends Over Time")

# Hitung jumlah pesanan per bulan
df['order_month'] = df['order_purchase_timestamp'].dt.to_period(
    'M').astype(str)
orders_over_time = df.groupby('order_month')[
    'order_id'].nunique().reset_index()
orders_over_time.columns = ['Month', 'Number of Orders']

# Tampilkan tren pesanan
st.write("**Number of Orders Over Time:**")
st.write(orders_over_time)

# Visualisasi tren pesanan
fig_trend = px.line(orders_over_time, x='Month',
                    y='Number of Orders', title='Order Trends Over Time')
st.plotly_chart(fig_trend)

# Analisis 3: Metode Pembayaran Terfavorit
st.subheader("💳 Most Popular Payment Methods")

# Hitung jumlah penggunaan metode pembayaran
payment_methods = df['payment_type'].value_counts().reset_index()
payment_methods.columns = ['Payment Method', 'Count']

# Tampilkan metode pembayaran terfavorit
st.write("**Most Popular Payment Methods:**")
st.write(payment_methods)

# Visualisasi metode pembayaran terfavorit
fig_payment = px.pie(payment_methods, values='Count',
                     names='Payment Method', title='Payment Method Distribution')
st.plotly_chart(fig_payment)

# Hitung RFM Metrics
st.subheader("📊 RFM Metrics Calculation")
latest_date = df['order_purchase_timestamp'].max()
rfm_df = df.groupby('customer_id').agg({
    # Recency
    'order_purchase_timestamp': lambda x: (latest_date - x.max()).days,
    'order_id': 'count',  # Frequency
    'payment_value': 'sum'  # Monetary
})

# Ganti nama kolom agar lebih jelas
rfm_df.rename(columns={
    'order_purchase_timestamp': 'Recency',
    'order_id': 'Frequency',
    'payment_value': 'Monetary'
}, inplace=True)

# Tampilkan RFM Metrics
st.write("RFM Metrics:")
st.write(rfm_df.head())

# Terapkan RFM Segmentation
st.subheader("📌 RFM Segmentation")
rfm_df['R_Score'] = pd.cut(rfm_df['Recency'].rank(
    method="first"), bins=3, labels=[3, 2, 1])
rfm_df['F_Score'] = pd.cut(rfm_df['Frequency'].rank(
    method="first"), bins=3, labels=[1, 2, 3])
rfm_df['M_Score'] = pd.cut(rfm_df['Monetary'].rank(
    method="first"), bins=3, labels=[1, 2, 3])

# Gabungkan skor menjadi RFM Score
rfm_df['RFM_Score'] = (
    rfm_df['R_Score'].astype(str) +
    rfm_df['F_Score'].astype(str) +
    rfm_df['M_Score'].astype(str)
)

# Buat RFM Segmentation


def segment_customer(row):
    r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])

    if r == 3 and f == 3 and m == 3:
        return 'Loyal Customers'
    elif r == 3 and (f < 3 or m < 3):
        return 'Promising'
    elif r < 3 and f >= 2 and m >= 2:
        return 'Customers Needing Attention'
    else:
        return 'Hibernating'


# Buat kolom baru untuk segmentasi
rfm_df['Segment'] = rfm_df.apply(segment_customer, axis=1)

# Tampilkan RFM Segmentation
st.write("RFM Segmentation:")
st.write(rfm_df.head())

# Visualisasi Segmentasi Pelanggan
st.subheader("📊 Customer Segmentation Distribution")
segmentation_counts = rfm_df['Segment'].value_counts().reset_index()
segmentation_counts.columns = ['Segment', 'Count']
fig_seg = px.bar(segmentation_counts, x='Segment', y='Count',
                 color='Segment', title='Customer Segmentation')
st.plotly_chart(fig_seg)
