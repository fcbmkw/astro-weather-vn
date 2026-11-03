import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import folium
from streamlit_folium import st_folium
import pandas as pd
import altair as alt
import math
from collections import Counter
import ephem
import re
import time
#------------------------------------------------------------------------------
# KHỐI A — DÁN NGAY DƯỚI DÒNG "import ephem" (dòng 9, đầu file)
# ------------------------------------------------------------------------------
import os
import functools
from google import genai
from google.genai import types as genai_types
 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
_astro_ai_client = genai.Client(api_key=GEMINI_API_KEY)
 
# Cùng danh sách model fallback như app_ai.py — sửa ở đây nếu bạn đổi model.
ASTRO_AI_MODEL_CANDIDATES = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
]
# ------------------------------------------------------------------------------ (hết KHỐI A)
# --- CƠ SỞ DỮ LIỆU ĐỊA ĐIỂM ---
LOCATION_DATABASE = {
    "1. Long Coc Tea Hill Đồi chè Long Cốc, Phu Tho": [21.2181, 105.1528],
    "2. Bac Son Valley Thung lũng Bắc Sơn, Lang Son": [21.9056, 106.3312],
    "3. Mu Cang Chai Mù Cang Chải, Yen Bai": [21.8485, 104.1082],
    "4. Khau Pha Pass Đèo Khau Phạ, Yen Bai": [21.7619, 104.2867],
    "5. Lung Cu Flag Tower Cột cờ Lũng Cú, Ha Giang": [23.3592, 105.3156],
    "6. Ma Pi Leng Pass Đèo Mã Pí Lèng, Ha Giang": [23.2386, 105.3853],
    "7. Y Ty Y Tý, Lao Cai": [22.6288, 103.6069],
    "8. Ta Xua Peak Đỉnh Tà Xùa, Son La": [21.2588, 104.4647],
    "9. Thang Hen Lake Hồ Thăng Hen, Cao Bang": [22.7533, 106.3005],
    "10. Quan Lan Island Đảo Quan Lạn, Quang Ninh": [20.9065, 107.5452],
    "11. O Quy Ho Pass Đèo Ô Quy Hồ, Lao Cai": [22.3564, 103.7753],
    "12. Fansipan Peak Đỉnh Fansipan, Lao Cai": [22.3033, 103.7750],
    "13. Muong Hoa Valley Thung lũng Mường Hoa, Lao Cai": [22.3021, 103.8642],
    "14. Hoang Su Phi Hoàng Su Phì, Ha Giang": [22.7483, 104.6811],
    "15. Dong Van Karst Plateau Cao nguyên đá Đồng Văn, Ha Giang": [23.2778, 105.3611],
    "16. Du Gia Village Làng Du Già, Ha Giang": [22.9058, 105.2183],
    "17. Nho Que River Dòng sông Nho Quế, Ha Giang": [23.2281, 105.4128],
    "18. Ban Gioc Waterfall Thác Bản Giốc, Cao Bang": [22.8562, 106.7217],
    "19. Nui Mat thần Núi Mắt Thần, Cao Bang": [22.7667, 106.3050],
    "20. Pac Bo Relic Suối Lê Nin - Pắc Bó, Cao Bang": [22.9811, 106.0561],
    "21. Ba Be Lake Hồ Ba Bể, Bac Kan": [22.4111, 105.6178],
    "22. Mau Son Peak Đỉnh Mẫu Sơn, Lang Son": [21.8419, 106.9208],
    "23. Co To Island Đảo Cô Tô, Quang Ninh": [20.9822, 107.7583],
    "24. Binh Lieu Ridge Bống Cỏ Bình Liêu, Quang Ninh": [21.5303, 107.4431],
    "25. Yen Tu Mountain Núi Yên Tử, Quang Ninh": [21.1569, 106.7183],
    "26. Thung Nai Thung Nai, Hoa Binh": [20.7303, 105.2106],
    "27. Mai Chau Valley Thung lũng Mai Châu, Hoa Binh": [20.6592, 105.0789],
    "28. Pu Luong Nature Reserve Khu bảo tồn Pù Luông, Thanh Hoa": [20.4561, 105.2344],
    "29. Pha Luong Peak Đỉnh Pha Luông, Son La": [20.8872, 104.6256],
    "30. Moc Chau Tea Hill Đồi chè Mộc Châu, Son La": [20.8433, 104.6200],
    "31. Tam Dao Mountain Peak Đỉnh Tam Đảo, Vinh Phuc": [21.4589, 105.6486],
    "32. Ba Vi Peak Đỉnh Ba Vì, Hanoi": [21.0808, 105.3622],
    "33. Dong Cao Plateau Cao nguyên Đồng Cao, Bac Giang": [21.3653, 106.8406],
    "34. Cuc Phuong National Park Vườn quốc gia Cúc Phương, Ninh Binh": [20.3183, 105.6078],
    "35. Van Long Wetland Khu bảo tồn Vân Long, Ninh Binh": [20.3708, 105.8825],
    "36. Hang Mua Peak Đỉnh Hang Múa, Ninh Binh": [20.2828, 105.9525],
    "37. Xuan Thuy National Park Vườn quốc gia Xuân Thủy, Nam Dinh": [20.2333, 106.5500],
    "38. Sam Son Coast Bờ biển Sầm Sơn, Thanh Hoa": [19.7428, 105.9069],
    "39. Ben En National Park Vườn quốc gia Bến En, Thanh Hoa": [19.6208, 105.5181],
    "40. Pu Mat National Park Vườn quốc gia Pù Mát, Nghe An": [18.9667, 104.8000],
    "41. Cua Lo Beach Biển Cửa Lò, Nghe An": [18.8108, 105.7186],
    "42. Phong Nha - Ke Bang Vườn quốc gia Phong Nha - Kẻ Bàng, Quang Binh": [17.5333, 106.1500],
    "43. Da Nhay Beach Biển Đá Nhảy, Quang Binh": [17.5858, 106.4636],
    "44. Son Doong Cave Entrance Cửa hang Sơn Đoòng, Quang Binh": [17.4619, 106.2872],
    "45. Nhat Le Beach Biển Nhật Lệ, Quang Binh": [17.4897, 106.6264],
    "46. Cua Tung Beach Biển Cửa Tùng, Quang Tri": [17.0200, 107.1000],
    "47. Con Co Island Đảo Cồn Cỏ, Quang Tri": [17.1583, 107.3333],
    "48. Hai Van Pass Đèo Hải Vân, Thua Thien Hue": [16.1983, 108.1311],
    "49. Lap An Lagoon Đầm Lập An, Thua Thien Hue": [16.2167, 108.0833],
    "50. Bach Ma National Park Vườn quốc gia Bạch Mã, Thua Thien Hue": [16.1969, 107.8542],
    "51. Son Tra Peninsula Bán đảo Sơn Trà, Da Nang": [16.1000, 108.2500],
    "52. An Bang Beach Biển An Bàng, Quang Nam": [15.9128, 108.3378],
    "53. Cu Lao Cham Island Cù Lao Chàm, Quang Nam": [15.9583, 108.5167],
    "54. My Son Sanctuary Thánh địa Mỹ Sơn, Quang Nam": [15.7647, 108.1239],
    "55. Ly Son Island Đảo Lý Sơn, Quang Ngai": [15.3789, 109.1172],
    "56. Sa Huynh Beach Biển Sa Huỳnh, Quang Ngai": [14.6500, 109.0667],
    "57. Mang Den Măng Đen, Kon Tum": [14.6000, 108.3000],
    "58. Chu Dang Ya Volcano Núi lửa Chư Đăng Ya, Gia Lai": [14.1353, 108.0169],
    "59. Bien Ho Lake Hồ T'Nưng (Biển Hồ), Gia Lai": [14.0083, 108.0000],
    "60. Phu Yen Cape Dien Mũi Điện (Đại Lãnh), Phu Yen": [12.8908, 109.4589],
    "61. Ghenh Da Dia Ghềnh Đá Đĩa, Phu Yen": [13.3517, 109.2978],
    "62. Xuan Dai Bay Vịnh Xuân Đài, Phu Yen": [13.4333, 109.2333],
    "63. Eo Gio Quy Nhon Eo Gió Quy Nhơn, Binh Dinh": [13.8969, 109.3083],
    "64. Ky Co Beach Biển Kỳ Cò, Binh Dinh": [13.8833, 109.3167],
    "65. Cu Lao Xanh Island Cù Lao Xanh, Binh Dinh": [13.6167, 109.3500],
    "66. Lak Lake Hồ Lắk, Dak Lak": [12.4283, 108.1758],
    "67. Dray Nur Waterfall Thác Dray Nur, Dak Lak": [12.5053, 107.8931],
    "68. Ta Dung Lake Hồ Tà Đùng, Dak Nong": [11.8500, 107.9833],
    "69. Langbiang Mountain Đỉnh Langbiang, Lam Dong": [12.0428, 108.4386],
    "70. Tuyen Lam Lake Hồ Tuyền Lâm, Lam Dong": [11.8986, 108.4353],
    "71. Cau Dat Tea Hill Đồi chè Cầu Đất, Lam Dong": [11.8500, 108.5500],
    "72. Linh Quy Phuoc Dien Chùa Linh Quy Pháp Ấn, Lam Dong": [11.5333, 107.9167],
    "73. Cam Ranh Bay Vịnh Cam Ranh, Khanh Hoa": [11.8833, 109.1500],
    "74. Van Phong Bay Vịnh Vân Phong, Khanh Hoa": [12.6000, 109.3833],
    "75. Diep Son Island Đảo Điệp Sơn, Khanh Hoa": [12.7000, 109.2500],
    "76. Binh Ba Island Đảo Bình Ba, Khanh Hoa": [11.8333, 109.2333],
    "77. Vinh Hy Bay Vịnh Vĩnh Hy, Ninh Thuan": [11.7167, 109.1833],
    "78. Nui Chua National Park Vườn quốc gia Núi Chúa, Ninh Thuan": [11.7000, 109.1333],
    "79. Mui Dinh Cape Mũi Dinh, Ninh Thuan": [11.4833, 109.0167],
    "80. Phu Quy Island Đảo Phú Quý, Binh Thuan": [10.5167, 108.9333],
    "81. Mui Ne Sand Dunes Đồi Cát Mũi Né, Binh Thuan": [10.9500, 108.2833],
    "82. Ke Ga Cape Mũi Kê Gà, Binh Thuan": [10.6975, 107.9903],
    "83. Cu Lao Cau Island Cù Lao Câu, Binh Thuan": [11.2333, 108.8500],
    "84. Tri An Lake Hồ Trị An, Dong Nai": [11.1333, 107.0167],
    "85. Nam Cat Tien Park Vườn quốc gia Nam Cát Tiên, Dong Nai": [11.4167, 107.4333],
    "86. Ba Den Mountain Núi Bà Đen, Tay Ninh": [11.3708, 106.1689],
    "87. Dau Tieng Lake Hồ Dầu Tiếng, Tay Ninh": [11.3500, 106.3500],
    "88. Vung Tau Lighthouse Hải đăng Vũng Tàu, Ba Ria - Vung Tau": [10.3386, 107.0850],
    "89. Ho Tram Beach Biển Hồ Tràm, Ba Ria - Vung Tau": [10.4833, 107.4333],
    "90. Con Dao Island Đảo Côn Đảo, Ba Ria - Vung Tau": [8.6833, 106.6000],
    "91. Can Gio Mangrove Rừng sác Cần Giờ, Ho Chi Minh City": [10.4333, 106.8833],
    "92. Tan Lap Floating Village Làng nổi Tân Lập, Long An": [10.6167, 105.9833],
    "93. Tram Chim National Park Vườn quốc gia Tràm Chim, Dong Thap": [10.7000, 105.5500],
    "94. Ba Hon Dam Island Bà Hòn Dầm, Kien Giang": [10.2333, 104.5333],
    "95. Nam Du Island Quần đảo Nam Du, Kien Giang": [9.6833, 104.3500],
    "96. Phu Quoc Island (Ganh Dau) Gành Dầu Phú Quốc, Kien Giang": [10.3667, 103.8500],
    "97. Phu Quoc Island (Rach Vem) Rạch Vẹm Phú Quốc, Kien Giang": [10.3500, 103.9333],
    "98. Hon Son Island Đảo Hòn Sơn, Kien Giang": [9.8000, 104.8333],
    "99. U Minh Ha Park Vườn quốc gia U Minh Hạ, Ca Mau": [9.2500, 104.9167],
    "100. Ca Mau Cape Mũi Cà Mau, Ca Mau": [8.6083, 104.7167],
}

