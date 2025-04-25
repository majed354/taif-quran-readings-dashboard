# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="دكتوراه القراءات | قسم القراءات", 
    page_icon="📘",
    layout="wide"
)

# --- تحميل ملف CSS المخصص ---
def load_css():
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap');

    * { font-family: 'Tajawal', sans-serif !important; }
    .stApp { direction: rtl; text-align: right; }

    /* إخفاء عناصر Streamlit الافتراضية */
    [data-testid="stToolbar"], #MainMenu, header, footer,
    [class^="viewerBadge_"], [id^="GithubIcon"],
    [data-testid="stThumbnailsChipContainer"], .stProgress,
    [data-testid="stBottomNavBar"], [data-testid*="bottomNav"],
    [aria-label*="community"], [aria-label*="profile"],
    [title*="community"], [title*="profile"],
    h1 > div > a, h2 > div > a, h3 > div > a,
    h4 > div > a, h5 > div > a, h6 > div > a { display: none !important; visibility: hidden !important; }
    [data-testid="stSidebar"], [data-testid="stSidebarNavToggler"], [data-testid="stSidebarCollapseButton"] { display: none !important; }

    /* تنسيق العناوين */
    h1,h2,h3 { color: #1e88e5; font-weight: 600; }
    h1 { padding-bottom: 15px; border-bottom: 2px solid #1e88e5; margin-bottom: 30px; font-size: calc(1.2rem + 1vw); }
    h2 { margin-top: 30px; margin-bottom: 20px; font-size: calc(1rem + 0.5vw); }
    h3 { margin-top: 30px; margin-bottom: 20px; font-size: calc(1rem + 0.2vw); }

    /* تنسيق عناصر page_link */
    [data-testid="StyledLinkIconContainer"] > div > a {
        background-color: #f8f9fa;
        color: #333;
        display: block;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
        border: 1px solid #e7e7e7;
        text-align: center;
    }
    [data-testid="StyledLinkIconContainer"] > div > a:hover {
        background-color: #1e88e5;
        color: white;
    }

    /* الاستجابة للشاشات الصغيرة */
    @media only screen and (max-width: 768px) {
        [data-testid="StyledLinkIconContainer"] > div > a {
            padding: 6px;
            font-size: 0.8rem;
        }
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css()

# --- العنوان الرئيسي ---
st.markdown("<h1 style='text-align: center;'>قسم القراءات - كلية القرآن الكريم والدراسات الإسلامية</h1>", unsafe_allow_html=True)

# --- إنشاء قائمة التنقل ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link(".", label="🏠 الرئيسية", icon="🏠")
    st.page_link("هيئة_التدريس", label="👥 هيئة التدريس", icon="👥")
with col2:
    st.page_link("إنجاز_المهام", label="🏆 إنجاز المهام", icon="🏆")
    st.page_link("بكالوريوس_القرآن_وعلومه", label="📚 بكالوريوس القرآن وعلومه", icon="📚")
with col3:
    st.page_link("بكالوريوس_القراءات", label="📖 بكالوريوس القراءات", icon="📖")
    st.page_link("ماجستير_الدراسات_القرآنية", label="🎓 ماجستير الدراسات", icon="🎓")
with col4:
    st.page_link("ماجستير_القراءات", label="📜 ماجستير القراءات", icon="📜")
    st.page_link("دكتوراه_علوم_القرآن", label="🔍 دكتوراه علوم القرآن", icon="🔍")

# رمز للفصل بين قائمة التنقل ومحتوى الصفحة
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h2>📘 دكتوراه القراءات - قسم القراءات</h2>", unsafe_allow_html=True)

# --- محتوى الصفحة ---
st.info("صفحة دكتوراه القراءات قيد الإنشاء...")

# --- إضافة نص تذييل الصفحة ---
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #666; font-size: 0.8em;">
    © كلية القرآن الكريم والدراسات الإسلامية - جامعة الطائف {0}
</div>
""".format(datetime.now().year), unsafe_allow_html=True)
