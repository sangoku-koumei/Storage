import datetime
import calendar
import random
import math
import ephem
import jpholiday
from lunardate import LunarDate

# ==========================================
# ★ 依頼者データ設定
# ==========================================
CLIENT_NAME = "山田 花子 様"
BIRTH_YEAR = 1995
BIRTH_MONTH = 6
BIRTH_DAY = 20
BIRTH_TIME = "10:15"
BIRTH_LAT = 35.6895
BIRTH_LON = 139.6917

TARGET_YEAR = 2026

# ==========================================
# 1. アドバイス生成ロジック (言葉と絵文字のライブラリ)
# ==========================================
class AdviceGenerator:
    def __init__(self):
        # 良い日（大安・一粒万倍日など）用のアドバイス
        self.good_luck_msgs = [
            "今日は追い風が吹いています。✨ 新しい靴を履いて、一歩踏み出してみませんか？",
            "蒔いた種が大きく育つ日です。🌱 小さなことでも「始める」ことが幸運の鍵ですよ。",
            "あなたの笑顔が、周りの人を幸せにします。🌸 今日は思いっきり笑って過ごしましょう。",
            "直感が冴え渡る素晴らしい日。🪄 ふと思いついたアイデアは、宝物の原石かもしれません。",
            "星々があなたの背中を押しています。🌈 自信を持って、やりたかったことに挑戦して。",
            "感謝の気持ちを言葉にすると、倍になって返ってきます。🎁 「ありがとう」を大切に。",
            "今日は何をやってもスムーズに進みそう。🕊️ 軽やかなステップで一日を楽しんで。",
            "ご褒美のような一日。🍰 頑張っている自分に、素敵なプレゼントをあげましょう。",
            "キラキラとしたチャンスが舞い込んできそう。✨ 手を伸ばせば、きっと届きますよ。",
            "人との縁が深まる日です。🤝 大切な人に連絡をとってみると、心が温まります。"
        ]

        # 静養すべき日（仏滅・不成就日など）用のアドバイス
        self.quiet_msgs = [
            "今日は心の洗濯日。🫧 焦らずゆっくり、自分自身の内側と対話してみましょう。",
            "無理に進まず、立ち止まることも大切です。☕ 温かい飲み物でほっと一息ついて。",
            "外の世界よりも、お部屋の中を整えると吉。🪞 鏡を磨けば、心もクリアになりますよ。",
            "少し疲れが出やすいかもしれません。🌿 今夜は早めにお布団に入って、夢の世界へ。",
            "「待つ」ことが最良の選択になることも。🕰️ 時が熟すのを、穏やかな心で待ちましょう。",
            "古いものを手放すと、新しい運気が入ってきます。🍃 断捨離をするのにぴったりの日。",
            "今日は聞き役に徹するのが良さそうです。👂 相手の言葉に耳を傾けると、信頼が深まります。",
            "雨の日は、雨音を楽しむように。☂️ 憂鬱な気分も、優しく受け入れてあげてくださいね。",
            "情報のデトックスをしましょう。📱 スマホを置いて、静寂を楽しむ時間を作ってみて。",
            "充電期間です。🔋 今日しっかり休むことが、明日の活力になりますよ。"
        ]

        # 月のイベント（新月・満月）用のアドバイス
        self.moon_msgs = [
            "空っぽの器には、無限の可能性があります。🌑 新しい願い事を、そっと月に託して。",
            "満ち足りた月の光が、あなたを祝福しています。🌕 これまでの成果を、誇らしく思ってください。",
            "リセットするのに最適なタイミング。🛁 バスタイムを充実させて、心身を浄化しましょう。",
            "感情の波が大きくなるかもしれません。🌊 それもまた、あなたが豊かである証拠ですよ。",
            "月の引力が、不要なものを洗い流してくれます。🧼 執着を手放して、軽やかになりましょう。"
        ]

        # 通常日用のアドバイス (日常を彩る言葉)
        self.normal_msgs = [
            "道端に咲く花のように、小さな幸せを見つけてみてください。🌼",
            "今日は「色」を意識してみて。🎨 明るい服を着ると、気分も晴れやかになりますよ。",
            "深呼吸をひとつ。🌬️ 新鮮な空気が、あなたの身体をエネルギーで満たしてくれます。",
            "懐かしい音楽を聴いてみませんか？🎵 素敵な思い出が、勇気をくれるはず。",
            "あなたの優しさは、魔法のように世界を変えます。🪄 誰かに親切にしてみましょう。",
            "美味しい食事は、明日への活力。🍎 旬の食材を食べて、大地のパワーを取り入れて。",
            "読書にぴったりの日です。📖 本の中に、今のあなたに必要な言葉があるかも。",
            "迷ったら、ワクワクする方を選んで。💖 あなたの「好き」という気持ちが羅針盤です。",
            "言葉は言霊。💫 ポジティブな言葉を使うと、素敵な出来事が引き寄せられますよ。",
            "空を見上げてみましょう。☁️ 雲の流れを見ているだけで、心がスーッと軽くなります。",
            "いつもより少し丁寧にスキンケアを。🧴 自分を大切に扱うことが、運気アップの秘訣。",
            "お気に入りの香りに包まれて。💐 香りは一瞬で気分を変える魔法のスイッチです。",
            "大丈夫、あなたは守られています。🛡️ 安心して、ありのままの自分でいてくださいね。",
            "偶然の一致（シンクロニシティ）に注目して。🗝️ それは宇宙からの秘密のサインです。",
            "少しだけ遠回りをしてみませんか？🚶‍♀️ いつもの道に、新しい発見があるかもしれません。"
        ]

    def get_advice(self, specials, warnings, moon_status):
        # 優先順位: 月イベント > 特別な吉日 > 凶日 > 通常
        if moon_status:
            return random.choice(self.moon_msgs)
        elif specials: # 大安や一粒万倍日など
            return random.choice(self.good_luck_msgs)
        elif warnings: # 仏滅など
            return random.choice(self.quiet_msgs)
        else:
            return random.choice(self.normal_msgs)