st.set_page_config(page_title="Astro Map Pro", page_icon="🌌", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .block-container { padding-top: 0.8rem; padding-bottom: 0.8rem; padding-left: 2rem; padding-right: 2rem; }
    iframe { width: 100% !important; }
    .stTable table { width: 100% !important; margin-bottom: 0px !important; }
    .metric-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 12px;
    }
    .source-card {
        background-color: #1e293b;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 12px;
        padding: 10px 15px 4px 15px;
    }
    .geo-highlight {
        font-family: 'Courier New', monospace;
        font-size: 19px;
        font-weight: bold;
        line-height: 1.6;
        margin-top: 5px;
    }
    .zenith-subtext {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #94a3b8;
        margin-top: 8px;
        border-top: 1px solid #475569;
        padding-top: 6px;
    }
    .footer-copyright {
        text-align: center; color: #64748b; font-size: 13px;
        font-weight: 500; margin-top: 30px; padding-top: 15px;
        border-top: 1px solid #334155;
    }
    /* Shrink gap between source label div and the selectbox below it */
    .source-card + div { margin-top: -10px !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────────────────
for k, v in [("lat", 21.0285), ("lon", 105.8542),
             ("map_center", [21.0285, 105.8542]), ("zoom", 6),
             ("day_offset", 0), ("location_name", "Hanoi, Vietnam"),
             ("is_custom_point", True), ("weather_source", "🔀 Blend (ECMWF+GFS)"),
             ("active_source_used", "ECMWF"),
             ("_last_tip", None), ("_last_lc", None),
             ("_source_auto", True), ("_ecmwf_available", True),
             ("map_tile", "himawari"),
             ("_need_fly", False), ("_skip_prefetch", False),
             ("_scan_result", None), ("_scan_days", 0), ("_scan_scanning", False), ("_scan_region", "bac"), ("_scan_best", False),
             ("_scan_tonight", False), ("_scan_fallback_label", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ──────────────────────────────────────────────────────────────────
def _strip_loc_num(name: str) -> str:
    """Bỏ số thứ tự ở đầu tên địa danh: '15. Kamikochi...' → 'Kamikochi...'"""
    import re
    return re.sub(r'^\d+\.\s*', '', name).strip()

# Vài tên không tách đúng bằng quy tắc chung (phần tiếng Anh/Việt trùng hoặc không có dấu)
_EN_PART_FIX = {"Y Ty Y": "Y Ty", "Nui": "Nui Mat", "Eo Gio Quy Nhon Eo": "Eo Gio Quy Nhon"}

def _vn_en_part(s: str) -> str:
    """Lấy phần tiếng Anh ở đầu tên địa điểm (bỏ phần tiếng Việt có dấu theo sau).
    'Long Coc Tea Hill Đồi chè Long Cốc' -> 'Long Coc Tea Hill'
    'Bac Son Valley Thung lũng Bắc Sơn'  -> 'Bac Son Valley'
    'Thung Nai Thung Nai'                -> 'Thung Nai'"""
    toks = s.split()
    cut = len(toks)
    for i, t in enumerate(toks):
        if any(ord(c) > 127 for c in t):
            cut = i
            # từ ngay trước là từ tiếng Việt viết hoa không dấu (vd 'Thung' trong 'Thung lũng')
            if i >= 2 and t[0].islower() and toks[i-1][0].isupper() and toks[i-1].isascii():
                cut = i - 1
            break
    toks = toks[:cut]
    h = len(toks) // 2
    if len(toks) >= 2 and len(toks) % 2 == 0 and toks[:h] == toks[h:]:   # 'Thung Nai Thung Nai'
        toks = toks[:h]
    out = " ".join(toks).strip() or s
    return _EN_PART_FIX.get(out, out)

def _disp_name(name: str) -> str:
    """Tên hiển thị gọn: bỏ số thứ tự đầu + phần tiếng Việt, giữ tỉnh.
    '1. Long Coc Tea Hill Đồi chè Long Cốc, Phu Tho' -> 'Long Coc Tea Hill, Phu Tho'. Chỉ dùng để HIỂN THỊ."""
    n = _strip_loc_num(name or "")
    if "," in n:
        head, prov = n.rsplit(",", 1)
        return f"{_vn_en_part(head.strip())}, {prov.strip()}"
    return _vn_en_part(n) if n else (name or "")

def _disp_name_html(name: str) -> str:
    """Tên hiển thị tô màu cam, dùng trong tiêu đề."""
    import html as _h
    return f'<span style="color:#fb923c;">{_h.escape(_disp_name(name))}</span>'

@st.cache_data(ttl=3600, show_spinner=False)   # cache 1 giờ — tên địa điểm không đổi
def fetch_location_name(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
    try:
        res = requests.get(url, headers={"User-Agent": "AstroMapPro/7.0"}, timeout=3)
        if res.status_code == 200:
            addr = res.json().get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county")
            state = addr.get("state")
            if city and state: return f"{city}, {state}"
            return state or city or "Unknown"
    except: pass
    return "Unknown Location"

def get_moon_phase_percent(date_obj):
    base = datetime(2024, 1, 11)
    phase = ((date_obj - base).total_seconds() / 86400.0 / 29.53059) % 1.0
    illum = round((1 - math.cos(phase * 2 * math.pi)) / 2 * 100, 1)
    if phase < 0.03 or phase > 0.97: desc = "New Moon 🌑"
    elif phase < 0.22: desc = "Waxing Crescent"
    elif phase < 0.28: desc = "First Quarter"
    elif phase < 0.47: desc = "Waxing Gibbous"
    elif phase < 0.53: desc = "Full Moon 🌕"
    elif phase < 0.72: desc = "Waning Gibbous"
    elif phase < 0.78: desc = "Last Quarter"
    else: desc = "Waning Crescent"
    return illum, desc

@st.cache_data(ttl=86400, show_spinner=False)  # cache 24 giờ — quỹ đạo trăng không đổi trong ngày
def calculate_exact_moon_altitude_ephem(lat, lon, year, month, day, hour_local, utc_offset_h=7.0):
    """Tính độ cao mặt trăng (có thể âm khi dưới đường chân trời).
    utc_offset_h là offset của location (ICT=+7).
    Dùng +30 phút để tính giữa khung giờ → chính xác hơn khi hiển thị trên chart."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0
    obs.epoch = ephem.J2000
    local_dt = datetime(year, month, day, hour_local, 30, 0)   # giữa giờ
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = ephem.Date(utc_dt)
    moon = ephem.Moon(); moon.compute(obs)
    return round(math.degrees(float(moon.alt)), 1)

@st.cache_data(ttl=86400, show_spinner=False)
def calculate_exact_sun_altitude_ephem(lat, lon, year, month, day, hour_local, utc_offset_h=7.0):
    """Tính độ cao mặt trời (có thể âm khi dưới đường chân trời = ban đêm).
    utc_offset_h là offset của location (ICT=+7)."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0
    obs.epoch = ephem.J2000
    local_dt = datetime(year, month, day, hour_local, 30, 0)   # giữa giờ
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = ephem.Date(utc_dt)
    sun = ephem.Sun(); sun.compute(obs)
    return round(math.degrees(float(sun.alt)), 1)

@st.cache_data(ttl=86400, show_spinner=False)
def calculate_milkyway_altitude(lat, lon, year, month, day, hour_local, utc_offset_h=7.0):
    """Tính độ cao trung tâm Dải Ngân Hà (Galactic Center, Sgr A*).
    RA = 17h45m40s, Dec = -29°00'28" (J2000)
    Trả về (altitude_deg, azimuth_deg) — altitude < 0 = dưới chân trời."""
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.pressure = 0
    obs.epoch = ephem.J2000
    local_dt = datetime(year, month, day, hour_local, 30, 0)
    utc_dt   = local_dt - timedelta(hours=utc_offset_h)
    obs.date = ephem.Date(utc_dt)
    # Galactic Center: RA 17h45m40s, Dec -29°00'28" (J2000)
    gc = ephem.FixedBody()
    gc._ra  = ephem.hours('17:45:40.04')
    gc._dec = ephem.degrees('-29:00:28.1')
    gc._epoch = ephem.J2000
    gc.compute(obs)
    return round(math.degrees(float(gc.alt)), 1), round(math.degrees(float(gc.az)), 1)

def calculate_zenith_ra_dec(lat, lon):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    d = (now - datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
    lst = (18.697374558 + 24.06570982441908 * d + lon / 15.0) % 24
    ra_h, ra_m = int(lst), int((lst % 1) * 60)
    dec_d, dec_m = int(lat), int((lat % 1) * 60)
    return f"{ra_h:02d}h {ra_m:02d}m", f"{dec_d:+03d}° {dec_m:02d}'"

def calculate_accurate_bortle(lat, lon):
    """Estimate Bortle class and SQM (mag/arcsec2) from coordinates.

    Methodology:
    -----------------------------------------------------
    Priority 1 - Per-location lookup table: values calibrated for the
      250+ curated Vietnam astrophotography locations, based on
      lightpollutionmap.info (VIIRS) sky-brightness data.

    Priority 2 - Weighted multi-city distance heuristic with per-city
      Bortle/SQM curves, used as a fallback for any point outside the
      curated list (e.g. a custom map click).

    Bortle <-> SQM reference (Wikipedia / Bortle 2001 / Sky & Telescope):
      Class 1:   21.76-22.0    Class 2:   21.6-21.75
      Class 3:   21.3-21.6     Class 4:   20.8-21.3
      Class 4.5: 20.3-20.8     Class 5:   19.25-20.3
      Class 6:   18.5-19.25    Class 7:   18.0-18.5
      Class 8/9: < 18.0
    """
    _LOC_BORTLE = {
        (21.2181, 105.1528): (3.0, 21.70), # 1 Long Coc Tea Hill, Phu Tho
        (21.9056, 106.3312): (3.0, 21.75), # 2 Bac Son Valley, Lang Son
        (21.8485, 104.1082): (2.5, 21.85), # 3 Mu Cang Chai, Yen Bai
        (21.7619, 104.2867): (2.0, 21.90), # 4 Khau Pha Pass, Yen Bai
        (23.3592, 105.3156): (2.0, 21.92), # 5 Lung Cu Flag Tower, Ha Giang
        (23.2386, 105.3853): (2.0, 21.95), # 6 Ma Pi Leng Pass, Ha Giang
        (22.6288, 103.6069): (2.0, 21.90), # 7 Y Ty, Lao Cai
        (21.2588, 104.4647): (2.5, 21.80), # 8 Ta Xua Peak, Son La
        (22.7533, 106.3005): (2.0, 21.90), # 9 Thang Hen Lake, Cao Bang
        (20.9065, 107.5452): (3.0, 21.65), # 10 Quan Lan Island, Quang Ninh
        (22.3564, 103.7753): (2.0, 21.90), # 11 O Quy Ho Pass, Lao Cai
        (22.3033, 103.7750): (1.5, 22.00), # 12 Fansipan Peak, Lao Cai
        (22.3021, 103.8642): (2.5, 21.82), # 13 Muong Hoa Valley, Lao Cai
        (22.7483, 104.6811): (2.0, 21.91), # 14 Hoang Su Phi, Ha Giang
        (23.2778, 105.3611): (2.0, 21.93), # 15 Dong Van Karst Plateau, Ha Giang
        (22.9058, 105.2183): (2.0, 21.90), # 16 Du Gia Village, Ha Giang
        (23.2281, 105.4128): (2.0, 21.94), # 17 Nho Que River, Ha Giang
        (22.8562, 106.7217): (2.0, 21.88), # 18 Ban Gioc Waterfall, Cao Bang
        (22.7667, 106.3050): (2.0, 21.92), # 19 Nui Mat Than, Cao Bang
        (22.9811, 106.0561): (2.0, 21.90), # 20 Pac Bo Relic, Cao Bang
        (22.4111, 105.6178): (2.5, 21.80), # 21 Ba Be Lake, Bac Kan
        (21.8419, 106.9208): (2.5, 21.83), # 22 Mau Son Peak, Lang Son
        (20.9822, 107.7583): (2.5, 21.80), # 23 Co To Island, Quang Ninh
        (21.5303, 107.4431): (2.0, 21.88), # 24 Binh Lieu Ridge, Quang Ninh
        (21.1569, 106.7183): (3.0, 21.60), # 25 Yen Tu Mountain, Quang Ninh
        (20.7303, 105.2106): (3.0, 21.68), # 26 Thung Nai, Hoa Binh
        (20.6592, 105.0789): (3.0, 21.72), # 27 Mai Chau Valley, Hoa Binh
        (20.4561, 105.2344): (2.5, 21.80), # 28 Pu Luong Nature Reserve, Thanh Hoa
        (20.8872, 104.6256): (2.0, 21.88), # 29 Pha Luong Peak, Son La
        (20.8433, 104.6200): (3.0, 21.70), # 30 Moc Chau Tea Hill, Son La
        (21.4589, 105.6486): (3.5, 21.40), # 31 Tam Dao Mountain Peak, Vinh Phuc
        (21.0808, 105.3622): (3.5, 21.45), # 32 Ba Vi Peak, Hanoi
        (21.3653, 106.8406): (2.5, 21.78), # 33 Dong Cao Plateau, Bac Giang
        (20.3183, 105.6078): (2.5, 21.82), # 34 Cuc Phuong National Park, Ninh Binh
        (20.3708, 105.8825): (3.5, 21.48), # 35 Van Long Wetland, Ninh Binh
        (20.2828, 105.9525): (3.5, 21.50), # 36 Hang Mua Peak, Ninh Binh
        (20.2333, 106.5500): (3.0, 21.65), # 37 Xuan Thuy National Park, Nam Dinh
        (19.7428, 105.9069): (4.0, 20.90), # 38 Sam Son Coast, Thanh Hoa
        (19.6208, 105.5181): (2.5, 21.78), # 39 Ben En National Park, Thanh Hoa
        (18.9667, 104.8000): (2.0, 21.90), # 40 Pu Mat National Park, Nghe An
        (18.8108, 105.7186): (4.0, 20.85), # 41 Cua Lo Beach, Nghe An
        (17.5333, 106.1500): (2.0, 21.92), # 42 Phong Nha - Ke Bang, Quang Binh
        (17.5858, 106.4636): (2.5, 21.75), # 43 Da Nhay Beach, Quang Binh
        (17.4619, 106.2872): (1.5, 22.02), # 44 Son Doong Cave Entrance, Quang Binh
        (17.4897, 106.6264): (3.5, 21.30), # 45 Nhat Le Beach, Quang Binh
        (17.0200, 107.1000): (3.0, 21.65), # 46 Cua Tung Beach, Quang Tri
        (17.1583, 107.3333): (2.0, 21.88), # 47 Con Co Island, Quang Tri
        (16.1983, 108.1311): (3.0, 21.60), # 48 Hai Van Pass, Thua Thien Hue
        (16.2167, 108.0833): (2.5, 21.72), # 49 Lap An Lagoon, Thua Thien Hue
        (16.1969, 107.8542): (2.0, 21.88), # 50 Bach Ma National Park, Thua Thien Hue
        (16.1000, 108.2500): (3.5, 21.35), # 51 Son Tra Peninsula, Da Nang
        (15.9128, 108.3378): (3.5, 21.40), # 52 An Bang Beach, Quang Nam
        (15.9583, 108.5167): (2.0, 21.85), # 53 Cu Lao Cham Island, Quang Nam
        (15.7647, 108.1239): (2.5, 21.78), # 54 My Son Sanctuary, Quang Nam
        (15.3789, 109.1172): (2.0, 21.90), # 55 Ly Son Island, Quang Ngai
        (14.6500, 109.0667): (2.5, 21.75), # 56 Sa Huynh Beach, Quang Ngai
        (14.6000, 108.3000): (2.0, 21.88), # 57 Mang Den, Kon Tum
        (14.1353, 108.0169): (2.5, 21.80), # 58 Chu Dang Ya Volcano, Gia Lai
        (14.0083, 108.0000): (3.0, 21.60), # 59 Bien Ho Lake, Gia Lai
        (12.8908, 109.4589): (2.0, 21.92), # 60 Phu Yen Cape Dien, Phu Yen
        (13.3517, 109.2978): (2.5, 21.82), # 61 Ghenh Da Dia, Phu Yen
        (13.4333, 109.2333): (2.5, 21.80), # 62 Xuan Dai Bay, Phu Yen
        (13.8969, 109.3083): (2.5, 21.78), # 63 Eo Gio Quy Nhon, Binh Dinh
        (13.8833, 109.3167): (2.5, 21.80), # 64 Ky Co Beach, Binh Dinh
        (13.6167, 109.3500): (2.0, 21.88), # 65 Cu Lao Xanh Island, Binh Dinh
        (12.4283, 108.1758): (2.0, 21.85), # 66 Lak Lake, Dak Lak
        (12.5053, 107.8931): (2.5, 21.80), # 67 Dray Nur Waterfall, Dak Lak
        (11.8500, 107.9833): (2.0, 21.90), # 68 Ta Dung Lake, Dak Nong
        (12.0428, 108.4386): (2.5, 21.75), # 69 Langbiang Mountain, Lam Dong
        (11.8986, 108.4353): (3.0, 21.60), # 70 Tuyen Lam Lake, Lam Dong
        (11.8500, 108.5500): (2.5, 21.78), # 71 Cau Dat Tea Hill, Lam Dong
        (11.5333, 107.9167): (2.0, 21.88), # 72 Linh Quy Phuoc Dien, Lam Dong
        (11.8833, 109.1500): (3.0, 21.65), # 73 Cam Ranh Bay, Khanh Hoa
        (12.6000, 109.3833): (2.0, 21.90), # 74 Van Phong Bay, Khanh Hoa
        (12.7000, 109.2500): (2.0, 21.88), # 75 Diep Son Island, Khanh Hoa
        (11.8333, 109.2333): (2.0, 21.88), # 76 Binh Ba Island, Khanh Hoa
        (11.7167, 109.1833): (2.0, 21.92), # 77 Vinh Hy Bay, Ninh Thuan
        (11.7000, 109.1333): (1.5, 21.98), # 78 Nui Chua National Park, Ninh Thuan
        (11.4833, 109.0167): (2.0, 21.90), # 79 Mui Dinh Cape, Ninh Thuan
        (10.5167, 108.9333): (1.5, 22.00), # 80 Phu Quy Island, Binh Thuan
        (10.9500, 108.2833): (3.0, 21.55), # 81 Mui Ne Sand Dunes, Binh Thuan
        (10.6975, 107.9903): (2.0, 21.88), # 82 Ke Ga Cape, Binh Thuan
        (11.2333, 108.8500): (1.5, 21.96), # 83 Cu Lao Cau Island, Binh Thuan
        (11.1333, 107.0167): (3.0, 21.60), # 84 Tri An Lake, Dong Nai
        (11.4167, 107.4333): (2.0, 21.88), # 85 Nam Cat Tien Park, Dong Nai
        (11.3708, 106.1689): (3.0, 21.65), # 86 Ba Den Mountain, Tay Ninh
        (11.3500, 106.3500): (2.5, 21.75), # 87 Dau Tieng Lake, Tay Ninh
        (10.3386, 107.0850): (4.0, 20.80), # 88 Vung Tau Lighthouse, Ba Ria - Vung Tau
        (10.4833, 107.4333): (3.0, 21.62), # 89 Ho Tram Beach, Ba Ria - Vung Tau
        (8.6833, 106.6000): (1.5, 22.05), # 90 Con Dao Island, Ba Ria - Vung Tau
        (10.4333, 106.8833): (3.5, 21.30), # 91 Can Gio Mangrove, Ho Chi Minh City
        (10.6167, 105.9833): (3.0, 21.60), # 92 Tan Lap Floating Village, Long An
        (10.7000, 105.5500): (2.5, 21.78), # 93 Tram Chim National Park, Dong Thap
        (10.2333, 104.5333): (2.0, 21.88), # 94 Ba Hon Dam Island, Kien Giang
        (9.6833, 104.3500): (1.5, 22.00), # 95 Nam Du Island, Kien Giang
        (10.3667, 103.8500): (2.5, 21.80), # 96 Phu Quoc Island (Ganh Dau), Kien Giang
        (10.3500, 103.9333): (2.5, 21.82), # 97 Phu Quoc Island (Rach Vem), Kien Giang
        (9.8000, 104.8333): (2.0, 21.88), # 98 Hon Son Island, Kien Giang
        (9.2500, 104.9167): (2.0, 21.90), # 99 U Minh Ha Park, Ca Mau
        (8.6083, 104.7167): (1.5, 22.02), # 100 Ca Mau Cape, Ca Mau
    }

    def _km(la1, lo1, la2, lo2):
        dlat = (la1 - la2) * 111.0
        dlon = (lo1 - lo2) * 111.0 * math.cos(math.radians((la1 + la2) / 2))
        return math.sqrt(dlat**2 + dlon**2)

    # Priority 1: exact location match within 5 km
    for (plat, plon), (bc, sq) in _LOC_BORTLE.items():
        if _km(lat, lon, plat, plon) < 5.0:
            return bc, sq

    # -- Priority 2: Min-distance heuristic --------------------------------
    # Each city has a center SQM (calibrated from lightpollutionmap.info).
    # SQM recovers with distance via a universal delta table.
    # Final SQM = min across all cities (most polluted city wins).
    #
    # Delta table (km from city center -> SQM added to city's center_sqm):
    #   <=4km:+0.0  <=8km:+0.3  <=15km:+0.7  <=25km:+1.2  <=40km:+1.8
    #   <=65km:+2.5  <=100km:+3.2  <=150km:+3.7  >150km:+4.0
    _DELTA_BANDS = [
        (4,   0.0),
        (8,   0.3),
        (15,  0.7),
        (25,  1.2),
        (40,  1.8),
        (65,  2.5),
        (100, 3.2),
        (150, 3.7),
    ]
    def _get_delta(d):
        for _thresh, _delta in _DELTA_BANDS:
            if d <= _thresh:
                return _delta
        return 4.0  # > 150km -> negligible

    # (lat, lon, name, center_sqm) - center_sqm calibrated from lightpollutionmap.info
    _CITIES = [
        (21.3167, 105.4000, "PhuTho-C", 19.80), # Gần 1
        (21.8525, 106.7592, "LangSon-C", 19.20), # Gần 2, 22
        (21.7050, 104.8731, "YenBai-C", 19.40), # Gần 3, 4
        (22.8233, 104.9836, "HaGiang-C", 19.90), # Gần 5, 6, 14, 15, 16, 17
        (22.4856, 103.9707, "LaoCai-C", 19.10), # Gần 7, 11, 12, 13
        (21.3272, 103.9142, "SonLa-C", 19.50), # Gần 8, 29, 30
        (22.6667, 106.2500, "CaoBang-C", 19.60), # Gần 9, 18, 19, 20
        (21.0100, 107.2900, "CamPha-C", 18.90), # Gần 10, 23, 24, 25
        (22.1462, 105.8350, "BacKan-C", 19.70), # Gần 21
        (20.8172, 105.3375, "HoaBinh-C", 19.30), # Gần 26, 27
        (19.8067, 105.7853, "ThanhHoa-C", 18.90), # Gần 28, 38, 39
        (21.3089, 105.6047, "VinhYen-C", 18.70), # Gần 31
        (21.0285, 105.8542, "HaNoi-C", 17.10), # Gần 32
        (21.2731, 106.1947, "BacGiang-C", 19.10), # Gần 33
        (20.2506, 105.9744, "NinhBinh-C", 18.80), # Gần 34, 35, 36
        (20.4283, 106.1683, "NamDinh-C", 18.60), # Gần 37
        (18.6733, 105.6819, "Vinh-C", 18.50), # Gần 40, 41
        (17.4686, 106.6222, "DongHoi-C", 19.10), # Gần 42, 43, 44, 45
        (16.8167, 107.1000, "DongHa-C", 19.30), # Gần 46, 47
        (16.4667, 107.6000, "Hue-C", 18.80), # Gần 48, 49, 50
        (16.0544, 108.2022, "DaNang-C", 17.80), # Gần 51
        (15.8801, 108.3380, "HoiAn-C", 18.60), # Gần 52, 53, 54
        (15.1200, 108.8000, "QuangNgai-C", 19.00), # Gần 55, 56
        (14.3500, 108.0000, "KonTum-C", 19.40), # Gần 57
        (13.9833, 108.0000, "Pleiku-C", 18.90), # Gần 58, 59
        (13.0833, 109.3000, "TuyHoa-C", 19.10), # Gần 60, 61, 62
        (13.7750, 109.2333, "QuyNhon-C", 18.70), # Gần 63, 64, 65
        (12.6667, 108.0500, "BuonMaThuot-C", 18.60), # Gần 66, 67
        (12.0000, 107.6833, "GiaNghia-C", 19.30), # Gần 68
        (11.9404, 108.4583, "DaLat-C", 18.40), # Gần 69, 70, 71
        (11.5469, 107.8089, "BaoLoc-C", 19.10), # Gần 72
        (12.2388, 109.1969, "NhaTrang-C", 18.20), # Gần 73, 74, 75, 76
        (11.5667, 108.9833, "PhanRang-C", 19.00), # Gần 77, 78, 79
        (10.9333, 108.1000, "PhanThiet-C", 18.60), # Gần 80, 81, 82, 83
        (10.9572, 106.8426, "BienHoa-C", 17.90), # Gần 84, 85
        (11.3100, 106.0983, "TayNinh-C", 19.20), # Gần 86, 87
        (10.3460, 107.0843, "VungTau-C", 18.10), # Gần 88, 89, 90
        (10.7769, 106.7009, "HCM-C", 16.80), # Gần 91
        (10.5333, 106.4000, "TanAn-C", 18.80), # Gần 92
        (10.4583, 105.6333, "CaoLanh-C", 19.10), # Gần 93
        (10.0167, 105.0833, "RachGia-C", 18.70), # Gần 94, 95, 98
        (10.2167, 103.9667, "PhuQuoc-C", 19.00), # Gần 96, 97
        (9.1769, 105.1500, "CaMau-C", 19.20), # Gần 99, 100
    ]

    sqm_est = 22.30  # start pristine, find most polluted influence
    for _clat, _clon, _cname, _csqm in _CITIES:
        _d = _km(lat, lon, _clat, _clon)
        _sqm_here = _csqm + _get_delta(_d)
        sqm_est = min(sqm_est, _sqm_here)

    sqm_est = max(16.5, min(22.3, round(sqm_est, 2)))

    # Convert SQM -> Bortle class
    if   sqm_est >= 21.76: bc = 1
    elif sqm_est >= 21.60: bc = 2
    elif sqm_est >= 21.30: bc = 3
    elif sqm_est >= 20.30: bc = 4   # merge 4 and 4.5
    elif sqm_est >= 19.41: bc = 5
    elif sqm_est >= 18.50: bc = 6
    elif sqm_est >= 18.00: bc = 7
    elif sqm_est >= 17.62: bc = 8
    else:                  bc = 9

    return bc, sqm_est

# ── WEATHER FETCH ─────────────────────────────────────────────────────────────
# Các endpoint fallback theo thứ tự ưu tiên:
#   1. Primary: ECMWF + GFS — đầy đủ nhất
#   2. Fallback: chỉ GFS — nhẹ hơn, luôn hoạt động
#   3. Fallback B: chỉ GFS — luôn hoạt động, không phụ thuộc server đơn lẻ
_FIELDS = "cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,relative_humidity_2m,wind_speed_10m,temperature_2m,precipitation"
_ENDPOINTS = [
    # (label, url_suffix)
    ("full",    f"&hourly={_FIELDS}&models=gfs_seamless,ecmwf_ifs025&wind_speed_unit=ms&timezone=auto"),
    ("gfs_only",f"&hourly={_FIELDS}&models=gfs_seamless&wind_speed_unit=ms&timezone=auto"),
]

@st.cache_resource
def _wx_prefetch_store():
    """Kho dùng chung giữa các lần rerun: data = kết quả đã tải sẵn, at = thời điểm tải (epoch giây)."""
    return {"data": {}, "at": {}}

def _wx_prefetch(coords, workers=8):
    """Tải song song thời tiết cho nhiều toạ độ (chỉ requests thuần, không đụng streamlit trong thread).
    Kết quả để trong kho; _fetch_weather_raw (có cache) sẽ lấy ra dùng -> cache vẫn ghi ở thread chính."""
    import time as _t
    from concurrent.futures import ThreadPoolExecutor
    store = _wx_prefetch_store()
    now = _t.time()
    todo = [c for c in dict.fromkeys(coords) if now - store["at"].get(c, 0) > 3300]
    if not todo:
        return
    def one(c):
        try:
            return c, _fetch_weather_raw_impl(c[0], c[1])
        except Exception:
            return c, None
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for c, res in ex.map(one, todo):
            if res and res[2] != "offline":      # lỗi thì để _fetch_weather_raw tự thử lại
                store["data"][c] = res
                store["at"][c] = now

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_weather_raw(lat, lon):
    pre = _wx_prefetch_store()["data"].pop((lat, lon), None)
    if pre is not None:
        return pre
    return _fetch_weather_raw_impl(lat, lon)

def _fetch_weather_raw_impl(lat, lon):
    """Raw API fetch với retry + multi-endpoint fallback.
    Returns (hourly_dict, utc_offset_seconds, endpoint_used_label, last_error)"""
    import time as _time
    base = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
    headers = {"User-Agent": "Mozilla/5.0 (AstroMapPro/7.0)"}
    last_error = None
    for ep_label, ep_suffix in _ENDPOINTS:
        url = base + ep_suffix
        for attempt in range(3):   # 3 lần thử mỗi endpoint (network có thể chập chờn)
            try:
                # Multi-model request (full) nặng hơn, cần timeout dài hơn
                _timeout = 12 if ep_label != "gfs_only" else 8
                res = requests.get(url, headers=headers, timeout=_timeout)
                if res.status_code == 200:
                    j = res.json()
                    return j.get("hourly", {}), j.get("utc_offset_seconds", 32400), ep_label, None
                # 5xx = server lỗi → thử endpoint tiếp theo ngay
                last_error = f"HTTP {res.status_code}"
                if res.status_code >= 500:
                    break
            except requests.exceptions.Timeout:
                last_error = "timeout"
                # timeout → thử lại
            except requests.exceptions.ConnectionError as e:
                last_error = f"connection_error: {e.__class__.__name__}"
                _time.sleep(0.5 * (attempt + 1))  # backoff rồi thử lại — có thể chỉ là lỗi mạng tạm thời
                continue
            except Exception as e:
                last_error = f"{e.__class__.__name__}: {e}"
                break  # lỗi khác → chuyển endpoint ngay
    return {}, 32400, "offline", last_error

def fetch_weather_7days(lat, lon, source="ECMWF"):
    """Wrapper giữ nguyên interface cũ — delegate sang cached raw fetch."""
    hourly, utc_offset, ep_label, last_error = _fetch_weather_raw(lat, lon)
    return hourly, source, utc_offset, ep_label, last_error

def get_val(hourly, field, idx, prefer_ecmwf=True):
    """
    Extract a single numeric value for a field at index idx.
    If prefer_ecmwf: try _ecmwf_ifs025 first, fallback to _gfs_seamless.
    Else: try _gfs_seamless first, fallback to _ecmwf_ifs025.
    Also tries bare key as last resort.
    Returns (float_value, source_used: 'ECMWF'|'GFS'|None)
    """
    order = ["_ecmwf_ifs025", "_gfs_seamless"] if prefer_ecmwf else ["_gfs_seamless", "_ecmwf_ifs025"]
    labels = ["ECMWF", "GFS"] if prefer_ecmwf else ["GFS", "ECMWF"]
    for suffix, label in zip(order, labels):
        lst = hourly.get(f"{field}{suffix}", [])
        if idx < len(lst) and lst[idx] is not None:
            return float(lst[idx]), label
    # bare key fallback
    lst = hourly.get(field, [])
    if idx < len(lst) and lst[idx] is not None:
        return float(lst[idx]), "?"
    return 0.0, None

def _get_raw(hourly, field, suffix, idx):
    """Get raw value for a specific model suffix. Returns None if missing."""
    lst = hourly.get(f"{field}{suffix}", [])
    if idx < len(lst) and lst[idx] is not None:
        return float(lst[idx])
    return None

def get_val_blended(hourly, field, idx, day_offset):
    """
    Weighted blend of ECMWF + GFS based on day_offset.
    Day 0-3: ECMWF x0.75 + GFS x0.25 (ECMWF IFS025, best short-range accuracy)
    Day 4-7: ECMWF x0.60 + GFS x0.40 (GFS gains weight further out)
    Re-normalises weights if any model has missing data.
    Returns (float_value, label_string)
    """
    ecmwf = _get_raw(hourly, field, "_ecmwf_ifs025",  idx)
    gfs   = _get_raw(hourly, field, "_gfs_seamless",  idx)

    if day_offset <= 3:
        weights = {"ecmwf": 0.75, "gfs": 0.25}
    else:
        weights = {"ecmwf": 0.60, "gfs": 0.40}

    vals  = {"ecmwf": ecmwf, "gfs": gfs}
    avail = {k: v for k, v in vals.items() if v is not None}
    if not avail:
        return 0.0, None

    total_w = sum(weights[k] for k in avail)
    blended = sum(weights[k] * v for k, v in avail.items()) / total_w
    return round(blended, 1), "Blend"

# ── COMPUTED STATE ────────────────────────────────────────────────────────────
bortle_class, sqm_val = calculate_accurate_bortle(st.session_state.lat, st.session_state.lon)
ra_val, dec_val = calculate_zenith_ra_dec(st.session_state.lat, st.session_state.lon)

ICT = timezone(timedelta(hours=7))   # Indochina Time (Vietnam, UTC+7)

# ── Night-start offset ─────────────────────────────────────────────────────────
# A "night" runs 18:00 → 06:00 next day.
# If current ICT time is 00:00–17:59 we are still inside last-night's second half
# (00:00–06:00 already passed, 18:00 tonight is the NEXT upcoming block).
# So: if hour < 18, "night 0" = today's evening (18:00 today → 06:00 tomorrow),
#     which means we base target_date on today's date.
# The past-data problem (18:00-23:59 gone after midnight): we fix it by
# skipping slots that are in the past when rendering the table.
_now_ict        = datetime.now(ICT)
# If 00:00~05:59 → we're still in the previous night (18:00 yesterday → 06:00 today)
# so shift base back 1 day to keep tonight's 00:00~06:00 slots visible
if _now_ict.hour < 6:
    _night_base_ict = _now_ict - timedelta(days=1)
else:
    _night_base_ict = _now_ict
# date_options i=0 → tonight (18:00 of _night_base_ict)
_wd_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
def _en_date(d, suffix):
    return f"{d.month}/{d.day} {suffix} ({_wd_names[d.weekday()]})"
date_options = [
    f"{_en_date(_night_base_ict+timedelta(days=i), 'eve')} → {_en_date(_night_base_ict+timedelta(days=i+1), 'morn')}"
    for i in range(7)
]

target_date = (_night_base_ict + timedelta(days=st.session_state.day_offset)).replace(tzinfo=None)
next_date   = target_date + timedelta(days=1)

moon_pct, moon_text = get_moon_phase_percent(target_date)

prefer_ecmwf = (st.session_state.weather_source != "US (GFS)")
use_blend  = (st.session_state.weather_source == "🔀 Blend (ECMWF+GFS)")
use_ecmwf  = (st.session_state.weather_source == "EU (ECMWF)")
hourly_data, _, _loc_utc_offset, _ep_label, _last_error = fetch_weather_7days(
    st.session_state.lat, st.session_state.lon, st.session_state.weather_source
)

# UTC offset của location hiện tại (tính bằng giây) — dùng cho moon altitude
loc_utc_offset_h = _loc_utc_offset / 3600.0  # đổi sang giờ, ví dụ ICT=+7

desired_slots = [
    (target_date.year, target_date.month, target_date.day, 18, "18:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 19, "19:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 20, "20:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 21, "21:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 22, "22:00", target_date.strftime("%Y-%m-%d")),
    (target_date.year, target_date.month, target_date.day, 23, "23:00", target_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 0,  "00:00", next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 1,  "01:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 2,  "02:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 3,  "03:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 4,  "04:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 5,  "05:00",    next_date.strftime("%Y-%m-%d")),
    (next_date.year, next_date.month, next_date.day, 6,  "06:00",    next_date.strftime("%Y-%m-%d")),
]

# Always show full night 18:00-06:00 regardless of current time
_full_night_slots = list(desired_slots)
# (past slots kept — table and graph always display 18:00→06:00)

@st.cache_data(ttl=3600, show_spinner=False)
def _build_night_data(lat, lon, slots, hourly_data_frozen, weather_source, loc_utc_offset_h):
    """Cache toàn bộ vòng lặp tính weather table + moon/sun/MW altitudes.
    Key cache = (lat, lon, slots, source) — chỉ recompute khi thực sự đổi ngày/địa điểm/source."""
    # hourly_data_frozen là tuple-of-items để hashable
    hourly = dict(hourly_data_frozen) if hourly_data_frozen else {}

    _prefer_ecmwf = weather_source not in ["US (GFS)", "EU (ECMWF)"]
    _use_blend  = weather_source == "🔀 Blend (ECMWF+GFS)"
    _use_ecmwf  = weather_source == "EU (ECMWF)"

    # day_offset chỉ ảnh hưởng blend weight — dùng slot index 0 làm proxy
    _day_offset_proxy = 0
    if slots:
        yr0, mo0, dy0 = slots[0][0], slots[0][1], slots[0][2]
        from datetime import date as _date
        _today = _date.today()
        _day_offset_proxy = (_date(yr0, mo0, dy0) - _today).days
        _day_offset_proxy = max(0, min(6, _day_offset_proxy))

    out_table  = []
    out_hours  = []
    out_moon   = []
    out_sun    = []
    out_mw     = []
    out_debug  = {"low": 0, "mid": 0, "high": 0, "total": 0}
    out_srcs   = set()

    times_list = hourly.get("time", [])

    for yr, mo, dy, hr_local, label, date_prefix in slots:
        out_hours.append(label)
        out_moon.append(calculate_exact_moon_altitude_ephem(lat, lon, yr, mo, dy, hr_local, loc_utc_offset_h))
        out_sun.append(calculate_exact_sun_altitude_ephem(lat, lon, yr, mo, dy, hr_local, loc_utc_offset_h))
        mw_alt, _ = calculate_milkyway_altitude(lat, lon, yr, mo, dy, hr_local, loc_utc_offset_h)
        out_mw.append(mw_alt)

        if not times_list:
            continue

        target_ts = f"{date_prefix}T{hr_local:02d}:00"
        idx = next((i for i, t in enumerate(times_list) if t.startswith(target_ts)), -1)
        if idx == -1:
            continue

        if _use_blend:
            avg_cloud, src1 = get_val_blended(hourly, "cloud_cover",          idx, _day_offset_proxy)
            low_c,     _    = get_val_blended(hourly, "cloud_cover_low",       idx, _day_offset_proxy)
            mid_c,     _    = get_val_blended(hourly, "cloud_cover_mid",       idx, _day_offset_proxy)
            high_c,    _    = get_val_blended(hourly, "cloud_cover_high",      idx, _day_offset_proxy)
            humid,     _    = get_val_blended(hourly, "relative_humidity_2m",  idx, _day_offset_proxy)
            wind_speed,_    = get_val_blended(hourly, "wind_speed_10m",        idx, _day_offset_proxy)
            temp_val,  _    = get_val_blended(hourly, "temperature_2m",        idx, _day_offset_proxy)
            precip_val,_    = get_val_blended(hourly, "precipitation",         idx, _day_offset_proxy)
            if src1: out_srcs.add(src1)
        elif _use_ecmwf:
            avg_cloud  = _get_raw(hourly, "cloud_cover",          "_ecmwf_ifs025", idx) or 0.0
            low_c      = _get_raw(hourly, "cloud_cover_low",       "_ecmwf_ifs025", idx) or 0.0
            mid_c      = _get_raw(hourly, "cloud_cover_mid",       "_ecmwf_ifs025", idx) or 0.0
            high_c     = _get_raw(hourly, "cloud_cover_high",      "_ecmwf_ifs025", idx) or 0.0
            humid      = _get_raw(hourly, "relative_humidity_2m",  "_ecmwf_ifs025", idx) or 0.0
            wind_speed = _get_raw(hourly, "wind_speed_10m",        "_ecmwf_ifs025", idx) or 0.0
            temp_val   = _get_raw(hourly, "temperature_2m",        "_ecmwf_ifs025", idx) or 0.0
            precip_val = _get_raw(hourly, "precipitation",         "_ecmwf_ifs025", idx) or 0.0
            src1 = "ECMWF"
            out_srcs.add("ECMWF")
        else:
            avg_cloud, src1 = get_val(hourly, "cloud_cover",          idx, _prefer_ecmwf)
            low_c,     _    = get_val(hourly, "cloud_cover_low",      idx, _prefer_ecmwf)
            mid_c,     _    = get_val(hourly, "cloud_cover_mid",      idx, _prefer_ecmwf)
            high_c,    _    = get_val(hourly, "cloud_cover_high",     idx, _prefer_ecmwf)
            humid,     _    = get_val(hourly, "relative_humidity_2m", idx, _prefer_ecmwf)
            wind_speed,_    = get_val(hourly, "wind_speed_10m",       idx, _prefer_ecmwf)
            temp_val,  _    = get_val(hourly, "temperature_2m",       idx, _prefer_ecmwf)
            precip_val,_    = get_val(hourly, "precipitation",        idx, _prefer_ecmwf)
            if src1: out_srcs.add(src1)

        if len(out_table) == 0:
            out_debug = {"low": int(low_c), "mid": int(mid_c), "high": int(high_c), "total": int(avg_cloud)}

        score = 100 - avg_cloud
        if score >= 92:   stars = "⭐⭐⭐⭐"
        elif score >= 75: stars = "⭐⭐⭐☆"
        elif score >= 50: stars = "⭐⭐☆☆"
        elif score >= 20: stars = "⭐☆☆☆"
        else:             stars = "☆☆☆☆"

        out_table.append({
            "⏰": label,
            "☁️": f"{int(avg_cloud)}%",
            "💧": f"{int(humid)}%",
            "💨": f"{round(wind_speed,1)}m/s",
            "📸": stars,
            "_temp": temp_val,
            "_precip": precip_val,
        })

    return out_table, out_hours, out_moon, out_sun, out_mw, out_debug, out_srcs

# Chuyển hourly_data sang dạng hashable để cache key hoạt động
_hourly_frozen = tuple(
    (k, tuple(v) if isinstance(v, list) else v)
    for k, v in (hourly_data.items() if hourly_data else [])
)

# ── PREFETCH TẤT CẢ 7 ĐÊM ngay sau khi có hourly_data ────────────────────────
# Mục đích: warm up cache cho toàn bộ 7 ngày ngay khi chọn location.
# Khi user bấm Next/Prev → _build_night_data đã có cache → gần như instant.
# Chạy tuần tự (không thread) vì @st.cache_data không thread-safe khi write.
def _make_slots_for_offset(base_ict, day_off):
    td = (base_ict + timedelta(days=day_off)).replace(tzinfo=None)
    nd = td + timedelta(days=1)
    return tuple([
        (td.year, td.month, td.day, 18, "18:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 19, "19:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 20, "20:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 21, "21:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 22, "22:00", td.strftime("%Y-%m-%d")),
        (td.year, td.month, td.day, 23, "23:00", td.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  0, "00:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  1, "01:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  2, "02:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  3, "03:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  4, "04:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  5, "05:00", nd.strftime("%Y-%m-%d")),
        (nd.year, nd.month, nd.day,  6, "06:00", nd.strftime("%Y-%m-%d")),
    ])

# Prefetch các ngày KHÁC: skip hoàn toàn ngay sau khi đổi location,
# lần rerun tiếp theo mới prefetch theo thứ tự ngày liền kề trước.
if st.session_state._skip_prefetch:
    st.session_state._skip_prefetch = False
else:
    _day_off = st.session_state.day_offset
    _prio = []
    if _day_off + 1 < 7: _prio.append(_day_off + 1)
    if _day_off - 1 >= 0: _prio.append(_day_off - 1)
    for _p in range(7):
        if _p not in _prio and _p != _day_off:
            _prio.append(_p)
    for _poff in _prio:
        try:
            _build_night_data(
                st.session_state.lat, st.session_state.lon,
                _make_slots_for_offset(_night_base_ict, _poff),
                _hourly_frozen,
                st.session_state.weather_source,
                loc_utc_offset_h,
            )
        except Exception:
            pass

(weather_table_data, hours_labels, moon_altitudes, sun_altitudes,
 milkyway_altitudes, current_cloud_debug, sources_used) = _build_night_data(
    st.session_state.lat, st.session_state.lon,
    tuple(desired_slots),
    _hourly_frozen,
    st.session_state.weather_source,
    loc_utc_offset_h,
)
sources_used = set(sources_used)  # trả về từ cache là frozenset hoặc set, đảm bảo là set

# Label thực tế đã dùng — phân biệt auto-fallback với user chọn tay
if use_blend:
    active_source_label = "🔀 Blend (ECMWF+GFS)"
elif "ECMWF" in sources_used:
    active_source_label = "EU (ECMWF IFS025)"
elif "GFS" in sources_used:
    active_source_label = "US (GFS)"
else:
    active_source_label = st.session_state.weather_source

# ── NIGHT VERDICT (full night 18:00~06:00) ───────────────────────────────────
def _build_night_verdict(table_data, sun_alts=None, moon_illum=None):
    """Tính đánh giá tổng hợp cho cả đêm 18:00~06:00, dựa chủ yếu trên Cloud %
    (và precip/temp để phân biệt mưa/tuyết) — giống Clear Outside / Astrospheric
    nhưng đơn giản, dễ hiểu: PERFECT NIGHT / GOOD STARRY NIGHT / FAIR SKIES /
    PATCHY CLEAR / PARTLY CLOUDY / CLOUDY NIGHT / RAINY NIGHT / SNOWY NIGHT / TOO BRIGHT.

    'Giờ tốt' = slot trời đã tối thiên văn (sun_alt ≤ -12°) và cloud ≤ 25%.

    Trả về dict với tier, icon, stars, sub, màu sắc, v.v."""
    if not table_data:
        return None
    # 13 slots = 18:00..23:00 + 00:00..06:00, nhưng "đêm" chỉ tính 12 giờ (18:00→06:00).
    # Slot 06:00 cuối chỉ là điểm mốc kết thúc (đã là sáng), không tính vào giờ clear.
    if len(table_data) > 12:
        table_data = table_data[:-1]
        if sun_alts is not None:
            sun_alts = sun_alts[:-1]
    if sun_alts is None:
        sun_alts = [-90] * len(table_data)

    total = 0
    rain_hours = 0
    snow_hours = 0
    cloud_vals = []
    # streak[i] = True nếu slot i là "giờ tốt" (trong khung tối thiên văn)
    good_flags = []
    for r, sa in zip(table_data, sun_alts):
        # Chỉ tính các slot trời đã tối thiên văn thực sự (sun_alt ≤ -12°)
        if sa is not None and sa > -12:
            continue
        total += 1
        cloud_str = r.get("☁️", "100%")
        precip    = r.get("_precip", 0.0) or 0.0
        temp_val  = r.get("_temp")
        cloud_pct = int(cloud_str.replace("%","")) if cloud_str.replace("%","").isdigit() else 100
        cloud_vals.append(cloud_pct)

        if precip >= 0.3:
            if temp_val is not None and temp_val < 2.0:
                snow_hours += 1
            else:
                rain_hours += 1

        is_good = (precip < 0.3) and (cloud_pct <= 25)
        good_flags.append(is_good)

    # ── Không có khung giờ tối thiên văn (đêm hè, trời sáng suốt) ──────────────
    if total == 0:
        return {"tier": "TOO BRIGHT", "icon": "🌃", "stars": "✕",
                "sub": "no astro-dark",
                "color": "#94a3b8", "border": "rgba(148,163,184,0.55)",
                "bg": "rgba(10,14,22,0.88)", "anim": "blink-warn",
                "good_hours": 0, "total": 0}

    # ── Tìm cửa sổ liên tiếp dài nhất có điều kiện tốt (longest good streak) ──
    best_streak = 0
    cur_streak = 0
    for g in good_flags:
        if g:
            cur_streak += 1
            best_streak = max(best_streak, cur_streak)
        else:
            cur_streak = 0
    good_hours = sum(good_flags)  # tổng giờ tốt (rời rạc), dùng cho sub-label
    avg_cloud = round(sum(cloud_vals) / len(cloud_vals)) if cloud_vals else 100

    # ── Trăng sáng? (ảnh hưởng đến chụp Milky Way / DSO mờ) ────────────────────
    bright_moon = (moon_illum is not None) and (moon_illum >= 50)

    # ── Smart Labeling: ưu tiên Cloud % trung bình của cả đêm, dễ hiểu ─────────
    if snow_hours >= int(total * 0.3):
        tier = "SNOWY NIGHT"
        icon = "❄️"; stars = "✕"
        color = "#bae6fd"; border = "rgba(186,230,253,0.70)"
        bg    = "rgba(8,18,30,0.88)"; anim = "blink-warn"
        sub   = f"{snow_hours}h snow"
    elif rain_hours >= int(total * 0.3):
        tier = "RAINY NIGHT"
        icon = "🌧️"; stars = "✕"
        color = "#fca5a5"; border = "rgba(239,68,68,0.70)"
        bg    = "rgba(30,8,8,0.88)"; anim = "blink-warn"
        sub   = f"{rain_hours}h rain"
    elif best_streak >= 5 and not bright_moon:
        tier = "PERFECT NIGHT"
        icon = "🌌"; stars = "★★★★"
        color = "#6ee7b7"; border = "rgba(52,211,153,0.75)"
        bg    = "rgba(5,25,18,0.88)"; anim = "blink-smile"
        sub   = f"avg cloud {avg_cloud}%, {best_streak}h clear"
    elif best_streak >= 3 and bright_moon:
        tier = "GOOD STARRY NIGHT"
        icon = "🔭"; stars = "★★★"
        color = "#93c5fd"; border = "rgba(96,165,250,0.70)"
        bg    = "rgba(6,16,30,0.88)"; anim = "blink-smile"
        sub   = f"avg cloud {avg_cloud}%, bright moon"
    elif best_streak >= 1:
        tier = "FAIR SKIES"
        icon = "🌤️"; stars = "★★"
        color = "#fde68a"; border = "rgba(251,191,36,0.65)"
        bg    = "rgba(20,16,4,0.88)"; anim = "blink-neutral"
        sub   = f"avg cloud {avg_cloud}%, {best_streak}h window"
    elif avg_cloud <= 40:
        tier = "PATCHY CLEAR"
        icon = "🌥️"; stars = "★"
        color = "#fef08a"; border = "rgba(250,204,21,0.55)"
        bg    = "rgba(20,16,4,0.88)"; anim = "blink-neutral"
        sub   = f"avg cloud {avg_cloud}%, no long window"
    elif avg_cloud <= 70:
        tier = "PARTLY CLOUDY"
        icon = "🌥️"; stars = "★"
        color = "#fdba74"; border = "rgba(251,146,60,0.55)"
        bg    = "rgba(20,12,4,0.88)"; anim = "blink-neutral"
        sub   = f"avg cloud {avg_cloud}%"
    else:
        tier = "CLOUDY NIGHT"
        icon = "☁️"; stars = "✕"
        color = "#94a3b8"; border = "rgba(148,163,184,0.55)"
        bg    = "rgba(10,14,22,0.88)"; anim = "blink-warn"
        sub   = f"avg cloud {avg_cloud}%"

    return {"tier": tier, "icon": icon, "stars": stars, "sub": sub,
            "color": color, "border": border, "bg": bg, "anim": anim,
            "good_hours": good_hours, "best_streak": best_streak, "total": total}

# ── Tier → short natural-language weather label (cho fallback "no result") ──
# Dùng tier THỰC TẾ phổ biến nhất trong các verdict đã quét (không phải icon cố định).
_TIER_SHORT_LABEL = {
    "SNOWY NIGHT":      "snow",
    "RAINY NIGHT":      "rain",
    "CLOUDY NIGHT":     "cloud",
    "PARTLY CLOUDY":    "cloud & some clear",
    "PATCHY CLEAR":     "patchy cloud",
    "FAIR SKIES":       "mostly clear",
    "TOO BRIGHT":       "bright sky (no astro-dark)",
}

def _summarize_fallback_tiers(tier_counter):
    """Nhận Counter({tier_name: count}) từ các verdict đã quét (không đạt PERFECT/GOOD),
    trả về label ngắn dựa trên tier PHỔ BIẾN NHẤT thực tế, ví dụ 'cloud & rain'.
    Nếu 2 tier đứng đầu có số lượng gần bằng nhau (>=40% mỗi loại), nối bằng '&'."""
    if not tier_counter:
        return "unsettled weather"
    ranked = tier_counter.most_common(3)
    total_n = sum(tier_counter.values())
    parts = []
    for tier_name, cnt in ranked:
        if cnt / total_n >= 0.30 and tier_name in _TIER_SHORT_LABEL:
            parts.append(_TIER_SHORT_LABEL[tier_name])
        if len(parts) == 2:
            break
    if not parts:
        top_tier = ranked[0][0]
        parts = [_TIER_SHORT_LABEL.get(top_tier, "unsettled weather")]
    # Khử trùng lặp giữ thứ tự
    seen = set(); uniq = []
    for p in parts:
        if p not in seen:
            seen.add(p); uniq.append(p)
    return " & ".join(uniq)


# ── GREAT NIGHT SCAN — quét 30 địa điểm yêu thích × 7 ngày tới ───────────────
# Điều kiện thông báo (AND):
#   1) Moon illumination < 32%
#   2) Có ít nhất 1/30 địa điểm đầu (sao xanh) đạt tier == "PERFECT NIGHT"
#   3) Chỉ báo NGÀY SỚM NHẤT thoả mãn (1-7 ngày tới)
_FAV_30  = [(n,c) for n,c in LOCATION_DATABASE.items()
            if (lambda nm: nm.split(".")[0].strip().isdigit()
                and int(nm.split(".")[0].strip()) <= 30)(n)]
_FAV_50  = [(n,c) for n,c in LOCATION_DATABASE.items()
            if (lambda nm: nm.split(".")[0].strip().isdigit()
                and int(nm.split(".")[0].strip()) <= 50)(n)]
_FAV_ALL = list(LOCATION_DATABASE.items())

# ── REGION REGISTRY — Việt Nam chia theo 3 miền địa lý (Bắc/Trung/Nam) + "vietnam" (toàn quốc) ──
# Mỗi vùng áp dụng đồng nhất cho cả 3 loại lệnh: <region> (scan) / best <region> / tonight <region>
_REGIONS = {
    "bac":   {"Ha Giang", "Cao Bang", "Lang Son", "Lao Cai", "Yen Bai", "Bac Kan", "Bac Giang",
              "Phu Tho", "Vinh Phuc", "Hanoi", "Hoa Binh", "Son La", "Quang Ninh",
              "Nam Dinh", "Ninh Binh"},
    "trung": {"Thanh Hoa", "Nghe An", "Quang Binh", "Quang Tri", "Thua Thien Hue", "Da Nang",
              "Quang Nam", "Quang Ngai", "Binh Dinh", "Phu Yen", "Khanh Hoa", "Ninh Thuan",
              "Binh Thuan", "Kon Tum", "Gia Lai", "Dak Lak", "Dak Nong", "Lam Dong"},
    "nam":   {"Ho Chi Minh City", "Dong Nai", "Ba Ria - Vung Tau", "Tay Ninh", "Long An",
              "Dong Thap", "Kien Giang", "Ca Mau"},
}
_REGION_ORDER = ["bac", "trung", "nam"]
_REGION_LABELS = {
    "bac": "Mien Bac (North)", "trung": "Mien Trung (Central)", "nam": "Mien Nam (South)",
    "vietnam": "All Vietnam",
}
# ── Region representative city center (lat, lon, zoom) — dùng để fly map khi scan ──
_REGION_MAP_CENTER = {
    "bac":     (21.0285, 105.8542, 7),   # Hanoi
    "trung":   (16.0544, 108.2022, 7),   # Da Nang
    "nam":     (10.7769, 106.7009, 7),   # Ho Chi Minh City
    "vietnam": (16.0000, 106.5000, 6),   # Vietnam center
}
# ── Region representative city display name ────────────────────────────────────
_REGION_CITY_NAME = {
    "bac":     "Hanoi",
    "trung":   "Da Nang",
    "nam":     "Ho Chi Minh City",
    "vietnam": "Vietnam",
}

_FAV_RAW_BY_REGION = {
    rk: [(n, c) for n, c in LOCATION_DATABASE.items()
         if n.rsplit(",", 1)[-1].strip() in prefs]
    for rk, prefs in _REGIONS.items()
}

def _haversine_km(lat1, lon1, lat2, lon2):
    """Khoảng cách Haversine giữa 2 điểm (km)."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Bỏ địa điểm gần nhau <km để tăng tốc scan/best/tonight
def _dedupe_locs_km(locs, km=30):
    kept = []
    for name, coords in locs:
        too_close = any(
            _haversine_km(coords[0], coords[1], kc[0], kc[1]) < km
            for _, kc in kept
        )
        if not too_close:
            kept.append((name, coords))
    return kept

# Mỗi vùng: bản dedupe <60km dùng cho best/tonight, <30km dùng cho scan thường (region-only).
# "vietnam" = toàn bộ 100 địa điểm (_FAV_ALL), dedupe tương tự các vùng khác.
_FAV_BY_REGION_60 = {rk: _dedupe_locs_km(locs, km=60) for rk, locs in _FAV_RAW_BY_REGION.items()}
_FAV_BY_REGION_30 = {rk: _dedupe_locs_km(locs, km=30) for rk, locs in _FAV_RAW_BY_REGION.items()}
_FAV_BY_REGION_60["vietnam"] = _dedupe_locs_km(_FAV_ALL, km=60)
_FAV_BY_REGION_30["vietnam"] = _dedupe_locs_km(_FAV_ALL, km=30)

def _locs_for_region(region_key, for_best_or_tonight):
    """Trả về danh sách địa điểm cho 1 vùng. region_key in _REGION_ORDER + 'vietnam'.
    for_best_or_tonight=True → dedupe 60km, False (scan thường) → dedupe 30km."""
    table = _FAV_BY_REGION_60 if for_best_or_tonight else _FAV_BY_REGION_30
    return table.get(region_key, table["bac"])

def _run_great_night_scan(start_day=0, region="bac"):
    """Quét từ start_day (0-6) trong 7 ngày tới, cho 1 vùng địa lý (region key, hoặc 'vietnam' = toàn quốc).
    - all_locs: danh sách TẤT CẢ địa điểm PERFECT NIGHT trong ngày sớm nhất thoả (sau khi lọc <20km)
    - loc_name / loc_coords: địa điểm đầu tiên (để hiển thị banner chính)
    Trả về None nếu không có ngày nào thoả (kèm "_fallback_tiers": Counter tier thực tế đã quét,
    để hiển thị fallback "cloud & rain in (region) next 7 days" dựa trên dữ liệu thật)."""
    _fallback_tiers = Counter()
    for day_off in range(start_day, 7):
        d = (_night_base_ict + timedelta(days=day_off)).replace(tzinfo=None)
        moon_illum, _ = get_moon_phase_percent(d)
        if moon_illum >= 32:
            continue
        slots = _make_slots_for_offset(_night_base_ict, day_off)
        _locs_to_scan = _locs_for_region(region, for_best_or_tonight=False)
        perfect_locs = []  # (loc_name, loc_coords, verdict) tất cả địa điểm pass
        for loc_name, loc_coords in _locs_to_scan:
            lat, lon = loc_coords
            try:
                hourly, _, utc_off, _, _ = fetch_weather_7days(lat, lon, st.session_state.weather_source)
            except Exception:
                continue
            if not hourly:
                continue
            frozen = tuple(
                (k, tuple(v) if isinstance(v, list) else v)
                for k, v in hourly.items()
            )
            try:
                table, _, _, sun_alts, *_r = _build_night_data(
                    lat, lon, slots, frozen, st.session_state.weather_source, utc_off / 3600.0
                )
            except Exception:
                continue
            verdict = _build_night_verdict(table, sun_alts, moon_illum)
            if verdict:
                _fallback_tiers[verdict["tier"]] += 1
            if verdict and verdict["tier"] == "PERFECT NIGHT":
                perfect_locs.append((loc_name, loc_coords, verdict))

        if not perfect_locs:
            continue

        # ── Lọc bỏ các địa điểm gần nhau < 20km (giữ lại địa điểm đầu tiên) ──
        deduped = []
        for entry in perfect_locs:
            _, coords, _ = entry
            too_close = False
            for kept in deduped:
                _, kept_coords, _ = kept
                if _haversine_km(coords[0], coords[1], kept_coords[0], kept_coords[1]) < 20:
                    too_close = True
                    break
            if not too_close:
                deduped.append(entry)

        first_name, first_coords, first_verdict = deduped[0]
        return {
            "date": d, "day_off": day_off,
            "loc_name": first_name, "loc_coords": first_coords,
            "moon_illum": moon_illum, "verdict": first_verdict,
            "all_locs": deduped,  # [(loc_name, loc_coords, verdict), ...]
            "region": region,
        }
    return {"_fallback": True, "_fallback_label": _summarize_fallback_tiers(_fallback_tiers)} if _fallback_tiers else None

# ── BEST NIGHT SCAN — quét toàn bộ 7 ngày × N địa điểm, chọn top 3 tốt nhất ────────
# Tiêu chí: moon<35%, tier=PERFECT NIGHT(4★) > GOOD STARRY NIGHT(3★), streak dài nhất.
# Ưu tiên cuối tuần (Fri=4, Sat=5, Sun=6). Weekday (Mon-Thu) hiển thị màu trắng.
_WEEKEND_DAYS = {4, 5, 6}  # weekday(): Mon=0..Sun=6; Fri=4, Sat=5, Sun=6

def _run_best_scan(region="bac"):
    """Quét 7 ngày tới cho 1 vùng địa lý (region key, hoặc 'vietnam' = toàn quốc), trả về top 3 (dedupe <60km).
    - Ưu tiên cuối tuần (Fri/Sat/Sun) trước Mon-Thu.
    - Trong cùng tier + streak: ưu tiên cuối tuần, rồi streak dài hơn.
    - Trả về None nếu không có kết quả nào."""
    _TIER_RANK = {"PERFECT NIGHT": 2, "GOOD STARRY NIGHT": 1}
    _locs = _locs_for_region(region, for_best_or_tonight=True)
    # candidates: list of (tier_rank, is_weekend, streak, good_hours, date, day_off, loc_name, loc_coords, verdict, moon_illum)
    candidates = []
    _fallback_tiers = Counter()
    for day_off in range(0, 7):
        d = (_night_base_ict + timedelta(days=day_off)).replace(tzinfo=None)
        moon_illum, _ = get_moon_phase_percent(d)
        if moon_illum >= 41.5:
            continue
        is_weekend = d.weekday() in _WEEKEND_DAYS
        slots = _make_slots_for_offset(_night_base_ict, day_off)
        for loc_name, loc_coords in _locs:
            lat, lon = loc_coords
            try:
                hourly, _, utc_off, _, _ = fetch_weather_7days(lat, lon, st.session_state.weather_source)
            except Exception:
                continue
            if not hourly:
                continue
            frozen = tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in hourly.items())
            try:
                table, _, _, sun_alts, *_ = _build_night_data(
                    lat, lon, slots, frozen, st.session_state.weather_source, utc_off / 3600.0)
            except Exception:
                continue
            verdict = _build_night_verdict(table, sun_alts, moon_illum)
            if not verdict:
                continue
            _fallback_tiers[verdict["tier"]] += 1
            rank = _TIER_RANK.get(verdict["tier"], 0)
            if rank == 0:
                continue
            streak = verdict.get("best_streak", 0)
            good_hours = verdict.get("good_hours", 0)
            candidates.append((rank, int(is_weekend), streak, good_hours, d, day_off, loc_name, loc_coords, verdict, moon_illum))

    if not candidates:
        return {"_fallback": True, "_fallback_label": _summarize_fallback_tiers(_fallback_tiers)} if _fallback_tiers else None

    # Sort: tier_rank DESC, is_weekend DESC, streak DESC, good_hours DESC
    candidates.sort(key=lambda x: (x[0], x[1], x[2], x[3]), reverse=True)

    # Pick top 3, dedupe by location <60km
    # Guarantee: at least 1 weekend (Fri/Sat/Sun) slot in top3 if any exists.
    # Strategy: first fill normally from sorted list, then if no weekend found,
    # swap the worst non-weekend slot for the best available weekend candidate.
    top3 = []
    seen_coords = []
    for cand in candidates:
        _, _, _, _, d, day_off, loc_name, loc_coords, verdict, moon_illum = cand
        # Dedupe location: skip nếu trong vòng 60km với địa điểm đã chọn
        too_close = any(
            _haversine_km(loc_coords[0], loc_coords[1], sc[0], sc[1]) < 60
            for sc in seen_coords
        )
        if too_close:
            continue
        seen_coords.append(loc_coords)
        top3.append((d, day_off, loc_name, loc_coords, verdict, moon_illum))
        if len(top3) == 3:
            break

    # Guarantee at least 1 weekend in top3
    if top3:
        _has_weekend_in_top3 = any(d.weekday() in _WEEKEND_DAYS for d, *_ in top3)
        if not _has_weekend_in_top3:
            # Find best weekend candidate NOT already in top3 (dedupe <60km vs existing)
            _seen_top3_coords = [lc for _, _, _, lc, _, _ in top3]
            for cand in candidates:
                _, _is_we, _, _, d_we, do_we, ln_we, lc_we, vd_we, mi_we = cand
                if not _is_we:
                    continue
                too_close = any(
                    _haversine_km(lc_we[0], lc_we[1], sc[0], sc[1]) < 60
                    for sc in _seen_top3_coords
                )
                if too_close:
                    continue
                # Swap out the last (worst) slot in top3 for this weekend entry
                top3[-1] = (d_we, do_we, ln_we, lc_we, vd_we, mi_we)
                break

    if not top3:
        return {"_fallback": True, "_fallback_label": _summarize_fallback_tiers(_fallback_tiers)} if _fallback_tiers else None

    # Xác định is_weekend cho từng kết quả
    top3_with_weekend = []
    for (d, day_off, loc_name, loc_coords, verdict, moon_illum) in top3:
        is_weekend = d.weekday() in _WEEKEND_DAYS
        top3_with_weekend.append((d, day_off, loc_name, loc_coords, verdict, moon_illum, is_weekend))

    # Primary result = top3[0]
    d0, day_off0, loc_name0, loc_coords0, verdict0, moon_illum0, _ = top3_with_weekend[0]
    return {
        "date": d0, "day_off": day_off0,
        "loc_name": loc_name0, "loc_coords": loc_coords0,
        "moon_illum": moon_illum0, "verdict": verdict0,
        "all_locs": [(loc_name0, loc_coords0, verdict0)],  # vòng tròn map chỉ cho loc chính
        "top3": top3_with_weekend,  # [(date, day_off, loc_name, loc_coords, verdict, moon_illum, is_weekend)]
        "region": region,
    }

# ── TONIGHT SCAN — quét đêm nay (day_off=0) cho Kanto hoặc toàn quốc ────────
def _run_tonight_scan(region="bac"):
    """Quét đêm nay (day_off=0) và trả về top3 địa điểm tốt nhất màu pink, cho 1 vùng địa lý.
    region='vietnam' → 100 địa điểm toàn quốc, khác → vùng tương ứng (dedupe <60km).
    - Không yêu cầu moon < 35% (tonight hiển thị kết quả dù trăng sáng).
    - Tiêu chí: tier PERFECT NIGHT > GOOD STARRY NIGHT, streak dài nhất.
    Trả về None nếu không có kết quả nào."""
    _TIER_RANK = {"PERFECT NIGHT": 2, "GOOD STARRY NIGHT": 1}
    _locs = _locs_for_region(region, for_best_or_tonight=True)
    day_off = 0
    d = (_night_base_ict + timedelta(days=day_off)).replace(tzinfo=None)
    moon_illum, _ = get_moon_phase_percent(d)
    slots = _make_slots_for_offset(_night_base_ict, day_off)
    candidates = []
    _fallback_tiers = Counter()
    for loc_name, loc_coords in _locs:
        lat, lon = loc_coords
        try:
            hourly, _, utc_off, _, _ = fetch_weather_7days(lat, lon, st.session_state.weather_source)
        except Exception:
            continue
        if not hourly:
            continue
        frozen = tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in hourly.items())
        try:
            table, _, _, sun_alts, *_ = _build_night_data(
                lat, lon, slots, frozen, st.session_state.weather_source, utc_off / 3600.0)
        except Exception:
            continue
        verdict = _build_night_verdict(table, sun_alts, moon_illum)
        if not verdict:
            continue
        _fallback_tiers[verdict["tier"]] += 1
        rank = _TIER_RANK.get(verdict["tier"], 0)
        if rank == 0:
            continue
        streak = verdict.get("best_streak", 0)
        good_hours = verdict.get("good_hours", 0)
        candidates.append((rank, streak, good_hours, loc_name, loc_coords, verdict, moon_illum))

    if not candidates:
        return {"_fallback": True, "_fallback_label": _summarize_fallback_tiers(_fallback_tiers)} if _fallback_tiers else None

    candidates.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)

    # Pick top 3, dedupe by location <60km
    top3 = []
    seen_coords = []
    for cand in candidates:
        rank, streak, good_hours, loc_name, loc_coords, verdict, moon_illum = cand
        too_close = any(
            _haversine_km(loc_coords[0], loc_coords[1], sc[0], sc[1]) < 60
            for sc in seen_coords
        )
        if too_close:
            continue
        seen_coords.append(loc_coords)
        top3.append((d, day_off, loc_name, loc_coords, verdict, moon_illum, False))
        if len(top3) == 3:
            break

    if not top3:
        return {"_fallback": True, "_fallback_label": _summarize_fallback_tiers(_fallback_tiers)} if _fallback_tiers else None

    d0, day_off0, loc_name0, loc_coords0, verdict0, moon_illum0, _ = top3[0]
    return {
        "date": d0, "day_off": day_off0,
        "loc_name": loc_name0, "loc_coords": loc_coords0,
        "moon_illum": moon_illum0, "verdict": verdict0,
        "all_locs": [(loc_name0, loc_coords0, verdict0)],
        "top3": top3,
        "_is_tonight": True,
        "region": region,
    }
# ------------------------------------------------------------------------------
# KHỐI B — AI TOOLS: bọc lại các hàm scan/bortle đã có sẵn thành "tool" cho
# Gemini. Nguyên tắc: KHÔNG viết lại logic thời tiết/bortle/moon — chỉ convert
# output (datetime, tuple, dict UI-only) thành dict JSON gọn, dễ đọc cho AI.
# DÁN THAY THẾ TOÀN BỘ KHỐI B CŨ (sau khi _run_tonight_scan kết thúc, trước
# "# ── MKW SCAN...").
# ------------------------------------------------------------------------------

def _serialize_scan_result(result):
    """Chuẩn hoá output của _run_best_scan / _run_tonight_scan thành dict JSON-safe,
    bỏ các field chỉ dùng cho UI (color/border/bg/anim)."""
    if result is None:
        return {"found": False, "reason": "Không có dữ liệu — có thể do lỗi tải thời tiết."}
    if result.get("_fallback"):
        return {
            "found": False,
            "reason": f"Không có đêm nào đủ đẹp trong khoảng quét. "
                      f"Điều kiện phổ biến nhất: {result.get('_fallback_label', 'không rõ')}.",
        }

    def _one(d, day_off, loc_name, loc_coords, verdict, moon_illum, is_weekend=None):
        return {
            "date": d.strftime("%Y-%m-%d (%a)") if hasattr(d, "strftime") else str(d),
            "days_from_today": day_off,
            "location_name": loc_name,
            "lat": loc_coords[0],
            "lon": loc_coords[1],
            "sky_tier": verdict.get("tier"),          # PERFECT NIGHT / GOOD STARRY NIGHT / ...
            "stars": verdict.get("stars"),
            "detail": verdict.get("sub"),              # vd "avg cloud 12%, 6h clear"
            "clear_hours": verdict.get("good_hours"),
            "moon_illumination_pct": round(moon_illum, 1) if moon_illum is not None else None,
            "is_weekend": bool(is_weekend) if is_weekend is not None else None,
        }

    top3 = result.get("top3", [])
    is_weekend_best = top3[0][6] if top3 and len(top3[0]) > 6 else None
    best = _one(result["date"], result["day_off"], result["loc_name"], result["loc_coords"],
                result["verdict"], result["moon_illum"], is_weekend_best)

    alternatives = []
    for row in top3[1:3]:
        d, day_off, loc_name, loc_coords, verdict, moon_illum, is_weekend = row
        alternatives.append(_one(d, day_off, loc_name, loc_coords, verdict, moon_illum, is_weekend))

    return {"found": True, "best": best, "alternatives": alternatives}


def tool_scan_best_weekend(region: str = "bac") -> dict:
    """Tìm địa điểm và ngày chụp ảnh sao TỐT NHẤT trong 7 ngày tới, ưu tiên cuối tuần
    (Thứ 6/7/Chủ Nhật). Dùng khi user hỏi mơ hồ về thời gian: 'cuối tuần này',
    'tuần này', 'vài ngày tới', hoặc không nói rõ đêm nào.

    Args:
        region: vùng địa lý Việt Nam cần quét. Phải là một trong:
            'bac', 'trung', 'nam', 'vietnam' (vietnam = toàn quốc, chậm hơn).
            Mặc định 'bac' nếu user không nói rõ vùng nào.

    Returns:
        dict: {"found": true, "best": {...}, "alternatives": [...]}
        hoặc {"found": false, "reason": "..."} nếu không có đêm nào đủ đẹp.
    """
    return _serialize_scan_result(_run_best_scan(region=region))


def tool_scan_tonight(region: str = "bac") -> dict:
    """Kiểm tra điều kiện chụp ảnh sao ĐÊM NAY (chỉ đêm nay, không phải ngày khác)
    cho 1 vùng địa lý. Dùng khi user hỏi cụ thể 'tối nay', 'đêm nay'.

    Args:
        region: vùng địa lý, cùng danh sách như tool_scan_best_weekend. Mặc định 'bac'.

    Returns:
        dict cùng cấu trúc như tool_scan_best_weekend, nhưng chỉ xét đêm nay.
    """
    return _serialize_scan_result(_run_tonight_scan(region=region))


def tool_check_location_darkness(location_name: str) -> dict:
    """Tra cứu độ tối bầu trời (thang Bortle 1-9, 1 = tối nhất/đẹp nhất) của MỘT
    địa điểm cụ thể đã có trong database, theo tên hoặc từ khoá gần đúng.
    CHỈ dùng khi user hỏi về 1 địa điểm cụ thể đã biết tên VÀ chỉ hỏi về mức
    ô nhiễm ánh sáng — KHÔNG dùng cho câu hỏi liên quan thời tiết đêm nay (dùng
    tool_check_location_tonight cho việc đó), cũng KHÔNG dùng để tìm địa điểm mới.

    Args:
        location_name: tên hoặc từ khoá gần đúng, ví dụ 'Jogashima', 'Kamikochi'.

    Returns:
        dict: {"found": true, "matched_name", "lat", "lon", "bortle_class", "sqm"}
        hoặc {"found": false, "reason": "..."} nếu không khớp địa điểm nào.
    """
    needle = location_name.strip().lower()
    match = next(((n, c) for n, c in LOCATION_DATABASE.items() if needle in n.lower()), None)
    if not match:
        return {"found": False, "reason": f"Không tìm thấy địa điểm khớp '{location_name}' trong database."}
    name, (lat, lon) = match
    bortle, sqm = calculate_accurate_bortle(lat, lon)
    return {"found": True, "matched_name": name, "lat": lat, "lon": lon,
            "bortle_class": bortle, "sqm": sqm}


def _infer_region_from_loc_name(loc_name: str) -> str:
    """Suy ra region key (bac, trung, nam) từ tên địa điểm, dựa theo tỉnh
    (phần sau dấu phẩy cuối cùng trong tên, vd '..., Phu Tho' -> bac)."""
    pref = loc_name.rsplit(",", 1)[-1].strip()
    for rk, prefs in _REGIONS.items():
        if pref in prefs:
            return rk
    return "bac"  # fallback an toàn nếu không khớp tỉnh nào


def _night_verdict_for_single_loc(lat, lon, day_off=0):
    """Tính verdict thời tiết đêm cho 1 toạ độ cụ thể (không quét cả vùng).
    day_off=0 -> tối nay. Trả về None nếu lỗi tải thời tiết."""
    d = (_night_base_ict + timedelta(days=day_off)).replace(tzinfo=None)
    moon_illum, _ = get_moon_phase_percent(d)
    slots = _make_slots_for_offset(_night_base_ict, day_off)
    try:
        hourly, _, utc_off, _, _ = fetch_weather_7days(lat, lon, st.session_state.weather_source)
    except Exception:
        return None
    if not hourly:
        return None
    frozen = tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in hourly.items())
    try:
        table, _, _, sun_alts, *_ = _build_night_data(
            lat, lon, slots, frozen, st.session_state.weather_source, utc_off / 3600.0)
    except Exception:
        return None
    verdict = _build_night_verdict(table, sun_alts, moon_illum)
    if not verdict:
        return None
    return {"verdict": verdict, "moon_illum": moon_illum}


def tool_check_location_tonight(location_name: str) -> dict:
    """Kiểm tra điều kiện chụp ảnh sao ĐÊM NAY tại MỘT địa điểm cụ thể theo tên
    (không phải quét cả vùng). Dùng khi user hỏi về 1 địa điểm cụ thể cho tối nay,
    ví dụ 'Jogashima tối nay thế nào', 'Kamikochi có sao không'.

    QUAN TRỌNG: nếu kết quả trả về is_good=false (thời tiết/mây không tốt tại
    địa điểm này), hãy GỌI THÊM tool_scan_tonight với region=giá trị "region"
    trong kết quả này, để tìm địa điểm thay thế tốt hơn trong cùng khu vực,
    rồi đề xuất tên các địa điểm đó cho user thay vì chỉ báo "không tốt".

    Args:
        location_name: tên hoặc từ khoá gần đúng của địa điểm, vd 'Jogashima'.

    Returns:
        dict: {"found": true, "matched_name", "lat", "lon", "region",
               "sky_tier", "stars", "detail", "clear_hours",
               "moon_illumination_pct", "is_good": bool}
        hoặc {"found": false, "reason": "..."} nếu không khớp địa điểm/lỗi thời tiết.
    """
    needle = location_name.strip().lower()
    match = next(((n, c) for n, c in LOCATION_DATABASE.items() if needle in n.lower()), None)
    if not match:
        return {"found": False, "reason": f"Không tìm thấy địa điểm khớp '{location_name}' trong database."}
    name, (lat, lon) = match
    region = _infer_region_from_loc_name(name)
    result = _night_verdict_for_single_loc(lat, lon, day_off=0)
    if not result:
        return {"found": False, "reason": f"Không lấy được dữ liệu thời tiết cho {name}."}
    verdict = result["verdict"]
    tier_rank = {"PERFECT NIGHT": 2, "GOOD STARRY NIGHT": 1}.get(verdict["tier"], 0)
    return {
        "found": True,
        "matched_name": name,
        "lat": lat, "lon": lon,
        "region": region,
        "sky_tier": verdict.get("tier"),
        "stars": verdict.get("stars"),
        "detail": verdict.get("sub"),
        "clear_hours": verdict.get("good_hours"),
        "moon_illumination_pct": round(result["moon_illum"], 1) if result["moon_illum"] is not None else None,
        "is_good": tier_rank >= 1,
    }


def ask_astro_ai(user_question: str):
    """Gửi câu hỏi tới Gemini KÈM LỊCH SỬ hội thoại (st.session_state.astro_ai_history)
    để AI nhớ ngữ cảnh câu trước (vd hỏi tiếp 'thế cuối tuần thì sao' sau khi đã hỏi
    về Hokkaido). Lịch sử chỉ lưu text câu hỏi + câu trả lời cuối, không lưu các
    bước gọi tool trung gian (để tránh phình payload không cần thiết).

    Trả về tuple (answer_text: str, fly_to: dict|None).
    """
    now_ict = datetime.now(timezone(timedelta(hours=7)))
    system_prompt = (
        f"Hôm nay là {now_ict.strftime('%A, %Y-%m-%d')} (giờ Việt Nam, ICT). "
        "Bạn là trợ lý tư vấn địa điểm/thời điểm chụp ảnh thiên văn (sao, Milky Way) "
        "ở Việt Nam, gắn liền với 1 bản đồ Bortle + dự báo thời tiết đã có sẵn. Đây "
        "là 1 cuộc hội thoại nhiều lượt — nếu câu hỏi hiện tại thiếu chi tiết (vd "
        "'thế cuối tuần thì sao' không nói lại vùng/địa điểm), hãy DÙNG LẠI vùng/địa "
        "điểm đã nhắc ở các lượt hỏi trước trong hội thoại này.\n\n"
        "QUY TẮC CHỌN TOOL:\n"
        "- Nếu user hỏi về 1 địa điểm CỤ THỂ cho tối nay (vd 'Mu Cang Chai tối nay thế "
        "nào') -> gọi tool_check_location_tonight trước. Nếu is_good=false, gọi "
        "THÊM tool_scan_tonight(region=<region trả về>) để tìm chỗ tốt hơn, rồi đề "
        "xuất tên các chỗ đó thay vì điểm ban đầu.\n"
        "- Nếu user hỏi mơ hồ về thời gian ('cuối tuần này', 'vài ngày tới') không "
        "gắn với 1 địa điểm cụ thể -> gọi tool_scan_best_weekend.\n"
        "- Nếu user hỏi 'tối nay'/'đêm nay' chung chung không gắn địa điểm cụ thể "
        "-> gọi tool_scan_tonight.\n"
        "- Nếu chỉ hỏi độ tối bầu trời (Bortle) của 1 nơi, không liên quan thời tiết "
        "-> gọi tool_check_location_darkness.\n"
        "- LUÔN gọi ít nhất 1 tool trước khi trả lời, không được tự bịa thời tiết/"
        "địa điểm/toạ độ.\n\n"
        "Trả lời ngắn gọn (3-5 câu), thân thiện, bằng tiếng Việt. Nếu địa điểm ban "
        "đầu xấu và bạn đề xuất chỗ khác, nói rõ kiểu: 'Mu Cang Chai thời tiết không "
        "tốt, các địa điểm có thời tiết tốt hơn là Y Ty, Ta Xua...' kèm lý do "
        "(mây %, trăng %, Bortle)."
    )

    history = st.session_state.get("astro_ai_history", [])
    contents = history + [{"role": "user", "parts": [{"text": user_question}]}]

    last_result = {"data": None, "tool": None}

    def _wrap(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            out = fn(*args, **kwargs)
            if isinstance(out, dict) and out.get("found"):
                last_result["data"] = out
                last_result["tool"] = fn.__name__
            return out
        return wrapped

    wrapped_tools = [_wrap(tool_scan_best_weekend),
                      _wrap(tool_scan_tonight),
                      _wrap(tool_check_location_darkness),
                      _wrap(tool_check_location_tonight)]

    answer_text = None
    last_err = None
 
    for model in ASTRO_AI_MODEL_CANDIDATES:
        for attempt in range(2):  # tối đa 1 lần thử lại cho mỗi model nếu dính 429
            try:
                response = _astro_ai_client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        tools=wrapped_tools,
                    ),
                )
                answer_text = response.text or "(AI không trả lời được, thử lại câu hỏi khác nhé.)"
                break
            except Exception as e:
                last_err = e
                msg = str(e)
                is_quota_err = "429" in msg or "RESOURCE_EXHAUSTED" in msg
                if is_quota_err and attempt == 0:
                    # Đọc đúng số giây Google yêu cầu chờ (vd "retry in 32.1s")
                    m = re.search(r"retry in ([\d.]+)s", msg)
                    wait_s = float(m.group(1)) + 1 if m else 5.0
                    if wait_s <= 15:  # chờ được thì chờ, tránh treo UI quá lâu
                        time.sleep(wait_s)
                        continue  # thử lại đúng model này 1 lần nữa
                break  # lỗi khác 429, hoặc đã retry rồi -> chuyển sang model kế tiếp
        if answer_text is not None:
            break
 
    if answer_text is None:
        if last_err and ("429" in str(last_err) or "RESOURCE_EXHAUSTED" in str(last_err)):
            return ("⏳ AI đang bị giới hạn tần suất (free tier Gemini chỉ 5-15 "
                     "request/phút). Đợi khoảng 30 giây rồi hỏi lại nhé."), None
        return f"⚠️ Lỗi gọi AI (đã thử {len(ASTRO_AI_MODEL_CANDIDATES)} model): {last_err}", None

    # Lưu lịch sử cho lượt hỏi sau (chỉ text, không lưu tool-call nội bộ)
    st.session_state.astro_ai_history = contents + [
        {"role": "model", "parts": [{"text": answer_text}]}
    ]

    fly_to = None
    data = last_result["data"]
    if data:
        loc = data if "lat" in data else data.get("best")
        if loc and "lat" in loc:
            fly_to = {"lat": loc["lat"], "lon": loc["lon"],
                      "name": loc.get("matched_name") or loc.get("location_name")}

    return answer_text, fly_to
# ------------------------------------------------------------------------------ (hết KHỐI B)
# ── MKW SCAN — top-50 personal favourite locations ──────────────────────
_MKW_LOCS = _FAV_50

def _run_mkw_scan(start_day=0):
    """Scan from start_day in 7 days, using mkw list (top-50 locations)."""
    _fallback_tiers = Counter()
    for day_off in range(start_day, 7):
        d = (_night_base_ict + timedelta(days=day_off)).replace(tzinfo=None)
        moon_illum, _ = get_moon_phase_percent(d)
        if moon_illum >= 32:
            continue
        slots = _make_slots_for_offset(_night_base_ict, day_off)
        perfect_locs = []
        for loc_name, loc_coords in _MKW_LOCS:
            lat, lon = loc_coords
            try:
                hourly, _, utc_off, _, _ = fetch_weather_7days(lat, lon, st.session_state.weather_source)
            except Exception:
                continue
            if not hourly: continue
            frozen = tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in hourly.items())
            try:
                table, _, _, sun_alts, *_ = _build_night_data(
                    lat, lon, slots, frozen, st.session_state.weather_source, utc_off / 3600.0)
            except Exception:
                continue
            verdict = _build_night_verdict(table, sun_alts, moon_illum)
            if not verdict: continue
            _fallback_tiers[verdict["tier"]] += 1
            if verdict["tier"] == "PERFECT NIGHT":
                perfect_locs.append((loc_name, loc_coords, verdict))
        if perfect_locs:
            deduped_nc = _dedupe_locs_km([(n, c) for n, c, _ in perfect_locs], km=20)
            _v_map = {(n, c): v for n, c, v in perfect_locs}
            deduped = [(n, c, _v_map.get((n, c))) for n, c in deduped_nc]
            best = deduped[0]
            return {"loc_name": best[0], "loc_coords": best[1], "verdict": best[2],
                    "moon_illum": moon_illum, "all_locs": deduped,
                    "day_off": day_off, "date": d, "_is_mkw": True}
    if _fallback_tiers:
        top = _fallback_tiers.most_common(1)[0][0]
        return {"_fallback": True, "_fallback_label": top}
    return None

def _run_mkw_best_scan():
    """Best night in next 7 days across mkw list (top-50)."""
    _TIER_RANK = {"PERFECT NIGHT": 2, "GOOD STARRY NIGHT": 1}
    candidates = []
    _fallback_tiers = Counter()
    for day_off in range(0, 7):
        d = (_night_base_ict + timedelta(days=day_off)).replace(tzinfo=None)
        moon_illum, _ = get_moon_phase_percent(d)
        if moon_illum >= 41.5: continue
        is_weekend = d.weekday() in _WEEKEND_DAYS
        slots = _make_slots_for_offset(_night_base_ict, day_off)
        for loc_name, loc_coords in _MKW_LOCS:
            lat, lon = loc_coords
            try:
                hourly, _, utc_off, _, _ = fetch_weather_7days(lat, lon, st.session_state.weather_source)
            except Exception:
                continue
            if not hourly: continue
            frozen = tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in hourly.items())
            try:
                table, _, _, sun_alts, *_ = _build_night_data(
                    lat, lon, slots, frozen, st.session_state.weather_source, utc_off / 3600.0)
            except Exception:
                continue
            verdict = _build_night_verdict(table, sun_alts, moon_illum)
            if not verdict: continue
            _fallback_tiers[verdict["tier"]] += 1
            rank = _TIER_RANK.get(verdict["tier"], 0)
            if rank == 0: continue
            streak = verdict.get("good_hours", 0)
            candidates.append((-rank, not is_weekend, -streak, day_off, loc_name, loc_coords, verdict, moon_illum))
    if not candidates:
        if _fallback_tiers:
            return {"_fallback": True, "_fallback_label": _fallback_tiers.most_common(1)[0][0]}
        return None
    candidates.sort(key=lambda x: x[:4])
    seen = []; results = []
    for row in candidates:
        _, _, _, day_off, loc_name, loc_coords, verdict, moon_illum = row
        if all(abs(loc_coords[0]-s[1][0]) > 0.5 or abs(loc_coords[1]-s[1][1]) > 0.5 for s in seen):
            results.append((loc_name, loc_coords, verdict, day_off, moon_illum))
            seen.append((loc_name, loc_coords))
        if len(results) >= 3: break
    if not results: return None
    best = results[0]
    return {"loc_name": best[0], "loc_coords": best[1], "verdict": best[2],
            "moon_illum": best[4],
            "all_locs": [(r[0], r[1], r[2]) for r in results],
            "day_off": best[3],
            "date": (_night_base_ict + timedelta(days=best[3])).replace(tzinfo=None),
            "_is_best": True, "_is_mkw": True}

# ── GREAT NIGHT SCAN EXECUTION — chạy ngay khi _scan_scanning=True ─────────
# Thực hiện scan TRƯỚC khi map render → sau khi scan xong, rerun lần 2 mới vẽ banner.
# Spinner cũ (st.spinner ngoài map) đã bị xóa — "Scanning..." hiện bên trong map
# qua overlay bottom-left (xem phần banner bên dưới).
if st.session_state._scan_scanning:
    st.session_state._scan_scanning = False
    _region = st.session_state._scan_region
    if _region == "__mkw__":
        if st.session_state._scan_best:
            _scan_res = _run_mkw_best_scan()
        else:
            _scan_res = _run_mkw_scan(start_day=st.session_state._scan_days)
    elif st.session_state._scan_tonight:
        _scan_res = _run_tonight_scan(region=_region)
    elif st.session_state._scan_best:
        _scan_res = _run_best_scan(region=_region)
    else:
        _start = st.session_state._scan_days
        _scan_res = _run_great_night_scan(start_day=_start, region=_region)
    _is_fallback_only = isinstance(_scan_res, dict) and _scan_res.get("_fallback")
    if _is_fallback_only:
        st.session_state._scan_result = "none"
        st.session_state._scan_fallback_label = _scan_res.get("_fallback_label", "unsettled weather")
        # ── Fly map + move pin to region representative city ──────────────────────
        _fb_region = st.session_state._scan_region
        if _fb_region in _REGION_MAP_CENTER:
            _fb_lat, _fb_lon, _fb_zoom = _REGION_MAP_CENTER[_fb_region]
            _fb_city_name = _REGION_CITY_NAME.get(_fb_region, _REGION_LABELS.get(_fb_region, _fb_region))
            st.session_state.lat             = _fb_lat
            st.session_state.lon             = _fb_lon
            st.session_state.map_center      = [_fb_lat, _fb_lon]
            st.session_state.zoom            = _fb_zoom
            st.session_state.location_name   = _fb_city_name
            st.session_state.is_custom_point = True
            st.session_state.day_offset      = 0
            st.session_state.sel_date        = date_options[0]
            st.session_state._need_fly       = True
            st.session_state._last_tip       = None
            st.session_state._skip_prefetch  = True
    elif _scan_res is None:
        st.session_state._scan_result = "none"
        st.session_state._scan_fallback_label = "unsettled weather"
        # Fly map + move pin to region center even when no data at all
        _fb_region = st.session_state._scan_region
        if _fb_region in _REGION_MAP_CENTER:
            _fb_lat, _fb_lon, _fb_zoom = _REGION_MAP_CENTER[_fb_region]
            _fb_city_name = _REGION_CITY_NAME.get(_fb_region, _REGION_LABELS.get(_fb_region, _fb_region))
            st.session_state.lat             = _fb_lat
            st.session_state.lon             = _fb_lon
            st.session_state.map_center      = [_fb_lat, _fb_lon]
            st.session_state.zoom            = _fb_zoom
            st.session_state.location_name   = _fb_city_name
            st.session_state.is_custom_point = True
            st.session_state.day_offset      = 0
            st.session_state.sel_date        = date_options[0]
            st.session_state._need_fly       = True
            st.session_state._last_tip       = None
            st.session_state._skip_prefetch  = True
    else:
        st.session_state._scan_result = _scan_res
        st.session_state._scan_fallback_label = None

    # ── Apply kết quả 1st vào session state → map + table cập nhật ngay ──────
    # Giống hệt Priority 1 (click sao): set lat/lon, location_name, day_offset,
    # sel_date, map_center, _need_fly để map bay đến địa điểm + ngày kết quả 1st.
    if _scan_res is not None and not _is_fallback_only:
        _r1_name   = _scan_res["loc_name"]
        _r1_coords = _scan_res["loc_coords"]
        _r1_dayoff = _scan_res.get("day_off", 0)
        st.session_state.lat             = _r1_coords[0]
        st.session_state.lon             = _r1_coords[1]
        st.session_state.map_center      = [_r1_coords[0], _r1_coords[1]]
        st.session_state.location_name   = _r1_name
        st.session_state.is_custom_point = False
        st.session_state.day_offset      = _r1_dayoff
        st.session_state.sel_date        = date_options[_r1_dayoff]
        st.session_state._need_fly       = True
        st.session_state._last_tip       = None
        st.session_state._skip_prefetch  = True

    st.rerun()

# ── MAP ───────────────────────────────────────────────────────────────────────
# Add top margin so the in-map tile buttons are not obscured by Streamlit toolbar
st.markdown("<div style='margin-top:38px'></div>", unsafe_allow_html=True)

# ── MAP tile switcher — ASCII keys only, no emoji in any string passed to folium ──
_TILE_SAT_URL  = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'

if st.session_state.map_tile not in ("satellite", "himawari", "windy"):
    st.session_state.map_tile = "himawari"
 
# ==============================================================================
# KHỐI C (v7 — bản sửa đúng) — xoá sạch KHỐI C cũ, dán nguyên khối này vào,
# ngay trước dòng "m = folium.Map(".
#
# So với bản trước: GIỮ NGUYÊN kích thước chatbox đã "vừa mắt" (không dùng
# :has(), không set height cho container kết quả), CHỈ thêm đúng 1 dòng
# "flex-direction: row !important;" để sửa lệch nút gửi — vì hàng chứa
# textarea + nút gửi mặc định có thể là flex-direction: column, khiến
# align-items: center chỉ canh giữa theo chiều NGANG chứ không phải dọc.
# ==============================================================================

# --- NÚT NEW CHAT — góc trên-phải màn hình, position:fixed ---
st.markdown(
    """
    <style>
    .st-key-astro_newchat_btn {
        position: fixed !important;
        top: 0.85rem !important;
        right: 0.9rem !important;
        z-index: 999999 !important;
        width: 40px !important;
    }
    .st-key-astro_newchat_btn button {
        width: 40px !important;
        height: 40px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
with st.container(key="astro_newchat_btn"):
    if st.button("", key="astro_new_chat", icon=":material/edit_square:", help="New chat", use_container_width=True):
        st.session_state.astro_ai_history = []
        st.session_state.astro_ai_answer = None
        st.session_state.astro_last_question = "Hỏi AI tìm địa điểm & thời điểm chụp ảnh milkyway..."
        st.session_state.astro_last_processed_query = None
        st.rerun()

# --- CSS: chatbox gọn (bản đã "vừa mắt"), chỉ thêm flex-direction: row để
# sửa lệch nút gửi, ẩn toolbar Streamlit ---
st.markdown(
    """
    <style>
    /* 1. ẨN TOOLBAR STREAMLIT (không ẩn được thanh Share/Star/Edit/GitHub
    của Streamlit Community Cloud — thanh đó nằm ngoài DOM app). */
    [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. KHUNG CHAT_INPUT */
    div[data-testid="stChatInput"] {
        padding: 0 !important;
        min-height: unset !important;
        margin-bottom: 0px !important;
    }

    div[data-testid="stChatInput"] > div {
        min-height: 38px !important;
        height: 38px !important;
        padding: 0 8px 0 12px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
    }

    div[data-testid="stChatInput"] textarea {
        min-height: 24px !important;
        height: 24px !important;
        max-height: 24px !important;
        padding: 0 !important;
        margin-top: 2px !important;
        margin-bottom: 0 !important;
        font-size: 13px !important;
        line-height: 24px !important;
        resize: none !important;
        overflow: hidden !important;
        white-space: nowrap !important;
        text-overflow: ellipsis !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #888888 !important;
        opacity: 0.8 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    div[data-testid="stChatInput"] button {
        position: static !important;
        top: auto !important;
        bottom: auto !important;
        right: auto !important;
        height: 26px !important;
        width: 26px !important;
        min-height: 26px !important;
        min-width: 26px !important;
        padding: 0 !important;
        margin: 0 !important;
        align-self: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* 3. KHUNG HIỂN THỊ KẾT QUẢ */
    div[class*="st-key-astro_ai_answer_box"] {
        min-height: auto !important;
        height: auto !important;
        padding: 14px 16px !important;
        margin-top: -10px !important;
    }
    div[class*="st-key-astro_ai_answer_box"] p,
    div[class*="st-key-astro_ai_answer_box"] li,
    div[class*="st-key-astro_ai_answer_box"] span,
    div[class*="st-key-astro_ai_answer_box"] div {
        font-size: 13px !important;
        line-height: 1.5 !important;
        margin-top: 0 !important;
        margin-bottom: 0.4rem !important;
    }
    div[class*="st-key-astro_ai_answer_box"] ol,
    div[class*="st-key-astro_ai_answer_box"] ul {
        padding-left: 1.2rem !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.4rem !important;
    }
    div[class*="st-key-astro_ai_answer_box"] *:last-child {
        margin-bottom: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- KHUNG CHAT: input trên, khung kết quả bên dưới ---
_placeholder_text = st.session_state.get(
    "astro_last_question",
    "Hỏi AI tìm địa điểm & thời điểm chụp ảnh milkyway...",
)

_ai_panel = st.container()
with _ai_panel:
    _ai_question = st.chat_input(
        placeholder=_placeholder_text,
        key="astro_ai_input",
    )

    _astro_chat_box = st.container(border=True, key="astro_ai_answer_box")
    with _astro_chat_box:
        _answer_slot = st.empty()
        if st.session_state.get("astro_ai_answer"):
            _answer_slot.markdown(st.session_state.astro_ai_answer)

# --- LOGIC XỬ LÝ ---
if _ai_question and _ai_question.strip():
    user_query = _ai_question.strip()

    if user_query != st.session_state.get("astro_last_processed_query"):
        st.session_state.astro_last_processed_query = user_query
        st.session_state.astro_last_question = user_query

        with _answer_slot:
            st.caption("⏳ AI đang kiểm tra thời tiết & địa điểm...")

        answer, fly_to = ask_astro_ai(user_query)
        st.session_state.astro_ai_answer = answer

        if fly_to:
            st.session_state.lat = fly_to["lat"]
            st.session_state.lon = fly_to["lon"]
            st.session_state.map_center = [fly_to["lat"], fly_to["lon"]]
            st.session_state.zoom = 9
        st.rerun()
# ------------------------------------------------------------------------------ (hết KHỐI C v7)

# ── Folium map — location/zoom từ session state (key cố định → không recreate) ──
# prefer_location=False: KHÔNG reset vị trí camera khi rerun — chỉ set lần đầu.
# Điều này là chìa khoá giúp pan/zoom mượt: Streamlit không can thiệp vào
# camera position sau mỗi rerun.
m = folium.Map(
    location=st.session_state.map_center,
    zoom_start=st.session_state.zoom,
    tiles=None,           # không load tile mặc định; tile được inject qua JS bên dưới
    prefer_canvas=True,   # dùng Canvas renderer → ít DOM node hơn, scroll mượt hơn
)

# (Street tab removed. OpenRailwayMap is now added by JS only in Satellite mode.)

# ── Combined BottomRight control: [📍 Label  LPM] + [Windy|Satellite|Himawari] ──
# Gộp thành một control duy nhất (column) để kiểm soát khoảng cách chính xác.
from folium import MacroElement
from jinja2 import Template

_lpm_url = (f"https://lightpollutionmap.app/"
            f"?lat={st.session_state.lat:.4f}&lng={st.session_state.lon:.4f}&zoom=10")

_COMBINED_CTRL_TEMPLATE = Template("""
{% macro script(this, kwargs) %}
(function(){
  // ── localStorage keys ─────────────────────────────────────────────────────
  var LS_TILE   = 'astro_map_tile';
  var LS_W_LAT  = 'astro_windy_lat';
  var LS_W_LON  = 'astro_windy_lon';
  var LS_W_ZOOM = 'astro_windy_zoom';

  // ── Windy defaults (Kanto, zoom 7) ────────────────────────────────────────
  var _W_DEF_LAT  = 35.80;
  var _W_DEF_LON  = 139.50;
  var _W_DEF_ZOOM = 7;

  function _lsGet(k, def) {
    try { var v = localStorage.getItem(k); return (v !== null) ? v : def; } catch(e) { return def; }
  }
  function _lsSet(k, v) { try { localStorage.setItem(k, String(v)); } catch(e){} }

  function _buildWindySrc(lat, lon, zoom) {
    var latStr = parseFloat(lat).toFixed(4);
    var lonStr = parseFloat(lon).toFixed(4);
    return 'https://embed.windy.com/embed2.html'
      + '?lat=' + latStr
      + '&lon=' + lonStr
      + '&detailLat=' + latStr
      + '&detailLon=' + lonStr
      + '&width=650&height=450&zoom=' + Math.round(zoom)
      + '&level=surface&overlay=rain&product=ecmwf'
      + '&menu=&message=true&marker=' + latStr + ',' + lonStr + '&calendar=now'
      + '&pressure=&type=map&location=coordinates'
      + '&detail=&metricWind=default&metricTemp=default&radarRange=-1';
  }

  var _windyFrame = null;

  function _ensureWindyFrame(mapEl) {
    if (_windyFrame) return;
    _windyFrame = mapEl.querySelector('#astro-windy-iframe');
    if (_windyFrame) return;
    var lat  = parseFloat(_lsGet(LS_W_LAT,  _W_DEF_LAT));
    var lon  = parseFloat(_lsGet(LS_W_LON,  _W_DEF_LON));
    var zoom = parseInt(  _lsGet(LS_W_ZOOM, _W_DEF_ZOOM), 10);
    _windyFrame = document.createElement('iframe');
    _windyFrame.id  = 'astro-windy-iframe';
    _windyFrame.src = _buildWindySrc(lat, lon, zoom);
    _windyFrame.style.cssText = (
      'position:absolute;top:0;left:0;width:100%;height:100%;'
      + 'border:none;z-index:500;display:none;border-radius:inherit;'
    );
    _windyFrame.setAttribute('allowfullscreen', '');
    _windyFrame.setAttribute('sandbox',
      'allow-scripts allow-same-origin allow-forms allow-popups allow-top-navigation');
    mapEl.style.position = 'relative';
    mapEl.appendChild(_windyFrame);
  }

  window.flyWindy = function(lat, lon, zoom) {
    zoom = zoom || 9;
    _lsSet(LS_W_LAT,  lat);
    _lsSet(LS_W_LON,  lon);
    _lsSet(LS_W_ZOOM, zoom);
    if (_windyFrame) { _windyFrame.src = _buildWindySrc(lat, lon, zoom); }
  };

  var CombinedCtrl = L.Control.extend({
    options: { position: 'bottomright' },
    onAdd: function(map) {
      // ── Outer column wrapper ───────────────────────────────────────────────
      var col = L.DomUtil.create('div', '');
      col.style.cssText = (
        'display:flex;flex-direction:column;align-items:flex-end;'
        + 'gap:6px;margin-bottom:44px;'
      );
      L.DomEvent.disableClickPropagation(col);

      // ── Row 1: 📍 Label + LPM ─────────────────────────────────────────────
      var infoRow = L.DomUtil.create('div', '', col);
      infoRow.style.cssText = (
        'display:flex;align-items:center;gap:6px;'
        + 'background:rgba(15,23,42,0.88);border:1px solid #334155;'
        + 'border-radius:8px;padding:5px 8px;'
        + 'box-shadow:0 2px 8px rgba(0,0,0,0.6);'
      );

      var pin = L.DomUtil.create('span', '', infoRow);
      pin.innerHTML = '&#128205;';
      pin.style.cssText = 'font-size:13px;flex-shrink:0;line-height:1;';

      var loc = L.DomUtil.create('span', '', infoRow);
      loc.textContent = '{{ this.location_name }}';
      loc.style.cssText = 'color:#e2e8f0;font-size:12px;font-weight:600;'
        + 'white-space:nowrap;display:inline-block;';

      var a = L.DomUtil.create('a', '', infoRow);
      var _gMapUrl = 'https://www.google.com/maps?q={{ this.lat }},{{ this.lon }}';
      a.href = _gMapUrl;
      a.target = '_blank'; a.rel = 'noopener'; a.title = 'Open in Google Maps';
      a.textContent = 'GoogleMap';
      a.style.cssText = 'display:inline-flex;align-items:center;justify-content:center;'
        + 'background:rgba(34,197,94,0.12);border:1.5px solid rgba(34,197,94,0.45);'
        + 'border-radius:6px;padding:2px 7px;text-decoration:none;'
        + 'color:#86efac;font-size:10px;font-weight:700;'
        + 'transition:background 0.2s;white-space:nowrap;cursor:pointer;flex-shrink:0;';
      a.onmouseover = function(){ a.style.background = 'rgba(34,197,94,0.28)'; };
      a.onmouseout  = function(){ a.style.background = 'rgba(34,197,94,0.12)'; };

      // ── SCAN trigger — hidden; called by search box with "best <region>", "tonight <region>" ───
      // Sentinel encoding (lat below Mercator max 85.05, always valid click):
      //   lat=89.85 → best <region>   (no day_off needed — always scans 7 days)
      //   lat=89.75 → tonight <region> (no day_off needed — always tonight)
      // lng = 100 + region_idx  (region_idx: 0=bac,1=trung,2=nam,3=vietnam)
      var _REGION_IDX = { bac:0, trung:1, nam:2, vietnam:3 };
      window._triggerBest = function(region) {
        var idx = (region in _REGION_IDX) ? _REGION_IDX[region] : _REGION_IDX['bac'];
        map.fire('click', { latlng: L.latLng(89.85, 100 + idx) });
      };
      window._triggerTonight = function(region) {
        var idx = (region in _REGION_IDX) ? _REGION_IDX[region] : _REGION_IDX['bac'];
        map.fire('click', { latlng: L.latLng(89.75, 100 + idx) });
      };
      // lat=89.65 → "off": tắt banner/ring ngay, không load data
      window._triggerOff = function() {
        map.fire('click', { latlng: L.latLng(89.65, 100) });
      };
      // lat=89.55 → mkw scan  (lng=200+day_off*0.01, day_off=days-1 for days 1-6, 0 for days=0)
      window._triggerMkwScan = function(days) {
        var d = (days >= 1 && days <= 6) ? (days - 1) : 0;
        map.fire('click', { latlng: L.latLng(89.55, 200 + d * 0.01) });
      };
      // lat=89.45 → mkw best
      window._triggerMkwBest = function() {
        map.fire('click', { latlng: L.latLng(89.45, 200) });
      };
      // ── REGION scan trigger — rewritten from scratch, mirrors mkw's pattern exactly ──
      // lat=89.35 → region scan "<region> N" (N=1..6), region_idx in tens place, day_off-1 in hundredths.
      // lng = 300 + region_idx*10 + (N-1)   (region_idx 0-9, N-1 is 0-5 → always fits, no rounding ambiguity)
      window._triggerRegionScan = function(region, n) {
        var idx = (region in _REGION_IDX) ? _REGION_IDX[region] : _REGION_IDX['bac'];
        var nn = (n >= 1 && n <= 6) ? n : 1;
        var lng = 300 + idx * 10 + (nn - 1);
        map.fire('click', { latlng: L.latLng(89.35, lng) });
      };


      // ── Row 2: Windy | Satellite | Himawari ─────────────────────────────────
      var tileRow = L.DomUtil.create('div', '', col);
      tileRow.style.cssText = (
        'display:flex;gap:4px;background:rgba(15,23,42,0.88);'
        + 'border:1px solid #334155;border-radius:8px;padding:5px 8px;'
        + 'box-shadow:0 2px 8px rgba(0,0,0,0.6);'
      );

      var tiles = {
        satellite: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
      };
      var attrs = { satellite: 'Google Satellite Hybrid' };
      var current = null;
      var ormLayer = null;   // OpenRailwayMap overlay, Satellite mode only
      var btns = {};

      // ── Himawari (JMA) infrared: dark base + labels + short animation ────────
      // Tiles are plain <img> requests, so no CORS problem. The frame list comes
      // from targetTimes_jp.json (fetch); if that fetch is blocked we probe tiles
      // backwards in 10-min steps instead (basetime == validtime for satimg).
      var HIM_BASE   = 'https://www.jma.go.jp/bosai/himawari/data/satimg/';
      var HIM_AREA   = 'fd';              // full disk: phủ cả Việt Nam (vùng 'jp' chỉ phủ Nhật)
      var HIM_ELEM   = 'B13/TBB';          // infrared (works day and night)
      var HIM_MINZ   = 3;                  // native tile zoom range (upscaled beyond)
      var HIM_MAXZ   = 5;                  // fd chỉ có zoom 3-5
      var HIM_FRAMES = 8;                  // frames in the loop (10 min apart)
      var HIM_OPAC   = 1.0;    // max by default; adjustable with the slider
      var HIM_CONT   = 1.2;    // cloud contrast (CSS contrast()); 1.0 = original, higher = darker gaps between clouds
      // Base map = NASA VIIRS Black Marble (city lights on black), free, no API key.
      // (Carto basemaps now print "API KEY REQUIRED" over every tile, so Carto is no longer used.)
      var HIM_BASE_PRIMARY  = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png';
      var HIM_BASE_FALLBACK = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_CityLights_2012/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg';
      // CSS filter on the lights layer: contrast>1 kills the faint grey haze and keeps bright cores -> crisper, darker look.
      // Tune here: brightness(0.8-1.2), contrast(1.2-2.0).
      // Gamma curve out = AMP * in^EXP on the lights: EXP>1 darkens the haze/mid-tones, AMP<1 caps the blown-out city cores.
      //   core too bright -> lower HIM_GAMMA_AMP (0.6-0.9)   |   too dim overall -> lower HIM_GAMMA_EXP (1.3-2.2)
      var HIM_GAMMA_AMP = 0.20;
      var HIM_GAMMA_EXP = 1.9;
      (function() {
        if (document.getElementById('him-gamma-svg')) return;
        var d = document.createElement('div');
        d.id = 'him-gamma-svg';
        d.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;';
        var fn = function(c) { return '<feFunc' + c + ' type="gamma" amplitude="' + HIM_GAMMA_AMP + '" exponent="' + HIM_GAMMA_EXP + '" offset="0"/>'; };
        d.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0"><filter id="him-gamma" color-interpolation-filters="sRGB">'
          + '<feComponentTransfer>' + fn('R') + fn('G') + fn('B') + '</feComponentTransfer></filter></svg>';
        document.body.appendChild(d);
      })();
      var HIM_LIGHT_FILTER = 'url(#him-gamma)';
      // Max zoom in Himawari mode (data is coarse, so deeper zoom is just an enlarged/blurry view).
      var HIM_VIEW_MAXZ = 11;
      // Labels: Esri reference layer (free, no key), designed to overlay dark imagery.
      var HIM_LABELS = 'https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}';
      var PLAY_HTML  = '&#9654;';
      var PAUSE_HTML = '&#10074;&#10074;';
      var himFrames = [], himIdx = 0, himTimer = null, himTok = 0, himPlaying = false;
      var himLabelLayer = null;
      var himNote = '';
      var himBorderLayers = [], himBorderCache = {};
      var HIM_BORDERS = [
        { w: 1.0, o: 0.9, urls: [
          'https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@master/geojson/ne_50m_admin_0_boundary_lines_land.geojson',
          'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_boundary_lines_land.geojson' ] },
        { w: 0.9, o: 0.8, urls: [
          'https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@master/geojson/ne_50m_coastline.geojson',
          'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_coastline.geojson' ] }
      ];

      var himRow = L.DomUtil.create('div', '', col);
      himRow.style.cssText = (
        'display:none;align-items:center;gap:6px;'
        + 'background:rgba(15,23,42,0.88);border:1px solid #334155;'
        + 'border-radius:8px;padding:4px 8px;box-shadow:0 2px 8px rgba(0,0,0,0.6);'
      );
      var himPlay = L.DomUtil.create('button', '', himRow);
      himPlay.innerHTML = PLAY_HTML;
      himPlay.title = 'Play / pause the last ~70 min';
      himPlay.style.cssText = (
        'border:none;cursor:pointer;border-radius:5px;padding:2px 9px;'
        + 'font-size:12px;font-weight:700;background:#3b82f6;color:#ffffff;'
      );
      var himLbl = L.DomUtil.create('span', '', himRow);
      himLbl.style.cssText = 'color:#e2e8f0;font-size:11px;font-weight:600;white-space:nowrap;';
      var himSlider = L.DomUtil.create('input', '', himRow);
      himSlider.type = 'range'; himSlider.min = '15'; himSlider.max = '100';
      himSlider.value = String(Math.round(HIM_OPAC * 100));
      himSlider.title = 'IR cloud opacity (lower = see borders better)';
      himSlider.style.cssText = 'display:none;width:70px;height:4px;cursor:pointer;';   // hidden: fixed 100%
      var himContLbl = L.DomUtil.create('span', '', himRow);
      himContLbl.textContent = 'Contrast';
      himContLbl.style.cssText = 'display:none;color:#94a3b8;font-size:10px;font-weight:600;';
      var himCont = L.DomUtil.create('input', '', himRow);
      himCont.type = 'range'; himCont.min = '100'; himCont.max = '300';
      himCont.value = String(Math.round(HIM_CONT * 100));
      himCont.title = 'Cloud contrast (higher = whiter clouds, darker gaps)';
      himCont.style.cssText = 'display:none;width:70px;height:4px;cursor:pointer;';   // hidden: fixed default
      function _himApplyFilter(f) {
        if (!f.layer) return;
        var el = f.layer.getContainer();
        if (el) el.style.filter = 'contrast(' + HIM_CONT + ')';
        if (el) el.style.mixBlendMode = 'screen';
      }
      L.DomEvent.on(himCont, 'input', function() {
        HIM_CONT = (+himCont.value) / 100;
        himFrames.forEach(_himApplyFilter);
      });
      L.DomEvent.disableClickPropagation(himRow);
      L.DomEvent.on(himSlider, 'input', function() {
        HIM_OPAC = (+himSlider.value) / 100;
        if (himFrames[himIdx] && himFrames[himIdx].layer) himFrames[himIdx].layer.setOpacity(HIM_OPAC);
      });

      function _p2(n) { return (n < 10 ? '0' : '') + n; }

      // 'yyyymmddhhmmss' (UTC) -> 'MM/DD HH:mm ICT'
      function _himFmt(v) {
        var d = new Date(Date.UTC(+v.slice(0, 4), +v.slice(4, 6) - 1, +v.slice(6, 8), +v.slice(8, 10), +v.slice(10, 12)));
        d = new Date(d.getTime() + 7 * 3600 * 1000);
        return _p2(d.getUTCMonth() + 1) + '/' + _p2(d.getUTCDate()) + ' '
          + _p2(d.getUTCHours()) + ':' + _p2(d.getUTCMinutes()) + ' ICT';
      }
      function _himUtcStamp(ms) {
        var d = new Date(ms);
        return d.getUTCFullYear() + _p2(d.getUTCMonth() + 1) + _p2(d.getUTCDate())
          + _p2(d.getUTCHours()) + _p2(d.getUTCMinutes()) + '00';
      }
      function _himUrl(f) {
        return HIM_BASE + f.b + '/' + HIM_AREA + '/' + f.v + '/' + HIM_ELEM + '/{z}/{x}/{y}.jpg';
      }

      function _himParse(j) {
        var out = [];
        if (!Array.isArray(j)) return out;
        j.forEach(function(x) {
          if (x && x.basetime && x.validtime) out.push({ b: String(x.basetime), v: String(x.validtime) });
        });
        out.sort(function(a, b) { return a.v < b.v ? -1 : (a.v > b.v ? 1 : 0); });
        var ded = [];
        out.forEach(function(x) {
          if (ded.length && ded[ded.length - 1].v === x.v) { ded[ded.length - 1] = x; } else { ded.push(x); }
        });
        return ded.slice(-HIM_FRAMES);
      }

      // Fallback: find the newest frame by loading a Vietnam tile (z5 x25 y14), 10-min steps back.
      function _himProbe(cb) {
        var step = 10 * 60 * 1000;
        var t = Math.floor((Date.now() - 10 * 60 * 1000) / step) * step;
        var tries = 0;
        function next() {
          if (tries++ > 12) { cb([]); return; }
          var v = _himUtcStamp(t);
          var img = new Image();
          img.onload = function() {
            var out = [];
            for (var k = HIM_FRAMES - 1; k >= 0; k--) {
              var vv = _himUtcStamp(t - k * step);
              out.push({ b: vv, v: vv });
            }
            cb(out);
          };
          img.onerror = function() { t -= step; next(); };
          img.src = HIM_BASE + v + '/' + HIM_AREA + '/' + v + '/' + HIM_ELEM + '/5/25/14.jpg';
        }
        next();
      }

      function _himLoadTimes(cb) {
        var finished = false;
        function done(list) { if (finished) return; finished = true; cb(list); }
        function fallback() { _himProbe(done); }
        try {
          fetch(HIM_BASE + 'targetTimes_' + HIM_AREA + '.json', { cache: 'no-store' })
            .then(function(r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
            .then(function(j) {
              var l = _himParse(j);
              if (l.length) { done(l); } else { fallback(); }
            })
            .catch(fallback);
        } catch (e) { fallback(); }
      }

      function _himEnsure(f) {
        if (f.layer) return;
        f.layer = L.tileLayer(_himUrl(f), {
          opacity: 0, minNativeZoom: HIM_MINZ, maxNativeZoom: HIM_MAXZ, maxZoom: 19,
          zIndex: 5, attribution: 'JMA'
        });
        f.layer.addTo(map);
        _himApplyFilter(f);
      }
      function _himShow(i) {
        himIdx = i;
        himFrames.forEach(function(f, k) {
          if (f.layer) f.layer.setOpacity(k === i ? HIM_OPAC : 0);
        });
        himLbl.textContent = 'JMA Himawari IR  ' + _himFmt(himFrames[i].v) + himNote;
      }
      // Base layer = city lights (always on). If the primary Black Marble tiles all fail, fall back to CityLights 2012.
      function _himBaseLayer() {
        var oks = 0, errs = 0, swapped = false;
        var lyr = L.tileLayer(HIM_BASE_PRIMARY, {
          maxNativeZoom: 8, maxZoom: 19, zIndex: 1, attribution: 'NASA GIBS / VIIRS Black Marble'
        });
        lyr.on('tileload', function() { oks++; });
        lyr.on('tileerror', function() {
          errs++;
          if (!swapped && oks === 0 && errs >= 4) { swapped = true; lyr.setUrl(HIM_BASE_FALLBACK); }
        });
        return lyr;
      }
      function _himStop() {
        himPlaying = false;
        if (himTimer) { clearTimeout(himTimer); himTimer = null; }
        himPlay.innerHTML = PLAY_HTML;
      }
      function _himCleanup() {
        himTok++;
        _himStop();
        himFrames.forEach(function(f) { if (f.layer) { map.removeLayer(f.layer); } });
        himFrames = [];
        if (himLabelLayer) { map.removeLayer(himLabelLayer); himLabelLayer = null; }
        map.setMaxZoom(19);   // undo the Himawari zoom cap
        himBorderLayers.forEach(function(l) { map.removeLayer(l); });
        himBorderLayers = [];
        himNote = '';
        himRow.style.display = 'none';
      }
      function _himFetchFirst(urls, cb) {
        var i = 0;
        (function next() {
          if (i >= urls.length) { cb(null); return; }
          var u = urls[i++];
          if (himBorderCache[u]) { cb(himBorderCache[u]); return; }
          try {
            fetch(u).then(function(r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
              .then(function(j) { himBorderCache[u] = j; cb(j); })
              .catch(next);
          } catch (e) { next(); }
        })();
      }
      // Vector borders (country borders + coastlines) drawn ABOVE the cloud tiles.
      function _himBorders(tok) {
        if (!map.getPane('himBorders')) {
          var pn = map.createPane('himBorders');
          pn.style.zIndex = 250;
          pn.style.pointerEvents = 'none';
        }
        var okCount = 0, doneCount = 0;
        HIM_BORDERS.forEach(function(src) {
          _himFetchFirst(src.urls, function(data) {
            doneCount++;
            if (tok === himTok && data) {
              var lyr = L.geoJSON(data, {
                pane: 'himBorders', interactive: false,
                style: { color: '#f8fafc', weight: src.w, opacity: src.o, fill: false }
              });
              lyr.addTo(map);
              himBorderLayers.push(lyr);
              okCount++;
            }
            if (tok === himTok && doneCount === HIM_BORDERS.length && okCount === 0) {
              himNote = '  (no border data)';
              if (himFrames[himIdx]) _himShow(himIdx);
            }
          });
        });
      }

      // Auto-loop: 600 ms per frame, 1.8 s pause on the newest frame, then restart.
      function _himStart(from) {
        if (!himFrames.length) return;
        himPlaying = true;
        himPlay.innerHTML = PAUSE_HTML;
        himFrames.forEach(function(f) { _himEnsure(f); });
        var tok = himTok;
        var i = from || 0;
        var last = himFrames.length - 1;
        _himShow(i);
        function tick() {
          if (!himPlaying || tok !== himTok) return;
          i = (i + 1) % himFrames.length;
          _himShow(i);
          himTimer = setTimeout(tick, i === last ? 1800 : 600);
        }
        himTimer = setTimeout(tick, 1200);   // let the extra frames load their tiles first
      }

      function _himEnter() {
        himRow.style.display = 'flex';
        himLbl.textContent = 'JMA Himawari IR  loading...';
        himLabelLayer = L.tileLayer(HIM_LABELS, { maxZoom: 19, zIndex: 10, opacity: 0.9 });
        himLabelLayer.addTo(map);
        var tok = ++himTok;
        _himBorders(tok);
        _himLoadTimes(function(list) {
          if (tok !== himTok) return;
          if (!list.length) { himLbl.textContent = 'Himawari: no data'; return; }
          himFrames = list.map(function(t) { return { b: t.b, v: t.v, layer: null }; });
          _himStart(0);
        });
      }

      L.DomEvent.on(himPlay, 'click', function() {
        if (!himFrames.length) return;
        if (himPlaying) { _himStop(); return; }
        _himStart(himIdx);
      });

      function switchTile(mode) {
        var mapEl = map.getContainer();
        var prevMode = _lsGet(LS_TILE, null);
        _ensureWindyFrame(mapEl);
        // ── Disable/enable zoom buttons based on tile mode ─────────────────────
        var zoomIn  = mapEl.querySelector('.leaflet-control-zoom-in');
        var zoomOut = mapEl.querySelector('.leaflet-control-zoom-out');
        var isWindy = (mode === 'windy');
        if (zoomIn)  { zoomIn.style.opacity  = isWindy ? '0.35' : '1'; zoomIn.style.pointerEvents  = isWindy ? 'none' : 'auto'; zoomIn.style.cursor  = isWindy ? 'not-allowed' : ''; }
        if (zoomOut) { zoomOut.style.opacity = isWindy ? '0.35' : '1'; zoomOut.style.pointerEvents = isWindy ? 'none' : 'auto'; zoomOut.style.cursor = isWindy ? 'not-allowed' : ''; }
        _himCleanup();
        if (ormLayer) { map.removeLayer(ormLayer); ormLayer = null; }
        if (mode === 'windy') {
          var c = map.getCenter();
          var z = map.getZoom();
          var needSync = (prevMode !== 'windy') || (_lsGet(LS_W_LAT, null) === null);
          if (needSync) { window.flyWindy(c.lat, c.lng, z); }
          if (current) { map.removeLayer(current); current = null; }
          _windyFrame.style.display = 'block';
        } else if (mode === 'himawari') {
          if (_windyFrame) _windyFrame.style.display = 'none';
          if (current) { map.removeLayer(current); }
          current = _himBaseLayer();
          current.addTo(map);
          var _bc = current.getContainer();
          if (_bc) _bc.style.filter = HIM_LIGHT_FILTER;
          map.setMaxZoom(HIM_VIEW_MAXZ);
          if (map.getZoom() > HIM_VIEW_MAXZ) map.setZoom(HIM_VIEW_MAXZ);
          _himEnter();
        } else {
          if (_windyFrame) _windyFrame.style.display = 'none';
          if (current) { map.removeLayer(current); }
          current = L.tileLayer(tiles[mode], { attribution: attrs[mode], maxZoom: 19 });
          current.addTo(map);
          if (mode === 'satellite') {
            ormLayer = L.tileLayer('https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png',
              { opacity: 0.25, maxZoom: 19, attribution: 'OpenRailwayMap' });
            ormLayer.addTo(map);
          }
        }
        _lsSet(LS_TILE, mode);
        Object.keys(btns).forEach(function(k){
          btns[k].style.background = (k === mode) ? '#3b82f6' : 'transparent';
          btns[k].style.color      = (k === mode) ? '#ffffff' : '#94a3b8';
        });
      }

      ['windy','satellite','himawari'].forEach(function(mode){
        var btn = L.DomUtil.create('button', '', tileRow);
        btn.textContent = mode === 'windy' ? 'Windy'
                        : mode.charAt(0).toUpperCase() + mode.slice(1);
        btn.style.cssText = 'border:none;cursor:pointer;border-radius:5px;'
          + 'padding:3px 10px;font-size:12px;font-weight:600;'
          + 'transition:background 0.2s,color 0.2s;background:transparent;color:#94a3b8;';
        btns[mode] = btn;
        L.DomEvent.on(btn, 'click', function(){ switchTile(mode); });
      });

      map.whenReady(function(){
        var saved = _lsGet(LS_TILE, 'himawari');
        if (saved !== 'himawari' && saved !== 'windy') saved = 'himawari';   // Satellite no longer the start tab
        switchTile(saved);
      });

      return col;
    }
  });
  new CombinedCtrl().addTo({{ this._parent.get_name() }});
})();
{% endmacro %}
""")

class _CombinedControl(MacroElement):
    def __init__(self, lpm_url, location_name, initial_tile="himawari", lat=35.6895, lon=139.6917):
        super().__init__()
        self._name = '_CombinedControl'
        self._template = _COMBINED_CTRL_TEMPLATE
        self.lpm_url = lpm_url
        self.location_name = location_name
        self.initial_tile = initial_tile
        self.lat = round(lat, 4)
        self.lon = round(lon, 4)

# ── COMBINED CONTROL (Label/GoogleMap on top, Tile switcher below, gap=6px) ────
_CombinedControl(
    lpm_url=_lpm_url,
    location_name=_strip_loc_num(st.session_state.location_name),
    initial_tile=st.session_state.map_tile,
    lat=st.session_state.lat,
    lon=st.session_state.lon,
).add_to(m)

# ── SEARCH CONTROL — inject location list vào JS, nằm topleft trên map ──────
import json as _json

# ── KANJI ⇄ ROMAJI ALIAS TABLE ───────────────────────────────────────────────
# (giữ chỗ — bảng alias không cần dùng cho địa danh Việt Nam)
# (vd "Fukushima", "Akimoto"). Mỗi entry sẽ được gắn thêm "alias text" chứa tất
# cả romaji keyword tương ứng với kanji xuất hiện trong tên.
# — không cần bảng alias Kanji/Romaji cho địa danh Việt Nam (chỉ dùng chữ Latin) —
_KANJI_ALIAS = {}

_loc_js_list = _json.dumps([
    {"name": name, "lat": coords[0], "lon": coords[1]}
    for name, coords in LOCATION_DATABASE.items()
])
_kanji_alias_js = _json.dumps(_KANJI_ALIAS, ensure_ascii=False)




_SEARCH_CTRL_TEMPLATE = Template("""
{% macro script(this, kwargs) %}
(function(){
  var _DB = {{ this.loc_list }};
  var _ALIAS = {{ this.alias_dict }};

  var SearchCtrl = L.Control.extend({
    options: { position: 'topleft' },
    onAdd: function(map) {
      var wrapper = L.DomUtil.create('div', '');
      wrapper.style.cssText = 'position:relative;';
      L.DomEvent.disableClickPropagation(wrapper);
      L.DomEvent.disableScrollPropagation(wrapper);

      // ── Container row ──────────────────────────────────────────────────────
      var row = L.DomUtil.create('div', '', wrapper);
      row.style.cssText = (
        'display:flex;align-items:center;gap:4px;'
        + 'background:rgba(15,23,42,0.92);border:1px solid #334155;'
        + 'border-radius:8px;padding:4px 7px;box-shadow:0 2px 8px rgba(0,0,0,0.6);'
      );

      // ── Search icon ────────────────────────────────────────────────────────
      var icon = L.DomUtil.create('span', '', row);
      icon.innerHTML = '&#128269;';
      icon.style.cssText = 'font-size:14px;cursor:pointer;color:#94a3b8;line-height:1;flex-shrink:0;';

      // ── Input ──────────────────────────────────────────────────────────────
      var inp = L.DomUtil.create('input', '', row);
      inp.type = 'text';
      inp.placeholder = 'Search location…';
      inp.style.cssText = (
        'background:transparent;border:none;outline:none;'
        + 'color:#e2e8f0;font-size:12px;width:105px;'
        + 'font-family:sans-serif;padding:0;'
      );

      // ── Clear button ───────────────────────────────────────────────────────
      var clr = L.DomUtil.create('span', '', row);
      clr.innerHTML = '&#10005;';
      clr.style.cssText = 'font-size:11px;cursor:pointer;color:#64748b;display:none;flex-shrink:0;';
      L.DomEvent.on(clr, 'click', function(){
        inp.value = '';
        clr.style.display = 'none';
        dropdown.style.display = 'none';
        inp.focus();
      });

      // ── Dropdown ───────────────────────────────────────────────────────────
      var dropdown = L.DomUtil.create('div', '', wrapper);
      dropdown.style.cssText = (
        'position:absolute;top:36px;left:0;z-index:9999;'
        + 'background:rgba(15,23,42,0.97);border:1px solid #334155;'
        + 'border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,0.7);'
        + 'max-height:400px;overflow-y:auto;min-width:260px;display:none;'
      );

      var _activeIdx = -1;
      var _items = [];

      function _highlight(idx) {
        _items.forEach(function(el, i){
          el.style.background = (i === idx) ? 'rgba(59,130,246,0.35)' : '';
        });
        _activeIdx = idx;
      }

      function _selectItem(item) {
        inp.value = item.name;
        dropdown.style.display = 'none';
        clr.style.display = 'inline';
        map.setView([item.lat, item.lon], 11, {animate:true, duration:0.8});
        // Fly Windy to same location
        if (typeof window.flyWindy === 'function') {
          window.flyWindy(item.lat, item.lon, 8);
        }
        // Fire synthetic click so Python receives last_clicked and updates session state.
        // Delay 900ms to let map animation finish first.
        setTimeout(function(){
          map.fire('click', { latlng: L.latLng(item.lat, item.lon) });
        }, 900);
      }

      function _buildDropdown(results, isTopList) {
        isTopList = !!isTopList;
        dropdown.innerHTML = '';
        _items = [];
        _activeIdx = -1;
        if (results.length === 0) {
          // Nếu query là region command (có trailing space chờ số) → ẩn dropdown
          // để không rơi vào geocodeAndFly khi Enter
          var _qNow = inp.value.trim().toLowerCase().replace(/\s+/g,' ');
          var _RNchk = ['bac','trung','nam','vietnam'];
          var _isRegionCmd = _RNchk.some(function(r){
            return _qNow === r || new RegExp('^'+r+' [1-6]$').test(_qNow)
              || new RegExp('^'+r+' *$').test(_qNow);
          }) || /^mkw(\s+(best|[1-6]))?$/.test(_qNow);
          if (_isRegionCmd) { dropdown.style.display = 'none'; return; }
          var empty = L.DomUtil.create('div', '', dropdown);
          empty.style.cssText = 'padding:10px 14px;color:#64748b;font-size:12px;';
          empty.textContent = 'No match — press Enter to geocode';
          dropdown.style.display = 'block';
          return;
        }
        // Header label
        var hdr = L.DomUtil.create('div', '', dropdown);
        hdr.style.cssText = 'padding:5px 14px 3px;font-size:10px;color:#475569;'
          + 'font-weight:700;letter-spacing:0.05em;text-transform:uppercase;'
          + 'border-bottom:1px solid rgba(51,65,85,0.5);';
        hdr.textContent = isTopList ? 'All locations (' + _DB.length + ')' : 'Results';
        results.slice(0, isTopList ? _DB.length : 30).forEach(function(item, i) {
          var el = L.DomUtil.create('div', '', dropdown);
          el.style.cssText = (
            'padding:7px 14px;cursor:pointer;font-size:12px;'
            + 'color:#cbd5e1;border-bottom:1px solid rgba(51,65,85,0.4);'
            + 'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
          );
          el.title = item.name;
          // Strip number prefix for display
          var cleanName = item.name.replace(/^\d+\.\s*/, '');
          el.textContent = cleanName;
          _items.push(el);
          L.DomEvent.on(el, 'click', function(){ _selectItem(item); });
          L.DomEvent.on(el, 'mouseover', function(){ _highlight(i); });
        });
        dropdown.style.display = 'block';
      }

      // ── Geocode fallback via Nominatim ─────────────────────────────────────
      function _geocodeAndFly(query) {
        var url = 'https://nominatim.openstreetmap.org/search?format=json&q='
          + encodeURIComponent(query) + '&limit=1';
        fetch(url, { headers: { 'User-Agent': 'AstroMapPro/7.0' }})
          .then(function(r){ return r.json(); })
          .then(function(data){
            if (data && data.length > 0) {
              var lat = parseFloat(data[0].lat);
              var lon = parseFloat(data[0].lon);
              map.setView([lat, lon], 11, {animate:true, duration:0.8});
              // Fly Windy to geocoded location
              if (typeof window.flyWindy === 'function') {
                window.flyWindy(lat, lon, 8);
              }
              dropdown.innerHTML = '';
              var found = L.DomUtil.create('div', '', dropdown);
              found.style.cssText = 'padding:8px 14px;font-size:12px;color:#34d399;';
              found.textContent = data[0].display_name;
              found.innerHTML = '&#128205; ' + data[0].display_name;
              dropdown.style.display = 'block';
              setTimeout(function(){
                map.fire('click', { latlng: L.latLng(lat, lon) });
              }, 900);
            } else {
              dropdown.innerHTML = '';
              var nf = L.DomUtil.create('div', '', dropdown);
              nf.style.cssText = 'padding:8px 14px;font-size:12px;color:#f87171;';
              nf.textContent = 'Location not found';
              dropdown.style.display = 'block';
            }
          })
          .catch(function(){
            dropdown.innerHTML = '';
            var err = L.DomUtil.create('div', '', dropdown);
            err.style.cssText = 'padding:8px 14px;font-size:12px;color:#f87171;';
            err.textContent = 'Geocoding error';
            dropdown.style.display = 'block';
          });
      }

      // ── Input events ───────────────────────────────────────────────────────
      // Show all locations on focus (when input is empty)
      L.DomEvent.on(inp, 'focus', function(){
        if (inp.value.trim() === '') {
          _buildDropdown(_DB, true);
        }
      });

      L.DomEvent.on(inp, 'blur', function(){
        // Slight delay so click on dropdown item fires first
        setTimeout(function(){
          if (inp.value.trim() === '') {
            dropdown.style.display = 'none';
          }
        }, 200);
      });

      L.DomEvent.on(inp, 'input', function(){
        var qRaw = inp.value.trim();
        var q = qRaw.toLowerCase().replace(/\u00A0/g, ' ').replace(/\s+/g, ' ');
        clr.style.display = q ? 'inline' : 'none';
        if (!q) { dropdown.style.display = 'none'; return; }
        var _REGION_LABEL = { bac:'Mien Bac', trung:'Mien Trung', nam:'Mien Nam', vietnam:'All Vietnam' };
        // ── "help" — hiển thị danh sách keyword, không thực hiện lệnh gì ──────
        if (/^help$/.test(q)) {
          dropdown.innerHTML = '';
          _items = []; _activeIdx = -1;
          var helpLines = [
            {label: 'Search area keyword:', desc: 'bac / trung / nam / vietnam', color: '#94a3b8'},
            {label: 'Search best location keyword:', desc: 'best', color: '#34d399'},
            {label: 'Search tonight keyword:', desc: 'tonight', color: '#fbcfe8'},
            {label: 'Turn off search results:', desc: 'off', color: '#94a3b8'},
          ];
          helpLines.forEach(function(h) {
            var row = L.DomUtil.create('div', '', dropdown);
            row.style.cssText = 'padding:7px 14px;font-size:12px;'
              + 'color:#cbd5e1;border-bottom:1px solid rgba(51,65,85,0.4);'
              + 'cursor:default;';
            var lbl = L.DomUtil.create('div', '', row);
            lbl.textContent = h.label; lbl.style.cssText = 'font-weight:700;color:' + h.color + ';margin-bottom:2px;';
            var desc = L.DomUtil.create('div', '', row);
            desc.textContent = h.desc; desc.style.cssText = 'font-size:11px;opacity:0.85;color:' + h.color + ';';
          });
          dropdown.style.display = 'block';
          return;
        }
        // ── "off" — tắt kết quả search ngay, không load data ──────────────────
        if (/^off$/.test(q)) {
          dropdown.innerHTML = '';
          _items = []; _activeIdx = -1;
          var row = L.DomUtil.create('div', '', dropdown);
          row.style.cssText = 'padding:7px 14px;cursor:pointer;font-size:12px;'
            + 'color:#94a3b8;display:flex;justify-content:space-between;align-items:center;';
          var lbl = L.DomUtil.create('span', '', row);
          lbl.textContent = 'off'; lbl.style.fontWeight = '700';
          var desc = L.DomUtil.create('span', '', row);
          desc.textContent = 'Turn off search results'; desc.style.cssText = 'font-size:10px;opacity:0.65;';
          L.DomEvent.on(row, 'click', function(){
            inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
            if (typeof window._triggerOff === 'function') window._triggerOff();
          });
          dropdown.style.display = 'block';
          return;
        }
        // Hidden keyword — "<region>" / "<region> N" / "best <region>" / "tonight <region>"
        // NOTE: q is already normalized (single space between words) by the input handler above,
        // so we use a literal space character here instead of \s+ to avoid any risk of backslash
        // characters being altered across Python/Jinja2/iframe-srcdoc serialization layers.
        var _REGION_NAMES = ['bac','trung','nam','vietnam'];
        var _regionPattern = '(' + _REGION_NAMES.join('|') + ')';
        var _bareRegionRe  = new RegExp('^' + _regionPattern + '( [1-6])?$');
        var _bareTypingRe  = new RegExp('^' + _regionPattern + ' *$');
        var _regionBestRe  = new RegExp('^' + _regionPattern + ' best$');
        var _bestRegionRe   = new RegExp('^best( ' + _regionPattern + ')?$');
        var _tonightRegionRe= new RegExp('^tonight( ' + _regionPattern + ')?$');
        var _qIsBest    = (q === 'best' || q.indexOf('best ') === 0);
        var _qIsTonight = (q === 'tonight' || q.indexOf('tonight ') === 0);
        var _qIsRegionBest = _regionBestRe.test(q);
        var _qIsBareRegion = _bareRegionRe.test(q) || _bareTypingRe.test(q);
        console.log('[mkw-debug] q=', JSON.stringify(q), 'qIsBareRegion=', _qIsBareRegion, 'qIsBest=', _qIsBest, 'qIsTonight=', _qIsTonight);
        console.log('[mkw-debug] _bareRegionRe.source=', JSON.stringify(_bareRegionRe.source));
        console.log('[mkw-debug] _bareRegionRe.toString=', _bareRegionRe.toString());
        console.log('[mkw-debug] _regionPattern=', JSON.stringify(_regionPattern));
        if (_qIsBest || _qIsTonight || _qIsRegionBest || _qIsBareRegion) {
          dropdown.innerHTML = '';
          _items = []; _activeIdx = -1;
          function _renderRegionHints(items, color, borderRgba) {
            items.forEach(function(h) {
              var row = L.DomUtil.create('div', '', dropdown);
              row.style.cssText = 'padding:7px 14px;cursor:pointer;font-size:12px;'
                + 'color:' + color + ';border-bottom:1px solid ' + borderRgba + ';'
                + 'display:flex;justify-content:space-between;align-items:center;';
              var lbl = L.DomUtil.create('span', '', row);
              lbl.textContent = h.label; lbl.style.fontWeight = '700';
              var desc = L.DomUtil.create('span', '', row);
              desc.textContent = h.desc; desc.style.cssText = 'font-size:10px;opacity:0.65;';
              L.DomEvent.on(row, 'click', (function(fn){ return function(){
                inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
                fn();
              }; })(h.fn));
              _items.push(row);  // ← push vào _items để Enter key có thể click
            });
            dropdown.style.display = 'block';
          }
          // Helper: lấy danh sách region khớp với prefix đã gõ (sau keyword "best"/"tonight")
          function _filterRegionsByPrefix(typedAfterKeyword) {
            var prefix = typedAfterKeyword ? typedAfterKeyword.trim() : '';
            if (!prefix) return _REGION_NAMES;
            // Nếu là exact region → chỉ trả về region đó
            if (_REGION_NAMES.indexOf(prefix) !== -1) return [prefix];
            // Không phải exact → filter theo startsWith prefix
            return _REGION_NAMES.filter(function(r){ return r.indexOf(prefix) === 0; });
          }
          if (_qIsRegionBest) {
            var _mRB = q.match(_regionBestRe);
            var _rbRegion = _mRB ? _mRB[1] : null;
            if (_rbRegion) {
              _renderRegionHints([{
                label: _rbRegion + ' best', desc: 'Best night 7d (' + _REGION_LABEL[_rbRegion] + ')',
                fn: (function(rr){ return function(){ window._triggerBest(rr); }; })(_rbRegion)
              }], '#34d399', 'rgba(51,65,85,0.4)');
            }
            return;
          }
          if (_qIsTonight) {
            var _typedTn = q.slice('tonight'.length).trim(); // phần sau "tonight"
            var _regionsTn = _filterRegionsByPrefix(_typedTn);
            var tonightHints = _regionsTn.map(function(r){
              return {label: 'tonight ' + r, desc: 'Best spots tonight (' + _REGION_LABEL[r] + ')',
                       fn: (function(rr){ return function(){ window._triggerTonight(rr); }; })(r)};
            });
            _renderRegionHints(tonightHints, '#fbcfe8', 'rgba(251,207,232,0.2)');
            return;
          }
          if (_qIsBest) {
            var _typedBest = q.slice('best'.length).trim(); // phần sau "best"
            var _regionsBest = _filterRegionsByPrefix(_typedBest);
            var bestHints = _regionsBest.map(function(r){
              return {label: 'best ' + r, desc: 'Best night 7d (' + _REGION_LABEL[r] + ')',
                       fn: (function(rr){ return function(){ window._triggerBest(rr); }; })(r)};
            });
            _renderRegionHints(bestHints, '#34d399', 'rgba(51,65,85,0.4)');
            return;
          }
          // ── Bare region command — rewritten from scratch, mirrors mkw dropdown exactly ──
          var _mBare = q.match(_bareRegionRe);
          var _region = _mBare ? _mBare[1] : (q.match(_bareTypingRe)||[])[1];
          var _suffix = (_mBare && _mBare[2]) ? _mBare[2].trim() : null; // '1'~'6' | null
          var _regionDayLbl = ['Tonight','Tomorrow night','Day after tomorrow','4th night','5th night','6th night'];
          if (_suffix !== null) {
            // Exact command e.g. 'bac 3' → single clickable row (same as 'mkw 3')
            var _dayNum = parseInt(_suffix);
            _renderRegionHints([{
              label: _region + ' ' + _dayNum,
              desc:  _regionDayLbl[_dayNum - 1] + ' (' + _REGION_LABEL[_region] + ')',
              fn: (function(rr,nn){ return function(){ window._triggerRegionScan(rr,nn); }; })(_region,_dayNum)
            }], '#34d399', 'rgba(51,65,85,0.4)');
            return;
          }
          // 'bac' (no number) → full menu: bac best + bac 1..6 (same shape as 'mkw' bare menu)
          var _regionHints = [{
            label: _region + ' best', desc: 'Best night 7d (' + _REGION_LABEL[_region] + ')',
            fn: (function(rr){ return function(){ window._triggerBest(rr); }; })(_region)
          }];
          for (var _rn = 1; _rn <= 6; _rn++) {
            _regionHints.push({label: _region + ' ' + _rn, desc: _regionDayLbl[_rn - 1] + ' (' + _REGION_LABEL[_region] + ')',
              fn: (function(rr,nn){ return function(){ window._triggerRegionScan(rr,nn); }; })(_region,_rn)});
          }
          _renderRegionHints(_regionHints, '#34d399', 'rgba(51,65,85,0.4)');
          return;
        }

        // ── mkw commands (private): 'mkw 1'~'mkw 6' / 'mkw best' ──────────────
        if (/^mkw(\s+(best|[1-6]))?$/.test(q)) {
          dropdown.innerHTML = ''; _items = []; _activeIdx = -1;
          var _mkwHints = [];
          if (q === 'mkw' || q === 'mkw ') {
            // show full menu
            _mkwHints.push({label:'mkw best', desc:'Best night 7d (My locations)', fn:function(){ window._triggerMkwBest(); }});
            var _mkwDl = ['Tonight','Tomorrow night','Day after tomorrow','4th night','5th night','6th night'];
            for (var _mi=1; _mi<=6; _mi++) {
              _mkwHints.push({label:'mkw '+_mi, desc:_mkwDl[_mi-1]+' (My locations)',
                fn:(function(dd){ return function(){ window._triggerMkwScan(dd); }; })(_mi)});
            }
          } else if (q === 'mkw best') {
            _mkwHints.push({label:'mkw best', desc:'Best night 7d (My locations)', fn:function(){ window._triggerMkwBest(); }});
          } else {
            var _mkwN = parseInt(q.replace('mkw','').trim());
            var _mkwDl2 = ['Tonight','Tomorrow night','Day after tomorrow','4th night','5th night','6th night'];
            _mkwHints.push({label:'mkw '+_mkwN, desc:_mkwDl2[_mkwN-1]+' (My locations)',
              fn:(function(dd){ return function(){ window._triggerMkwScan(dd); }; })(_mkwN)});
          }
          _mkwHints.forEach(function(h){
            var row = L.DomUtil.create('div','',dropdown);
            row.style.cssText = 'padding:7px 14px;cursor:pointer;font-size:12px;'
              +'color:#a78bfa;border-bottom:1px solid rgba(167,139,250,0.25);'
              +'display:flex;justify-content:space-between;align-items:center;';
            var lbl=L.DomUtil.create('span','',row); lbl.textContent=h.label; lbl.style.fontWeight='700';
            var desc=L.DomUtil.create('span','',row); desc.textContent=h.desc; desc.style.cssText='font-size:10px;opacity:0.65;';
            L.DomEvent.on(row,'click',(function(fn){ return function(){
              inp.value=''; clr.style.display='none'; dropdown.style.display='none'; fn();
            }; })(h.fn));
            _items.push(row);
          });
          dropdown.style.display = 'block';
          return;
        }
        // Translate any kanji substrings in the query to their romaji alias
        var translations = [];
        for (var kanji in _ALIAS) {
          if (qRaw.indexOf(kanji) !== -1) {
            translations.push(_ALIAS[kanji].toLowerCase());
          }
        }

        var results = _DB.filter(function(item){
          var nl = item.name.toLowerCase();
          if (nl.indexOf(q) !== -1) return true;
          for (var i = 0; i < translations.length; i++) {
            if (nl.indexOf(translations[i]) !== -1) return true;
          }
          return false;
        });
        _buildDropdown(results);
      });

      L.DomEvent.on(inp, 'keydown', function(e){
        if (e.key === 'Enter') {
          e.preventDefault();
          // ── Hidden SCAN trigger: "<region>" / "<region> N" / "best <region>" / "tonight <region>" + Enter ──
          var _sv = inp.value.trim().toLowerCase().replace(/\u00A0/g, ' ').replace(/\s+/g, ' ');
          if (_sv === 'off') {
            inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
            if (typeof window._triggerOff === 'function') window._triggerOff();
            return;
          }
          if (_sv === 'help') {
            // "help" chỉ hiển thị gợi ý, không thực hiện hành động khi Enter
            return;
          }
          var _RN = ['bac','trung','nam','vietnam'];
          var _rgx = '(' + _RN.join('|') + ')';
          var _mTonight = _sv.match(new RegExp('^tonight( ' + _rgx + ')?$'));
          if (_mTonight) {
            var _rTn = _mTonight[2] || 'bac';
            inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
            if (typeof window._triggerTonight === 'function') window._triggerTonight(_rTn);
            return;
          }
          var _mBest = _sv.match(new RegExp('^best( ' + _rgx + ')?$'));
          if (_mBest) {
            var _rBest = _mBest[2] || 'bac';
            inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
            if (typeof window._triggerBest === 'function') window._triggerBest(_rBest);
            return;
          }
          var _mScan = _sv.match(new RegExp('^' + _rgx + ' ([1-6])$'));
          if (_mScan) {
            var _rScan = _mScan[1];
            var _days = parseInt(_mScan[2]);
            inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
            if (typeof window._triggerRegionScan === 'function') window._triggerRegionScan(_rScan, _days);
            return;
          }
          var _mRegionBest = _sv.match(new RegExp('^' + _rgx + ' best$'));
          if (_mRegionBest) {
            var _rRB = _mRegionBest[1];
            inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
            if (typeof window._triggerBest === 'function') window._triggerBest(_rRB);
            return;
          }
          // Defensive fallback: "tonight ..." / "best ..." that didn't parse cleanly above
          // (e.g. unexpected whitespace) still triggers rather than falling through to geocode.
          if (/^tonight(\s|$)/.test(_sv)) {
            var _rTnFb = 'bac';
            for (var _i = 0; _i < _RN.length; _i++) { if (_sv.indexOf(_RN[_i]) !== -1) { _rTnFb = _RN[_i]; break; } }
            inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
            if (typeof window._triggerTonight === 'function') window._triggerTonight(_rTnFb);
            return;
          }
          if (/^best(\s|$)/.test(_sv)) {
            var _rBestFb = 'bac';
            for (var _j = 0; _j < _RN.length; _j++) { if (_sv.indexOf(_RN[_j]) !== -1) { _rBestFb = _RN[_j]; break; } }
            inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
            if (typeof window._triggerBest === 'function') window._triggerBest(_rBestFb);
            return;
          }
          // mkw commands in keydown
          if (/^mkw\s+best$/.test(_sv)) {
            inp.value=''; clr.style.display='none'; dropdown.style.display='none';
            if (typeof window._triggerMkwBest==='function') window._triggerMkwBest();
            return;
          }
          var _mkwMatch = _sv.match(/^mkw\s+([1-6])$/);
          if (_mkwMatch) {
            inp.value=''; clr.style.display='none'; dropdown.style.display='none';
            if (typeof window._triggerMkwScan==='function') window._triggerMkwScan(parseInt(_mkwMatch[1]));
            return;
          }
          if (dropdown.style.display === 'none') {
            // Dropdown ẩn nhưng có thể là region command → check trước khi return
            var _mScanH = _sv.match(new RegExp('^' + _rgx + ' ([1-6])$'));
            if (_mScanH) {
              var _rScanH = _mScanH[1];
              var _daysH = parseInt(_mScanH[2]);
              inp.value = ''; clr.style.display = 'none';
              if (typeof window._triggerRegionScan === 'function') window._triggerRegionScan(_rScanH, _daysH);
            }
            return;
          }
          if (_activeIdx >= 0 && _activeIdx < _items.length) {
            _items[_activeIdx].click();
          } else {
            // Last-resort: nếu dropdown đang hiện nhưng không có item được chọn,
            // thử match region command một lần nữa trước khi geocode
            var _RN2 = ['bac','trung','nam','vietnam'];
            var _rgx2 = '(' + _RN2.join('|') + ')';
            var _mScan2 = _sv.match(new RegExp('^' + _rgx2 + ' ([1-6])$'));
            if (_mScan2) {
              var _rScan2 = _mScan2[1];
            var _days2 = parseInt(_mScan2[2]);
              inp.value = ''; clr.style.display = 'none'; dropdown.style.display = 'none';
              if (typeof window._triggerRegionScan === 'function') window._triggerRegionScan(_rScan2, _days2);
              return;
            }
            dropdown.style.display = 'none';
            _geocodeAndFly(inp.value.trim());
          }
          return;
        }
        if (dropdown.style.display === 'none') return;
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          _highlight(Math.min(_activeIdx + 1, _items.length - 1));
          if (_items[_activeIdx]) _items[_activeIdx].scrollIntoView({block:'nearest'});
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          _highlight(Math.max(_activeIdx - 1, 0));
          if (_items[_activeIdx]) _items[_activeIdx].scrollIntoView({block:'nearest'});
        } else if (e.key === 'Escape') {
          dropdown.style.display = 'none';
        }
      });

      // Close dropdown when clicking outside
      map.on('click', function(){ dropdown.style.display = 'none'; });

      return wrapper;
    }
  });
  new SearchCtrl().addTo({{ this._parent.get_name() }});
})();
{% endmacro %}
""")

class _SearchControl(MacroElement):
    def __init__(self, loc_list="[]", alias_dict="{}"):
        super().__init__()
        self._name = '_SearchControl'
        self._template = _SEARCH_CTRL_TEMPLATE
        self.loc_list = loc_list
        self.alias_dict = alias_dict

_SearchControl(loc_list=_loc_js_list, alias_dict=_kanji_alias_js).add_to(m)

# ── CSS cho tooltip (hover) ────────────────────────────────────────────────────
m.get_root().html.add_child(folium.Element("""
<style>
.leaflet-tooltip {
    background: white !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
    padding: 6px !important;
    max-width: 240px !important;
}
.leaflet-tooltip::before { display: none !important; }
.leaflet-control-attribution { display: none !important; }
</style>
"""))

# ── LOCATION MARKERS ──────────────────────────────────────────────────────────
import os, base64

def _get_loc_image_b64(loc_name: str):
    """Tìm ảnh theo số thứ tự ở đầu tên địa danh (vd: '23. Hoshinomura...' → tìm images/23.*).
    Trả về (base64_string, mime_type) hoặc (None, None) nếu không tìm thấy."""
    num = loc_name.split(".")[0].strip()
    img_dir = os.path.join(os.path.dirname(__file__), "images")
    if not os.path.isdir(img_dir):
        return None, None
    for ext, mime in [("jpg","image/jpeg"),("jpeg","image/jpeg"),("png","image/png"),("webp","image/webp")]:
        path = os.path.join(img_dir, f"{num}.{ext}")
        if os.path.isfile(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode(), mime
    return None, None

_selected_marker_args = None  # lưu lại marker được chọn, vẽ sau cùng để nổi lên trên

# ── Region color map — mỗi vùng 1 màu riêng để phân biệt trên map ─────────────
# prefecture → (normal_color, selected_color, selected_glow)
_PREF_REGION_COLOR = {
    # Mien Bac (North) — cyan
    "Ha Giang": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Cao Bang": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Lang Son": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Lao Cai": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Yen Bai": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Bac Kan": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Bac Giang": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Phu Tho": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Vinh Phuc": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Hanoi": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Hoa Binh": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Son La": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Quang Ninh": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Nam Dinh": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    "Ninh Binh": ("#22D3EE", "#00FFFF", "drop-shadow(0 0 7px cyan)"),
    # Mien Trung (Central) — orange
    "Thanh Hoa": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Nghe An": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Quang Binh": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Quang Tri": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Thua Thien Hue": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Da Nang": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Quang Nam": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Quang Ngai": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Binh Dinh": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Phu Yen": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Khanh Hoa": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Ninh Thuan": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Binh Thuan": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Kon Tum": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Gia Lai": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Dak Lak": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Dak Nong": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    "Lam Dong": ("#FB923C", "#FF6A00", "drop-shadow(0 0 7px #FB923C)"),
    # Mien Nam (South) — green
    "Ho Chi Minh City": ("#86EFAC", "#4ADE80", "drop-shadow(0 0 7px #86EFAC)"),
    "Dong Nai": ("#86EFAC", "#4ADE80", "drop-shadow(0 0 7px #86EFAC)"),
    "Ba Ria - Vung Tau": ("#86EFAC", "#4ADE80", "drop-shadow(0 0 7px #86EFAC)"),
    "Tay Ninh": ("#86EFAC", "#4ADE80", "drop-shadow(0 0 7px #86EFAC)"),
    "Long An": ("#86EFAC", "#4ADE80", "drop-shadow(0 0 7px #86EFAC)"),
    "Dong Thap": ("#86EFAC", "#4ADE80", "drop-shadow(0 0 7px #86EFAC)"),
    "Kien Giang": ("#86EFAC", "#4ADE80", "drop-shadow(0 0 7px #86EFAC)"),
    "Ca Mau": ("#86EFAC", "#4ADE80", "drop-shadow(0 0 7px #86EFAC)"),
}
_DEFAULT_COLOR = ("#FFA500", "#FFD700", "drop-shadow(0 0 6px gold)")

def _get_star_colors(loc_name):
    """Extract prefecture from loc name (last segment after last comma) and return colors."""
    parts = loc_name.rsplit(",", 1)
    pref = parts[-1].strip() if len(parts) > 1 else ""
    return _PREF_REGION_COLOR.get(pref, _DEFAULT_COLOR)

for loc_name, loc_coords in LOCATION_DATABASE.items():
    is_sel = abs(loc_coords[0]-st.session_state.lat)<0.001 and abs(loc_coords[1]-st.session_state.lon)<0.001
    try:
        loc_num = int(loc_name.split(".")[0].strip())
    except ValueError:
        loc_num = 99
    is_frequent = (loc_num <= 27)
    _nc, _sc, _sg = _get_star_colors(loc_name)
    if is_sel:
        star_color = _sc
        star_glow  = _sg
        star_size  = "22px"
    else:
        star_color = _nc
        star_glow  = "none"
        star_size  = "16px"
    b64, mime = _get_loc_image_b64(loc_name)
    if b64:
        img_html = (f'<img src="data:{mime};base64,{b64}" '
                    f'style="width:220px;max-height:150px;object-fit:cover;border-radius:6px;'
                    f'display:block;margin-bottom:6px;">')
    else:
        img_html = ""
    _loc_label = _strip_loc_num(loc_name)
    _label_fs = 13 if len(_loc_label) <= 28 else (11 if len(_loc_label) <= 38 else 9.5)
    tooltip_html = (f'<div style="font-family:sans-serif;font-size:{_label_fs}px;font-weight:600;'
                    f'color:#1e293b;max-width:230px;line-height:1.35;'
                    f'white-space:normal;word-break:break-word;overflow-wrap:break-word;">'
                    f'{img_html}{_loc_label}</div>')
    if is_sel:
        # Ngôi sao được chọn: nhấp nháy (pulse) để dễ nhận biết + z-index cao để
        # không bị các ngôi sao khác che mất khi zoom nhỏ.
        _star_html = (
            f'<style>@keyframes star-pulse-sel {{'
            f'0%,100%{{transform:scale(1);opacity:1;}}'
            f'50%{{transform:scale(1.35);opacity:0.55;}}}}</style>'
            f'<div style="font-size:{star_size};color:{star_color};'
            f'text-shadow:0 0 4px rgba(0,0,0,0.9);filter:{star_glow};'
            f'cursor:pointer;line-height:1;font-family:serif;'
            f'animation:star-pulse-sel 1.1s ease-in-out infinite;'
            f'transform-origin:center;display:inline-block;'
            f'position:relative;z-index:10000;">★</div>'
        )
        # Lưu lại, vẽ sau cùng (sau loop) để marker này nằm trên cùng DOM stack
        _selected_marker_args = (loc_coords, _star_html, tooltip_html)
        continue
    else:
        _star_html = (
            f'<div style="font-size:{star_size};color:{star_color};'
            f'text-shadow:0 0 4px rgba(0,0,0,0.9);filter:{star_glow};'
            f'cursor:pointer;line-height:1;font-family:serif;">★</div>'
        )
    folium.Marker(
        loc_coords,
        icon=folium.DivIcon(
            html=_star_html,
            icon_size=(24,24), icon_anchor=(12,12)),
        tooltip=folium.Tooltip(tooltip_html, sticky=False, offset=(20, -10), parse_html=False),
    ).add_to(m)

# ── Vẽ marker được chọn SAU CÙNG → nằm trên cùng trong DOM stack của Leaflet ──
# Leaflet gắn className của DivIcon trực tiếp lên thẻ .leaflet-marker-icon (chính
# thẻ có inline z-index do Leaflet tự set theo vị trí lat). Dùng class riêng +
# CSS !important để ép z-index của marker được chọn luôn cao nhất, không bị
# các sao khác (kể cả ở lat thấp hơn → z-index Leaflet cao hơn) che mất.
if _selected_marker_args:
    _sel_coords, _sel_html, _sel_tooltip = _selected_marker_args
    m.get_root().html.add_child(folium.Element("""
        <style>
            .selected-star-marker { z-index: 999999 !important; }
        </style>
    """))
    folium.Marker(
        _sel_coords,
        icon=folium.DivIcon(
            html=_sel_html,
            icon_size=(24,24), icon_anchor=(12,12),
            class_name="selected-star-marker"),
        tooltip=folium.Tooltip(_sel_tooltip, sticky=False, offset=(20, -10), parse_html=False),
    ).add_to(m)

is_bookmark = any(abs(c[0]-st.session_state.lat)<0.001 and abs(c[1]-st.session_state.lon)<0.001
                  for c in LOCATION_DATABASE.values())

# ── GREAT NIGHT SCAN result — vòng tròn nhấp nháy quanh tất cả địa điểm ──────
# Kích thước cố định theo pixel (DivIcon) → không thay đổi khi zoom in/out.
_scan_r = st.session_state._scan_result
if _scan_r and _scan_r != "none":
    # ── Ring helper — CSS injected once, ring div absolutely centered on the coordinate ──
    # icon_size=(0,0) / icon_anchor=(0,0): Leaflet places the DivIcon origin exactly at
    # the lat/lon pixel. The ring div uses position:absolute + transform:translate(-50%,-50%)
    # to center itself around that origin — no offset from <style> tags possible.
    _ring_css = (
        '<style>'
        '@keyframes great-night-pulse {'
        '0%{transform:translate(-50%,-50%) scale(0.6);opacity:0.9;}'
        '70%{transform:translate(-50%,-50%) scale(2.2);opacity:0;}'
        '100%{transform:translate(-50%,-50%) scale(0.6);opacity:0;}}'
        '.great-night-ring{'
        'pointer-events:none!important;'
        'overflow:visible!important;}'
        '</style>'
    )

    def _make_ring_div(color, shadow):
        return (
            '<div style="position:absolute;top:0;left:0;'
            'width:64px;height:64px;border-radius:50%;'
            f'border:3px solid {color};'
            f'box-shadow:0 0 14px {shadow};'
            'animation:great-night-pulse 1.8s ease-out infinite;'
            'pointer-events:none;"></div>'
        )

    def _add_rings(locations, color, shadow, css_already_injected=False):
        """Render ring markers for a list of (lat,lon) or (name,coords,verdict) entries."""
        ring_div = _make_ring_div(color, shadow)
        for _i, entry in enumerate(locations):
            coords = entry[1] if isinstance(entry[0], str) else list(entry)
            _html = (_ring_css if (_i == 0 and not css_already_injected) else "") + ring_div
            folium.Marker(
                list(coords),
                icon=folium.DivIcon(
                    html=_html,
                    icon_size=(0, 0), icon_anchor=(0, 0),
                    class_name="great-night-ring"),
            ).add_to(m)
        return True  # css injected

    _is_best_ring    = st.session_state.get("_scan_best", False)
    _is_tonight_ring = st.session_state.get("_scan_tonight", False)

    if _is_tonight_ring:
        _top3_ring_tn = _scan_r.get("top3", None)
        if _top3_ring_tn:
            # top3 entries: (date, day_off, loc_name, loc_coords, verdict, moon_illum, is_weekend)
            _locs_tn = [(_tln3, _tlc3, None) for _, _, _tln3, _tlc3, *_ in _top3_ring_tn]
        else:
            _locs_tn = _scan_r.get("all_locs", [(_scan_r["loc_name"], _scan_r["loc_coords"], _scan_r["verdict"])])
        _add_rings(_locs_tn, "#fbcfe8", "rgba(251,207,232,0.85)")

    elif _is_best_ring:
        _top3_ring = _scan_r.get("top3", None)
        if _top3_ring:
            _locs_best = [(_tln3, _tlc3, None) for _, _, _tln3, _tlc3, *_ in _top3_ring]
        else:
            _locs_best = _scan_r.get("all_locs", [(_scan_r["loc_name"], _scan_r["loc_coords"], _scan_r["verdict"])])
        _add_rings(_locs_best, "#fbbf24", "rgba(251,191,36,0.85)")

    else:
        # Scan command: vẽ vòng tròn xanh cho tất cả địa điểm PERFECT NIGHT
        _all_locs = _scan_r.get("all_locs", [(_scan_r["loc_name"], _scan_r["loc_coords"], _scan_r["verdict"])])
        _add_rings(_all_locs, "#6ee7b7", "rgba(110,231,183,0.8)")

if not is_bookmark:
    folium.Marker(
        [st.session_state.lat, st.session_state.lon],
        icon=folium.DivIcon(
            html='<div style="font-size:28px;line-height:1;filter:drop-shadow(0 0 6px rgba(255,50,50,0.9));cursor:pointer;">📍</div>',
            icon_size=(32,32), icon_anchor=(10,30)),
        tooltip=folium.Tooltip(f"📍 {_strip_loc_num(st.session_state.location_name)}", sticky=True)
    ).add_to(m)

# ── st_folium ─────────────────────────────────────────────────────────────────
# QUAN TRỌNG: KHÔNG đưa "zoom"/"center" vào returned_objects.
# Nếu có → mỗi pan/zoom map trả data về Python → Streamlit rerun → map refresh.
# Chỉ return những gì cần xử lý click. Zoom/center được lưu qua _need_fly flag.
_map_key = "astro_map_main"
_stfolium_kwargs = dict(
    width='stretch', height=575, key=_map_key,
    returned_objects=["last_clicked", "last_object_clicked_tooltip"],
)
if st.session_state._need_fly:
    _stfolium_kwargs["center"] = st.session_state.map_center
    st.session_state._need_fly = False   # reset ngay — chỉ fly 1 lần
map_data = st_folium(m, **_stfolium_kwargs)

# ── TOP-CENTER MAP LABEL — NIGHT VERDICT (full night 18:00~06:00) ────────────
if st.session_state.day_offset == 0:
    (_full_table_data, _full_hours_labels, _full_moon_alt, _full_sun_alt, *_rest_full) = _build_night_data(
        st.session_state.lat, st.session_state.lon,
        tuple(_full_night_slots),
        _hourly_frozen,
        st.session_state.weather_source,
        loc_utc_offset_h,
    )
    _verdict = _build_night_verdict(_full_table_data, _full_sun_alt, moon_pct)
else:
    _verdict = _build_night_verdict(weather_table_data, sun_altitudes, moon_pct)
if _verdict:
    # ── Tính nhiệt độ min/max của đêm (18:00~06:00) ──────────────────────────
    if st.session_state.day_offset == 0:
        _temp_src_table = _full_table_data
    else:
        _temp_src_table = weather_table_data
    _night_temps = [r.get("_temp") for r in _temp_src_table[:12] if r.get("_temp") is not None]
    if _night_temps:
        _temp_range_str = f"{round(max(_night_temps))}°-{round(min(_night_temps))}°"
    else:
        _temp_range_str = ""

    # ── Date label: "Tonight" nếu day_offset=0, còn lại "MM/DD night(min°~max°)" ─
    if st.session_state.day_offset == 0:
        _date_label = f"Tonight{f' ({_temp_range_str})' if _temp_range_str else ''}"
    else:
        _date_label = f"{target_date.month}/{target_date.day} night{f' ({_temp_range_str})' if _temp_range_str else ''}"

    _warn_speed = "1.1s" if _verdict["anim"] == "blink-warn" else "1.9s"
    _html_label = f"""
<style>
@keyframes blink-warn   {{0%,100%{{opacity:1}}50%{{opacity:0.25}}}}
@keyframes blink-smile  {{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:0.80;transform:scale(1.05)}}}}
@keyframes blink-neutral{{0%,100%{{opacity:1}}50%{{opacity:0.55}}}}
.astro-maplabel{{
  position:absolute;top:40px;left:50%;transform:translateX(-50%);
  z-index:9999;pointer-events:none;
  display:inline-flex;flex-direction:column;align-items:center;gap:1px;
  padding:5px 18px 6px 14px;border-radius:22px;
  font-family:sans-serif;
  white-space:nowrap;
  box-shadow:0 2px 16px rgba(0,0,0,0.75);
  backdrop-filter:blur(3px);
  background:{_verdict["bg"]};border:1.5px solid {_verdict["border"]};color:{_verdict["color"]};
}}
.astro-maplabel-top{{ font-size:9px;opacity:0.55;font-weight:600;letter-spacing:0.04em;line-height:1.2; }}
.astro-maplabel-main{{ display:flex;align-items:center;gap:7px;font-size:13px;font-weight:700;line-height:1.3; }}
.astro-maplabel-stars{{ font-size:11px;opacity:0.85;letter-spacing:1px; }}
.astro-maplabel-sub{{ font-size:10px;opacity:0.65;font-weight:500; }}
</style>
<div style="position:relative;margin-top:-644px;height:0;overflow:visible;z-index:9999;">
<div class="astro-maplabel">
  <span class="astro-maplabel-top">{_date_label}</span>
  <div class="astro-maplabel-main">
    <span style="animation:{_verdict["anim"]} {_warn_speed} ease-in-out infinite;display:inline-block;font-size:17px;">{_verdict["icon"]}</span>
    <span>{_verdict["tier"]}</span>
    <span class="astro-maplabel-stars">{_verdict["stars"]}</span>
    <span class="astro-maplabel-sub">{_verdict["sub"]}</span>
  </div>
</div>
</div>"""
    st.markdown(_html_label, unsafe_allow_html=True)

# ── SCAN RESULT BANNER — overlay bottom-left của map ────────────────────────
# Dùng cùng cơ chế margin-top âm như top-center label (đã được xác nhận hoạt động).
# Map height=575. top-center dùng margin-top=-644, position:absolute;top:40px.
# Bottom-left: margin-top=-644 + position:absolute;top:505px (575-56px banner-14px padding)
_scan_r2 = st.session_state._scan_result

if _scan_r2 and _scan_r2 != "none":
    _sr_date2   = _scan_r2["date"]
    _all_locs2  = _scan_r2.get("all_locs", [(_scan_r2["loc_name"], _scan_r2["loc_coords"], _scan_r2["verdict"])])
    _n_spots    = len(_all_locs2)
    _is_best_banner = st.session_state.get("_scan_best", False)
    _is_tonight_banner = st.session_state.get("_scan_tonight", False)
    _sr_tier    = _scan_r2["verdict"].get("tier", "PERFECT NIGHT")
    _top3       = _scan_r2.get("top3", None)

    if _is_tonight_banner and _top3:
        # ── Tonight banner: pink theme, top3 đêm nay ────────────────────────────
        _EN_WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        _rank_icons = ["🥇", "🥈", "🥉"]
        _rows_html_parts_tn = []
        _top3_len_tn = len(_top3)
        for _i, (_td, _tdoff, _tln, _tlc, _tv, _tmi, _tiw) in enumerate(_top3):
            _rank_icon = _rank_icons[_i] if _i < 3 else "▪"
            _short_name = _tln.split(",")[0].strip()
            _short_name = _short_name.split(".", 1)[-1].strip() if "." in _short_name else _short_name
            _streak = _tv.get("best_streak", 0)
            _stars = _tv.get("stars", "")
            _day_str = f"{_td.month}/{_td.day} {_EN_WD[_td.weekday()]}"
            _is_last_row_tn = (_i == _top3_len_tn - 1)
            _row_border_tn = "" if _is_last_row_tn else "border-bottom:1px solid rgba(251,207,232,0.22);"
            _rows_html_parts_tn.append(
                f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;{_row_border_tn}">'
                f'<span style="font-size:15px;flex-shrink:0;">{_rank_icon}</span>'
                f'<span style="color:#fbcfe8;font-weight:700;font-size:13px;flex:1;'
                f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{_short_name}</span>'
                f'<span style="color:#f9a8d4;font-size:11px;flex-shrink:0;">{_day_str}</span>'
                f'<span style="color:#f472b6;font-size:12px;flex-shrink:0;">{_stars}</span>'
                f'<span style="color:#fbcfe8;font-size:10px;flex-shrink:0;">{_streak}h</span>'
                f'</div>'
            )
        _moon_tn = _scan_r2["moon_illum"]
        _rows_joined_tn = "".join(_rows_html_parts_tn)
        _region_lbl_tn = _REGION_LABELS.get(_scan_r2.get("region", "bac"), "Mien Bac (North)")
        st.markdown(f"""
<div style="position:relative;margin-top:-644px;height:0;overflow:visible;z-index:9998;pointer-events:none;">
<div style="
  position:absolute;top:457px;left:2px;
  width:320px;
  background:rgba(40,5,20,0.95);border:1.5px solid rgba(251,207,232,0.80);
  border-radius:10px;padding:8px 12px;
  font-family:sans-serif;
  box-shadow:0 2px 16px rgba(0,0,0,0.75);backdrop-filter:blur(3px);
  pointer-events:none;
">
<div style="color:#fbcfe8;font-size:10px;font-weight:700;letter-spacing:0.5px;margin-bottom:6px;">
🌸 Tonight — best spots ({_region_lbl_tn}) / moon {_moon_tn:.0f}%
</div>
{_rows_joined_tn}
</div>
</div>""", unsafe_allow_html=True)
    elif _is_best_banner and _top3:
        # ── Best banner: hiện 3 địa điểm xếp hạng cao nhất ─────────────────────
        _EN_WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        _top3_dates_seen = set()
        _top3_dates_list = []
        for (_td, _tdoff, _tln, _tlc, _tv, _tmi, _tiw) in _top3:
            _dk = _td.strftime("%Y-%m-%d")
            if _dk not in _top3_dates_seen:
                _top3_dates_seen.add(_dk)
                _top3_dates_list.append(_td)
        if len(_top3_dates_list) == 1:
            _dh0 = _top3_dates_list[0]
            _date_header = f"Best locations this week ({_dh0.month}/{_dh0.day} {_EN_WD[_dh0.weekday()]})"
        else:
            _dparts = [f"{_dx.month}/{_dx.day} {_EN_WD[_dx.weekday()]}" for _dx in _top3_dates_list]
            _date_header = f"Best locations this week ({', '.join(_dparts)})"
        _region_lbl_best = _REGION_LABELS.get(_scan_r2.get("region", "bac"), "Mien Bac (North)")
        _date_header = f"{_date_header} — {_region_lbl_best}"
        _rank_icons = ["🥇", "🥈", "🥉"]
        _rows_html_parts = []
        _top3_len = len(_top3)
        for _i, (_td, _tdoff, _tln, _tlc, _tv, _tmi, _tiw) in enumerate(_top3):
            _rank_icon = _rank_icons[_i] if _i < 3 else "▪"
            _short_name = _tln.split(",")[0].strip()
            _short_name = _short_name.split(".", 1)[-1].strip() if "." in _short_name else _short_name
            _streak = _tv.get("best_streak", 0)
            _stars = _tv.get("stars", "")
            _loc_color = "#fcd34d" if _tiw else "#e2e8f0"
            _day_str = f"{_td.month}/{_td.day} {_EN_WD[_td.weekday()]}"
            _is_last_row = (_i == _top3_len - 1)
            _row_border = "" if _is_last_row else "border-bottom:1px solid rgba(251,146,36,0.18);"
            _rows_html_parts.append(
                f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;{_row_border}">'
                f'<span style="font-size:15px;flex-shrink:0;">{_rank_icon}</span>'
                f'<span style="color:{_loc_color};font-weight:700;font-size:13px;flex:1;'
                f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{_short_name}</span>'
                f'<span style="color:#94a3b8;font-size:11px;flex-shrink:0;">{_day_str}</span>'
                f'<span style="color:#fbbf24;font-size:12px;flex-shrink:0;">{_stars}</span>'
                f'<span style="color:#6ee7b7;font-size:10px;flex-shrink:0;">{_streak}h</span>'
                f'</div>'
            )
        _rows_joined = "".join(_rows_html_parts)
        st.markdown(f"""
<div style="position:relative;margin-top:-644px;height:0;overflow:visible;z-index:9998;pointer-events:none;">
<div style="
  position:absolute;top:457px;left:2px;
  width:320px;
  background:rgba(40,15,5,0.95);border:1.5px solid rgba(251,146,36,0.85);
  border-radius:10px;padding:8px 12px;
  font-family:sans-serif;
  box-shadow:0 2px 16px rgba(0,0,0,0.75);backdrop-filter:blur(3px);
  pointer-events:none;
">
<div style="color:#fb923c;font-size:10px;font-weight:700;letter-spacing:0.5px;margin-bottom:6px;">
🏆 {_date_header}
</div>
{_rows_joined}
</div>
</div>""", unsafe_allow_html=True)
    else:
        # ── scan banner (không phải best) hoặc best không có top3 ──────────────
        if _is_best_banner:
            _ban_bg  = "rgba(40,15,5,0.93)"
            _ban_bdr = "rgba(251,146,36,0.85)"
            _ban_clr = "#fcd34d"
            _ban_loc = _scan_r2["loc_name"].split(",")[0].strip()
            _ban_loc = _ban_loc.split(".",1)[-1].strip() if "." in _ban_loc else _ban_loc
            _region_lbl_fb = _REGION_LABELS.get(_scan_r2.get("region", "bac"), "Mien Bac (North)")
            _ban_txt = f"{_sr_date2.month}/{_sr_date2.day} : {_sr_tier} · {_ban_loc} ({_region_lbl_fb}) / moon {_scan_r2['moon_illum']:.0f}%"
        else:
            _ban_bg  = "rgba(5,25,18,0.92)"
            _ban_bdr = "rgba(52,211,153,0.75)"
            _ban_clr = "#6ee7b7"
            _region_lbl_fb = _REGION_LABELS.get(_scan_r2.get("region", "bac"), "Mien Bac (North)")
            _ban_txt = f"{_sr_date2.month}/{_sr_date2.day} : PERFECT NIGHT ({_region_lbl_fb})   {_n_spots} spot{'s' if _n_spots > 1 else ''} / moon {_scan_r2['moon_illum']:.0f}%"
        st.markdown(f"""
<div style="position:relative;margin-top:-644px;height:0;overflow:visible;z-index:9998;pointer-events:none;">
<div style="
  position:absolute;top:557px;left:2px;
  display:inline-flex;align-items:center;
  white-space:nowrap;width:fit-content;
  background:{_ban_bg};border:1.5px solid {_ban_bdr};
  border-radius:10px;padding:6px 13px;
  font-family:sans-serif;color:{_ban_clr};font-size:13px;font-weight:700;
  box-shadow:0 2px 16px rgba(0,0,0,0.75);backdrop-filter:blur(3px);
  pointer-events:none;
">
{_ban_txt}
</div>
</div>""", unsafe_allow_html=True)

elif _scan_r2 == "none":
    _is_tonight_none = st.session_state.get("_scan_tonight", False)
    _is_best_none    = st.session_state.get("_scan_best", False)
    if _is_tonight_none:
        _range_lbl = "tonight"
    elif _is_best_none:
        _range_lbl = "next 7 days"
    else:
        _scan_days_lbl = st.session_state._scan_days
        _range_lbl = f"day {_scan_days_lbl}+" if _scan_days_lbl > 0 else "tonight+"
    _region_lbl_none = _REGION_LABELS.get(st.session_state.get("_scan_region", "bac"), "Kanto")
    _fallback_lbl = st.session_state.get("_scan_fallback_label") or "unsettled weather"
    # ── Map fallback label → weather icons ──────────────────────────────────────
    def _fallback_icons(label):
        """Trả về 1-3 icon tương ứng với thời tiết trong fallback label."""
        _icons = []
        _lbl_lower = label.lower()
        if "snow" in _lbl_lower:
            _icons.append("❄️")
        if "rain" in _lbl_lower:
            _icons.append("🌧️")
        if "cloud" in _lbl_lower:
            _icons.append("☁️")
        if not _icons:
            if "clear" in _lbl_lower or "mostly clear" in _lbl_lower:
                _icons.append("🌟")
            elif "patchy" in _lbl_lower:
                _icons.append("🌤️")
            elif "bright" in _lbl_lower:
                _icons.append("🌃")
            else:
                _icons.append("🌥️")
        return " ".join(_icons)
    _fallback_icon_str = _fallback_icons(_fallback_lbl)
    st.markdown(f"""
<div style="position:relative;margin-top:-644px;height:0;overflow:visible;z-index:9998;pointer-events:none;">
<div style="
  position:absolute;top:557px;left:2px;
  display:inline-flex;align-items:center;gap:5px;white-space:nowrap;width:fit-content;
  background:rgba(10,14,22,0.90);border:1.5px solid rgba(148,163,184,0.35);
  border-radius:10px;padding:6px 13px;
  font-family:sans-serif;color:#94a3b8;font-size:12px;font-weight:600;
  box-shadow:0 2px 16px rgba(0,0,0,0.75);backdrop-filter:blur(3px);
  pointer-events:none;
">
<span style="font-size:15px;">{_fallback_icon_str}</span><span>{_fallback_lbl} in {_region_lbl_none} {_range_lbl}</span>
</div>
</div>""", unsafe_allow_html=True)

# ── LPM EXTERNAL LINK ─────────────────────────────────────────────────────────
# URL is used inline in the nav row beside the location selectbox
_lpm_url = (f"https://lightpollutionmap.app/"
            f"?lat={st.session_state.lat:.4f}&lng={st.session_state.lon:.4f}&zoom=10")

# ── MAP CLICK HANDLER ─────────────────────────────────────────────────────────
if map_data:
    clicked_tip = map_data.get("last_object_clicked_tooltip")
    lc          = map_data.get("last_clicked")

    # ── Priority 0: SCAN sentinel — generic region-based encoding ───────────────
    # lat=89.85 → best <region>     (lng = 100+region_idx)
    # lat=89.75 → tonight <region>  (lng = 100+region_idx)
    # lat=89.65 → "off": tắt banner/ring ngay lập tức, không load data
    # lat=89.35 → "<region> N" plain scan (lng = 300 + region_idx*10 + (N-1))  ← rewritten from scratch
    # region_idx: 0=bac,1=trung,2=nam,3=vietnam
    _REGION_BY_IDX = ["bac", "trung", "nam", "vietnam"]
    _lc_lat = lc.get("lat", 0) if lc else 0
    _lc_lng = lc.get("lng", 0) if lc else 0
    _is_best_trig    = abs(_lc_lat - 89.85) < 0.02
    _is_tonight_trig = abs(_lc_lat - 89.75) < 0.02
    _is_off_trig     = abs(_lc_lat - 89.65) < 0.02
    _is_mkw_scan_trig = abs(_lc_lat - 89.55) < 0.02
    _is_mkw_best_trig = abs(_lc_lat - 89.45) < 0.02
    _is_region_scan_trig = abs(_lc_lat - 89.35) < 0.02
    if _is_mkw_scan_trig and lc and lc != st.session_state._last_lc:
        _d = max(0, min(6, round((_lc_lng - 200.0) * 100)))
        st.session_state._last_lc = lc
        st.session_state._scan_days = _d
        st.session_state._scan_region = "__mkw__"
        st.session_state._scan_best = False
        st.session_state._scan_tonight = False
        st.session_state._scan_scanning = True
        st.rerun()
    if _is_mkw_best_trig and lc and lc != st.session_state._last_lc:
        st.session_state._last_lc = lc
        st.session_state._scan_days = 0
        st.session_state._scan_region = "__mkw__"
        st.session_state._scan_best = True
        st.session_state._scan_tonight = False
        st.session_state._scan_scanning = True
        st.rerun()
    if _is_off_trig and lc and lc != st.session_state._last_lc:
        # "off": tắt kết quả search ngay — không gọi _run_*_scan, không gọi API.
        st.session_state._last_lc       = lc
        st.session_state._scan_result   = None
        st.session_state._scan_fallback_label = None
        st.session_state._scan_scanning = False
        st.rerun()
    if _is_region_scan_trig and lc and lc != st.session_state._last_lc:
        # lng = 300 + region_idx*10 + (N-1)  →  region_idx = (lng-300)//10, N-1 = (lng-300)%10
        _raw = int(round(_lc_lng - 300.0))
        _ridx2 = max(0, min(9, _raw // 10))
        _nminus1 = max(0, min(5, _raw % 10))
        st.session_state._last_lc = lc
        st.session_state._scan_days = _nminus1
        st.session_state._scan_region = _REGION_BY_IDX[_ridx2]
        st.session_state._scan_best = False
        st.session_state._scan_tonight = False
        st.session_state._scan_scanning = True
        st.rerun()
    _is_any_scan = _is_best_trig or _is_tonight_trig
    _matched_region = None
    if _is_any_scan:
        _offset = _lc_lng - 100.0
        if -0.01 <= _offset <= 9.01:  # region_idx 0-9
            _ridx = int(round(_offset))
            if 0 <= _ridx <= 9:
                _matched_region = _REGION_BY_IDX[_ridx]
    if lc and lc != st.session_state._last_lc and _matched_region is not None:
        st.session_state._last_lc       = lc
        st.session_state._scan_days     = 0
        st.session_state._scan_region   = _matched_region
        st.session_state._scan_best     = _is_best_trig
        st.session_state._scan_tonight  = _is_tonight_trig
        st.session_state._scan_scanning = True
        st.rerun()


    # ── Priority 1: star marker click (via tooltip) ───────────────────────────
    # last_clicked luôn NULL với DivIcon, chỉ dùng tooltip để detect click ngôi sao.
    # Tooltip HTML chỉ chứa _strip_loc_num(bname) → match theo tên stripped.
    if clicked_tip:
        matched = None
        tip_str = str(clicked_tip)
        for bname, bcoords in LOCATION_DATABASE.items():
            stripped = _strip_loc_num(bname)
            if stripped in tip_str:
                matched = (bname, bcoords)
                break
        if matched:
            bname, bcoords = matched
            _tip_key = f"{bcoords[0]:.4f},{bcoords[1]:.4f}"
            if _tip_key != st.session_state._last_tip:
                # Nếu click sao mới → xử lý và lưu key để chặn rerun kép
                # Nếu click lại cùng sao → _tip_key == _last_tip → skip (không cần rerun)
                st.session_state._last_tip       = _tip_key
                st.session_state._last_lc        = lc
                st.session_state.lat             = bcoords[0]
                st.session_state.lon             = bcoords[1]
                st.session_state.map_center      = [bcoords[0], bcoords[1]]
                st.session_state.location_name   = bname
                st.session_state.is_custom_point = False
                st.session_state._need_fly       = False
                st.session_state.day_offset      = 0
                st.session_state._skip_prefetch  = True
                st.session_state.sel_date        = date_options[0]
                st.rerun()
        else:
            # Tooltip không match sao nào → reset để lần sau click cùng sao vẫn work
            st.session_state._last_tip = None

    # ── Priority 2: free-click on empty map ──────────────────────────────────
    elif lc and lc != st.session_state._last_lc:
        st.session_state._last_lc = lc
        c_lat = round(lc["lat"], 4)
        c_lon = ((round(lc["lng"], 4) + 180) % 360) - 180
        hit = next(((n, c) for n, c in LOCATION_DATABASE.items()
                    if abs(c_lat - c[0]) < 0.03 and abs(c_lon - c[1]) < 0.03), None)
        if hit:
            bname, bcoords = hit
            if (abs(bcoords[0] - st.session_state.lat) > 0.0001 or
                    abs(bcoords[1] - st.session_state.lon) > 0.0001 or
                    st.session_state.is_custom_point):
                st.session_state.lat             = bcoords[0]
                st.session_state.lon             = bcoords[1]
                st.session_state.map_center      = [bcoords[0], bcoords[1]]
                st.session_state.location_name   = bname
                st.session_state.is_custom_point = False
                st.session_state._last_tip       = None
                st.session_state.day_offset      = 0
                st.session_state._skip_prefetch  = True
                st.session_state.sel_date        = date_options[0]
                st.rerun()
        else:
            if abs(c_lat - st.session_state.lat) > 0.0001 or abs(c_lon - st.session_state.lon) > 0.0001:
                st.session_state.lat             = c_lat
                st.session_state.lon             = c_lon
                st.session_state.map_center      = [c_lat, c_lon]
                st.session_state.location_name   = fetch_location_name(c_lat, c_lon)
                st.session_state.is_custom_point = True
                st.session_state._last_tip       = None
                st.session_state.day_offset      = 0
                st.session_state._skip_prefetch  = True
                st.session_state.sel_date        = date_options[0]
                st.rerun()

# ── SKY QUALITY (Transparency/Seeing/Dew Risk) — tính trước khi vào layout ───
def _build_sky_quality(table_data, sun_alts=None):
    """Tính Transparency%, Seeing% và Dew Risk% trung bình cho khung tối thiên văn của đêm.

    - Transparency: dựa trên cloud cover (hệ số cao) + humidity (hệ số nhẹ, ẩm cao/khói
      mù làm mờ ảnh). 100% = trời trong hoàn toàn, khô.
    - Seeing: ước lượng từ wind speed (gió mạnh ở mặt đất → nhiễu động khí quyển cao),
      NHƯNG chỉ có ý nghĩa khi trời quang — nếu mây dày, seeing cũng bị giảm theo
      (không thể "thấy rõ" qua lớp mây). 100% = khí quyển ổn định VÀ trời trong.
    - Dew Risk: humidity càng cao → nguy cơ đọng sương trên ống kính càng cao.
      100% = nguy cơ rất cao (cần dây sưởi kính), 0% = không lo sương.

    Lưu ý: Humidity (độ ẩm tương đối, %) khác Dew Point (điểm sương, °C).
    Ở đây dùng Humidity làm proxy cho Dew Risk vì không có dữ liệu dew point riêng."""
    if not table_data:
        return None
    if len(table_data) > 12:
        table_data = table_data[:-1]
        if sun_alts is not None:
            sun_alts = sun_alts[:-1]
    if sun_alts is None:
        sun_alts = [-90] * len(table_data)

    transp_vals = []
    seeing_vals = []
    dew_vals = []
    for r, sa in zip(table_data, sun_alts):
        if sa is not None and sa > -12:
            continue
        cloud_str = r.get("☁️", "100%")
        humid_str = r.get("💧", "0%")
        wind_str  = r.get("💨", "0m/s")
        cloud_pct = int(cloud_str.replace("%","")) if cloud_str.replace("%","").isdigit() else 100
        humid_pct = int(humid_str.replace("%","")) if humid_str.replace("%","").isdigit() else 0
        try:
            wind_ms = float(wind_str.replace("m/s",""))
        except ValueError:
            wind_ms = 0.0

        # Transparency: trừ điểm theo cloud cover (hệ số cao) và humidity (hệ số nhẹ)
        transp = 100 - cloud_pct * 0.9 - max(0, humid_pct - 60) * 0.5
        transp_vals.append(max(0, min(100, transp)))

        # Seeing: gió nhẹ → ổn định khí quyển tốt. Gió > 2m/s → nhiễu động tăng.
        # Nhân thêm hệ số theo cloud cover — mây dày thì seeing không còn ý nghĩa.
        seeing_atmos = 100 - max(0, wind_ms - 2) * 9
        seeing_atmos = max(0, min(100, seeing_atmos))
        cloud_factor = max(0, 100 - cloud_pct) / 100  # 1.0 nếu trời quang, 0 nếu mây kín
        seeing = seeing_atmos * cloud_factor
        seeing_vals.append(max(0, min(100, seeing)))

        # Dew Risk: humidity ≥ 70% bắt đầu có nguy cơ, ≥ 95% → nguy cơ rất cao
        dew_risk = max(0, (humid_pct - 70)) * (100 / 30)  # 70%→0, 100%→100
        dew_vals.append(max(0, min(100, dew_risk)))

    if not transp_vals:
        return None
    avg_transp = round(sum(transp_vals) / len(transp_vals))
    avg_seeing = round(sum(seeing_vals) / len(seeing_vals))
    avg_dew    = round(sum(dew_vals) / len(dew_vals))
    return {"transparency": avg_transp, "seeing": avg_seeing, "dew_risk": avg_dew}

if st.session_state.day_offset == 0:
    _sky_q = _build_sky_quality(_full_table_data, _full_sun_alt)
else:
    _sky_q = _build_sky_quality(weather_table_data, sun_altitudes)

def _quality_color(val):
    if val >= 75: return "#6ee7b7"   # xanh lá — tốt
    elif val >= 45: return "#fde68a" # vàng — trung bình
    else: return "#fca5a5"           # đỏ — kém

def _quality_label(val):
    if val >= 75: return "Excellent"
    elif val >= 45: return "Average"
    else: return "Poor"

def _risk_color(val):
    """Cho các chỉ số mà cao = xấu (ví dụ Dew Risk)."""
    if val >= 60: return "#fca5a5"   # đỏ — nguy cơ cao
    elif val >= 25: return "#fde68a" # vàng — trung bình
    else: return "#6ee7b7"           # xanh lá — an toàn

def _risk_label(val):
    if val >= 60: return "High"
    elif val >= 25: return "Moderate"
    else: return "Low"

# ── LAYOUT: LEFT PANEL + RIGHT PANEL ─────────────────────────────────────────
st.markdown("""
    <style>
        /* Ép bảng chiếm toàn bộ chiều rộng nhưng cột 2 (Mây) chỉ chiếm 10% */
        [data-testid="stTable"] table { width: 100% !important; table-layout: fixed; }
        [data-testid="stTable"] td:nth-child(2), [data-testid="stTable"] th:nth-child(2) { width: 10% !important; }
        /* Đảm bảo cột 📸 Đánh giá có đủ chỗ hiển thị sao */
        [data-testid="stTable"] td:nth-child(5), [data-testid="stTable"] th:nth-child(5) { width: 35% !important; }
    </style>
""", unsafe_allow_html=True)
col_left, col_right = st.columns([2.5, 1.1])

with col_right:
    # Bortle — luôn hiện khung Bortle Scale (model được hiệu chỉnh cho Việt Nam)
    st.markdown(f"""
    <div class="metric-card">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <span style="color:#94a3b8;font-size:13px;font-weight:bold;">🌌 SKY QUALITY</span>
            <a href="{_lpm_url}" target="_blank" rel="noopener" title="Light Pollution Map"
               style="display:inline-flex;align-items:center;justify-content:center;
                      background:rgba(124,58,237,0.18);border:1.5px solid rgba(124,58,237,0.55);
                      border-radius:5px;padding:2px 7px;text-decoration:none;
                      color:#a78bfa;font-size:10px;font-weight:700;
                      white-space:nowrap;cursor:pointer;flex-shrink:0;
                      transition:background 0.2s;"
               onmouseover="this.style.background='rgba(124,58,237,0.38)'"
               onmouseout="this.style.background='rgba(124,58,237,0.18)'">LPM</a>
        </div>
        <div style="font-size:28px;font-weight:bold;color:#38bdf8;margin-top:5px;">Bortle Class {bortle_class}</div>
        <div style="font-size:14px;color:#e2e8f0;margin-top:2px;">SQM: <b>{sqm_val}</b> mag/arcsec²</div>
    </div>""", unsafe_allow_html=True)

    # Moon Phase + Coordinate — 1 block, trái/phải
    st.markdown(f"""
    <div class="metric-card">
        <div style="display:flex;gap:10px;">
            <div style="flex:1;">
                <span style="color:#94a3b8;font-size:13px;font-weight:bold;">🌙 MOON PHASE</span>
                <div style="font-size:28px;font-weight:bold;color:#fbbf24;margin-top:5px;">{moon_pct}%</div>
                <div style="font-size:12px;color:#cbd5e1;margin-top:4px;font-style:italic;">{moon_text}</div>
            </div>
            <div style="flex:1;border-left:1px solid #334155;padding-left:10px;">
                <span style="color:#94a3b8;font-size:13px;font-weight:bold;">📍 COORDINATE</span>
                <div class="geo-highlight" style="font-size:15px;margin-top:5px;color:#38bdf8;">
                    LON: {round(st.session_state.lon,4)}<br>
                    LAT: {round(st.session_state.lat,4)}
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Transparency + Seeing + Dew Risk — 1 block, 3 cột (thay vị trí Position & Coordinate cũ)
    if _sky_q:
        _tc = _quality_color(_sky_q["transparency"])
        _sc = _quality_color(_sky_q["seeing"])
        _dc = _risk_color(_sky_q["dew_risk"])
        _tl = _quality_label(_sky_q["transparency"])
        _sl = _quality_label(_sky_q["seeing"])
        _dl = _risk_label(_sky_q["dew_risk"])
        st.markdown(f"""
        <div class="metric-card">
            <div style="display:flex;gap:8px;">
                <div style="flex:1;text-align:center;">
                    <div style="font-size:10.5px;color:#94a3b8;font-weight:700;letter-spacing:0.04em;">TRANSPARENCY</div>
                    <div style="font-size:22px;font-weight:800;color:{_tc};margin-top:4px;">{_sky_q["transparency"]}%</div>
                    <div style="font-size:11px;color:{_tc};opacity:0.85;margin-top:1px;">{_tl}</div>
                </div>
                <div style="flex:1;text-align:center;border-left:1px solid #334155;">
                    <div style="font-size:10.5px;color:#94a3b8;font-weight:700;letter-spacing:0.04em;">SEEING</div>
                    <div style="font-size:22px;font-weight:800;color:{_sc};margin-top:4px;">{_sky_q["seeing"]}%</div>
                    <div style="font-size:11px;color:{_sc};opacity:0.85;margin-top:1px;">{_sl}</div>
                </div>
                <div style="flex:1;text-align:center;border-left:1px solid #334155;">
                    <div style="font-size:10.5px;color:#94a3b8;font-weight:700;letter-spacing:0.04em;">DEW RISK</div>
                    <div style="font-size:22px;font-weight:800;color:{_dc};margin-top:4px;">{_sky_q["dew_risk"]}%</div>
                    <div style="font-size:11px;color:{_dc};opacity:0.85;margin-top:1px;">{_dl}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Weather source selectbox + source label
    # Dynamic key theo weather_source → widget re-render đúng khi auto-fallback sang GFS
    source_options = ["US (GFS)", "EU (ECMWF)", "🔀 Blend (ECMWF+GFS)"]
    cur_src = st.session_state.weather_source
    if cur_src not in source_options:
        cur_src = "🔀 Blend (ECMWF+GFS)"
    src_key = f"sel_source_{cur_src.replace(' ', '_').replace('(', '').replace(')', '').replace('🔀','')}"
    chosen = st.selectbox("src", source_options,
                          index=source_options.index(cur_src),
                          label_visibility="collapsed", key=src_key)
    if chosen != st.session_state.weather_source:
        st.session_state.weather_source = chosen
        st.session_state._source_auto = False  # user chọn tay → không auto-switch nữa
        st.rerun()

    # ── TODAY HIGHLIGHT — thay vị trí 7-DAY FORECAST cũ (cùng kích thước) ─────
    # Mỗi vùng: liệt kê các địa điểm có thời tiết đêm nay OK (PERFECT / GOOD STARRY NIGHT).
    # Không có địa điểm nào → ghi "None" (xám). Muốn thêm/bớt vùng chỉ cần sửa _TH_REGIONS.
    _TH_REGIONS = ["bac", "trung", "nam"]
    _TH_LABELS  = {"bac": "North", "trung": "Central", "nam": "South"}
    _TH_MAX_SHOW = 2   # số địa điểm hiển thị tối đa mỗi vùng (còn lại gộp thành +N)

    def _th_short(name):
        n = _strip_loc_num(name).rsplit(",", 1)[0].strip()
        return _vn_en_part(n) or name

    @st.cache_data(ttl=1800, show_spinner=False)
    def _today_highlight_data(source, day_key):
        """{region: [(short_name, full_name, tier), ...]} — PERFECT trước, GOOD sau.
        Chạy tuần tự (không thread) vì @st.cache_data không thread-safe khi write.
        Dùng danh sách dedupe 60km; weather fetch đã cache 1h."""
        out = {}
        _wx_prefetch([(la, lo) for rk in _TH_REGIONS
                      for _nm, (la, lo) in _locs_for_region(rk, for_best_or_tonight=True)])
        for rk in _TH_REGIONS:
            hits = []
            for nm, (la, lo) in _locs_for_region(rk, for_best_or_tonight=True):
                res = _night_verdict_for_single_loc(la, lo, day_off=0)
                if not res:
                    continue
                tier = res["verdict"].get("tier")
                if tier in ("PERFECT NIGHT", "GOOD STARRY NIGHT"):
                    hits.append((_th_short(nm), nm, tier))
            hits.sort(key=lambda x: 0 if x[2] == "PERFECT NIGHT" else 1)
            out[rk] = hits
        return out

    def _th_html(_th_data):
        _th_rows = ""
        for _rk in _TH_REGIONS:
            _hits = (_th_data or {}).get(_rk, [])
            _lbl_col = "#e2e8f0" if _hits else "#64748b"
            if _hits:
                _chips = ""
                for _sn, _fn, _tier in _hits[:_TH_MAX_SHOW]:
                    _c = "#6ee7b7" if _tier == "PERFECT NIGHT" else "#93c5fd"
                    _chips += (f'<span title="{_fn} — {_tier}" style="color:{_c};font-weight:600;'
                               f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'
                               f'min-width:0;flex:0 1 auto;">{_sn}</span>')
                if len(_hits) > _TH_MAX_SHOW:
                    _more = "&#10;".join(h[1] for h in _hits[_TH_MAX_SHOW:])
                    _chips += (f'<span title="{_more}" style="color:#94a3b8;flex:0 0 auto;">'
                               f'+{len(_hits) - _TH_MAX_SHOW}</span>')
            elif _th_data is None:
                _chips = '<span style="color:#64748b;">loading…</span>'
            else:
                _chips = '<span style="color:#64748b;font-weight:600;">None</span>'
            _th_rows += (
                f'<div style="display:flex;align-items:center;gap:6px;height:16px;'
                f'background:rgba(255,255,255,0.04);border:1px solid #1e293b;border-radius:6px;'
                f'padding:0 6px;font-size:10px;line-height:16px;">'
                f'<span style="flex:0 0 56px;color:{_lbl_col};font-weight:700;">'
                f'{_TH_LABELS.get(_rk, _rk.title())}</span>'
                f'<div style="display:flex;gap:6px;min-width:0;flex:1;overflow:hidden;">{_chips}</div>'
                f'</div>'
            )
        _html = (
            '<div style="margin-top:8px;">'
            '<div style="font-size:12px;color:#94a3b8;font-weight:700;margin-bottom:6px;letter-spacing:0.5px;">'
            '\U0001f31f TODAY HIGHLIGHT</div>'
            f'<div style="display:flex;flex-direction:column;gap:2px;width:100%;">{_th_rows}</div>'
            '<div style="font-size:10px;color:#475569;margin-top:5px;text-align:right;">'
            '<span style="color:#6ee7b7;">&#9679;</span> Perfect &nbsp;'
            '<span style="color:#93c5fd;">&#9679;</span> Good &nbsp;(tonight)</div>'
            '</div>')
        return _html

    _th_ph = st.empty()   # giữ chỗ: hiện ngay (dữ liệu lần trước hoặc 'loading…'), tính xong ở cuối script

    def _th_render():
        _d = st.session_state.get("_th_last")
        try:
            _d = _today_highlight_data(st.session_state.weather_source,
                                       _night_base_ict.strftime("%Y-%m-%d"))
            st.session_state._th_last = _d
        except Exception:
            pass
        _th_ph.markdown(_th_html(_d if _d is not None else {}), unsafe_allow_html=True)

    _th_ph.markdown(_th_html(st.session_state.get("_th_last")), unsafe_allow_html=True)


with col_left:
    # Inject CSS:
    # 1. Orange styling for date selectbox (nav2)
    # 2. Compact styling for location selectbox (nav3) — smaller font, tighter padding
    st.markdown("""
<style>
/* ── Pull col_left content closer to map ── */
.st-key-nav_box { margin-top: -58px !important; }

/* ── Date selectbox: shrink to fit content ── */
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) {
    width: fit-content !important;
    min-width: 0 !important;
}
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) div[data-baseweb="select"] {
    width: fit-content !important;
    min-width: 0 !important;
}
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) div[data-baseweb="select"] > div:first-child {
    background: rgba(154,52,18,0.60) !important;
    border: 1.5px solid rgba(234,88,12,0.75) !important;
    box-shadow: 0 0 8px rgba(234,88,12,0.18) !important;
    padding-left: 6px !important;
    padding-right: 6px !important;
}
[data-testid="stSelectbox"]:has(select[id*="sel_date"]) span {
    color: #fb923c !important;
    font-weight: 700 !important;
    font-size: 12px !important;
}

/* LPM button is now a floating map control (bottomright) */

/* ── NAV BOX: khung ngoài chứa 2 hàng con ──────────────────────────────────
   nav_row1: ⬅️  date  ➡️   → luôn nằm 1 hàng (no-wrap)
   nav_row2: location  LPM  → luôn nằm 1 hàng (no-wrap)
   - PC (rộng ≥ 600px): nav_row1 và nav_row2 nằm cùng 1 hàng ngang
   - iPhone (< 600px):  nav_row1 hàng trên, nav_row2 hàng dưới
   Cấu trúc DOM: .st-key-nav_box → stVerticalBlock → stElementContainer ×2
                 (mỗi cái wrap 1 sub-container nav_row1 / nav_row2)       */

/* --- nav_box: outer flex row, wrap trên mobile --- */
.st-key-nav_box,
.st-key-nav_box > div,
.st-key-nav_box [data-testid="stVerticalBlockBorderWrapper"],
.st-key-nav_box [data-testid="stVerticalBlockBorderWrapper"] > div {
    width: 100% !important;
}
.st-key-nav_box > div > [data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    gap: 6px !important;
    width: 100% !important;
    background: rgba(255,255,255,0.03);
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 6px;
    box-sizing: border-box;
}
/* Mỗi stElementContainer con trực tiếp của nav_box → chiếm auto */
.st-key-nav_box > div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {
    margin: 0 !important;
    flex: 0 0 auto;
}

/* --- nav_row1: ⬅️ date ➡️ — không bao giờ wrap, co lại theo nội dung --- */
.st-key-nav1,
.st-key-nav1 > div,
.st-key-nav1 [data-testid="stVerticalBlockBorderWrapper"],
.st-key-nav1 [data-testid="stVerticalBlockBorderWrapper"] > div { width: auto !important; }
.st-key-nav1 [data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 6px !important;
    width: auto !important;
}
.st-key-nav1 [data-testid="stElementContainer"] { margin: 0 !important; flex: 0 0 auto; }
.st-key-nav1 [data-testid="stButton"] button {
    width: 44px !important; min-width: 0 !important; padding: 0 !important;
}
.st-key-nav1 [data-testid="stElementContainer"]:has([data-testid="stButton"]) { flex: 0 0 44px; }
.st-key-nav1 [data-testid="stElementContainer"]:has(select[id*="sel_date"]) { flex: 0 1 auto; }
.st-key-nav1 [data-testid="stElementContainer"]:has(select[id*="sel_date"]) [data-testid="stSelectbox"] {
    width: fit-content !important;
}

/* nav2 (location+LPM) removed — now shown as floating label on map */

</style>""", unsafe_allow_html=True)

    # Nav controls — chỉ còn nav1: ⬅️  date  ➡️
    nav_box = st.container(key="nav_box")
    with nav_box:
        with st.container(key="nav1"):
            def _go_prev():
                if st.session_state.day_offset > 0:
                    st.session_state.day_offset -= 1
                    st.session_state.sel_date = date_options[st.session_state.day_offset]

            def _go_next():
                if st.session_state.day_offset < 6:
                    st.session_state.day_offset += 1
                    st.session_state.sel_date = date_options[st.session_state.day_offset]

            st.button("⬅️", key="btn_prev", on_click=_go_prev)

            sel_label = st.selectbox("ngay", date_options, index=st.session_state.day_offset,
                                     label_visibility="collapsed",
                                     key="sel_date")
            new_off = date_options.index(sel_label)
            if new_off != st.session_state.day_offset:
                st.session_state.day_offset = new_off
                st.rerun()

            st.button("➡️", key="btn_next", on_click=_go_next)





    # Table — custom styled HTML card
    if weather_table_data:
        # Hiện badge nếu đang dùng fallback endpoint
        if _ep_label == "gfs_only":
            st.markdown('<div style="background:#422006;border:1px solid #f97316;border-radius:8px;'
                        'padding:6px 14px;margin-bottom:8px;font-size:13px;color:#fed7aa;">'
                        '⚠️ ECMWF server error — using <b>GFS only</b> instead</div>',
                        unsafe_allow_html=True)
        def _cloud_icon_cell(pct_str, precip_val=0.0, temp_val=None):
            pct = int(pct_str.replace('%',''))
            if precip_val is not None and precip_val > 0.5:
                if temp_val is not None and temp_val < 1.0:
                    icon, col = '\u2744\ufe0f', '#93c5fd'
                elif pct > 70:
                    icon, col = '\u26c8\ufe0f', '#f87171'
                else:
                    icon, col = '\U0001f327\ufe0f', '#60a5fa'
            elif pct <= 20:
                icon, col = '\u2600\ufe0f', '#fbbf24'
            elif pct <= 45:
                icon, col = '\u26c5', '#fcd34d'
            elif pct <= 70:
                icon, col = '\U0001f325\ufe0f', '#94a3b8'
            else:
                icon, col = '\u2601\ufe0f', '#64748b'
            return (f'<div style="display:flex;align-items:center;gap:2px;white-space:nowrap;">'
                    f'<span style="font-size:15px;line-height:1;">{icon}</span>'
                    f'<span style="font-size:11px;color:{col};font-weight:600;">{pct_str}</span>'
                    f'</div>')

        def _wind_icon(ws_str):
            ws = float(ws_str.replace('m/s',''))
            if ws < 2:   icon,col = '','#94a3b8'
            elif ws < 5: icon,col = '','#60a5fa'
            else:        icon,col = '','#f97316'
            return f'<span style="color:{col}">{icon} {ws_str}</span>'

        rows_html = ''
        for i, row in enumerate(weather_table_data):
            bg = 'rgba(234,88,12,0.10)' if i % 2 == 0 else 'rgba(194,65,12,0.06)'
            time_lbl = row['⏰']
            cloud_cell = _cloud_icon_cell(row['☁️'], row.get('_precip', 0.0), row.get('_temp'))
            humid_val  = row['💧']
            wind_cell  = _wind_icon(row['💨'])
            stars      = row['📸']
            rows_html += (
                f'<tr style="background:{bg};border-bottom:1px solid rgba(234,88,12,0.18);">'
                f'<td style="padding:8px 8px;font-weight:700;color:#fb923c;white-space:nowrap;">{time_lbl}</td>'
                f'<td style="padding:8px 8px;overflow:hidden;">{cloud_cell}</td>'
                f'<td style="padding:8px 8px;color:#fb923c;">{humid_val}</td>'
                f'<td style="padding:8px 8px;color:#fb923c;">{wind_cell}</td>'
                f'<td style="padding:8px 8px;font-size:16px;letter-spacing:1px;">{stars}</td>'
                f'</tr>'
            )

        table_html = f"""
<div style="background:#1a0a00;border:1.5px solid rgba(234,88,12,0.45);border-radius:12px;overflow:hidden;margin-bottom:8px;box-shadow:0 0 20px rgba(234,88,12,0.10);">
  <table style="width:100%;border-collapse:collapse;font-size:14px;font-family:'Segoe UI',sans-serif;table-layout:fixed;">
    <thead>
      <tr style="background:linear-gradient(90deg,rgba(154,52,18,0.90),rgba(120,40,10,0.75));border-bottom:2px solid rgba(234,88,12,0.55);">
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:14%;">⏰</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:20%;">🌤️</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:13%;">💧</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:16%;">💨</th>
        <th style="padding:10px 8px;text-align:left;color:#fb923c;font-weight:700;width:37%;">📸</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>"""
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        # Hiển thị nguyên nhân thực tế thay vì hardcode "502 Bad Gateway"
        if _last_error == "timeout":
            _err_title = "⚠️ Open-Meteo API request timed out"
            _err_detail = (
                'The request did not respond within <b>25 seconds</b>. '
                'The server may be under heavy load.<br><br>'
                '<span style="color:#94a3b8;">This usually recovers within a few minutes. '
                'Press <b>Retry</b> to clear the cache and fetch again.</span>'
            )
        elif _last_error and _last_error.startswith("HTTP 5"):
            _code = _last_error.split(" ")[1]
            _err_title = f"⚠️ Open-Meteo API is temporarily unavailable"
            _err_detail = (
                f'Server <code style="color:#fbbf24;">api.open-meteo.com</code> returned '
                f'a <b>{_code} error</b> — this is an issue on the provider side, '
                'not with this app.<br><br>'
                '<span style="color:#94a3b8;">It usually recovers automatically within 5-30 minutes. '
                'Press <b>Retry</b> to clear the cache and fetch again.</span>'
            )
        elif _last_error and _last_error.startswith("connection_error"):
            _err_title = "⚠️ Cannot connect to Open-Meteo API"
            _err_detail = (
                'A network connection error occurred. '
                'Please check your internet connection.<br><br>'
                '<span style="color:#94a3b8;"><b>Retry</b> clears the cache and fetches again.</span>'
            )
        else:
            _err_title = "⚠️ Open-Meteo API is temporarily unavailable"
            _err_detail = (
                f'An unexpected error occurred'
                + (f' (details: <code style="color:#fbbf24;">{_last_error}</code>)' if _last_error else '')
                + '.<br><br>'
                '<span style="color:#94a3b8;">This usually recovers within a few minutes. '
                'Press <b>Retry</b> to clear the cache and fetch again.</span>'
            )
        st.markdown(f"""
<div style="background:#1e293b;border:1px solid #ef4444;border-radius:12px;padding:20px 24px;margin-top:8px;">
    <div style="font-size:18px;font-weight:700;color:#ef4444;margin-bottom:8px;">
        {_err_title}
    </div>
    <div style="color:#cbd5e1;font-size:14px;line-height:1.7;">
        {_err_detail}
    </div>
</div>""", unsafe_allow_html=True)
        if st.button("🔄 Retry", key="btn_retry_weather"):
            st.cache_data.clear()
            st.rerun(scope="app")

# ── CLEAR SKY CHART — 7 ngày × 24 giờ (kiểu Clear Sky Chart, đặt phía trên biểu đồ Moon/Sun/Milky Way) ──
# Mỗi hàng = 1 chỉ số, mỗi ô = 1 giờ (giờ địa phương). Dữ liệu lấy từ hourly_data đã fetch
# sẵn → đổi địa điểm là tự cập nhật. Màu: xanh đậm = tốt (trời quang), trắng = xấu (mây dày).
_CSC_DAYS = 7
_CSC_BG = (15, 23, 42)
_CSC_DAY_COLORS = ["#facc15", "#f8fafc", "#f9a8d4", "#86efac", "#7dd3fc", "#fdba74", "#c4b5fd"]
_CSC_CLOUD_STOPS = [(0, (10, 36, 99)), (20, (29, 78, 216)), (40, (59, 130, 246)),
                    (60, (147, 197, 253)), (80, (219, 234, 254)), (100, (255, 255, 255))]
_CSC_HUMID_STOPS = [(0, (10, 36, 99)), (30, (59, 130, 246)), (50, (34, 197, 94)),
                    (70, (250, 204, 21)), (85, (249, 115, 22)), (100, (220, 38, 38))]
_CSC_TEMP_STOPS = [(-10, (76, 29, 149)), (0, (37, 99, 235)), (8, (34, 211, 238)),
                   (15, (34, 197, 94)), (22, (250, 204, 21)), (30, (249, 115, 22)), (38, (220, 38, 38))]

def _csc_rgb(stops, v):
    if v <= stops[0][0]:
        return stops[0][1]
    if v >= stops[-1][0]:
        return stops[-1][1]
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if v <= p1:
            t = (v - p0) / float(p1 - p0)
            return tuple(c0[i] + (c1[i] - c0[i]) * t for i in range(3))
    return stops[-1][1]

def _csc_hex(rgb, f=1.0):
    return "#%02x%02x%02x" % tuple(int(max(0, min(255, rgb[i] * f + _CSC_BG[i] * (1.0 - f)))) for i in range(3))

def _csc_dark_hex(sun_alt, moon_alt, moon_illum):
    b = 1.0 if sun_alt >= 0 else max(0.0, (sun_alt + 18.0) / 18.0) ** 1.5
    if moon_alt > 0:
        b = max(b, (moon_illum / 100.0) * min(1.0, moon_alt / 25.0) * 0.55)
    return "#%02x%02x%02x" % (int(15 + 240 * b), int(23 + 220 * b), int(42 + 150 * b))

def _csc_get(hourly, field, idx, order, bare=True):
    for sfx in order:
        lst = hourly.get(f"{field}{sfx}", [])
        if idx < len(lst) and lst[idx] is not None:
            return float(lst[idx])
    if bare:
        lst = hourly.get(field, [])
        if idx < len(lst) and lst[idx] is not None:
            return float(lst[idx])
    return None

@st.cache_data(ttl=86400, show_spinner=False)
def _csc_astro_grid(lat, lon, d0_str, utc_off_h, n_days):
    d0 = datetime.strptime(d0_str, "%Y-%m-%d")
    sun, moon = {}, {}
    for d in range(n_days):
        dd = d0 + timedelta(days=d)
        for h in range(24):
            sun[(d, h)] = calculate_exact_sun_altitude_ephem(lat, lon, dd.year, dd.month, dd.day, h, utc_off_h)
            moon[(d, h)] = calculate_exact_moon_altitude_ephem(lat, lon, dd.year, dd.month, dd.day, h, utc_off_h)
    return sun, moon

def _csc_build_html(hourly, lat, lon, utc_off_s, target_dt, now_local):
    times = hourly.get("time", []) if hourly else []
    if not times:
        return None
    idx_of = {t: i for i, t in enumerate(times)}
    d0 = datetime.strptime(times[0][:10], "%Y-%m-%d")
    utc_off_h = utc_off_s / 3600.0
    sun_g, moon_g = _csc_astro_grid(lat, lon, times[0][:10], utc_off_h, _CSC_DAYS)
    illum = {d: get_moon_phase_percent(d0 + timedelta(days=d))[0] for d in range(_CSC_DAYS)}
    cols = [(d, d0 + timedelta(days=d), h) for d in range(_CSC_DAYS) for h in range(24)]
    n = len(cols)
    ALL = ("_ecmwf_ifs025", "_gfs_seamless")

    recs = []
    for d, day, h in cols:
        idx = idx_of.get(f"{day.strftime('%Y-%m-%d')}T{h:02d}:00")
        r = {"cloud": None, "src": "", "gfs": None, "hum": None, "wind": None, "temp": None}
        if idx is not None:
            c_ecm = _csc_get(hourly, "cloud_cover", idx, ("_ecmwf_ifs025",), bare=False)
            c_gfs = _csc_get(hourly, "cloud_cover", idx, ("_gfs_seamless",), bare=True)
            if c_ecm is not None:
                r["cloud"], r["src"] = c_ecm, "ECMWF"
            elif c_gfs is not None:
                r["cloud"], r["src"] = c_gfs, "GFS"
            r["gfs"] = c_gfs
            r["hum"] = _csc_get(hourly, "relative_humidity_2m", idx, ALL)
            r["wind"] = _csc_get(hourly, "wind_speed_10m", idx, ALL)
            r["temp"] = _csc_get(hourly, "temperature_2m", idx, ALL)
        sa = sun_g.get((d, h), -90.0)
        ma = moon_g.get((d, h), -90.0)
        r["sun"], r["moon"] = sa, ma
        r["dim"] = 1.0   # giữ đúng màu theo lượng mây (trước đây ban ngày bị pha tối -> ra màu xám)
        recs.append(r)

    def _tt(i):
        _, day, h = cols[i]
        return f"{day.month}/{day.day} {h:02d}:00"

    def _edge(i):
        d, day, h = cols[i]
        b0 = datetime(day.year, day.month, day.day, h)
        if b0 <= now_local < b0 + timedelta(hours=1):
            return "box-shadow:inset 4px 0 0 0 #facc15;"
        if h == 0 and d > 0:
            return "box-shadow:inset 2px 0 0 0 #ef4444;"
        return ""

    hatch = "repeating-linear-gradient(45deg,#1e293b,#1e293b 2px,#334155 2px,#334155 3px)"
    lab = "font-family:Consolas,'Courier New',monospace;font-size:11px;line-height:13px;color:#e2e8f0;white-space:nowrap;"

    def _cell(i, bg, tip, h_px=13):
        return f'<div title="{tip}" style="height:{h_px}px;background:{bg};{_edge(i)}"></div>'

    def _na(i, name):
        return _cell(i, hatch, f"{_tt(i)} {name}: n/a")

    stick = "position:sticky;left:0;z-index:2;background:#000;"

    def _row(label, cells, label_bg=""):
        lb = f"background:{label_bg};color:#0f172a;padding:0 3px;" if label_bg else ""
        return f'<div style="{lab}{stick}{lb}">{label}</div>' + "".join(cells)

    p = [f'<div id="sc" style="overflow-x:auto;cursor:grab;user-select:none;"><div style="width:max(233.34%,1773px);box-sizing:border-box;background:#000;border:1px solid #334155;'
         f'border-radius:10px;padding:8px 10px;">'
         f'<div style="display:grid;grid-template-columns:104px repeat({n},minmax(0,1fr));column-gap:1px;row-gap:1px;">']

    # Header: ngày + giờ
    p.append(f'<div style="{lab}{stick}font-size:10px;color:#94a3b8;">Local Time</div>')
    for d in range(_CSC_DAYS):
        day = d0 + timedelta(days=d)
        col = _CSC_DAY_COLORS[d % len(_CSC_DAY_COLORS)]
        p.append(f'<div style="grid-column:span 24;{lab}color:{col};overflow:hidden;">'
                 f'{day.strftime("%Y-%m-%d")} {day.strftime("%a")}</div>')
    p.append(f'<div style="{stick}"></div>')
    for d, day, h in cols:
        col = _CSC_DAY_COLORS[d % len(_CSC_DAY_COLORS)]
        txt = str(h) if h % 3 == 0 else ""
        p.append(f'<div style="{lab}font-size:9px;line-height:12px;color:{col};overflow:visible;">{txt}</div>')

    # Nhóm 1: bầu trời
    cells = []
    for i, r in enumerate(recs):
        if r["cloud"] is None:
            cells.append(_na(i, "Cloud"))
        else:
            cells.append(_cell(i, _csc_hex(_csc_rgb(_CSC_CLOUD_STOPS, r["cloud"]), r["dim"]),
                               f'{_tt(i)} Cloud ({r["src"]}): {int(round(r["cloud"]))}%'))
    p.append(_row("Cloud Cover:", cells))

    cells = []
    for i, r in enumerate(recs):
        if r["gfs"] is None:
            cells.append(_na(i, "GFS"))
        else:
            cells.append(_cell(i, _csc_hex(_csc_rgb(_CSC_CLOUD_STOPS, r["gfs"]), r["dim"]),
                               f'{_tt(i)} GFS cloud: {int(round(r["gfs"]))}%'))
    p.append(_row("GFS Cloud:", cells))

    cells = []
    for i, r in enumerate(recs):
        if r["cloud"] is None:
            cells.append(_na(i, "Transparency"))
        else:
            tr = 100 - r["cloud"] * 0.9 - max(0, (r["hum"] or 0) - 60) * 0.5
            tr = max(0, min(100, tr))
            cells.append(_cell(i, _csc_hex(_csc_rgb(_CSC_CLOUD_STOPS, 100 - tr), r["dim"]),
                               f'{_tt(i)} Transparency: {int(round(tr))}%'))
    p.append(_row("Transparency:", cells))

    cells = []
    for i, r in enumerate(recs):
        if r["cloud"] is None:
            cells.append(_na(i, "Seeing"))
        else:
            atm = max(0, min(100, 100 - max(0, (r["wind"] or 0) - 2) * 9))
            se = atm * max(0, 100 - r["cloud"]) / 100.0
            cells.append(_cell(i, _csc_hex(_csc_rgb(_CSC_CLOUD_STOPS, 100 - se), r["dim"]),
                               f'{_tt(i)} Seeing: {int(round(se))}%'))
    p.append(_row("Seeing:", cells))

    cells = [_cell(i, _csc_dark_hex(r["sun"], r["moon"], illum.get(cols[i][0], 0.0)),
                   f'{_tt(i)} sun {r["sun"]:.0f}° / moon {r["moon"]:.0f}°', 8)
             for i, r in enumerate(recs)]
    p.append(_row("Darkness:", cells, label_bg="#94a3b8"))

    p.append('<div style="grid-column:1/-1;height:10px;"></div>')

    # Nhóm 2: mặt đất
    cells = []
    for i, r in enumerate(recs):
        if r["wind"] is None:
            cells.append(_na(i, "Wind"))
        else:
            cells.append(_cell(i, _csc_hex(_csc_rgb(_CSC_CLOUD_STOPS, min(100, r["wind"] / 10.0 * 100))),
                               f'{_tt(i)} Wind: {r["wind"]:.1f} m/s'))
    p.append(_row("Wind:", cells))

    cells = []
    for i, r in enumerate(recs):
        if r["hum"] is None:
            cells.append(_na(i, "Humidity"))
        else:
            cells.append(_cell(i, _csc_hex(_csc_rgb(_CSC_HUMID_STOPS, r["hum"])),
                               f'{_tt(i)} Humidity: {int(round(r["hum"]))}%'))
    p.append(_row("Humidity:", cells))

    cells = []
    for i, r in enumerate(recs):
        if r["temp"] is None:
            cells.append(_na(i, "Temp"))
        else:
            cells.append(_cell(i, _csc_hex(_csc_rgb(_CSC_TEMP_STOPS, r["temp"])),
                               f'{_tt(i)} Temperature: {r["temp"]:.1f}°C'))
    p.append(_row("Temperature:", cells))

    # Thanh đêm đang chọn (18:00 → 06:00)
    sel_a = datetime(target_dt.year, target_dt.month, target_dt.day, 18)
    sel_b = sel_a + timedelta(hours=12)
    p.append('<div style="grid-column:1/-1;height:4px;"></div>')
    p.append(f'<div style="{lab}{stick}font-size:10px;color:#fb923c;">Night</div>')
    for d, day, h in cols:
        b0 = datetime(day.year, day.month, day.day, h)
        bg = "#fb923c" if (sel_a <= b0 < sel_b) else "transparent"
        p.append(f'<div style="height:3px;background:{bg};"></div>')
    p.append('</div>')  # grid

    p.append('<div style="display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-top:8px;'
             'font-size:10px;color:#94a3b8;font-family:sans-serif;">'
             '<span>Clear (dark blue)</span><div style="width:90px;height:6px;border-radius:3px;'
             'background:linear-gradient(90deg,#0a2463,#1d4ed8,#3b82f6,#93c5fd,#dbeafe,#ffffff);"></div>'
             '<span>Overcast (white)</span>'
             '<span><span style="color:#facc15;">|</span> now</span>'
             '<span><span style="color:#ef4444;">|</span> midnight</span>'
             '<span><span style="color:#fb923c;">&#9632;</span> selected night</span>'
             '<span style="color:#64748b;">· drag ↔ to see days 4–7</span>'
             '</div>')
    p.append('</div></div>')
    _sel_idx = next((i for i, (d, day, h) in enumerate(cols)
                     if sel_a <= datetime(day.year, day.month, day.day, h) < sel_b), 0)
    return "".join(p), _sel_idx, n

st.markdown("---")
st.markdown(f'### 🌌 Clear Sky Forecast "{_disp_name_html(st.session_state.location_name)}" (7 days)', unsafe_allow_html=True)
_csc_now_local = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=_loc_utc_offset)
_csc_res = _csc_build_html(hourly_data, st.session_state.lat, st.session_state.lon,
                           _loc_utc_offset, target_date, _csc_now_local)
if _csc_res:
    import streamlit.components.v1 as _csc_components
    _csc_html, _csc_sel, _csc_n = _csc_res
    _csc_doc = (
        '<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
        'html,body{margin:0;padding:0;background:transparent;}'
        '#sc{scrollbar-width:thin;scrollbar-color:#475569 #0f172a;}'
        '#sc::-webkit-scrollbar{height:8px;}#sc::-webkit-scrollbar-thumb{background:#475569;border-radius:4px;}'
        '</style></head><body>' + _csc_html +
        '<script>(function(){var sc=document.getElementById("sc");if(!sc)return;'
        'var down=false,sx=0,sl=0;'
        'sc.addEventListener("mousedown",function(e){down=true;sx=e.pageX;sl=sc.scrollLeft;sc.style.cursor="grabbing";});'
        'window.addEventListener("mouseup",function(){down=false;sc.style.cursor="grab";});'
        'window.addEventListener("mousemove",function(e){if(!down)return;e.preventDefault();sc.scrollLeft=sl-(e.pageX-sx);});'
        'var SEL=' + str(int(_csc_sel)) + ',N=' + str(int(_csc_n)) + ';'
        'if(SEL>=60){sc.scrollLeft=Math.max(0,SEL/N*sc.scrollWidth-sc.clientWidth*0.25);}'
        '})();</script></body></html>')
    _csc_components.html(_csc_doc, height=255)
else:
    st.caption("Clear Sky Forecast: weather data unavailable.")

# ── MOON + SUN + MILKY WAY ALTITUDE CHART ────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Moon, Sun & Milkyway Altitude (°)")

import plotly.graph_objects as go

# ── Sun brightness: opacity gradient theo Sun altitude ────────────────────────
# Sun > 0°  → cam đậm | Sun 0°~-13° → mờ dần | Sun <= -13° → tắt hẳn (full dark)
def _sun_bright_opacity(sun_alt):
    if sun_alt <= -13:
        return 0.0
    op = (sun_alt + 13) / 23.0 * 0.50   # -13°→0.0, 0°→0.28, +10°→0.50
    return round(min(max(op, 0.0), 0.50), 3)

fig = go.Figure()

# ── Background brightness bands (vrect per slot) ─────────────────────────────
_x_positions = list(range(len(hours_labels)))
for _i, (_lbl, _sa) in enumerate(zip(hours_labels, sun_altitudes)):
    _op = _sun_bright_opacity(_sa)
    if _op > 0.005:
        fig.add_vrect(
            x0=_i - 0.5, x1=_i + 0.5,
            fillcolor="rgba(251,146,60,1.0)",
            opacity=_op,
            layer="below",
            line_width=0,
        )

# ── Moon: filled area ─────────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=_x_positions, y=moon_altitudes,
    mode='lines',
    name='🌙 Moon',
    line=dict(color='#fbbf24', width=4),
    fill='tozeroy',
    fillcolor='rgba(251,191,36,0.20)',
    hovertemplate='%{customdata}<br>Moon: %{y:.1f}°<extra></extra>',
    customdata=hours_labels,
))

# ── Sun: dashed blue line ─────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=_x_positions, y=sun_altitudes,
    mode='lines',
    name='☀️ Sun',
    line=dict(color='#38bdf8', width=4, dash='dash'),
    hovertemplate='%{customdata}<br>Sun: %{y:.1f}°<extra></extra>',
    customdata=hours_labels,
))

# ── Milky Way GC: dashed purple ───────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=_x_positions, y=milkyway_altitudes,
    mode='lines',
    name='🌌 Milkyway',
    line=dict(color='#a78bfa', width=3.5, dash='dash'),
    hovertemplate='%{customdata}<br>Milkyway: %{y:.1f}°<extra></extra>',
    customdata=hours_labels,
))

# ── Horizon rule ──────────────────────────────────────────────────────────────
fig.add_hline(y=0, line=dict(color='#64748b', dash='dot', width=1.5))

# ── -13° rule ─────────────────────────────────────────────────────────────────
fig.add_hline(y=-13, line=dict(color='rgba(251,146,60,0.70)', dash='dot', width=1.5),
              annotation_text="−13°", annotation_font_color="rgba(251,146,60,0.7)",
              annotation_position="bottom right")

# ── Layout ────────────────────────────────────────────────────────────────────
fig.update_layout(
    height=480,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(15,23,42,0.0)',
    font=dict(color='#94a3b8', size=12),
    xaxis=dict(
        tickmode='array',
        tickvals=_x_positions,
        ticktext=hours_labels,
        gridcolor='rgba(71,85,105,0.3)',
        fixedrange=True,
    ),
    yaxis=dict(
        gridcolor='rgba(71,85,105,0.3)',
        title=None,
        zeroline=False,
        fixedrange=True,
    ),
    legend=dict(
        orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0,
        font=dict(color='#cbd5e1'),
        bgcolor='rgba(0,0,0,0)',
    ),
    margin=dict(l=50, r=20, t=40, b=40),
    hovermode='x unified',
    dragmode=False,
)

st.plotly_chart(fig, use_container_width=True,
                config={'displayModeBar': False, 'scrollZoom': False, 'doubleClick': False,
                        'showAxisDragHandles': False})

# Legend note





# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer-copyright">© Copyright: fcbzune</div>', unsafe_allow_html=True)

# ── TODAY HIGHLIGHT: tính sau cùng để trang hiện ra trước ─────────────────────
if "_th_render" in globals():
    _th_render()
