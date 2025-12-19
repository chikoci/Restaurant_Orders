# Import library
import streamlit as st
import pandas as pd
import plotly.express as px
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

# HELPER FUNCTIONS

def format_rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")

def filter_by_date_sidebar(df, date_col, key_prefix):
    """Filter tanggal di sidebar dengan tombol reset"""
    if df.empty or date_col not in df.columns:
        return df
    
    min_date = df[date_col].min().date()
    max_date = df[date_col].max().date()
    
    st.sidebar.markdown("**Filter Tanggal**")
    
    # Inisialisasi session state jika belum ada
    if f"date_{key_prefix}" not in st.session_state:
        st.session_state[f"date_{key_prefix}"] = (min_date, max_date)
    
    # Tombol reset
    if st.sidebar.button("Reset Tanggal", key=f"reset_{key_prefix}"):
        st.session_state[f"date_{key_prefix}"] = (min_date, max_date)
        st.rerun()
    
    date_range = st.sidebar.date_input(
        "Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        key=f"date_{key_prefix}"
    )
    
    if len(date_range) == 2:
        start, end = date_range
        return df[(df[date_col].dt.date >= start) & (df[date_col].dt.date <= end)]
    return df

def download_csv(df, filename, label):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label=label, data=csv, file_name=filename, mime='text/csv')

# CHART FUNCTIONS

def create_bar_chart_colored(data, x, y, title='', horizontal=False):
    """Bar chart dengan warna berbeda per kategori"""
    if horizontal:
        fig = px.bar(data, y=x, x=y, orientation='h', color=x,
                     color_discrete_sequence=COLORS['palette'], template=CHART_TEMPLATE)
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    else:
        fig = px.bar(data, x=x, y=y, color=x,
                     color_discrete_sequence=COLORS['palette'], template=CHART_TEMPLATE)
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20),
                      title=dict(text=title, x=0.5, font=dict(size=14)))
    return fig

def create_bar_chart(data, x, y, title='', horizontal=False, color=None):
    """Bar chart dengan satu warna"""
    if horizontal:
        fig = px.bar(data, y=x, x=y, orientation='h',
                     color_discrete_sequence=[color or COLORS['primary']], template=CHART_TEMPLATE)
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    else:
        fig = px.bar(data, x=x, y=y,
                     color_discrete_sequence=[color or COLORS['primary']], template=CHART_TEMPLATE)
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20),
                      title=dict(text=title, x=0.5, font=dict(size=14)))
    return fig

def create_pie_chart(values, names, title='', max_slices=6):
    """Donut chart"""
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
    """Line/Area chart"""
    if fill:
        fig = px.area(x=x, y=y, template=CHART_TEMPLATE, color_discrete_sequence=[COLORS['primary']])
    else:
        fig = px.line(x=x, y=y, markers=True, template=CHART_TEMPLATE, color_discrete_sequence=[COLORS['primary']])
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20),
                      title=dict(text=title, x=0.5, font=dict(size=14)), xaxis_title='', yaxis_title='')
    return fig

