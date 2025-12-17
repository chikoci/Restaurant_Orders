# Import library
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
# Import fungsi dari config.py
from config import *

# Setup halaman
st.set_page_config(page_title="Restaurant Orders Dashboard", layout="wide")

# Color palette profesional
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72', 
    'success': '#28A745',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'info': '#17A2B8',
    'palette': ['#2E86AB', '#A23B72', '#28A745', '#F18F01', '#C73E1D', '#17A2B8', '#6C757D', '#563D7C']
}

# Template plotly yang clean
CHART_TEMPLATE = 'plotly_white'

# Load semua data
df_customers = pd.DataFrame(view_customers(), columns=[
    'customer_id', 'customer_name', 'email', 'phone', 'total_spending'
])

df_categories = pd.DataFrame(view_categories(), columns=[
    'category_id', 'category_name', 'total_qty', 'order_date'
])

df_payment = pd.DataFrame(view_payment_methods(), columns=[
    'payment_id', 'method_name', 'revenue', 'order_date'
])

df_tables = pd.DataFrame(view_tables(), columns=[
    'table_id', 'table_number', 'capacity', 'location', 'status'
])

df_table_usage = pd.DataFrame(view_table_usage(), columns=[
    'table_id', 'table_number', 'capacity', 'times_used', 'order_date'
])

df_menu = pd.DataFrame(view_menu(), columns=[
    'menu_id', 'item_name', 'unit_price', 'member_only', 'category_name', 'total_ordered', 'order_date'
])

df_orders = pd.DataFrame(view_orders(), columns=[
    'order_id', 'customer_id', 'guest_name', 'service_type', 'table_id', 
    'payment_id', 'order_status', 'order_time', 'method_name', 'table_number', 
    'customer_name', 'order_date'
])

df_details = pd.DataFrame(view_order_details(), columns=[
    'order_detail_id', 'order_id', 'menu_id', 'quantity', 'total_price',
    'request_note', 'item_name', 'unit_price', 'order_date'
])

df_reservations = pd.DataFrame(view_reservations(), columns=[
    'reservation_id', 'customer_id', 'table_id', 'reservation_date',
    'check_in', 'check_out', 'party_size', 'status', 'special_request',
    'table_number', 'capacity', 'customer_name'
])

df_reviews = pd.DataFrame(view_reviews(), columns=[
    'review_id', 'order_id', 'rating', 'comment', 'review_date', 'customer_name'
])

# Format tanggal
for df in [df_categories, df_payment, df_table_usage, df_menu, df_orders, df_details]:
    if 'order_date' in df.columns and not df.empty:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

if not df_reservations.empty:
    df_reservations['reservation_date'] = pd.to_datetime(df_reservations['reservation_date'], errors='coerce')

if not df_reviews.empty:
    df_reviews['review_date'] = pd.to_datetime(df_reviews['review_date'], errors='coerce')

# Helper functions
def format_rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")

def filter_by_date(df, date_col, label):
    if df.empty or date_col not in df.columns:
        return df
    min_date = df[date_col].min().date()
    max_date = df[date_col].max().date()
    date_range = st.sidebar.date_input(
        label, value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    if len(date_range) == 2:
        start, end = date_range
        return df[(df[date_col].dt.date >= start) & (df[date_col].dt.date <= end)]
    return df

def download_csv(df, filename, label):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label=label, data=csv, file_name=filename, mime='text/csv')

# Fungsi buat chart yang konsisten
def create_bar_chart(data, x, y, title='', horizontal=False, color=None):
    if horizontal:
        fig = px.bar(data, y=x, x=y, orientation='h', color_discrete_sequence=[color or COLORS['primary']],
                     template=CHART_TEMPLATE)
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    else:
        fig = px.bar(data, x=x, y=y, color_discrete_sequence=[color or COLORS['primary']],
                     template=CHART_TEMPLATE)
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20),
                      title=dict(text=title, x=0.5, font=dict(size=14)))
    fig.update_traces(hovertemplate='%{x}: %{y:,.0f}<extra></extra>' if not horizontal else '%{y}: %{x:,.0f}<extra></extra>')
    return fig

