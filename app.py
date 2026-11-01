import streamlit as st
from PIL import Image, ImageDraw
import io
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Free Fire Point Table Maker", layout="centered")

st.title("🔥 Free Fire Esports Point Table Generator")
st.write("টিমের নাম, পজিশন ও কিল এডিট করুন এবং এক ক্লিকে পয়েন্ট টেবিল ওভারলে তৈরি করুন!")

# Sidebar Settings
st.sidebar.header("⚙️ টুর্নামেন্ট সেটিংস")
tourney_title = st.sidebar.text_input("টুর্নামেন্টের নাম", "CHAMPION RUSH")
sub_title = st.sidebar.text_input("সাব-টাইটেল", "Week 00 Day 00")

# Point System Mapping
position_points = {
    1: 12,
    2: 9,
    3: 8,
    4: 7,
    5: 6,
    6: 5,
    7: 4,
    8: 3,
    9: 2,
    10: 1,
}

st.sidebar.subheader("📊 পয়েন্ট সিস্টেম রুলস")
st.sidebar.info("Position: #1=12, #2=9, #3=8, #4=7, #5=6, #6=5, #7=4, #8=3, #9=2, #10=1 | Per Kill = 1 Pt")

# Manual/Editable Data Table for 12 Teams
st.subheader("📝 ম্যাচের রেজাল্ট ও টিম এডিটর")
st.write("💡 স্ক্রিনশট দেখে নিচের টেবিলে সরাসরি টিমের নাম, পজিশন (Rank) এবং কিল (Kills) লিখে এডিট করে দিন।")

if 'team_table_data' not in st.session_state:
    default_data = []
    for i in range(1, 13):
        default_data.append({
            "TEAM NAME": f"Team {i}",
            "RANK": i,
            "KILLS": 0
        })
    st.session_state.team_table_data = pd.DataFrame(default_data)

edited_df = st.data_editor(st.session_state.team_table_data, num_rows="dynamic", use_container_width=True)

if st.button("🚀 পয়েন্ট ক্যালকুলেট ও ফাইনাল ওভারলে জেনারেট করুন"):
    
    processed_data = []
    for index, row in edited_df.iterrows():
        try:
            r = int(row['RANK'])
            k = int(row['KILLS'])
        except:
            r = 15
            k = 0
            
        p_pts = position_points.get(r, 0)
        k_pts = k * 1
        total_pts = p_pts + k_pts
        win_val = 1 if r == 1 else 0
        
        processed_data.append({
            "TEAM": str(row['TEAM NAME']),
            "WIN": win_val,
            "POINT": p_pts,
            "KILLS": k_pts,
            "TOTAL": total_pts,
            "RAW_RANK": r
        })

    df = pd.DataFrame(processed_data)
    df = df.sort_values(by=['TOTAL', 'WIN', 'KILLS'], ascending=False).reset_index(drop=True)
    df.index += 1
    df.index.name = "RANK"

    st.write("### 📋 সাজানো পয়েন্ট স্ট্যান্ডিং টেবিল:")
    st.dataframe(df[['TEAM', 'WIN', 'POINT', 'KILLS', 'TOTAL']])

    st.success("পয়েন্ট টেবিল ওভারলে সফলভাবে তৈরি হয়েছে!")
    
    fig_img = Image.new('RGB', (900, 1100), color=(15, 23, 42))
    d = ImageDraw.Draw(fig_img)
    
    d.text((50, 40), f"{tourney_title}", fill=(255, 255, 255))
    d.text((50, 90), f"{sub_title}", fill=(200, 200, 200))
    
    y_offset = 160
    d.text((50, y_offset), "RANK   TEAM NAME                WIN    POINT    KILLS    TOTAL", fill=(255, 215, 0))
    d.line([(50, y_offset + 30), (850, y_offset + 30)], fill=(100, 100, 100), width=2)
    
    y_offset += 50
    for idx, row in df.iterrows():
        row_text = f"{idx:02d}      {row['TEAM']:<22}     {row['WIN']:02d}       {row['POINT']:02d}        {row['KILLS']:02d}        {row['TOTAL']:03d}"
        d.text((50, y_offset), row_text, fill=(255, 255, 255))
        y_offset += 40

    st.image(fig_img, caption="Generated Point Table Overlay", use_column_width=True)
    
    buf = io.BytesIO()
    fig_img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="📥 ওভারলে ইমেজ ডাউনলোড করুন",
        data=byte_im,
        file_name="ff_point_table.png",
        mime="image/png"
    )
