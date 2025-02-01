import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

def load_data():
    main_data = pd.read_csv("all_dataset.csv")
    return main_data

def plot_custom_bar_chart(data, title, xlabel, ylabel, rotation=0):
    plt.figure(figsize=(10, 6))
    data.plot(kind='bar', color='skyblue', alpha=0.8)
    plt.title(title, fontsize=14, weight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=rotation) 
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    st.pyplot(plt)


def plot_custom_line_chart(data, title, xlabel, ylabel):
    plt.figure(figsize=(10, 6))
    data.plot(color='dodgerblue', alpha=0.8, marker='o')
    plt.title(title, fontsize=14, weight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(axis='both', linestyle='--', alpha=0.6)
    plt.tight_layout()
    st.pyplot(plt)

def main():
    st.title("E-Commerce Public Dataset Dashboard")
    st.subheader("By: Salma Adzra Fathina")
    st.sidebar.header("Filter")

    data = load_data()

    category = st.sidebar.multiselect(
        "Pilih Kategori Produk",
        options=data["product_category_name_english"].unique(),
        default=data["product_category_name_english"].unique(),
    )
    state = st.sidebar.multiselect(
        "Pilih Negara Bagian",
        options=data["customer_state"].unique(),
        default=data["customer_state"].unique(),
    )

    filtered_data = data[
        (data["product_category_name_english"].isin(category)) &
        (data["customer_state"].isin(state))
    ]

    st.subheader("Total Penjualan Berdasarkan Kategori")
    sales_by_category = filtered_data.groupby("product_category_name_english")["price"].sum()
    plot_custom_bar_chart(
        sales_by_category,
        title="Total Penjualan Berdasarkan Kategori",
        xlabel="Kategori Produk",
        ylabel="Total Penjualan (BRL)",
        rotation=90
    )

    

    st.subheader("Tren Penjualan Bulanan")
    filtered_data["order_purchase_timestamp"] = pd.to_datetime(filtered_data["order_purchase_timestamp"])
    monthly_sales = (
        filtered_data.groupby(filtered_data["order_purchase_timestamp"].dt.to_period("M"))["price"].sum()
    )
    plot_custom_line_chart(
        monthly_sales,
        title="Tren Penjualan Bulanan",
        xlabel="Bulan",
        ylabel="Total Penjualan (BRL)"
    )

    st.subheader("Tren Penjualan Harian")
    daily_sales = (
        filtered_data.groupby(filtered_data["order_purchase_timestamp"].dt.to_period("D"))["price"].sum()
    )
    plot_custom_line_chart(
        daily_sales,
        title="Tren Penjualan Harian",
        xlabel="Tanggal",
        ylabel="Total Penjualan (BRL)"
    )

    st.subheader("Total Penjualan Berdasarkan Negara Bagian")
    sales_by_state = filtered_data.groupby("customer_state")["price"].sum()
    plot_custom_bar_chart(
    sales_by_state,
    title="Total Penjualan Berdasarkan Negara Bagian",
    xlabel="Negara Bagian",
    ylabel="Total Penjualan (BRL)"
    )

    
    st.subheader("Total Penjualan Berdasarkan Kota (Top 20)")
    sales_by_city = (
        filtered_data.groupby("customer_city")["price"].sum().sort_values(ascending=False).head(20)
    )
    plot_custom_bar_chart(
        sales_by_city,
        title="Total Penjualan Berdasarkan Kota (Top 20)",
        xlabel="Kota",
        ylabel="Total Penjualan (BRL)",
        rotation=90
    )

    st.subheader("RFM Analysis")
    all_df = filtered_data.copy()
    all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

    reference_date = all_df['order_purchase_timestamp'].max() + dt.timedelta(days=1)

    rfm = all_df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,
        'order_id': 'count',
        'price': 'sum'
    }).reset_index()

    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']

    frequency_bins = len(pd.qcut(rfm['frequency'], 4, duplicates='drop').dtype.categories)
    monetary_bins = len(pd.qcut(rfm['monetary'], 4, duplicates='drop').dtype.categories)

    rfm['recency_score'] = pd.qcut(rfm['recency'], 4, labels=[4, 3, 2, 1])
    rfm['frequency_score'] = pd.qcut(rfm['frequency'], frequency_bins, labels=range(1, frequency_bins + 1))
    rfm['monetary_score'] = pd.qcut(rfm['monetary'], monetary_bins, labels=range(1, monetary_bins + 1))

    rfm['rfm_score'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str)

    def segment_customer(rfm_score):
        if rfm_score == '444':
            return 'High Value Customers'
        elif rfm_score.startswith('4'):
            return 'Recent and Active Customers'
        elif rfm_score[1] == '4':
            return 'High Frequency Customers'
        elif rfm_score[2] == '4':
            return 'High Monetary Customers'
        elif rfm_score in ['111', '211', '311']:
            return 'Low Engagement Customers'
        else:
            return 'Medium Value Customers'

    rfm['segment'] = rfm['rfm_score'].apply(segment_customer)

    st.write("RFM Segments Distribution")
    plot_custom_bar_chart(
    rfm['segment'].value_counts(),
    title="Distribusi Segmen Pelanggan Berdasarkan RFM",
    xlabel="Segment",
    ylabel="Jumlah Pelanggan"
)


if __name__ == "__main__":
    main()