# ==========================================
# 2. 占星術計算ロジック (前回同様)
# ==========================================
class StarCompassLogic:
    def __init__(self, year, month, day, time_str, lat, lon):
        self.date_str = f"{year}/{month}/{day} {time_str}"
        self.lat = str(lat)
        self.lon = str(lon)
        self.ayanamsa = 24.1
        self.area_names = [
            "始まりの座 (Aries)", "豊穣の座 (Taurus)", "知恵の座 (Gemini)", "安らぎの座 (Cancer)",
            "王の座 (Leo)", "整えの座 (Virgo)", "調和の座 (Libra)", "変容の座 (Scorpio)",
            "探求の座 (Sagittarius)", "頂点の座 (Capricorn)", "革新の座 (Aquarius)", "浄化の座 (Pisces)"
        ]

    def _get_pos(self, body_name):
        observer = ephem.Observer()
        observer.date = self.date_str
        observer.lat = self.lat
        observer.lon = self.lon
        body = getattr(ephem, body_name)()
        body.compute(observer)
        return (math.degrees(body.ecliptic_lon) - self.ayanamsa) % 360

    def get_star_positions(self):
        planets = {
            "Sun": "太陽の紋章", "Moon": "月の鏡", "Mars": "炎の剣", 
            "Mercury": "翼の靴", "Jupiter": "黄金の冠", "Venus": "愛の薔薇", "Saturn": "時の砂時計"
        }
        pos_map = {}
        for p_key, p_name in planets.items():
            pos_map[p_name] = int(self._get_pos(p_key) // 30)
        return pos_map

    def get_soul_frequency(self):
        idx = int(self._get_pos("Moon") // 30)
        return self.area_names[idx], idx

    def generate_mandala_svg(self):
        positions = self.get_star_positions()
        coords = {
            0: (100, 0), 1: (200, 0), 2: (300, 0), 3: (300, 100),
            4: (300, 200), 5: (300, 300), 6: (200, 300), 7: (100, 300),
            8: (0, 300), 9: (0, 200), 10: (0, 100), 11: (0, 0)
        }
        svg = '<svg viewBox="0 0 400 400" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">'
        svg += '<defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#ffe0e9"/></pattern></defs>'
        svg += '<rect width="400" height="400" fill="url(#grid)" />'
        svg += '<rect x="5" y="5" width="390" height="390" fill="none" stroke="#ffabc2" stroke-width="3" rx="15" ry="15"/>'
        svg += '<rect x="15" y="15" width="370" height="370" fill="none" stroke="#ffabc2" stroke-width="1" stroke-dasharray="5,5" rx="10"/>'
        svg += '<line x1="100" y1="5" x2="100" y2="395" stroke="#ffabc2" stroke-width="2"/>'
        svg += '<line x1="300" y1="5" x2="300" y2="395" stroke="#ffabc2" stroke-width="2"/>'
        svg += '<line x1="5" y1="100" x2="395" y2="100" stroke="#ffabc2" stroke-width="2"/>'
        svg += '<line x1="5" y1="300" x2="395" y2="300" stroke="#ffabc2" stroke-width="2"/>'
        svg += '<rect x="100" y="100" width="200" height="200" fill="white" stroke="#ffabc2" stroke-width="2" rx="5"/>'
        svg += '<circle cx="200" cy="200" r="80" fill="#fff5f8" stroke="none"/>'
        svg += f'<text x="200" y="190" font-size="16" text-anchor="middle" fill="#ff8ba7" font-weight="bold" font-family="sans-serif">DESTINY MANDALA</text>'
        svg += f'<text x="200" y="220" font-size="12" text-anchor="middle" fill="#aaa" font-family="sans-serif">{CLIENT_NAME}</text>'
        
        box_items = {i: [] for i in range(12)}
        icon_map = {"太陽の紋章": "☀", "月の鏡": "☾", "炎の剣": "♂", "翼の靴": "☿", "黄金の冠": "♃", "愛の薔薇": "♀", "時の砂時計": "♄"}
        for p_name, area_idx in positions.items(): box_items[area_idx].append(icon_map[p_name])
            
        for idx, items in box_items.items():
            cx, cy = coords[idx]
            bx, by = cx + 50, cy + 50
            if idx in [0,1,2,11]: by = 50
            elif idx in [8,7,6,5]: by = 350
            short_name = self.area_names[idx].split("(")[0]
            svg += f'<text x="{bx}" y="{by-25}" font-size="9" text-anchor="middle" fill="#ff8ba7">{short_name}</text>'
            svg += f'<text x="{bx}" y="{by+5}" font-size="22" text-anchor="middle" fill="#555">{" ".join(items)}</text>'
        svg += '</svg>'
        return svg

    def get_monthly_message(self, birth_moon_idx, year, month):
        current_jupiter_idx = 2 if month < 6 else 3
        house = ((current_jupiter_idx - birth_moon_idx) % 12) + 1
        messages = {
            1: "あなた自身が主役の季節です。🌹 自信を持ってステージに立ちましょう。",
            2: "実りの時期です。豊かさを大切な人と分かち合うことで、幸せが循環します。🎁",
            3: "好奇心の翼を広げて。🕊️ 知らない場所への小さな旅が、心を潤してくれます。",
            4: "心が安らぐ場所を大切に。🏠 お部屋にお花を飾ると、運気がアップしますよ。",
            5: "情熱の火を灯して。🔥 好きなことに夢中になる時間が、あなたの輝きを増します。",
            6: "心と体のメンテナンス期間。🌿 温かいハーブティーで、自分を労ってください。",
            7: "素敵な出会いの予感。🤝 目の前の人の中に、あなたに必要なメッセージがあります。",
            8: "変容の時です。🦋 古いコートを脱ぎ捨てるように、新しい自分へ生まれ変わりましょう。",
            9: "高い視点を持ってみて。🔭 遠くを見渡せば、悩みもちっぽけに見えてきます。",
            10: "積み重ねてきたことが評価されます。🏔️ 頂上からの景色を楽しみにしていて。",
            11: "希望の光が射し込みます。🌟 仲間と語り合う時間が、未来への鍵になります。",
            12: "静かな浄化のひととき。🛁 心の澱を洗い流して、次なる物語の準備をしましょう。"
        }
        return messages.get(house, "星々の優しい光が、いつもあなたを見守っています。⭐")

# ==========================================
# 3. カレンダーロジック
# ==========================================
class JapanCalendarLogic:
    def __init__(self):
        self.rokuyo_map = {0: "大安", 1: "赤口", 2: "先勝", 3: "友引", 4: "先負", 5: "仏滅"}

    def get_day_info(self, year, month, day):
        d_obj = datetime.datetime(year, month, day)
        date_only = d_obj.date()
        lunar = LunarDate.fromSolarDate(year, month, day)
        rokuyo = self.rokuyo_map[(lunar.month + lunar.day) % 6]
        
        specials, warnings = [], []
        if rokuyo == "大安": specials.append("Lucky Day (大安)")
        if rokuyo == "友引": specials.append("Friends (友引)")
        if rokuyo == "仏滅": warnings.append("Rest Day (仏滅)")
        
        m = ephem.Moon()
        m.compute(d_obj)
        next_new = ephem.next_new_moon(d_obj).datetime().date()
        next_full = ephem.next_full_moon(d_obj).datetime().date()
        
        moon_str = ""
        if date_only == next_new: moon_str = "🌑 New Moon"
        elif date_only == next_full: moon_str = "🌕 Full Moon"
        
        return rokuyo, moon_str, specials, warnings

# ==========================================
# 4. HTML生成
# ==========================================
html_template = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Star Compass 2026</title>
    <link href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @page { size: A4; margin: 0; }
        body { 
            font-family: 'Zen Maru Gothic', sans-serif; 
            margin: 0; padding: 0; background-color: #fff; color: #555;
        }
        .page {
            width: 210mm; height: 296mm; padding: 10mm;
            box-sizing: border-box; page-break-after: always; position: relative;
            background-image: radial-gradient(#fff9fc 20%, transparent 20%), radial-gradient(#f0f8ff 20%, transparent 20%);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
        }
        .cover-frame {
            border: 8px double #ffd1dc; border-radius: 30px; height: 100%;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            background: white; padding: 20px;
        }
        .main-title { font-size: 32pt; color: #ff8ba7; margin-bottom: 10px; letter-spacing: 2px; }
        .sub-title { font-size: 14pt; color: #888; margin-bottom: 30px; }
        .mandala-box { width: 120mm; height: 120mm; margin: 20px 0; }
        .profile-box {
            background: #fff0f5; padding: 20px; border-radius: 15px; width: 80%;
            border: 2px dashed #ffb6c1; text-align: left;
        }
        h1 {
            color: #ff8ba7; font-size: 20pt; border-bottom: 3px dotted #ff8ba7;
            padding-bottom: 5px; display: flex; justify-content: space-between; align-items: baseline;
            background: rgba(255,255,255,0.8);
        }
        .message-box {
            background: linear-gradient(to right, #ffdde1, #ee9ca7); /* Gentle Pink Gradient */
            color: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;
            font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        table { width: 100%; border-collapse: separate; border-spacing: 0 5px; }
        th { color: #888; font-size: 0.9em; padding-bottom: 5px; }
        tr.day-row { background: white; }
        td { padding: 12px 10px; border-top: 1px solid #eee; border-bottom: 1px solid #eee; vertical-align: middle; }
        td:first-child { border-left: 1px solid #eee; border-top-left-radius: 10px; border-bottom-left-radius: 10px; }
        td:last-child { border-right: 1px solid #eee; border-top-right-radius: 10px; border-bottom-right-radius: 10px; }
        
        .date-cell { width: 15%; text-align: center; font-size: 1.2em; font-weight: bold; color: #ff8ba7; }
        .info-cell { width: 25%; }
        .advice-cell { width: 60%; font-size: 0.9em; color: #666; line-height: 1.6; }
        
        .sun { color: #ff6b6b; }
        .sat { color: #4dabf7; }
        .tag { display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 0.7em; margin-right: 3px; color: white; margin-bottom: 3px;}
        .t-good { background: #ffb6c1; } 
        .t-warn { background: #cfcfcf; } 
        .t-moon { background: #a0c4ff; font-weight: bold; }
        
        .footer { position: absolute; bottom: 10mm; right: 15mm; font-size: 8pt; color: #ccc; }
    </style>
</head>
<body>
"""

def generate_final_calendar():
    star_logic = StarCompassLogic(BIRTH_YEAR, BIRTH_MONTH, BIRTH_DAY, BIRTH_TIME, BIRTH_LAT, BIRTH_LON)
    jp_logic = JapanCalendarLogic()
    advice_gen = AdviceGenerator()
    
    mandala_svg = star_logic.generate_mandala_svg()
    soul_freq_name, soul_idx = star_logic.get_soul_frequency()
    
    content = html_template
    
    # --- Cover ---
    content += '<div class="page"><div class="cover-frame">'
    content += '<div class="main-title">星の羅針盤 2026</div>'
    content += f'<div class="sub-title">Celestial Compass for {CLIENT_NAME}</div>'
    content += '<div class="mandala-box">' + mandala_svg + '</div>'
    content += '<div class="profile-box">'
    content += '<h3 style="color:#ff8ba7; margin-top:0;">★ あなたの魂の地図</h3>'
    content += f'<p><strong>心の周波数 (Inner Sign):</strong> {soul_freq_name}</p>'
    content += '<p style="font-size:0.9em;">このカレンダーは、あなたのためだけに星を読み解いた特別な羅針盤です。<br>'
    content += '毎日の中に隠された「小さな幸せ」を見つけるお手伝いができますように。<br>'
    content += '星々の優しい光が、あなたの歩む道を照らしてくれます。</p>'
    content += '</div></div></div>'
    
    # --- Calendar ---
    for month in range(1, 13):
        num_days = calendar.monthrange(TARGET_YEAR, month)[1]
        if num_days == 31: chunks = [10, 10, 11]
        elif num_days == 30: chunks = [10, 10, 10]
        elif num_days == 29: chunks = [10, 10, 9]
        else: chunks = [10, 10, 8]
        
        monthly_msg = star_logic.get_monthly_message(soul_idx, TARGET_YEAR, month)
        
        current_day = 1
        for i, days_in_page in enumerate(chunks):
            content += '<div class="page">'
            content += f'<h1>{TARGET_YEAR} / {month} <span style="font-size:0.6em">Part {i+1}</span></h1>'
            
            if i == 0:
                content += f'<div class="message-box"><i class="fa-solid fa-star"></i> 今月の星のささやき<br><span style="font-size:0.95em; font-weight:normal;">{monthly_msg}</span></div>'
            else:
                content += f'<div style="color:#aaa; font-size:0.8em; margin-bottom:10px; text-align:right;">今月のテーマ: {monthly_msg[:15]}...</div>'
            
            content += '<table>'
            content += '<thead><tr><th>Date</th><th>Sky Guide</th><th>Today\'s Message</th></tr></thead>'
            content += '<tbody>'
            
            for _ in range(days_in_page):
                if current_day > num_days: break
                
                rokuyo, moon, specials, warnings = jp_logic.get_day_info(TARGET_YEAR, month, current_day)
                d_obj = datetime.date(TARGET_YEAR, month, current_day)
                weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d_obj.weekday()]
                
                d_style = ""
                if weekday == "Sun": d_style = "sun"
                elif weekday == "Sat": d_style = "sat"
                
                content += '<tr class="day-row">'
                content += f'<td class="date-cell {d_style}">{current_day}<br><span style="font-size:0.5em;">{weekday}</span></td>'
                
                content += '<td class="info-cell">'
                if moon: content += f'<div class="tag t-moon">{moon}</div>'
                for s in specials: content += f'<span class="tag t-good">{s}</span>'
                if warnings: 
                    if specials: content += "<br>"
                    for w in warnings: content += f'<span class="tag t-warn">{w}</span>'
                if not moon and not specials and not warnings:
                    content += '<span style="color:#ddd; font-size:0.8em;">- Calm -</span>'
                content += '</td>'
                
                # ★ アドバイス生成
                advice = advice_gen.get_advice(specials, warnings, moon)
                
                content += f'<td class="advice-cell">{advice}</td></tr>'
                current_day += 1
            
            content += '</tbody></table>'
            content += '<div class="footer">Celestial Compass Original Method</div>'
            content += '</div>'

    content += "</body></html>"
    
    with open("2026_final_star_calendar.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("生成完了: 2026_final_star_calendar.html")

if __name__ == "__main__":
    generate_final_calendar()
