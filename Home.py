# -*- coding: utf-8 -*-
"""
صفحة "الرئيسية" لواجهة Streamlit – متجاوبة للجوال والكمبيوتر
---------------------------------------------------------------
- قائمة علويّة مسطّحة (Top Navbar) تظهر على الشاشات ≥ 769px.
- قائمة برجر جانبيّة تظهر على الأجهزة الأصغر.
- تستورد بيانات القسم والبرامج وتعرض مؤشرات رئيسيّة ورسومًا تفاعليّة.
- جميع الدوال المساعدة مضمّنة في الأسفل (يمكن لاحقًا نقلها إلى utils).

> ملاحظة: تستعمل `get_github_file_content()` الافتراضية (dummy) إلى أن تُربط بخدمة الـ GitHub.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib

# ------------------------------------------------------------------
# إعدادات الصفحة
st.set_page_config(
    page_title="الرئيسية",
    page_icon="🏠",
    layout="wide",
)

# ------------------------------------------------------------------
# CSS + HTML لشريط التنقّل المتجاوب
# (تم تبسيطه – لا dropdowns، التفاف تلقائي)
# ------------------------------------------------------------------
responsive_menu_html_css = """
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
    /* إخفاء عناصر Streamlit الافتراضية */
    [data-testid="stToolbar"], header, footer, #MainMenu {display:none !important;}
    .stApp {direction:rtl; text-align:right; font-family:'Tajawal',sans-serif;}

    /*  Top‑navbar  */
    .top-navbar{background:#f8f9fa;border-bottom:1px solid #e7e7e7;padding:6px 12px;display:none;width:100%;box-sizing:border-box;}
    .top-navbar ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;align-items:center;}
    .top-navbar li{margin-left:1rem;margin-bottom:.25rem;}
    .top-navbar a{color:#333;text-decoration:none;font-weight:500;padding:4px 4px;white-space:nowrap;}
    .top-navbar a:hover{color:#1e88e5;}

    /* Burger button */
    .mobile-menu-trigger{display:none;position:fixed;top:10px;right:15px;z-index:1001;background:#1e88e5;color:#fff;padding:4px 10px;border-radius:4px;font-size:1.2rem;cursor:pointer;}
    .mobile-menu-checkbox{display:none;}
    .mobile-menu{display:none;position:fixed;top:0;right:0;width:240px;height:100%;background:#f8f9fa;z-index:1000;padding:60px 14px 14px 14px;box-shadow:-2px 0 5px rgba(0,0,0,.1);transform:translateX(100%);transition:transform .3s ease-in-out;overflow-y:auto;}
    .mobile-menu ul{list-style:none;padding:0;margin:0;}
    .mobile-menu li{margin-bottom:.6rem;}
    .mobile-menu a{display:block;padding:8px;color:#333;text-decoration:none;border-bottom:1px solid #eee;font-weight:500;}
    .mobile-menu a:hover{background:#eee;color:#1e88e5;}
    .mobile-menu-overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.4);z-index:999;}
    .mobile-menu-checkbox:checked~.mobile-menu{display:block;transform:translateX(0);}
    .mobile-menu-checkbox:checked~.mobile-menu-overlay{display:block;}

    /* Back‑to‑top */
    .back-to-top{position:fixed;bottom:20px;left:20px;width:42px;height:42px;background:#1e88e5;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;opacity:0;transform:scale(0);transition:opacity .3s,transform .3s;z-index:998;}
    .back-to-top.visible{opacity:1;transform:scale(1);}

    /* Typography */
    h1,h2,h3{color:#1e88e5;font-weight:600;margin-top:24px;margin-bottom:12px;}
    h1{font-size:calc(1.4rem + 1vw);border-bottom:2px solid #1e88e5;padding-bottom:10px;}
    h2{font-size:calc(1.1rem + .5vw);}
    h3{font-size:calc(1rem + .2vw);}

    /* Cards */
    .metric-card, .chart-container{background:#fff;border-radius:10px;box-shadow:0 2px 6px rgba(0,0,0,.08);padding:14px;margin-bottom:16px;}

    @media(max-width:768px){
        .top-navbar{display:none;}
        .mobile-menu-trigger{display:block;}
        .main .block-container{padding-top:60px !important;padding-right:1rem !important;padding-left:1rem !important;}
    }
    @media(min-width:769px){
        .top-navbar{display:block;}
    }
</style>

<nav class="top-navbar">
  <ul>
    <li><a href="/">الرئيسية</a></li>
    <li><a href="/هيئة_التدريس">هيئة التدريس</a></li>
    <li><a href="/إنجاز_المهام">إنجاز المهام</a></li>
    <li><a href="/program1">بكالوريوس قرآن وعلومه</a></li>
    <li><a href="/program2">بكالوريوس القراءات</a></li>
    <li><a href="/program3">ماجستير الدراسات القرآنية</a></li>
    <li><a href="/program4">ماجستير القراءات</a></li>
    <li><a href="/program5">دكتوراه علوم قرآن</a></li>
    <li><a href="/program6">دكتوراه القراءات</a></li>
  </ul>
</nav>

<input type="checkbox" id="mobile-menu-toggle" class="mobile-menu-checkbox">
<label for="mobile-menu-toggle" class="mobile-menu-trigger">☰</label>
<label for="mobile-menu-toggle" class="mobile-menu-overlay"></label>
<div class="mobile-menu">
  <ul>
    <li><a href="/">الرئيسية</a></li>
    <li><a href="/هيئة_التدريس">هيئة التدريس</a></li>
    <li><a href="/إنجاز_المهام">إنجاز المهام</a></li>
    <li><a href="/program1">بكالوريوس قرآن وعلومه</a></li>
    <li><a href="/program2">بكالوريوس القراءات</a></li>
    <li><a href="/program3">ماجستير الدراسات القرآنية</a></li>
    <li><a href="/program4">ماجستير القراءات</a></li>
    <li><a href="/program5">دكتوراه علوم قرآن</a></li>
    <li><a href="/program6">دكتوراه القراءات</a></li>
  </ul>
</div>

<div class="back-to-top" onclick="window.scrollTo({top:0,behavior:'smooth'});">↑</div>

<script>
// إظهار/إخفاء زر الرجوع للأعلى
window.addEventListener('scroll',function(){
  const btn=document.querySelector('.back-to-top');
  if(btn) btn.classList[(window.scrollY>300?'add':'remove')]('visible');
});
// إغلاق قائمة الجوال عند اختيار رابط
Array.from(document.querySelectorAll('.mobile-menu a')).forEach(el=>{
  el.addEventListener('click',()=>{document.getElementById('mobile-menu-toggle').checked=false;});
});
</script>
"""

st.markdown(responsive_menu_html_css, unsafe_allow_html=True)

# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------

def is_mobile():
    return st.runtime.scriptrunner.script_run_context.is_local if hasattr(st.runtime, "scriptrunner") else False

def prepare_chart_layout(fig, title: str, mobile=False, ctype="bar"):
    fig.update_layout(title=title,font_family="Tajawal",dragmode=False,plot_bgcolor="rgba(240,240,240,0.6)",paper_bgcolor="white")
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    if mobile:
        fig.update_layout(height=300 if ctype!="heatmap" else 350,margin=dict(t=40,b=90,l=20,r=20),title_font_size=14,font_size=10)
    else:
        fig.update_layout(height=450 if ctype!="heatmap" else 400,margin=dict(t=60,b=110,l=40,r=40),title_font_size=18,font_size=12)
    return fig

# ------------------------------------------------------------------
# Dummy GitHub data loaders (replace with real implementation)
# ------------------------------------------------------------------

def load_department_summary():
    data={
        "البرنامج":["بكالوريوس في القرآن وعلومه","بكالوريوس القراءات","ماجستير الدراسات القرآنية المعاصرة","ماجستير القراءات","دكتوراه علوم القرآن","دكتوراه القراءات"],
        "عدد الطلاب":[210,180,150,200,120
