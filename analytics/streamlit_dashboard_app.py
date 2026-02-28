# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Support Chat Analytics",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Support Chat Quality Analytics")
st.markdown("Аналіз якості підтримки клієнтів")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('support_analytics.csv')
        return df
    except FileNotFoundError:
        st.error("Файл support_analytics.csv не знайдено. Спочатку запусти data_aggregator.py")
        return None

df = load_data()

if df is not None:
    # Бокова панель з фільтрами
    st.sidebar.header("🔍 Фільтри")
    
    intents = ['Всі'] + sorted(df['intent'].unique().tolist())
    selected_intent = st.sidebar.selectbox("Виберіть інтент", intents)
    
    # Фільтруємо дані
    filtered_df = df.copy()
    if selected_intent != 'Всі':
        filtered_df = filtered_df[filtered_df['intent'] == selected_intent]
    
    # KPI картки
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Всього чатів", len(filtered_df))
    
    with col2:
        avg_score = filtered_df['quality_score'].mean()
        st.metric("Середня оцінка", f"{avg_score:.2f}/5.0")
    
    with col3:
        mistake_rate = (filtered_df['has_mistakes'].sum() / len(filtered_df) * 100)
        st.metric("Помилки", f"{mistake_rate:.1f}%")
    
    with col4:
        sat_rate = (filtered_df['satisfaction'] == 'satisfied').mean() * 100
        st.metric("Задоволені", f"{sat_rate:.1f}%")
    
    # Графіки
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Якість по інтентах
        intent_quality = filtered_df.groupby('intent')['quality_score'].mean().sort_values()
        fig = px.bar(
            x=intent_quality.values,
            y=intent_quality.index,
            orientation='h',
            title="Середня якість по інтентах",
            color=intent_quality.values,
            color_continuous_scale='RdYlGn',
            range_color=[1, 5]
        )
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        # Розподіл задоволеності
        sat_counts = filtered_df['satisfaction'].value_counts()
        colors = {'satisfied': '#2ecc71', 'neutral': '#f39c12', 'unsatisfied': '#e74c3c'}
        fig = px.pie(
            values=sat_counts.values,
            names=sat_counts.index,
            title="Розподіл задоволеності клієнтів",
            color=sat_counts.index,
            color_discrete_map=colors
        )
        st.plotly_chart(fig, width="stretch")
    
    st.markdown("---")
    
    # Таблиця з деталями
    st.header("📋 Деталі чатів")
    
    display_cols = ['chat_id', 'intent', 'satisfaction', 'quality_score', 
                    'has_mistakes', 'scenario_type', 'rationale']
    
    display_df = filtered_df[display_cols].copy()
    display_df.columns = ['ID', 'Інтент', 'Задоволення', 'Оцінка', 
                         'Помилки', 'Тип', 'Пояснення']
    
    st.dataframe(display_df, width="stretch", hide_index=True)
    
    # Кнопка для завантаження
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Завантажити дані CSV",
        csv,
        "filtered_data.csv",
        "text/csv"
    )

else:
    st.info("👈 Запусти спочатку data_aggregator.py щоб створити CSV файл")