def create_pie_chart(values, names, title='', max_slices=6):
    # Limit slices, gabung sisanya jadi 'Lainnya'
    df = pd.DataFrame({'names': names, 'values': values}).sort_values('values', ascending=False)
    if len(df) > max_slices:
        top = df.head(max_slices - 1)
        others = pd.DataFrame({'names': ['Lainnya'], 'values': [df.iloc[max_slices-1:]['values'].sum()]})
        df = pd.concat([top, others])
    
    fig = px.pie(df, values='values', names='names', hole=0.4,
                 color_discrete_sequence=COLORS['palette'], template=CHART_TEMPLATE)
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20),
                      title=dict(text=title, x=0.5, font=dict(size=14)),
                      legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5))
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_line_chart(x, y, title='', fill=False):
    fig = px.line(x=x, y=y, markers=True, template=CHART_TEMPLATE,
                  color_discrete_sequence=[COLORS['primary']])
    if fill:
        fig = px.area(x=x, y=y, template=CHART_TEMPLATE,
                      color_discrete_sequence=[COLORS['primary']])
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20),
                      title=dict(text=title, x=0.5, font=dict(size=14)),
                      xaxis_title='', yaxis_title='')
    return fig

# Fungsi tampilan Dashboard
def tampilkan_dashboard():
    st.title("Dashboard Utama")
    st.caption("Ringkasan performa restoran")
    
    # Metrics ringkasan dengan styling
    col1, col2, col3, col4 = st.columns(4)
    total_revenue = df_details['total_price'].sum() if not df_details.empty else 0
    avg_order = df_details.groupby('order_id')['total_price'].sum().mean() if not df_details.empty else 0
    
    with col1:
        st.metric("Total Customer", f"{len(df_customers):,}")
    with col2:
        st.metric("Total Menu", f"{df_menu['menu_id'].nunique():,}")
    with col3:
        st.metric("Total Order", f"{len(df_orders):,}")
    with col4:
        st.metric("Total Revenue", format_rupiah(total_revenue))
    
    st.markdown("")
    
    # Grafik ringkasan
    col_left, col_right = st.columns(2)
    
    with col_left:
        if not df_menu.empty:
            top_menu = df_menu.groupby('item_name')['total_ordered'].sum().sort_values(ascending=False).head(5).reset_index()
            top_menu.columns = ['Menu', 'Total']
            fig = create_bar_chart(top_menu, 'Menu', 'Total', 'Top 5 Menu Terlaris', horizontal=True)
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        if not df_details.empty:
            daily = df_details.groupby(df_details['order_date'].dt.date)['total_price'].sum()
            fig = create_line_chart(daily.index, daily.values, 'Trend Pendapatan Harian', fill=True)
            st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if not df_orders.empty:
            service = df_orders['service_type'].value_counts()
            fig = create_pie_chart(service.values, service.index, 'Distribusi Tipe Layanan')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not df_orders.empty:
            payment = df_orders['method_name'].value_counts()
            fig = create_pie_chart(payment.values, payment.index, 'Distribusi Pembayaran')
            st.plotly_chart(fig, use_container_width=True)

