# -*- coding: utf-8 -*-
"""
Home.py – صفحة "الرئيسية" المبنية على بيانات مجلد ‎data/‎
============================================================
* يقرأ إجماليات القسم من **data/department/department_summary.csv**.
* يدمج ملفات **students_YYYY.csv** و **kpi_YYYY.csv** لكل برنامج/سنة متاحة.
* يعرض مؤشرات رئيسية ورسومًا بيانية تفاعليّة.
* القائمة العلوية وبيرجر الجوال مضمنتان عبر كتلة CSS/HTML.

> يعتمد على المساعدات فى `pages/utils/github_helpers.py` (يجب أن تكون موجودة).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pages.utils.github_helpers import get_github_file_content, get_available_years

# ------------------------------------------------------------------
# إعداد الصفحة
# ------------------------------------------------------------------
st.set_page_config(page_title="الرئيسية", page_icon="🏠", layout="wide")

# ------------------------------------------------------------------
# CSS + HTML للقائمة (نفس التصميم السابق مختصرًا)
# ------------------------------------------------------------------
responsive_css = """
<style>
.stApp{direction:rtl;text-align:right;font-family:'Tajawal',sans-serif;}
/* إخفاء عناصر واجهة Streamlit الافتراضية */
header,footer,[data-testid="stToolbar"],#MainMenu{display:none !important;}
/* زر الرجوع لأعلى */
.back-to-top{position:fixed;bottom:20px;left:20px;width:40px;height:40px;background:#1e88e5;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;opacity:0;transform:scale(0);transition:.3s;z-index:998;cursor:pointer;}
.back-to-top.visible{opacity:1;transform:scale(1);}
</style>
<div class='back-to-top' onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</div>
<script>window.addEventListener('scroll',()=>{const b=document.querySelector('.back-to-top');if(b){b.classList[(window.scrollY>300?'add':'remove')]('visible');}});</script>
"""

st.markdown(responsive_css, unsafe_allow_html=True)

# ------------------------------------------------------------------
# ثابتات
# ------------------------------------------------------------------
PROGRAM_MAP = {
    "بكالوريوس في القرآن وعلومه":        "bachelor_quran",
    "بكالوريوس القراءات":               "bachelor_readings",
    "ماجستير الدراسات القرآنية المعاصرة":"master_contemporary",
    "ماجستير القراءات":                 "master_readings",
    "دكتوراه علوم القرآن":              "phd_quran",
    "دكتوراه القراءات":                 "phd_readings",
}
SHORT_MAP = {
    "بكالوريوس في القرآن وعلومه":"ب. قرآن",
    "بكالوريوس القراءات":"ب. قراءات",
    "ماجستير الدراسات القرآنية المعاصرة":"م. دراسات",
    "ماجستير القراءات":"م. قراءات",
    "دكتوراه علوم القرآن":"د. قرآن",
    "دكتوراه القراءات":"د. قراءات",
}
LATEST_YEAR = datetime.now().year if datetime.now().month >= 9 else datetime.now().year - 1

# ------------------------------------------------------------------
# دالة تنسيق الرسوم البيانية
# ------------------------------------------------------------------

def prepare_chart(fig, height=400):
    fig.update_layout(height=height, dragmode=False, plot_bgcolor="rgba(240,240,240,0.6)", paper_bgcolor="white", font_family="Tajawal")
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig

# ------------------------------------------------------------------
# تحميل بيانات القسم
# ------------------------------------------------------------------

def load_department_summary():
    try:
        df = get_github_file_content("data/department/department_summary.csv")
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception as e:
        st.error(f"تعذّر تحميل department_summary.csv: {e}")
        return pd.DataFrame()

# ------------------------------------------------------------------
# تحميل وتجميع بيانات البرامج سنويًا
# ------------------------------------------------------------------

def load_yearly_data():
    records = []
    for prog_name, code in PROGRAM_MAP.items():
        years, _ = get_available_years(code)
        for year in years:
            # عدد الطلاب
            stu_path = f"data/{code}/{year}/students_{year}.csv"
            students_total = None
            try:
                stu_df = get_github_file_content(stu_path)
                if isinstance(stu_df, pd.DataFrame):
                    if "إجمالي" in stu_df.columns:
                        students_total = stu_df["إجمالي"].iloc[0]
                    else:
                        students_total = stu_df.select_dtypes("number").sum().sum()
            except Exception:
                pass
            # مؤشرات النجاح والرضا
            kpi_path = f"data/{code}/{year}/kpi_{year}.csv"
            success_rate = satisfaction_rate = None
            try:
                kpi_df = get_github_file_content(kpi_path)
                if isinstance(kpi_df, pd.DataFrame) and "المؤشر" in kpi_df.columns:
                    def val(keyword):
                        sel = kpi_df[kpi_df["المؤشر"].str.contains(keyword, na=False)]
                        return sel["القيمة"].iloc[0] if not sel.empty else None
                    success_rate = val("نسبة النجاح")
                    satisfaction_rate = val("معدل الرضا")
            except Exception:
                pass
            records.append({
                "البرنامج": prog_name,
                "العام": year,
                "عدد الطلاب": students_total,
                "نسبة النجاح": success_rate,
                "معدل الرضا": satisfaction_rate,
            })
    return pd.DataFrame(records)

# ------------------------------------------------------------------
# تشغيل التحميل
# ------------------------------------------------------------------
summary_df = load_department_summary()
yearly_df  = load_yearly_data()

if summary_df.empty or yearly_df.empty:
    st.warning("لا توجد بيانات كافية – تأكد من رفع ملفات CSV الصحيحة في مجلد data/.")

# ------------------------------------------------------------------
# بطاقات المؤشرات الرئيسية
# ------------------------------------------------------------------

st.subheader("المؤشرات الرئيسية")
col1, col2, col3, col4 = st.columns(4)
if not summary_df.empty:
    if "عدد الطلاب" in summary_df.columns:
        col1.metric("إجمالي الطلاب", f"{int(summary_df['عدد الطلاب'].sum()):,}")
    if "أعضاء هيئة التدريس" in summary_df.columns:
        col2.metric("أعضاء هيئة التدريس", f"{int(summary_df['أعضاء هيئة التدريس'].sum()):,}")

latest_df = yearly_df[yearly_df["العام"] == LATEST_YEAR]
if not latest_df.empty:
    if latest_df["نسبة النجاح"].notna().any():
        col3.metric("متوسط النجاح", f"{latest_df['نسبة النجاح'].mean():.0f}%")
    if latest_df["معدل الرضا"].notna().any():
        col4.metric("متوسط الرضا", f"{latest_df['معدل الرضا'].mean():.0f}%")

# ------------------------------------------------------------------
# الرسوم البيانية
# ------------------------------------------------------------------

st.subheader("تحليل البرامج الأكاديمية")
latest_df = latest_df.assign(البرنامج_مختصر=lambda d: d["البرنامج"].map(SHORT_MAP))

if latest_df.empty:
    st.info("لا توجد بيانات للعام الحالي.")
else:
    t1, t2, t3 = st.tabs(["توزيع الطلاب", "مقارنة المؤشرات", "التطور السنوي"])
    with t1:
        if latest_df["عدد الطلاب"].notna().any():
            fig = px.pie(latest_df, names="البرنامج_مختصر", values="عدد الطلاب", title="توزيع الطلاب")
            st.plotly_chart(prepare_chart(fig, 380), use_container_width=True)
        else:
            st.info("بيانات عدد الطلاب غير متوفرة.")
    with t2:
        indicators = [c for c in ["نسبة النجاح", "معدل الرضا"] if latest_df[c].notna().any()]
        if indicators:
            fig = px.bar(latest_df, x="البرنامج_مختصر", y=indicators, barmode="group", title="مقارنة المؤشرات")
            st.plotly_chart(prepare_chart(fig), use_container_width=True)
        else:
            st.info("لا توجد بيانات مؤشرات.")
    with t3:
        if yearly_df.empty:
            st.info("لا توجد بيانات سنوية.")
        else:
            prog_options = {SHORT_MAP.get(p, p): p for p in yearly_df["البرنامج"].unique()}
            sel_short = st.selectbox("اختر برنامجًا", list(prog_options.keys()))
            sel_prog  = prog_options[sel_short]
            prog_df = yearly_df[yearly_df["البرنامج"] == sel_prog]
            if prog_df["عدد الطلاب"].notna().any():
                fig = px.line(prog_df, x="العام", y=["عدد الطلاب","نسبة النجاح","معدل الرضا"], markers=True, title=f"تطور مؤشرات {sel_short}")
                st.plotly_chart(prepare_chart(fig), use_container_width=True)
            else:
                st.info("لا توجد بيانات كافية لعرض التطور.")