# DASHBOARD
def tampilkan_dashboard():
    st.title("Dashboard Utama")
    st.caption("Ringkasan performa restoran")
    
    st.sidebar.markdown("**Filter Tanggal**")
    
    if not df_orders.empty:
        min_date = df_orders['order_date'].min().date()
        max_date = df_orders['order_date'].max().date()
        
        if 'dashboard_date' not in st.session_state:
            st.session_state['dashboard_date'] = (min_date, max_date)
        
        if st.sidebar.button("Reset Tanggal", key="reset_dashboard"):
            st.session_state['dashboard_date'] = (min_date, max_date)
            st.rerun()
        
        date_range = st.sidebar.date_input(
            "Rentang Waktu",
            min_value=min_date,
            max_value=max_date,
            key="dashboard_date"
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date, end_date = None, None
    
    # Filter visualisasi yang ditampilkan
    st.sidebar.markdown("**Pilih Visualisasi**")
    viz_options = {
        "Top Menu Terlaris": True,
        "Trend Pendapatan": True,
        "Tipe Layanan": True,
        "Metode Pembayaran": True
    }
    
    selected_viz = []
    for viz_name, default in viz_options.items():
        if st.sidebar.checkbox(viz_name, value=default, key=f"viz_{viz_name}"):
            selected_viz.append(viz_name)
    
    # Filter data berdasarkan tanggal
    if start_date and end_date:
        df_orders_filtered = df_orders[(df_orders['order_date'].dt.date >= start_date) & 
                                        (df_orders['order_date'].dt.date <= end_date)]
        df_details_filtered = df_details[(df_details['order_date'].dt.date >= start_date) & 
                                          (df_details['order_date'].dt.date <= end_date)]
        df_menu_filtered = df_menu[(df_menu['order_date'].dt.date >= start_date) & 
                                    (df_menu['order_date'].dt.date <= end_date)]
    else:
        df_orders_filtered = df_orders
        df_details_filtered = df_details
        df_menu_filtered = df_menu
    
    # Hitung metrics
    total_revenue = df_details_filtered['total_price'].sum() if not df_details_filtered.empty else 0
    total_orders = len(df_orders_filtered)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Metrics
    st.markdown("### Ringkasan Statistik")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Order", f"{total_orders:,}")
    with col2:
        st.metric("Total Revenue", format_rupiah(total_revenue))
    with col3:
        st.metric("Rata-rata/Order", format_rupiah(avg_order_value))
    with col4:
        st.metric("Total Reservasi", f"{len(df_reservations):,}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customer", f"{len(df_customers):,}")
    with col2:
        st.metric("Total Menu", f"{df_menu['menu_id'].nunique():,}")
    with col3:
        st.metric("Total Meja", f"{len(df_tables):,}")
    with col4:
        avg_rating = df_reviews['rating'].mean() if not df_reviews.empty else 0
        st.metric("Rating", f"{avg_rating:.1f}/5")
    
    st.markdown("---")
    
    # Visualisasi berdasarkan pilihan
    if len(selected_viz) == 0:
        st.info("Pilih visualisasi yang ingin ditampilkan di sidebar.")
        return
    
    # Layout dinamis berdasarkan jumlah visualisasi
    if len(selected_viz) == 1:
        cols = st.columns(1)
    elif len(selected_viz) == 2:
        cols = st.columns(2)
    elif len(selected_viz) == 3:
        cols = st.columns(3)
    else:
        cols = st.columns(2)
    
    col_idx = 0
    
    if "Top Menu Terlaris" in selected_viz:
        with cols[col_idx % len(cols)]:
            if not df_menu_filtered.empty:
                top_menu = df_menu_filtered.groupby('item_name')['total_ordered'].sum().sort_values(ascending=False).head(5).reset_index()
                top_menu.columns = ['Menu', 'Terjual']
                fig = create_bar_chart(top_menu, 'Menu', 'Terjual', 'Top 5 Menu Terlaris', horizontal=True, color=COLORS['primary'])
                st.plotly_chart(fig, use_container_width=True)
        col_idx += 1
    
    if "Trend Pendapatan" in selected_viz:
        with cols[col_idx % len(cols)]:
            if not df_details_filtered.empty:
                daily = df_details_filtered.groupby(df_details_filtered['order_date'].dt.date)['total_price'].sum()
                fig = create_line_chart(daily.index, daily.values, 'Trend Pendapatan Harian', fill=True)
                st.plotly_chart(fig, use_container_width=True)
        col_idx += 1
    
    if "Tipe Layanan" in selected_viz:
        with cols[col_idx % len(cols)]:
            if not df_orders_filtered.empty:
                service = df_orders_filtered['service_type'].value_counts()
                fig = create_pie_chart(service.values, service.index, 'Distribusi Tipe Layanan')
                st.plotly_chart(fig, use_container_width=True)
        col_idx += 1
    
    if "Metode Pembayaran" in selected_viz:
        with cols[col_idx % len(cols)]:
            if not df_orders_filtered.empty:
                payment = df_orders_filtered['method_name'].value_counts()
                fig = create_pie_chart(payment.values, payment.index, 'Distribusi Pembayaran')
                st.plotly_chart(fig, use_container_width=True)
        col_idx += 1

# CUSTOMERS
def tampilkan_customers():
    st.title("Data Customers")
    st.caption("Daftar pelanggan dan analisis pengeluaran")
    
    # Filter tanggal berdasarkan orders
    st.sidebar.markdown("**Filter Tanggal**")
    if not df_orders.empty:
        min_date = df_orders['order_date'].min().date()
        max_date = df_orders['order_date'].max().date()
        
        if 'customers_date' not in st.session_state:
            st.session_state['customers_date'] = (min_date, max_date)
        
        if st.sidebar.button("Reset Tanggal", key="reset_customers_date"):
            st.session_state['customers_date'] = (min_date, max_date)
            st.rerun()
        
        date_range = st.sidebar.date_input(
            "Rentang Waktu",
            min_value=min_date,
            max_value=max_date,
            key="customers_date"
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
        
        # Hitung spending per customer dalam rentang tanggal
        orders_filtered = df_orders[(df_orders['order_date'].dt.date >= start_date) & 
                                    (df_orders['order_date'].dt.date <= end_date)]
        details_filtered = df_details[(df_details['order_date'].dt.date >= start_date) & 
                                      (df_details['order_date'].dt.date <= end_date)]
        
        # Join untuk hitung spending
        spending_data = orders_filtered.merge(details_filtered[['order_id', 'total_price']], on='order_id', how='left')
        spending_by_customer = spending_data.groupby('customer_id')['total_price'].sum().reset_index()
        spending_by_customer.columns = ['customer_id', 'filtered_spending']
        
        # Gabung dengan data customer
        df_cust = df_customers.merge(spending_by_customer, on='customer_id', how='left')
        df_cust['filtered_spending'] = pd.to_numeric(df_cust['filtered_spending'], errors='coerce').fillna(0)
    else:
        df_cust = df_customers.copy()
        df_cust['filtered_spending'] = 0.0
    
    df_cust['total_spending'] = pd.to_numeric(df_cust['total_spending'], errors='coerce').fillna(0)
    df_cust['filtered_spending'] = pd.to_numeric(df_cust['filtered_spending'], errors='coerce').fillna(0)
    
    # Metrics berdasarkan filter
    col1, col2, col3 = st.columns(3)
    with col1:
        active_customers = len(df_cust[df_cust['filtered_spending'] > 0])
        st.metric("Customer Aktif", f"{active_customers:,}")
    with col2:
        st.metric("Total Spending", format_rupiah(df_cust['filtered_spending'].sum()))
    with col3:
        avg = df_cust[df_cust['filtered_spending'] > 0]['filtered_spending'].mean() if active_customers > 0 else 0
        st.metric("Rata-rata Spending", format_rupiah(avg))
    
    # Filter pencarian
    search = st.text_input("Cari customer (nama/email/telepon)")
    filtered = df_cust.copy()
    if search:
        filtered = filtered[
            filtered['customer_name'].str.contains(search, case=False, na=False) |
            filtered['email'].str.contains(search, case=False, na=False) |
            filtered['phone'].str.contains(search, case=False, na=False)
        ]
    
    # Visualisasi
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 Customer by Spending
        top10 = filtered.nlargest(10, 'filtered_spending')[['customer_name', 'filtered_spending']].copy()
        top10.columns = ['Customer', 'Spending']
        top10 = top10[top10['Spending'] > 0]  # Hanya yang ada spending
        
        if not top10.empty:
            fig = create_bar_chart(top10, 'Customer', 'Spending', 'Top 10 Customer (Spending)', horizontal=True, color=COLORS['success'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada data spending dalam rentang waktu ini.")
    
    with col2:
        # Distribusi spending dalam kategori
        df_spending = filtered[filtered['filtered_spending'] > 0].copy()
        if not df_spending.empty:
            # Buat kategori spending
            bins = [0, 100000, 500000, 1000000, 5000000, float('inf')]
            labels = ['< 100rb', '100rb-500rb', '500rb-1jt', '1jt-5jt', '> 5jt']
            df_spending['kategori'] = pd.cut(df_spending['filtered_spending'], bins=bins, labels=labels)
            kategori_count = df_spending['kategori'].value_counts().reindex(labels).fillna(0)
            
            fig = px.bar(x=kategori_count.index, y=kategori_count.values,
                        title='Distribusi Spending Customer',
                        color_discrete_sequence=[COLORS['primary']],
                        template=CHART_TEMPLATE)
            fig.update_layout(xaxis_title='Kategori Spending', yaxis_title='Jumlah Customer',
                             margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada data spending dalam rentang waktu ini.")
    
    # Tabel
    st.subheader("Daftar Customer")
    display = filtered[['customer_id', 'customer_name', 'email', 'phone', 'filtered_spending']].copy()
    display.columns = ['ID', 'Nama', 'Email', 'Telepon', 'Total Spending']
    display['Total Spending'] = display['Total Spending'].apply(format_rupiah)
    st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(filtered, 'customers.csv', 'Download CSV')

# CATEGORIES

def tampilkan_categories():
    st.title("Kategori Menu")
    st.caption("Analisis penjualan berdasarkan kategori")
    
    filtered = filter_by_date_sidebar(df_categories.copy(), 'order_date', 'categories')
    
    cat_summary = filtered.groupby('category_name')['total_qty'].sum().reset_index()
    cat_summary = cat_summary.sort_values('total_qty', ascending=False)
    cat_summary.columns = ['Kategori', 'Terjual']
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Kategori", f"{len(cat_summary):,}")
    with col2:
        st.metric("Total Item Terjual", f"{cat_summary['Terjual'].sum():,}")
    
    # Visualisasi
    col1, col2 = st.columns([3, 2])
    with col1:
        fig = create_bar_chart_colored(cat_summary, 'Kategori', 'Terjual', 'Penjualan per Kategori', horizontal=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = create_pie_chart(cat_summary['Terjual'].values, cat_summary['Kategori'].values, 'Proporsi Kategori')
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(cat_summary, use_container_width=True, hide_index=True)
    download_csv(cat_summary, 'categories.csv', 'Download CSV')

# PAYMENT METHODS

def tampilkan_payment():
    st.title("Metode Pembayaran")
    st.caption("Analisis revenue berdasarkan metode pembayaran")
    
    filtered = filter_by_date_sidebar(df_payment.copy(), 'order_date', 'payment')
    
    pay_summary = filtered.groupby('method_name')['revenue'].sum().reset_index()
    pay_summary = pay_summary.sort_values('revenue', ascending=False)
    pay_summary.columns = ['Metode', 'Revenue']
    
    # Metrics dinamis
    cols = st.columns(len(pay_summary) if len(pay_summary) <= 5 else 5)
    for i, (_, row) in enumerate(pay_summary.head(5).iterrows()):
        with cols[i]:
            st.metric(row['Metode'], format_rupiah(row['Revenue']))
    
    # Visualisasi
    col1, col2 = st.columns([3, 2])
    with col1:
        fig = create_bar_chart_colored(pay_summary, 'Metode', 'Revenue', 'Revenue per Metode', horizontal=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = create_pie_chart(pay_summary['Revenue'].values, pay_summary['Metode'].values, 'Proporsi Revenue')
        st.plotly_chart(fig, use_container_width=True)
    
    download_csv(pay_summary, 'payment_methods.csv', 'Download CSV')

# TABLES

def tampilkan_tables():
    st.title("Data Meja")
    st.caption("Informasi dan frekuensi penggunaan meja")
    
    filtered = filter_by_date_sidebar(df_table_usage.copy(), 'order_date', 'tables')
    usage_summary = filtered.groupby(['table_number', 'capacity'])['times_used'].sum().reset_index()
    usage_summary['Meja'] = 'Meja ' + usage_summary['table_number'].astype(str)
    usage_summary = usage_summary.rename(columns={'times_used': 'Penggunaan'})
    
    # Metrics - berdasarkan data yang sudah difilter
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Meja", f"{len(df_tables):,}")
    with col2:
        st.metric("Total Kapasitas", f"{df_tables['capacity'].sum():,} orang")
    with col3:
        if not usage_summary.empty:
            top_meja = usage_summary.loc[usage_summary['Penggunaan'].idxmax(), 'table_number']
            st.metric("Meja Terfavorit", f"Meja {top_meja}")
    
    # Visualisasi
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = create_bar_chart(usage_summary, 'Meja', 'Penggunaan', 'Frekuensi Penggunaan Meja', horizontal=True, color=COLORS['info'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Info Meja")
        st.dataframe(df_tables[['table_number', 'capacity', 'location', 'status']], use_container_width=True, hide_index=True)
    
    download_csv(df_tables, 'tables.csv', 'Download CSV')

# MENU

def tampilkan_menu():
    st.title("Data Menu")
    st.caption("Daftar menu dan performa penjualan")
    
    filtered = filter_by_date_sidebar(df_menu.copy(), 'order_date', 'menu')
    
    # Filter tambahan
    st.sidebar.markdown("**Filter Akses Menu**")
    menu_filter = st.sidebar.selectbox(
        "Tampilkan Menu", 
        ["Semua Menu", "Menu Paket (Member Only)", "Menu Reguler (Semua)"], 
        key="menu_type"
    )
    
    if menu_filter == "Menu Paket (Member Only)":
        filtered = filtered[filtered['member_only'] == 1]
    elif menu_filter == "Menu Reguler (Semua)":
        filtered = filtered[filtered['member_only'] == 0]
    
    # Filter harga
    if not filtered.empty:
        filtered['unit_price'] = pd.to_numeric(filtered['unit_price'], errors='coerce')
        min_p, max_p = float(filtered['unit_price'].min()), float(filtered['unit_price'].max())
        if min_p < max_p:
            price_range = st.sidebar.slider("Rentang Harga", min_p, max_p, (min_p, max_p), key="price_range")
            filtered = filtered[filtered['unit_price'].between(*price_range)]
    
    menu_summary = filtered.groupby(['menu_id', 'item_name', 'unit_price', 'category_name', 'member_only']).agg({
        'total_ordered': 'sum'
    }).reset_index().sort_values('total_ordered', ascending=False)
    
    # Hitung jumlah menu
    paket_count = len(menu_summary[menu_summary['member_only'] == 1])  # Menu paket (member only)
    reguler_count = len(menu_summary[menu_summary['member_only'] == 0])  # Menu reguler
    total_menu_member = paket_count + reguler_count  # Member bisa akses semua
    total_menu_guest = reguler_count  # Guest hanya reguler
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Menu", f"{len(menu_summary):,}")
    with col2:
        st.metric("Akses Member", f"{total_menu_member} menu")
    with col3:
        st.metric("Akses Guest", f"{total_menu_guest} menu")
    with col4:
        st.metric("Total Terjual", f"{menu_summary['total_ordered'].sum():,.0f}")
    
    # Info akses
    st.info(f"Member dapat mengakses semua {total_menu_member} menu (termasuk {paket_count} paket). Guest hanya dapat mengakses {total_menu_guest} menu reguler.")
    
    # Visualisasi
    top10 = menu_summary.head(10)[['item_name', 'total_ordered']].copy()
    top10.columns = ['Menu', 'Terjual']
    
    col1, col2 = st.columns([3, 2])
    with col1:
        fig = create_bar_chart(top10, 'Menu', 'Terjual', 'Top 10 Menu Terlaris', horizontal=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        cat_sales = menu_summary.groupby('category_name')['total_ordered'].sum()
        fig = create_pie_chart(cat_sales.values, cat_sales.index, 'Distribusi per Kategori')
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabel
    st.subheader("Daftar Menu")
    display = menu_summary[['item_name', 'unit_price', 'category_name', 'member_only', 'total_ordered']].copy()
    display.columns = ['Menu', 'Harga', 'Kategori', 'Akses', 'Terjual']
    display['Harga'] = display['Harga'].apply(format_rupiah)
    display['Akses'] = display['Akses'].map({1: 'Member Only', 0: 'Semua'})
    st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(menu_summary, 'menu.csv', 'Download CSV')

# ORDERS

def tampilkan_orders():
    st.title("Data Orders")
    st.caption("Riwayat dan analisis pesanan")
    
    filtered = filter_by_date_sidebar(df_orders.copy(), 'order_date', 'orders')
    
    # Metrics
    completed = len(filtered[filtered['order_status'] == 'Completed'])
    cancelled = len(filtered[filtered['order_status'] == 'Cancelled'])
    dine_in = len(filtered[filtered['service_type'] == 'Dine In'])
    take_away = len(filtered[filtered['service_type'] == 'Take Away'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Order", f"{len(filtered):,}")
    with col2:
        st.metric("Completed", f"{completed:,}")
    with col3:
        st.metric("Cancelled", f"{cancelled:,}")
    with col4:
        st.metric("Dine In", f"{dine_in:,}")
    with col5:
        st.metric("Take Away", f"{take_away:,}")
    
    if not filtered.empty:
        # Trend + Distribusi Jam
        col1, col2 = st.columns(2)
        with col1:
            daily = filtered.groupby(filtered['order_date'].dt.date).size().reset_index()
            daily.columns = ['Tanggal', 'Jumlah']
            fig = create_line_chart(daily['Tanggal'], daily['Jumlah'], 'Jumlah Order per Hari')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            filtered['hour'] = pd.to_datetime(filtered['order_time']).dt.hour
            hourly = filtered.groupby('hour').size().reset_index()
            hourly.columns = ['Jam', 'Jumlah']
            fig = create_bar_chart(hourly, 'Jam', 'Jumlah', 'Total Order per Jam (Akumulasi)', color=COLORS['info'])
            st.plotly_chart(fig, use_container_width=True)
        
        # Pie charts
        col1, col2 = st.columns(2)
        with col1:
            service = filtered['service_type'].value_counts()
            fig = create_pie_chart(service.values, service.index, 'Tipe Layanan')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            status = filtered['order_status'].value_counts()
            fig = create_pie_chart(status.values, status.index, 'Status Order')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabel
    st.subheader("Daftar Orders")
    display = filtered[['order_id', 'customer_name', 'guest_name', 'service_type', 'order_status', 'method_name', 'order_time']].copy()
    display['Nama'] = display.apply(lambda r: r['customer_name'] if pd.notna(r['customer_name']) and r['customer_name'] != '' else r['guest_name'], axis=1)
    display['Tipe'] = display.apply(lambda r: 'Member' if pd.notna(r['customer_name']) and r['customer_name'] != '' else 'Guest', axis=1)
    display = display[['order_id', 'Nama', 'Tipe', 'service_type', 'order_status', 'method_name', 'order_time']]
    display.columns = ['ID', 'Nama', 'Tipe Pelanggan', 'Layanan', 'Status', 'Pembayaran', 'Waktu']
    st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(filtered, 'orders.csv', 'Download CSV')

# ORDER DETAILS

def tampilkan_details():
    st.title("Order Details")
    st.caption("Detail item per pesanan dan analisis revenue")
    
    filtered = filter_by_date_sidebar(df_details.copy(), 'order_date', 'details')
    
    if not filtered.empty:
        total_qty = int(filtered['quantity'].sum())
        total_revenue = filtered['total_price'].sum()
        avg_per_order = filtered.groupby('order_id')['total_price'].sum().mean()
        total_transaksi = filtered['order_id'].nunique()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Item Order", f"{total_qty:,}")
        with col2:
            st.metric("Total Revenue", format_rupiah(total_revenue))
        with col3:
            st.metric("Avg per Order", format_rupiah(avg_per_order))
        with col4:
            st.metric("Total Transaksi", f"{total_transaksi:,}")
        
        # Visualisasi
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
    
    # Tabel
    st.subheader("Detail Pesanan")
    if not filtered.empty:
        display = filtered[['order_id', 'item_name', 'quantity', 'unit_price', 'total_price', 'request_note']].copy()
        display['subtotal'] = display['quantity'] * pd.to_numeric(display['unit_price'], errors='coerce')
        display = display[['order_id', 'item_name', 'quantity', 'unit_price', 'subtotal', 'request_note']]
        display.columns = ['Order ID', 'Menu', 'Qty', 'Harga Satuan', 'Total', 'Request']
        display['Harga Satuan'] = display['Harga Satuan'].apply(format_rupiah)
        display['Total'] = display['Total'].apply(format_rupiah)
        st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(filtered, 'order_details.csv', 'Download CSV')

# RESERVATIONS

def tampilkan_reservations():
    st.title("Reservations")
    st.caption("Manajemen reservasi meja")
    
    filtered = filter_by_date_sidebar(df_reservations.copy(), 'reservation_date', 'reservations')
    
    if not filtered.empty:
        def extract_hour(val):
            try:
                if pd.isna(val): return 0
                val_str = str(val)
                time_part = val_str.split(' ')[-1] if 'days' in val_str else val_str
                return int(time_part.split(':')[0])
            except: return 0
        
        filtered['check_in_hour'] = filtered['check_in'].apply(extract_hour)
        
        table_counts = filtered['table_number'].value_counts()
        top_table = table_counts.idxmax()
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
            st.metric("Avg Party Size", f"{avg_party:.1f} orang")
        
        # Visualisasi
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
    
    # Tabel
    st.subheader("Daftar Reservasi")
    if not filtered.empty:
        display = filtered[['reservation_id', 'customer_name', 'table_number', 'reservation_date', 
                           'check_in', 'check_out', 'party_size', 'status']].copy()
        # Format check_in dan check_out sebagai jam detail (HH:MM:SS)
        def format_time(val):
            try:
                if pd.isna(val): return '-'
                val_str = str(val)
                if 'days' in val_str:
                    time_part = val_str.split(' ')[-1]
                else:
                    time_part = val_str
                return time_part
            except:
                return '-'
        display['check_in'] = display['check_in'].apply(format_time)
        display['check_out'] = display['check_out'].apply(format_time)
        display.columns = ['ID', 'Customer', 'Meja', 'Tanggal', 'Check-in', 'Check-out', 'Party', 'Status']
        st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(filtered, 'reservations.csv', 'Download CSV')

# REVIEWS

def tampilkan_reviews():
    st.title("Reviews")
    st.caption("Ulasan dan rating dari pelanggan")
    
    filtered = filter_by_date_sidebar(df_reviews.copy(), 'review_date', 'reviews')
    
    if not filtered.empty:
        avg_rating = filtered['rating'].mean()
        total_reviews = len(filtered)
        rating_counts = filtered['rating'].value_counts().sort_index()
        most_common = rating_counts.idxmax()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Review", f"{total_reviews:,}")
        with col2:
            st.metric("Rata-rata Rating", f"{avg_rating:.2f}/5")
        with col3:
            st.metric("Rating Terbanyak", f"{most_common} Bintang")
        
        # Visualisasi
        col1, col2 = st.columns(2)
        with col1:
            rating_count = filtered['rating'].value_counts().sort_index().reset_index()
            rating_count.columns = ['Rating', 'Jumlah']
            fig = create_bar_chart(rating_count, 'Rating', 'Jumlah', 'Distribusi Rating', color=COLORS['warning'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            daily_rating = filtered.groupby(filtered['review_date'].dt.date)['rating'].mean().reset_index()
            daily_rating.columns = ['Tanggal', 'Rating']
            fig = create_line_chart(daily_rating['Tanggal'], daily_rating['Rating'], 'Trend Rating Harian')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabel
    st.subheader("Daftar Review")
    if not filtered.empty:
        display = filtered[['review_id', 'order_id', 'customer_name', 'rating', 'comment', 'review_date']].copy()
        display.columns = ['ID', 'Order ID', 'Customer', 'Rating', 'Komentar', 'Tanggal']
        st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(filtered, 'reviews.csv', 'Download CSV')

# CUSTOM VIEW

def tampilkan_custom():
    st.title("Custom View")
    st.caption("Pilih tabel, kolom, dan gabungkan data sesuai kebutuhan")
    
    st.sidebar.markdown("**Filter Tanggal**")
    if not df_orders.empty:
        min_date = df_orders['order_date'].min().date()
        max_date = df_orders['order_date'].max().date()
        
        if 'custom_date' not in st.session_state:
            st.session_state['custom_date'] = (min_date, max_date)
        
        if st.sidebar.button("Reset Tanggal", key="reset_custom"):
            st.session_state['custom_date'] = (min_date, max_date)
            st.rerun()
        
        date_range = st.sidebar.date_input(
            "Rentang Waktu",
            min_value=min_date,
            max_value=max_date,
            key="custom_date"
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date, end_date = None, None
    
    # Mode: Tabel Terpisah atau Gabungan
    mode = st.radio("Mode Tampilan", ["Tabel Terpisah", "Gabungkan Tabel"], horizontal=True)
    
    # Daftar semua tabel
    tabel_info = {
        "Customers": {"df": df_customers, "date_col": None, "key": "customer_id"},
        "Categories": {"df": df_categories, "date_col": "order_date", "key": "category_id"},
        "Payment Methods": {"df": df_payment, "date_col": "order_date", "key": "payment_id"},
        "Tables": {"df": df_tables, "date_col": None, "key": "table_id"},
        "Menu": {"df": df_menu, "date_col": "order_date", "key": "menu_id"},
        "Orders": {"df": df_orders, "date_col": "order_date", "key": "order_id"},
        "Order Details": {"df": df_details, "date_col": "order_date", "key": "order_detail_id"},
        "Reservations": {"df": df_reservations, "date_col": "reservation_date", "key": "reservation_id"},
        "Reviews": {"df": df_reviews, "date_col": "review_date", "key": "review_id"}
    }
    
    if mode == "Tabel Terpisah":
        # Mode tabel terpisah (seperti sebelumnya)
        selected_tables = st.multiselect(
            "Pilih Tabel",
            options=list(tabel_info.keys()),
            default=[],
            placeholder="Pilih satu atau lebih tabel..."
        )
        
        if not selected_tables:
            st.info("Silakan pilih minimal satu tabel.")
            return
        
        st.markdown("---")
        
        for tabel_name in selected_tables:
            info = tabel_info[tabel_name]
            df = info["df"].copy()
            date_col = info["date_col"]
            
            if date_col and start_date and end_date and date_col in df.columns:
                df = df[(df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)]
            
            with st.expander(f"Tabel: {tabel_name}", expanded=True):
                all_columns = list(df.columns)
                selected_columns = st.multiselect(
                    f"Pilih Kolom",
                    options=all_columns,
                    default=all_columns,
                    key=f"cols_{tabel_name}"
                )
                
                if selected_columns:
                    df_display = df[selected_columns]
                    st.metric("Total Baris", f"{len(df_display):,}")
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    
                    csv = df_display.to_csv(index=False).encode('utf-8')
                    st.download_button(f"Download CSV", csv, f"{tabel_name}.csv", key=f"dl_{tabel_name}")
    
    else:
        # Mode gabungkan tabel
        st.markdown("### Gabungkan Tabel")
        st.info("Pilih tabel yang ingin digabungkan. Tabel akan di-join berdasarkan kolom yang sesuai.")
        
        # Pilihan join yang tersedia
        join_options = {
            "Orders + Customers": {
                "tables": ["Orders", "Customers"],
                "description": "Data order dengan info customer",
                "join": lambda: df_orders.merge(df_customers[['customer_id', 'email', 'phone']], on='customer_id', how='left')
            },
            "Orders + Order Details + Menu": {
                "tables": ["Orders", "Order Details", "Menu"],
                "description": "Detail order lengkap dengan info menu",
                "join": lambda: df_orders.merge(
                    df_details, on='order_id', how='left', suffixes=('', '_det')
                ).merge(
                    df_menu[['menu_id', 'item_name', 'unit_price', 'category_name']].drop_duplicates(), 
                    on='menu_id', how='left', suffixes=('', '_menu')
                )
            },
            "Orders + Payment Methods": {
                "tables": ["Orders", "Payment Methods"],
                "description": "Data order dengan metode pembayaran",
                "join": lambda: df_orders.merge(
                    df_payment[['payment_id', 'method_name']].drop_duplicates(), 
                    on='payment_id', how='left'
                )
            },
            "Reservations + Customers + Tables": {
                "tables": ["Reservations", "Customers", "Tables"],
                "description": "Reservasi dengan info customer dan meja",
                "join": lambda: df_reservations.merge(
                    df_customers[['customer_id', 'email', 'phone']], on='customer_id', how='left'
                ).merge(
                    df_tables[['table_id', 'location', 'status']], on='table_id', how='left'
                )
            },
            "Reviews + Orders + Customers": {
                "tables": ["Reviews", "Orders", "Customers"],
                "description": "Review dengan info order dan customer",
                "join": lambda: df_reviews.merge(
                    df_orders[['order_id', 'customer_id', 'order_date', 'service_type']], 
                    on='order_id', how='left'
                ).merge(
                    df_customers[['customer_id', 'email', 'phone']], on='customer_id', how='left'
                )
            },
            "Menu + Categories": {
                "tables": ["Menu", "Categories"],
                "description": "Menu dengan info kategori",
                "join": lambda: df_menu.merge(
                    df_categories[['category_id', 'category_name']].drop_duplicates(),
                    on='category_name', how='left'
                )
            },
            "Full Order Report": {
                "tables": ["Orders", "Customers", "Order Details", "Menu", "Payment Methods"],
                "description": "Laporan order lengkap (semua informasi)",
                "join": lambda: df_orders.merge(
                    df_customers[['customer_id', 'email', 'phone']], on='customer_id', how='left'
                ).merge(
                    df_details[['order_id', 'menu_id', 'quantity', 'total_price', 'request_note']], 
                    on='order_id', how='left'
                ).merge(
                    df_menu[['menu_id', 'item_name', 'category_name']].drop_duplicates(),
                    on='menu_id', how='left'
                )
            }
        }
        
        selected_join = st.selectbox(
            "Pilih Kombinasi Tabel",
            options=list(join_options.keys()),
            format_func=lambda x: f"{x} - {join_options[x]['description']}"
        )
        
        if selected_join:
            join_info = join_options[selected_join]
            
            st.caption(f"Tabel yang digabungkan: {', '.join(join_info['tables'])}")
            
            try:
                df_joined = join_info["join"]()
                
                # Filter tanggal jika ada
                date_cols = ['order_date', 'reservation_date', 'review_date']
                for dc in date_cols:
                    if dc in df_joined.columns:
                        df_joined[dc] = pd.to_datetime(df_joined[dc], errors='coerce')
                        if start_date and end_date:
                            df_joined = df_joined[(df_joined[dc].dt.date >= start_date) & (df_joined[dc].dt.date <= end_date)]
                        break
                
                # Pilih kolom
                all_cols = list(df_joined.columns)
                selected_cols = st.multiselect(
                    "Pilih Kolom yang Ditampilkan",
                    options=all_cols,
                    default=all_cols[:15] if len(all_cols) > 15 else all_cols,
                    key="join_cols"
                )
                
                if selected_cols:
                    df_display = df_joined[selected_cols].copy()
                    
                    # Search
                    search = st.text_input("Cari data", key="join_search")
                    if search:
                        mask = df_display.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
                        df_display = df_display[mask]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Baris", f"{len(df_display):,}")
                    with col2:
                        st.metric("Total Kolom", f"{len(selected_cols):,}")
                    
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    
                    csv = df_display.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download Hasil Gabungan (CSV)",
                        csv,
                        f"{selected_join.lower().replace(' ', '_')}.csv",
                        key="dl_joined"
                    )
            except Exception as e:
                st.error(f"Error menggabungkan tabel: {str(e)}")

# SIDEBAR NAVIGATION

st.sidebar.title("Restaurant Dashboard")
st.sidebar.markdown("---")

halaman = st.sidebar.radio(
    "Navigasi",
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
        "Reviews",
        "Custom"
    ],
    index=0
)

st.sidebar.markdown("---")

# Render halaman
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
elif halaman == "Custom":
    tampilkan_custom()

st.sidebar.caption("© 2025 Restaurant Order Management")
