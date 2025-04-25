# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import os

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="هيئة التدريس | قسم القراءات", 
    page_icon="👥",
    layout="wide"
)

# --- تحميل ملف CSS (نفس الأسلوب المستخدم في الصفحة الرئيسية) ---
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
    h1, h2, h3 { color: #1e88e5; font-weight: 600; }
    h1 { padding-bottom: 15px; border-bottom: 2px solid #1e88e5; margin-bottom: 30px; font-size: calc(1.2rem + 1vw); }
    h2 { margin-top: 30px; margin-bottom: 20px; font-size: calc(1rem + 0.5vw); }
    h3 { margin-top: 30px; margin-bottom: 20px; font-size: calc(1rem + 0.2vw); }

    /* تنسيق روابط التنقل */
    .nav-container { background-color: #f8f9fa; padding: 10px; border-radius: 10px; margin-bottom: 20px; }
    .nav-link { background-color: white; padding: 8px 12px; border-radius: 5px; text-decoration: none; margin: 5px; display: inline-block; transition: all 0.3s; border: 1px solid #e7e7e7; }
    .nav-link:hover { background-color: #1e88e5; color: white !important; }
    
    /* تنسيقات عامة للبطاقات */
    .metric-card { background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); text-align: center; margin-bottom: 15px; }
    .chart-container { background-color: white; border-radius: 10px; padding: 10px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; width: 100%; overflow: hidden; }
    
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
    
    /* تنسيقات خاصة بصفحة هيئة التدريس */
    .faculty-profile-card {
        background-color: white;
        border-radius: 10px;
        border-right: 4px solid #1e88e5;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }
    .profile-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background-color: #f0f2f6;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: #1e88e5;
        margin-left: 15px;
        flex-shrink: 0;
    }
    .profile-info {
        flex-grow: 1;
    }
    .profile-name {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e88e5;
        margin-bottom: 5px;
    }
    .profile-title {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 10px;
    }
    .profile-details {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 8px;
    }
    .profile-detail-item {
        font-size: 0.85rem;
        background-color: #f0f2f6;
        padding: 4px 8px;
        border-radius: 4px;
        white-space: nowrap;
    }
    .profile-metrics {
        display: flex;
        gap: 15px;
        margin-top: 10px;
    }
    .profile-metric {
        text-align: center;
        flex-grow: 1;
        padding: 5px;
        border-radius: 5px;
        background-color: rgba(30, 136, 229, 0.05);
    }
    .profile-metric-value {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1e88e5;
    }
    .profile-metric-label {
        font-size: 0.8rem;
        color: #666;
    }
    
    /* تنسيق شارات المؤشرات */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 5px;
    }
    .badge-blue { background-color: rgba(30, 136, 229, 0.1); color: #1e88e5; }
    .badge-green { background-color: rgba(39, 174, 96, 0.1); color: #27AE60; }
    .badge-orange { background-color: rgba(243, 156, 18, 0.1); color: #F39C12; }
    .badge-red { background-color: rgba(231, 76, 60, 0.1); color: #E74C3C; }
    
    /* تجاوب بطاقة العضو للشاشات الصغيرة */
    @media only screen and (max-width: 768px) {
        .faculty-profile-card {
            flex-direction: column;
        }
        .profile-avatar {
            margin-left: 0;
            margin-bottom: 15px;
            align-self: center;
        }
        .profile-metrics {
            flex-direction: column;
            gap: 8px;
        }
        .profile-detail-item {
            font-size: 0.8rem;
        }
        [data-testid="StyledLinkIconContainer"] > div > a {
            padding: 6px;
            font-size: 0.8rem;
        }
    }
    
    /* تذييل الصفحة */
    .footer { margin-top: 50px; text-align: center; color: #666; font-size: 0.8em; }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css()

# --- العنوان الرئيسي ---
st.markdown("<h1 style='text-align: center;'>قسم القراءات - كلية القرآن الكريم والدراسات الإسلامية</h1>", unsafe_allow_html=True)

# --- إنشاء قائمة التنقل ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("Home.py", label="🏠 الرئيسية", icon="🏠")
    st.page_link("pages/1_👥_هيئة_التدريس.py", label="👥 هيئة التدريس", icon="👥")
with col2:
    st.page_link("pages/2_🏆_إنجاز_المهام.py", label="🏆 إنجاز المهام", icon="🏆")
    st.page_link("pages/3_📚_بكالوريوس_القرآن_وعلومه.py", label="📚 بكالوريوس القرآن وعلومه", icon="📚")
with col3:
    st.page_link("pages/4_📖_بكالوريوس_القراءات.py", label="📖 بكالوريوس القراءات", icon="📖")
    st.page_link("pages/5_🎓_ماجستير_الدراسات_القرآنية.py", label="🎓 ماجستير الدراسات", icon="🎓")
with col4:
    st.page_link("pages/6_📜_ماجستير_القراءات.py", label="📜 ماجستير القراءات", icon="📜")
    st.page_link("pages/7_🔍_دكتوراه_علوم_القرآن.py", label="🔍 دكتوراه علوم القرآن", icon="🔍")

# رمز للفصل بين قائمة التنقل ومحتوى الصفحة
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h2>👥 هيئة التدريس - قسم القراءات</h2>", unsafe_allow_html=True)

# --- دوال مساعدة ---
def is_mobile():
    """التحقق من كون العرض الحالي محتملاً أن يكون جهاز محمول"""
    if 'IS_MOBILE' not in st.session_state:
        st.session_state.IS_MOBILE = False
    return st.session_state.IS_MOBILE

def prepare_chart_layout(fig, title, is_mobile=False, chart_type="bar"):
    """تطبيق تنسيق موحد على مخططات Plotly مع الاستجابة للجوال"""
    try:
        fig.update_layout(dragmode=False)
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        
        # إعدادات التخطيط المشتركة
        layout_settings = {
            "title": title,
            "font": {"family": "Tajawal"},
            "plot_bgcolor": "rgba(240, 240, 240, 0.8)",
            "paper_bgcolor": "white",
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "xanchor": "center",
                "x": 0.5,
            }
        }
        
        # تعديلات خاصة بالجوال
        if is_mobile:
            mobile_settings = {
                "height": 300 if chart_type != "heatmap" else 350,
                "margin": {"t": 40, "b": 100, "l": 10, "r": 10, "pad": 0},
                "font": {"size": 10},
                "title": {"font": {"size": 13}},
                "legend": {"y": -0.4, "font": {"size": 9}}
            }
            layout_settings.update(mobile_settings)
            
            # تعديلات خاصة بنوع المخطط للجوال
            if chart_type == "pie":
                layout_settings["showlegend"] = False
            elif chart_type == "line":
                fig.update_traces(marker=dict(size=5))
            elif chart_type == "bar":
                fig.update_xaxes(tickangle=0, tickfont={"size": 8})
        else:
            # إعدادات سطح المكتب
            desktop_settings = {
                "height": 450 if chart_type != "heatmap" else 400,
                "margin": {"t": 50, "b": 90, "l": 30, "r": 30, "pad": 4},
                "legend": {"y": -0.25, "font": {"size": 10}}
            }
            layout_settings.update(desktop_settings)
            
        fig.update_layout(**layout_settings)
    except Exception as e:
        st.warning(f"تعذر تطبيق إعدادات التخطيط للرسم '{title}': {e}")
    
    return fig

def get_avatar_placeholder(name):
    """توليد حرف أولي من الاسم لاستخدامه كصورة افتراضية"""
    if not name or len(name) == 0:
        return "👤"
    # الحصول على الحرف الأول من الاسم بعد تجاوز أي بادئات شائعة
    parts = name.split()
    if len(parts) > 1 and parts[0] in ['د.', 'أ.', 'أ.د.', 'م.']:
        initial = parts[1][0] if len(parts[1]) > 0 else parts[0][0]
    else:
        initial = parts[0][0] if len(parts) > 0 and len(parts[0]) > 0 else "؟"
    return initial

# --- دوال تحميل البيانات ---
@st.cache_data(ttl=3600)
def load_faculty_data(year=None):
    """تحميل بيانات أعضاء هيئة التدريس للسنة المحددة"""
    try:
        # إذا لم تحدد سنة، استخدم أحدث سنة متوفرة
        available_years = list(range(2022, 2026))  # يتم تحديث السنوات المتوفرة حسب الملفات المتاحة
        
        if year is None:
            year = max(available_years)
        
        # المسار بناءً على هيكل المستودع والسنة
        file_path = f"data/department/{year}/faculty_{year}.csv"
        
        # التحقق من وجود الملف، وإلا حاول تحميل الملف القديم
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df["year"] = year  # إضافة عمود السنة للتمييز لاحقاً
            return df
        else:
            # إذا لم يجد ملف السنة المحددة، ابحث عن أقرب سنة متاحة
            for y in sorted(available_years, reverse=True):
                alt_file_path = f"data/department/{y}/faculty_{y}.csv"
                if os.path.exists(alt_file_path):
                    st.warning(f"بيانات سنة {year} غير متوفرة. تم تحميل بيانات سنة {y} بدلاً عنها.")
                    df = pd.read_csv(alt_file_path)
                    df["year"] = y  # إضافة عمود السنة الفعلية
                    return df
            
            # إذا لم يجد أي ملف، استخدم بيانات تجريبية
            st.warning(f"بيانات سنة {year} غير متوفرة. استخدام بيانات تجريبية.")
            return generate_sample_faculty_data(year)
            
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات أعضاء هيئة التدريس: {e}")
        return pd.DataFrame()

def generate_sample_faculty_data(year):
    """توليد بيانات تجريبية عند عدم وجود ملف"""
    # بيانات تجريبية لأعضاء هيئة التدريس
    data = [
        {"الاسم": "د. محمد أحمد علي", "الرتبة": "أستاذ مشارك", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي", "البريد الإلكتروني": "m.ahmed@example.edu", "عدد البحوث": 12},
        {"الاسم": "د. عائشة محمد سعيد", "الرتبة": "أستاذ", "التخصص": "علوم القرآن", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية", "البريد الإلكتروني": "a.saeed@example.edu", "عدد البحوث": 18},
        {"الاسم": "د. عبدالله محمد خالد", "الرتبة": "أستاذ مساعد", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي", "البريد الإلكتروني": "a.khalid@example.edu", "عدد البحوث": 8},
        {"الاسم": "د. فاطمة علي حسن", "الرتبة": "أستاذ مشارك", "التخصص": "الدراسات القرآنية", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية", "البريد الإلكتروني": "f.hassan@example.edu", "عدد البحوث": 15},
        {"الاسم": "د. خالد إبراهيم عمر", "الرتبة": "أستاذ", "التخصص": "قراءات", "حالة الموظف": "متعاون", "الجنس": "ذكر", "الجنسية": "مصري", "البريد الإلكتروني": "k.ibrahim@example.edu", "عدد البحوث": 22},
        {"الاسم": "د. نورا سعيد أحمد", "الرتبة": "أستاذ مساعد", "التخصص": "علوم القرآن", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية", "البريد الإلكتروني": "n.ahmed@example.edu", "عدد البحوث": 6},
        {"الاسم": "د. ياسر محمود علي", "الرتبة": "محاضر", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي", "البريد الإلكتروني": "y.mahmoud@example.edu", "عدد البحوث": 4},
        {"الاسم": "د. هدى سالم مبارك", "الرتبة": "أستاذ مساعد", "التخصص": "الدراسات القرآنية", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية", "البريد الإلكتروني": "h.mubarak@example.edu", "عدد البحوث": 7},
        {"الاسم": "أ. عمر سعد الدين", "الرتبة": "معيد", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي", "البريد الإلكتروني": "o.saadeddin@example.edu", "عدد البحوث": 2}
    ]
    df = pd.DataFrame(data)
    df["year"] = year
    return df

# --- دالة لتحميل بيانات السنة السابقة للمقارنة ---
@st.cache_data(ttl=3600)
def load_previous_year_data(current_year):
    """تحميل بيانات السنة السابقة للمقارنة"""
    previous_year = current_year - 1
    
    try:
        file_path = f"data/department/{previous_year}/faculty_{previous_year}.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df["year"] = previous_year  # إضافة عمود السنة
            return df
        else:
            return None
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات السنة السابقة: {e}")
        return None

# --- دالة لتحليل التغييرات بين السنوات ---
def analyze_faculty_changes(current_data, previous_data):
    """تحليل التغييرات في هيئة التدريس بين السنتين"""
    if previous_data is None or current_data.empty or previous_data.empty:
        return None, None, None, 0
    
    # استخراج الأسماء من كل مجموعة بيانات
    current_names = set(current_data["الاسم"].tolist())
    previous_names = set(previous_data["الاسم"].tolist())
    
    # تحديد الأعضاء الجدد والمغادرين
    new_members = current_names - previous_names
    departed_members = previous_names - current_names
    
    # الأعضاء المستمرين (موجودين في كلا السنتين)
    continuing_members = current_names.intersection(previous_names)
    
    # البحث عن ترقيات (تغيير في الرتبة الأكاديمية)
    promotions = []
    for member in continuing_members:
        current_rank = current_data[current_data["الاسم"] == member]["الرتبة"].iloc[0]
        previous_rank = previous_data[previous_data["الاسم"] == member]["الرتبة"].iloc[0]
        
        if current_rank != previous_rank:
            promotions.append({
                "الاسم": member,
                "الرتبة السابقة": previous_rank,
                "الرتبة الحالية": current_rank
            })
    
    # إجمالي البحوث في السنة الحالية مقارنة بالسنة السابقة
    current_research_total = current_data["عدد البحوث"].sum()
    previous_research_total = previous_data["عدد البحوث"].sum()
    research_increase = current_research_total - previous_research_total
    
    # الأعضاء المضافين (الجدد) مع بياناتهم الكاملة
    new_members_data = current_data[current_data["الاسم"].isin(new_members)]
    
    # الأعضاء المغادرين مع بياناتهم الكاملة
    departed_members_data = previous_data[previous_data["الاسم"].isin(departed_members)]
    
    return new_members_data, departed_members_data, promotions, research_increase

@st.cache_data(ttl=3600)
def load_faculty_achievements():
    """تحميل بيانات إنجازات أعضاء هيئة التدريس"""
    try:
        file_path = "data/department/achievements_latest.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            # بيانات إنجازات تجريبية
            achievements = [
                {"العضو": "عبد الله حماد حميد القرشي", "الإنجاز": "نشر بحث في مجلة عالمية", "التاريخ": "2025-04-15", "النقاط": 50},
                {"العضو": "ناصر سعود حمود القثامي", "الإنجاز": "إطلاق مبادرة تعليمية", "التاريخ": "2025-04-10", "النقاط": 40},
                {"العضو": "حاتم عابد عبد الله القرشي", "الإنجاز": "المشاركة في مؤتمر دولي", "التاريخ": "2025-04-05", "النقاط": 35},
                {"العضو": "منال منصور محمد القرشي", "الإنجاز": "تطوير مقرر دراسي", "التاريخ": "2025-04-01", "النقاط": 30},
                {"العضو": "عبدالعزيز عيضه حربي الحارثي", "الإنجاز": "تقديم ورشة عمل", "التاريخ": "2025-03-25", "النقاط": 25},
                {"العضو": "تهاني فيصل علي الحربي", "الإنجاز": "تأليف كتاب", "التاريخ": "2025-03-20", "النقاط": 60},
                {"العضو": "مهدي عبدالله قاري", "الإنجاز": "إعداد دورة تدريبية", "التاريخ": "2025-03-15", "النقاط": 20},
                {"العضو": "سلمى معيوض زويد الجميعي", "الإنجاز": "المشاركة في لجنة علمية", "التاريخ": "2025-03-10", "النقاط": 15},
                {"العضو": "عبد الله سعد عويض الثبيتي", "الإنجاز": "تقديم محاضرة عامة", "التاريخ": "2025-03-05", "النقاط": 10},
                {"العضو": "مها عيفان نوار الخليدي", "الإنجاز": "تحكيم بحوث علمية", "التاريخ": "2025-03-01", "النقاط": 20},
                {"العضو": "عبد الله حماد حميد القرشي", "الإنجاز": "رئاسة مؤتمر", "التاريخ": "2025-02-25", "النقاط": 45},
                {"العضو": "غدير محمد سليم الشريف", "الإنجاز": "الفوز بجائزة بحثية", "التاريخ": "2025-02-20", "النقاط": 40}
            ]
            return pd.DataFrame(achievements)
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات الإنجازات: {e}")
        return pd.DataFrame()

# --- تحديد عرض الجوال ---
mobile_view = is_mobile()

# --- محتوى صفحة هيئة التدريس ---
st.markdown("<h1>👥 هيئة التدريس - قسم القراءات</h1>", unsafe_allow_html=True)

# --- إضافة منتقي السنة ---
YEAR_LIST = list(range(2022, 2026))  # تُحدَّث سنويًا
selected_year = st.selectbox("اختر السنة", YEAR_LIST[::-1], index=0)  # القيمة الافتراضية هي أحدث سنة

# --- تحميل البيانات ---
faculty_data = load_faculty_data(selected_year)
faculty_achievements = load_faculty_achievements()

if faculty_data.empty:
    st.warning("لا تتوفر بيانات أعضاء هيئة التدريس. يرجى التحقق من مصدر البيانات.")
else:
    # --- المقاييس الإجمالية ---
    total_faculty = len(faculty_data)
    male_count = len(faculty_data[faculty_data["الجنس"] == "ذكر"])
    female_count = len(faculty_data[faculty_data["الجنس"] == "أنثى"])
    total_research = faculty_data["عدد البحوث"].sum() if "عدد البحوث" in faculty_data.columns else 0
    
    # عرض المقاييس في صف
    metric_cols = st.columns(4)
    with metric_cols[0]:
        st.metric("إجمالي أعضاء هيئة التدريس", f"{total_faculty:,}")
    with metric_cols[1]:
        st.metric("أعضاء (ذكور)", f"{male_count:,}")
    with metric_cols[2]:
        st.metric("أعضاء (إناث)", f"{female_count:,}")
    with metric_cols[3]:
        st.metric("إجمالي البحوث", f"{total_research:,}")
    
    # --- تحليلات هيئة التدريس ---
    st.subheader("توزيع أعضاء هيئة التدريس")
    
    # تحليل البيانات لتجهيز الرسوم
    if "الرتبة" in faculty_data.columns:
        rank_distribution = faculty_data["الرتبة"].value_counts().reset_index()
        rank_distribution.columns = ["الرتبة", "العدد"]
        
    if "التخصص" in faculty_data.columns:
        specialization_distribution = faculty_data["التخصص"].value_counts().reset_index()
        specialization_distribution.columns = ["التخصص", "العدد"]
    
    if "حالة الموظف" in faculty_data.columns:
        status_distribution = faculty_data["حالة الموظف"].value_counts().reset_index()
        status_distribution.columns = ["حالة الموظف", "العدد"]
        
    if "الجنسية" in faculty_data.columns:
        nationality_distribution = faculty_data["الجنسية"].value_counts().reset_index()
        nationality_distribution.columns = ["الجنسية", "العدد"]
    
    # عرض الرسوم البيانية في تبويبات
    tabs = st.tabs(["توزيع الرتب", "التخصصات", "حالة الموظف", "توزيع البحوث", "المقارنة السنوية"])
    
    # التبويب 1: توزيع الرتب
    with tabs[0]:
        if "الرتبة" in faculty_data.columns:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # رسم دائري لتوزيع الرتب الأكاديمية
                fig_rank_pie = px.pie(
                    rank_distribution, 
                    values="العدد", 
                    names="الرتبة",
                    title="توزيع الرتب الأكاديمية",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_rank_pie = prepare_chart_layout(fig_rank_pie, "توزيع الرتب الأكاديمية", is_mobile=mobile_view, chart_type="pie")
                st.plotly_chart(fig_rank_pie, use_container_width=True, config={"displayModeBar": False})
            
            with col2:
                # رسم شريطي للرتب حسب الجنس
                gender_rank_df = pd.crosstab(faculty_data['الرتبة'], faculty_data['الجنس'])
                fig_gender_rank = px.bar(
                    gender_rank_df, 
                    barmode='group',
                    title="توزيع الرتب حسب الجنس",
                    labels={"value": "العدد", "الجنس": "الجنس", "الرتبة": "الرتبة"},
                    color_discrete_sequence=["#1e88e5", "#E83E8C"]
                )
                fig_gender_rank = prepare_chart_layout(fig_gender_rank, "توزيع الرتب حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_gender_rank, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا تتوفر بيانات كافية لعرض توزيع الرتب.")
    
    # التبويب 2: التخصصات
    with tabs[1]:
        if "التخصص" in faculty_data.columns:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # رسم دائري لتوزيع التخصصات
                fig_spec_pie = px.pie(
                    specialization_distribution, 
                    values="العدد", 
                    names="التخصص",
                    title="توزيع التخصصات الدقيقة",
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_spec_pie = prepare_chart_layout(fig_spec_pie, "توزيع التخصصات", is_mobile=mobile_view, chart_type="pie")
                st.plotly_chart(fig_spec_pie, use_container_width=True, config={"displayModeBar": False})
            
            with col2:
                # رسم توزيع التخصصات حسب الجنس
                spec_gender_df = pd.crosstab(faculty_data['التخصص'], faculty_data['الجنس'])
                fig_spec_gender = px.bar(
                    spec_gender_df, 
                    barmode='group',
                    title="التخصصات حسب الجنس",
                    labels={"value": "العدد", "الجنس": "الجنس", "التخصص": "التخصص"},
                    color_discrete_sequence=["#1e88e5", "#E83E8C"]
                )
                fig_spec_gender = prepare_chart_layout(fig_spec_gender, "التخصصات حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_spec_gender, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا تتوفر بيانات كافية لعرض توزيع التخصصات.")
    
    # التبويب 3: حالة الموظف
    with tabs[2]:
        if "حالة الموظف" in faculty_data.columns:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # رسم شريطي أفقي لتوزيع الأعضاء حسب حالة الموظف
                fig_status_bar = px.bar(
                    status_distribution.sort_values("العدد", ascending=True), 
                    y="حالة الموظف", 
                    x="العدد",
                    title="توزيع الأعضاء حسب حالة الموظف",
                    color="العدد",
                    orientation='h',
                    color_continuous_scale="Blues"
                )
                fig_status_bar = prepare_chart_layout(fig_status_bar, "توزيع الأعضاء حسب حالة الموظف", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_status_bar, use_container_width=True, config={"displayModeBar": False})
            
            with col2:
                # رسم توزيع الرتب في كل حالة موظف
                status_rank_df = pd.crosstab(faculty_data['حالة الموظف'], faculty_data['الرتبة'])
                fig_status_rank = px.bar(
                    status_rank_df,
                    barmode='stack',
                    title="الرتب الأكاديمية حسب حالة الموظف",
                    labels={"value": "العدد", "الرتبة": "الرتبة", "حالة الموظف": "حالة الموظف"},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_status_rank = prepare_chart_layout(fig_status_rank, "الرتب حسب حالة الموظف", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_status_rank, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا تتوفر بيانات كافية لعرض توزيع حالة الموظف.")
    
    # التبويب 4: توزيع البحوث
    with tabs[3]:
        if "عدد البحوث" in faculty_data.columns:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # رسم شريطي لمتوسط البحوث حسب الرتبة
                research_by_rank = faculty_data.groupby("الرتبة")["عدد البحوث"].mean().reset_index()
                research_by_rank.columns = ["الرتبة", "متوسط عدد البحوث"]
                
                fig_research_rank = px.bar(
                    research_by_rank.sort_values("متوسط عدد البحوث", ascending=True), 
                    y="الرتبة", 
                    x="متوسط عدد البحوث",
                    title="متوسط البحوث حسب الرتبة",
                    color="متوسط عدد البحوث",
                    orientation='h',
                    color_continuous_scale="Greens"
                )
                fig_research_rank = prepare_chart_layout(fig_research_rank, "متوسط البحوث حسب الرتبة", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_research_rank, use_container_width=True, config={"displayModeBar": False})
            
            with col2:
                # رسم شريطي لإجمالي البحوث حسب الجنس
                research_by_gender = faculty_data.groupby("الجنس")["عدد البحوث"].sum().reset_index()
                research_by_gender.columns = ["الجنس", "إجمالي البحوث"]
                
                fig_research_gender = px.bar(
                    research_by_gender, 
                    y="الجنس", 
                    x="إجمالي البحوث",
                    title="إجمالي البحوث حسب الجنس",
                    color="إجمالي البحوث",
                    orientation='h',
                    color_continuous_scale="Greens"
                )
                fig_research_gender = prepare_chart_layout(fig_research_gender, "إجمالي البحوث حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_research_gender, use_container_width=True, config={"displayModeBar": False})
            
            # رسم توزيع حجم البحوث (الهستوجرام)
            fig_research_hist = px.histogram(
                faculty_data,
                x="عدد البحوث",
                title="توزيع عدد البحوث للأعضاء",
                color_discrete_sequence=["#1e88e5"]
            )
            fig_research_hist.update_layout(bargap=0.2)
            fig_research_hist = prepare_chart_layout(fig_research_hist, "توزيع عدد البحوث", is_mobile=mobile_view, chart_type="bar")
            st.plotly_chart(fig_research_hist, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا تتوفر بيانات كافية لعرض توزيع البحوث.")
    
    # التبويب 5: المقارنة السنوية
    with tabs[4]:
        # تحميل بيانات السنة السابقة للمقارنة
        previous_year = selected_year - 1
        previous_year_data = load_previous_year_data(selected_year)
        
        # إذا توفرت بيانات السنة السابقة، قم بتحليل التغييرات
        if previous_year_data is not None:
            # تحليل التغييرات
            new_members_data, departed_members_data, promotions, research_increase = analyze_faculty_changes(faculty_data, previous_year_data)
            
            # عرض ملخص التغييرات
            st.subheader(f"ملخص التغييرات بين {previous_year} و {selected_year}")
            
            summary_cols = st.columns(4)
            with summary_cols[0]:
                st.metric("أعضاء جدد", len(new_members_data) if new_members_data is not None else 0,
                         delta=f"+{len(new_members_data)}" if new_members_data is not None and len(new_members_data) > 0 else "0")
            with summary_cols[1]:
                st.metric("أعضاء مغادرون", len(departed_members_data) if departed_members_data is not None else 0,
                         delta=f"-{len(departed_members_data)}" if departed_members_data is not None and len(departed_members_data) > 0 else "0", delta_color="inverse")
            with summary_cols[2]:
                st.metric("إجمالي التغيير في العدد", 
                         len(faculty_data) - len(previous_year_data),
                         delta=f"{len(faculty_data) - len(previous_year_data)}")
            with summary_cols[3]:
                st.metric("زيادة البحوث",
                         research_increase,
                         delta=f"+{research_increase}" if research_increase > 0 else f"{research_increase}")
            
            # عرض الترقيات
            if promotions and len(promotions) > 0:
                st.subheader("الترقيات الأكاديمية")
                promotions_df = pd.DataFrame(promotions)
                st.dataframe(
                    promotions_df,
                    hide_index=True,
                    column_config={
                        "الاسم": st.column_config.TextColumn("الاسم"),
                        "الرتبة السابقة": st.column_config.TextColumn("الرتبة السابقة"),
                        "الرتبة الحالية": st.column_config.TextColumn("الرتبة الحالية")
                    },
                    use_container_width=True
                )
            
            # عرض الأعضاء الجدد
            if new_members_data is not None and len(new_members_data) > 0:
                st.subheader("الأعضاء الجدد")
                for _, row in new_members_data.iterrows():
                    name = row.get("الاسم", "غير متوفر")
                    gender = row.get("الجنس", "")
                    rank = row.get("الرتبة", "")
                    spec = row.get("التخصص", "")
                    
                    st.markdown(f"""
                    <div style="padding: 10px; border-right: 3px solid #27AE60; background-color: rgba(39, 174, 96, 0.1); margin-bottom: 10px; border-radius: 5px;">
                        <h4 style="color: #27AE60; margin: 0;">{name}</h4>
                        <p style="margin: 5px 0;">{rank} - {spec} - {gender}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # عرض الأعضاء المغادرين
            if departed_members_data is not None and len(departed_members_data) > 0:
                st.subheader("الأعضاء المغادرون")
                for _, row in departed_members_data.iterrows():
                    name = row.get("الاسم", "غير متوفر")
                    gender = row.get("الجنس", "")
                    rank = row.get("الرتبة", "")
                    spec = row.get("التخصص", "")
                    
                    st.markdown(f"""
                    <div style="padding: 10px; border-right: 3px solid #E74C3C; background-color: rgba(231, 76, 60, 0.1); margin-bottom: 10px; border-radius: 5px;">
                        <h4 style="color: #E74C3C; margin: 0;">{name}</h4>
                        <p style="margin: 5px 0;">{rank} - {spec} - {gender}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # مقارنة الإحصائيات العامة
            st.subheader("مقارنة الإحصائيات العامة")
            
            # مقارنة عدد الذكور والإناث
            current_male = len(faculty_data[faculty_data["الجنس"] == "ذكر"])
            current_female = len(faculty_data[faculty_data["الجنس"] == "أنثى"])
            previous_male = len(previous_year_data[previous_year_data["الجنس"] == "ذكر"])
            previous_female = len(previous_year_data[previous_year_data["الجنس"] == "أنثى"])
            
            gender_comparison = pd.DataFrame({
                "السنة": [previous_year, selected_year],
                "ذكور": [previous_male, current_male],
                "إناث": [previous_female, current_female]
            })
            
            # رسم بياني للمقارنة
            fig_gender_compare = px.bar(
                gender_comparison, 
                x="السنة", 
                y=["ذكور", "إناث"],
                title="مقارنة أعداد أعضاء هيئة التدريس حسب الجنس",
                barmode="group",
                color_discrete_sequence=["#1e88e5", "#E83E8C"]
            )
            fig_gender_compare = prepare_chart_layout(fig_gender_compare, "مقارنة حسب الجنس", is_mobile=mobile_view, chart_type="bar")
            st.plotly_chart(fig_gender_compare, use_container_width=True, config={"displayModeBar": False})
            
            # مقارنة التوزيع حسب الرتبة
            if "الرتبة" in faculty_data.columns and "الرتبة" in previous_year_data.columns:
                current_rank_counts = faculty_data["الرتبة"].value_counts().reset_index()
                current_rank_counts.columns = ["الرتبة", "العدد"]
                current_rank_counts["السنة"] = selected_year
                
                previous_rank_counts = previous_year_data["الرتبة"].value_counts().reset_index()
                previous_rank_counts.columns = ["الرتبة", "العدد"]
                previous_rank_counts["السنة"] = previous_year
                
                # دمج البيانات للمقارنة
                rank_comparison = pd.concat([previous_rank_counts, current_rank_counts])
                
                # رسم بياني للمقارنة
                fig_rank_compare = px.bar(
                    rank_comparison, 
                    x="الرتبة", 
                    y="العدد",
                    color="السنة",
                    title="مقارنة أعداد أعضاء هيئة التدريس حسب الرتبة",
                    barmode="group",
                    color_discrete_sequence=["#777777", "#1e88e5"]
                )
                fig_rank_compare = prepare_chart_layout(fig_rank_compare, "مقارنة حسب الرتبة", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_rank_compare, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info(f"لا تتوفر بيانات للسنة السابقة ({previous_year}) للمقارنة. يرجى التأكد من وجود ملف البيانات لتلك السنة.")
    
    # --- فلاتر البحث عن أعضاء هيئة التدريس ---
    st.subheader("بحث وتصفية أعضاء هيئة التدريس")
    
    # إنشاء صف للفلاتر
    filter_cols = st.columns([1, 1, 1, 1])
    
    # فلتر حالة الموظف
    with filter_cols[0]:
        if "حالة الموظف" in faculty_data.columns:
            all_statuses = ["الكل"] + sorted(faculty_data["حالة الموظف"].unique().tolist())
            selected_status = st.selectbox("حالة الموظف", all_statuses)
        else:
            selected_status = "الكل"
    
    # فلتر الرتبة الأكاديمية
    with filter_cols[1]:
        if "الرتبة" in faculty_data.columns:
            all_ranks = ["الكل"] + sorted(faculty_data["الرتبة"].unique().tolist())
            selected_rank = st.selectbox("الرتبة", all_ranks)
        else:
            selected_rank = "الكل"
    
    # فلتر التخصص
    with filter_cols[2]:
        if "التخصص" in faculty_data.columns:
            all_specs = ["الكل"] + sorted(faculty_data["التخصص"].unique().tolist())
            selected_spec = st.selectbox("التخصص", all_specs)
        else:
            selected_spec = "الكل"
    
    # فلتر الجنس
    with filter_cols[3]:
        if "الجنس" in faculty_data.columns:
            all_genders = ["الكل", "ذكر", "أنثى"]
            selected_gender = st.selectbox("الجنس", all_genders)
        else:
            selected_gender = "الكل"
    
    # تطبيق الفلاتر
    filtered_data = faculty_data.copy()
    
    if selected_status != "الكل" and "حالة الموظف" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["حالة الموظف"] == selected_status]
        
    if selected_rank != "الكل" and "الرتبة" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["الرتبة"] == selected_rank]
        
    if selected_spec != "الكل" and "التخصص" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["التخصص"] == selected_spec]
        
    if selected_gender != "الكل" and "الجنس" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["الجنس"] == selected_gender]
    
    # فلتر البحث بالنص (الاسم)
    search_query = st.text_input("البحث بالاسم", placeholder="ادخل اسم عضو هيئة التدريس...")
    if search_query and "الاسم" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["الاسم"].str.contains(search_query, case=False, na=False)]
    
    # --- عرض قائمة أعضاء هيئة التدريس ---
    if len(filtered_data) > 0:
        st.subheader(f"قائمة الأعضاء ({len(filtered_data)})")
        
        # معاملات تقييم النشاط البحثي
        filtered_data["تصنيف_البحوث"] = ""
        if "عدد البحوث" in filtered_data.columns:
            filtered_data.loc[filtered_data["عدد البحوث"] >= 15, "تصنيف_البحوث"] = "نشط جداً"
            filtered_data.loc[(filtered_data["عدد البحوث"] >= 10) & (filtered_data["عدد البحوث"] < 15), "تصنيف_البحوث"] = "نشط"
            filtered_data.loc[(filtered_data["عدد البحوث"] >= 5) & (filtered_data["عدد البحوث"] < 10), "تصنيف_البحوث"] = "متوسط"
            filtered_data.loc[filtered_data["عدد البحوث"] < 5, "تصنيف_البحوث"] = "محدود"
            
            # قاموس الشارات لكل تصنيف
            badge_map = {
                "نشط جداً": "badge-green",
                "نشط": "badge-blue",
                "متوسط": "badge-orange",
                "محدود": "badge-red"
            }
            
        # حساب نقاط الإنجازات لكل عضو من جدول الإنجازات إذا كان متاحًا
        has_achievements = False
        if not faculty_achievements.empty and "العضو" in faculty_achievements.columns and "النقاط" in faculty_achievements.columns:
            has_achievements = True
            faculty_points = faculty_achievements.groupby("العضو")["النقاط"].sum().reset_index()
            faculty_points.columns = ["الاسم", "نقاط_الإنجازات"]
            
            # دمج البيانات مع بيانات الأعضاء المفلترة
            filtered_data = pd.merge(filtered_data, faculty_points, on="الاسم", how="left")
            filtered_data["نقاط_الإنجازات"] = filtered_data["نقاط_الإنجازات"].fillna(0)
            
        # عرض بطاقات الأعضاء
        for i, row in filtered_data.iterrows():
            name = row.get("الاسم", "غير متوفر")
            gender = row.get("الجنس", "")
            rank = row.get("الرتبة", "")
            spec = row.get("التخصص", "")
            nationality = row.get("الجنسية", "")
            email = row.get("البريد الإلكتروني", "")
            status = row.get("حالة الموظف", "")
            research_count = int(row.get("عدد البحوث", 0))
            research_classification = row.get("تصنيف_البحوث", "")
            badge_class = badge_map.get(research_classification, "badge-blue") if "تصنيف_البحوث" in row and row["تصنيف_البحوث"] != "" else ""
            
            # الحصول على نقاط الإنجازات إذا كانت متاحة
            achievement_points = int(row.get("نقاط_الإنجازات", 0)) if has_achievements else 0
            
            # عرض بطاقة العضو
            st.markdown(f"""
            <div class="faculty-profile-card">
                <div class="profile-avatar">
                    {get_avatar_placeholder(name)}
                </div>
                <div class="profile-info">
                    <div class="profile-name">{name}</div>
                    <div class="profile-title">{rank} - {spec}</div>
                    <div class="profile-details">
                        <span class="profile-detail-item">{"👨" if gender == "ذكر" else "👩"} {gender}</span>
                        <span class="profile-detail-item">🌍 {nationality}</span>
                        <span class="profile-detail-item">📧 {email}</span>
                        <span class="profile-detail-item">👤 {status}</span>
                        {f'<span class="profile-detail-item badge {badge_class}">{research_classification}</span>' if research_classification else ''}
                    </div>
                    <div class="profile-metrics">
                        <div class="profile-metric">
                            <div class="profile-metric-value">{research_count}</div>
                            <div class="profile-metric-label">البحوث</div>
                        </div>
                        {f'''
                        <div class="profile-metric">
                            <div class="profile-metric-value">{achievement_points}</div>
                            <div class="profile-metric-label">نقاط الإنجاز</div>
                        </div>
                        ''' if has_achievements else ''}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات مطابقة للفلاتر المختارة. يرجى تعديل الفلاتر للحصول على نتائج.")
    
    # --- نصائح للاستخدام ---
    with st.expander("💡 نصائح للاستخدام", expanded=False):
        st.markdown("""
        - **منتقي السنة:** يمكنك اختيار السنة لعرض بيانات أعضاء هيئة التدريس لتلك السنة.
        - **تبويبة المقارنة السنوية:** تعرض التغييرات والفروقات بين السنة المحددة والسنة السابقة.
        - **شريط التنقل العلوي:** يعرض الأقسام الرئيسية والبرامج الأكاديمية مباشرة بشكل أفقي على الشاشات الكبيرة.
        - **على الجوال:** تظهر نفس القائمة بشكل رأسي عند النقر على أيقونة القائمة (☰).
        - **الفلاتر المتعددة:** يمكنك تطبيق أكثر من فلتر في نفس الوقت للوصول إلى بيانات محددة.
        - **البحث بالاسم:** يمكنك البحث عن عضو معين بكتابة جزء من اسمه.
        - **الرسوم البيانية تفاعلية:** مرر الفأرة فوقها لرؤية التفاصيل.
        - **التبويبات:** انقر على التبويبات المختلفة لعرض طرق متنوعة لتحليل البيانات.
        - **تصنيف النشاط البحثي:**
            - <span class="badge badge-green">نشط جداً</span>: 15 بحث أو أكثر
            - <span class="badge badge-blue">نشط</span>: 10-14 بحث
            - <span class="badge badge-orange">متوسط</span>: 5-9 بحوث
            - <span class="badge badge-red">محدود</span>: أقل من 5 بحوث
        """, unsafe_allow_html=True)

# --- إضافة نص تذييل الصفحة ---
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #666; font-size: 0.8em;">
    © كلية القرآن الكريم والدراسات الإسلامية - جامعة الطائف {0}
</div>
""".format(datetime.now().year), unsafe_allow_html=True)