# Fungsi tampilan Customers
def tampilkan_customers():
    st.title("Data Customers")
    st.caption("Daftar pelanggan dan total pengeluaran")
    
    # Konversi total_spending ke numeric
    df_cust = df_customers.copy()
    df_cust['total_spending'] = pd.to_numeric(df_cust['total_spending'], errors='coerce').fillna(0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customer", f"{len(df_cust):,}")
    with col2:
        total_spending = df_cust['total_spending'].sum() if not df_cust.empty else 0
        st.metric("Total Spending", format_rupiah(total_spending))
    with col3:
        avg_spending = df_cust['total_spending'].mean() if not df_cust.empty else 0
        st.metric("Rata-rata", format_rupiah(avg_spending))
    
    # Filter pencarian
    search = st.text_input("Cari (nama/email/telepon)")
    filtered = df_cust.copy()
    if search:
        filtered = filtered[
            filtered['customer_name'].str.contains(search, case=False, na=False) |
            filtered['email'].str.contains(search, case=False, na=False) |
            filtered['phone'].str.contains(search, case=False, na=False)
        ]
    
    # Grafik top spending - horizontal bar
    top10 = filtered.nlargest(10, 'total_spending')[['customer_name', 'total_spending']]
    top10.columns = ['Customer', 'Spending']
    fig = create_bar_chart(top10, 'Customer', 'Spending', 'Top 10 Customer (Spending)', horizontal=True, color=COLORS['secondary'])
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Tabel Customer")
    display = filtered.copy()
    display['total_spending'] = display['total_spending'].apply(format_rupiah)
    st.dataframe(display, use_container_width=True)
    download_csv(filtered, 'data_customers.csv', 'Download CSV')

# Fungsi tampilan Categories
def tampilkan_categories():
    st.title("Kategori Menu")
    st.caption("Analisis penjualan per kategori")
    
    filtered = filter_by_date(df_categories.copy(), 'order_date', 'Filter Tanggal')
    
    cat_summary = filtered.groupby('category_name')['total_qty'].sum().reset_index()
    cat_summary = cat_summary.sort_values('total_qty', ascending=False)
    cat_summary.columns = ['Kategori', 'Total']
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = create_bar_chart(cat_summary, 'Kategori', 'Total', 'Penjualan per Kategori', horizontal=True, color=COLORS['success'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = create_pie_chart(cat_summary['Total'].values, cat_summary['Kategori'].values, 'Proporsi')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(cat_summary, use_container_width=True)
    download_csv(cat_summary, 'data_categories.csv', 'Download CSV')

# Fungsi tampilan Payment Methods
def tampilkan_payment():
    st.title("Metode Pembayaran")
    st.caption("Analisis pendapatan per metode pembayaran")
    
    filtered = filter_by_date(df_payment.copy(), 'order_date', 'Filter Tanggal')
    
    pay_summary = filtered.groupby('method_name')['revenue'].sum().reset_index()
    pay_summary = pay_summary.sort_values('revenue', ascending=False)
    pay_summary.columns = ['Metode', 'Revenue']
    
    # Metrics
    cols = st.columns(len(pay_summary) if len(pay_summary) <= 4 else 4)
    for i, (_, row) in enumerate(pay_summary.head(4).iterrows()):
        with cols[i]:
            st.metric(row['Metode'], format_rupiah(row['Revenue']))
    
    col1, col2 = st.columns(2)
    with col1:
        fig = create_bar_chart(pay_summary, 'Metode', 'Revenue', 'Revenue per Metode', horizontal=True, color=COLORS['warning'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_pie_chart(pay_summary['Revenue'].values, pay_summary['Metode'].values, 'Distribusi Revenue')
        st.plotly_chart(fig, use_container_width=True)
    
    download_csv(pay_summary, 'data_payment.csv', 'Download CSV')

# Fungsi tampilan Tables
def tampilkan_tables():
    st.title("Data Meja")
    st.caption("Informasi dan penggunaan meja")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Meja", f"{len(df_tables):,}")
    with col2:
        st.metric("Total Kapasitas", f"{df_tables['capacity'].sum():,}")
    with col3:
        if not df_table_usage.empty:
            usage = df_table_usage.groupby('table_number')['times_used'].sum()
            if not usage.empty:
                st.metric("Meja Terfavorit", f"Meja {usage.idxmax()}")
    
    filtered = filter_by_date(df_table_usage.copy(), 'order_date', 'Filter Tanggal')
    usage_summary = filtered.groupby(['table_number', 'capacity'])['times_used'].sum().reset_index()
    usage_summary['Meja'] = 'Meja ' + usage_summary['table_number'].astype(str)
    usage_summary = usage_summary.rename(columns={'times_used': 'Penggunaan'})
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = create_bar_chart(usage_summary, 'Meja', 'Penggunaan', 'Frekuensi Penggunaan Meja', horizontal=True, color=COLORS['info'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Info Meja")
        st.dataframe(df_tables[['table_number', 'capacity', 'location', 'status']], use_container_width=True, hide_index=True)
    
    download_csv(df_tables, 'data_tables.csv', 'Download CSV')

# Fungsi tampilan Menu
def tampilkan_menu():
    st.title("Data Menu")
    st.caption("Daftar menu dan performa penjualan")
    
    filtered = filter_by_date(df_menu.copy(), 'order_date', 'Filter Tanggal')
    
    # Filter harga
    if not filtered.empty:
        filtered['unit_price'] = pd.to_numeric(filtered['unit_price'], errors='coerce')
        min_price = float(filtered['unit_price'].min())
        max_price = float(filtered['unit_price'].max())
        if min_price < max_price:
            price_range = st.sidebar.slider("Filter Harga", min_price, max_price, (min_price, max_price))
            filtered = filtered[filtered['unit_price'].between(*price_range)]
    
    menu_summary = filtered.groupby(['menu_id', 'item_name', 'unit_price', 'category_name', 'member_only']).agg({
        'total_ordered': 'sum'
    }).reset_index().sort_values('total_ordered', ascending=False)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Menu", f"{len(menu_summary):,}")
    with col2:
        member_only = len(menu_summary[menu_summary['member_only'] == 1])
        st.metric("Member Only", f"{member_only:,}")
    with col3:
        st.metric("Total Terjual", f"{menu_summary['total_ordered'].sum():,.0f}")
    
    # Top 10 horizontal
    top10 = menu_summary.head(10)[['item_name', 'total_ordered', 'category_name']].copy()
    top10.columns = ['Menu', 'Total', 'Kategori']
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = create_bar_chart(top10, 'Menu', 'Total', 'Top 10 Menu Terlaris', horizontal=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        cat_sales = menu_summary.groupby('category_name')['total_ordered'].sum()
        fig = create_pie_chart(cat_sales.values, cat_sales.index, 'Per Kategori')
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Daftar Menu")
    display = menu_summary[['item_name', 'unit_price', 'category_name', 'member_only', 'total_ordered']].copy()
    display.columns = ['Menu', 'Harga', 'Kategori', 'Member Only', 'Terjual']
    display['Harga'] = display['Harga'].apply(format_rupiah)
    display['Member Only'] = display['Member Only'].map({1: 'Ya', 0: 'Tidak'})
    st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(menu_summary, 'data_menu.csv', 'Download CSV')

# Fungsi tampilan Orders
def tampilkan_orders():
    st.title("Data Orders")
    st.caption("Riwayat dan analisis pesanan")
    
    filtered = filter_by_date(df_orders.copy(), 'order_date', 'Filter Tanggal')
    
    col1, col2, col3, col4 = st.columns(4)
    pending = len(filtered[filtered['order_status'] == 'Pending']) if not filtered.empty else 0
    completed = len(filtered[filtered['order_status'] == 'Completed']) if not filtered.empty else 0
    dine_in = len(filtered[filtered['service_type'] == 'Dine In']) if not filtered.empty else 0
    
    with col1:
        st.metric("Total Order", f"{len(filtered):,}")
    with col2:
        st.metric("Pending", f"{pending:,}", delta=f"{pending/len(filtered)*100:.1f}%" if len(filtered) > 0 else "0%")
    with col3:
        st.metric("Completed", f"{completed:,}")
    with col4:
        st.metric("Dine In", f"{dine_in:,}")
    
    if not filtered.empty:
        col1, col2 = st.columns(2)
        with col1:
            daily = filtered.groupby(filtered['order_date'].dt.date).size().reset_index()
            daily.columns = ['Tanggal', 'Jumlah']
            fig = create_line_chart(daily['Tanggal'], daily['Jumlah'], 'Trend Order Harian')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            filtered['hour'] = pd.to_datetime(filtered['order_time']).dt.hour
            hourly = filtered.groupby('hour').size().reset_index()
            hourly.columns = ['Jam', 'Jumlah']
            fig = create_bar_chart(hourly, 'Jam', 'Jumlah', 'Distribusi Order per Jam', color=COLORS['info'])
            st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            service = filtered['service_type'].value_counts()
            fig = create_pie_chart(service.values, service.index, 'Tipe Layanan')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            status = filtered['order_status'].value_counts()
            fig = create_pie_chart(status.values, status.index, 'Status Order')
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Tabel Orders")
    display = filtered[['order_id', 'customer_name', 'guest_name', 'service_type', 'order_status', 'method_name', 'order_time']].copy()
    display.columns = ['ID', 'Customer', 'Guest', 'Tipe', 'Status', 'Payment', 'Waktu']
    st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(filtered, 'data_orders.csv', 'Download CSV')

# Fungsi tampilan Order Details
def tampilkan_details():
    st.title("Order Details")
    st.caption("Detail item per pesanan dan analisis revenue")
    
    filtered = filter_by_date(df_details.copy(), 'order_date', 'Filter Tanggal')
    
    if not filtered.empty:
        avg = filtered.groupby('order_id')['total_price'].sum().mean()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Item", f"{int(filtered['quantity'].sum()):,}")
        with col2:
            st.metric("Total Revenue", format_rupiah(filtered['total_price'].sum()))
        with col3:
            st.metric("Avg per Order", format_rupiah(avg))
        with col4:
            st.metric("Total Transaksi", f"{filtered['order_id'].nunique():,}")
        
        col1, col2 = st.columns(2)
        with col1:
            daily = filtered.groupby(filtered['order_date'].dt.date)['total_price'].sum()
            fig = create_line_chart(daily.index, daily.values, 'Trend Revenue Harian', fill=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_products = filtered.groupby('item_name')['quantity'].sum().sort_values(ascending=False).head(10).reset_index()
            top_products.columns = ['Menu', 'Qty']
            fig = create_bar_chart(top_products, 'Menu', 'Qty', 'Top 10 Produk Terlaris', horizontal=True, color=COLORS['success'])
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Tabel Order Details")
    if not filtered.empty:
        display = filtered[['order_id', 'item_name', 'quantity', 'unit_price', 'total_price', 'request_note']].copy()
        display.columns = ['Order ID', 'Menu', 'Qty', 'Harga', 'Total', 'Request']
        display['Harga'] = display['Harga'].apply(format_rupiah)
        display['Total'] = display['Total'].apply(format_rupiah)
        st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(filtered, 'data_order_details.csv', 'Download CSV')

# Fungsi tampilan Reservations
def tampilkan_reservations():
    st.title("Reservations")
    st.caption("Manajemen reservasi meja")
    
    filtered = filter_by_date(df_reservations.copy(), 'reservation_date', 'Filter Tanggal')
    
    if not filtered.empty:
        # Handle check_in yang bisa berformat timedelta atau time
        def extract_hour(val):
            try:
                if pd.isna(val):
                    return 0
                val_str = str(val)
                # Format "0 days HH:MM:SS" atau "HH:MM:SS"
                if 'days' in val_str:
                    time_part = val_str.split(' ')[-1]
                else:
                    time_part = val_str
                return int(time_part.split(':')[0])
            except:
                return 0
        
        filtered['check_in_hour'] = filtered['check_in'].apply(extract_hour)
        top_table = filtered['table_number'].value_counts().idxmax()
        top_hour = filtered['check_in_hour'].value_counts().idxmax()
        avg_party = filtered['party_size'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Reservasi", f"{len(filtered):,}")
        with col2:
            st.metric("Meja Favorit", f"Meja {top_table}")
        with col3:
            st.metric("Jam Populer", f"{top_hour}:00")
        with col4:
            st.metric("Avg Party Size", f"{avg_party:.1f}")
        
        col1, col2 = st.columns(2)
        with col1:
            table_count = filtered['table_number'].value_counts().reset_index()
            table_count.columns = ['Meja', 'Jumlah']
            table_count['Meja'] = 'Meja ' + table_count['Meja'].astype(str)
            fig = create_bar_chart(table_count, 'Meja', 'Jumlah', 'Reservasi per Meja', horizontal=True, color=COLORS['secondary'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            hour_count = filtered['check_in_hour'].value_counts().sort_index().reset_index()
            hour_count.columns = ['Jam', 'Jumlah']
            fig = create_bar_chart(hour_count, 'Jam', 'Jumlah', 'Distribusi Jam Check-in', color=COLORS['info'])
            st.plotly_chart(fig, use_container_width=True)
        
        # Special requests
        with_request = filtered[filtered['special_request'].notna() & (filtered['special_request'] != '')]
        if not with_request.empty:
            st.subheader("Special Requests")
            display_req = with_request[['customer_name', 'table_number', 'reservation_date', 'special_request']].copy()
            display_req.columns = ['Customer', 'Meja', 'Tanggal', 'Request']
            st.dataframe(display_req, use_container_width=True, hide_index=True)
    
    st.subheader("Semua Reservasi")
    if not filtered.empty:
        display = filtered[['reservation_id', 'customer_name', 'table_number', 'reservation_date', 
                           'check_in', 'check_out', 'party_size', 'status']].copy()
        display.columns = ['ID', 'Customer', 'Meja', 'Tanggal', 'Check-in', 'Check-out', 'Party', 'Status']
        st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(filtered, 'data_reservations.csv', 'Download CSV')

# Fungsi tampilan Reviews
def tampilkan_reviews():
    st.title("Reviews")
    st.caption("Ulasan dan rating pelanggan")
    
    filtered = filter_by_date(df_reviews.copy(), 'review_date', 'Filter Tanggal')
    
    if not filtered.empty:
        avg_rating = filtered['rating'].mean()
        five_star = len(filtered[filtered['rating'] == 5])
        one_star = len(filtered[filtered['rating'] == 1])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Review", f"{len(filtered):,}")
        with col2:
            st.metric("Avg Rating", f"{avg_rating:.2f}/5")
        with col3:
            st.metric("Bintang 5", f"{five_star:,}", delta=f"{five_star/len(filtered)*100:.1f}%")
        with col4:
            st.metric("Bintang 1", f"{one_star:,}")
        
        col1, col2 = st.columns(2)
        with col1:
            rating_count = filtered['rating'].value_counts().sort_index().reset_index()
            rating_count.columns = ['Rating', 'Jumlah']
            fig = create_bar_chart(rating_count, 'Rating', 'Jumlah', 'Distribusi Rating', color=COLORS['warning'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Rating trend
            daily_rating = filtered.groupby(filtered['review_date'].dt.date)['rating'].mean().reset_index()
            daily_rating.columns = ['Tanggal', 'Rating']
            fig = create_line_chart(daily_rating['Tanggal'], daily_rating['Rating'], 'Trend Rating Harian')
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Semua Review")
    if not filtered.empty:
        display = filtered[['review_id', 'customer_name', 'rating', 'comment', 'review_date']].copy()
        display.columns = ['ID', 'Customer', 'Rating', 'Komentar', 'Tanggal']
        st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(filtered, 'data_reviews.csv', 'Download CSV')

# Sidebar navigasi - Radio button (single page)
st.sidebar.title("Restaurant Orders Dashboard")
st.sidebar.markdown("---")

halaman = st.sidebar.radio(
    "Pilih Halaman",
    options=[
        "Dashboard",
        "Customers",
        "Categories", 
        "Payment Methods",
        "Tables",
        "Menu",
        "Orders",
        "Order Details",
        "Reservations",
        "Reviews"
    ],
    index=0
)

st.sidebar.markdown("---")

# Tampilkan halaman sesuai pilihan
if halaman == "Dashboard":
    tampilkan_dashboard()
elif halaman == "Customers":
    tampilkan_customers()
elif halaman == "Categories":
    tampilkan_categories()
elif halaman == "Payment Methods":
    tampilkan_payment()
elif halaman == "Tables":
    tampilkan_tables()
elif halaman == "Menu":
    tampilkan_menu()
elif halaman == "Orders":
    tampilkan_orders()
elif halaman == "Order Details":
    tampilkan_details()
elif halaman == "Reservations":
    tampilkan_reservations()
elif halaman == "Reviews":
    tampilkan_reviews()

st.sidebar.caption("© 2025 Restaurant Order Management")
