"""Build the static site into ./site

    python build.py               normal build
    python build.py --ad-preview  show grey boxes where ads will go (for checking layout)

Content lives in content/weeks.py and in the page functions below.
Price data comes from site-data/ (made by scripts/update_prices.py).
"""
import argparse
import datetime
import html
import json
import os
import shutil
from urllib.parse import quote_plus

import config
from content import extra
from content import weeks as wk

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "site")
LANGS = ("en", "ms")
TODAY = datetime.date.today()
VER = datetime.datetime.now().strftime("%Y%m%d%H%M")
AD_PREVIEW = False
WRITTEN = []  # (lang, path) for the sitemap


def esc(s):
    return html.escape(str(s), quote=True)


def tr(lang):
    return lambda en, ms: ms if lang == "ms" else en


NAV = [
    # (page, English, Malay, icon, colour class); entries starting with "#" are group headings
    ("index.html", "Home", "Utama", "🏠", "t-home"),
    ("#preg", "Pregnant", "Sedang hamil", "🤰", ""),
    ("weeks/index.html", "Week by week", "Minggu demi minggu", "📅", "t-weeks"),
    ("fertility.html", "Fertile days", "Hari subur", "🌸", "t-fert"),
    ("names.html", "Baby names", "Nama bayi", "✨", "t-names"),
    ("labour.html", "Kicks & contractions", "Tendangan & kontraksi", "⏱️", "t-labour"),
    ("hospital-bag.html", "Hospital bag", "Beg hospital", "👜", "t-bag"),
    ("confinement-cost.html", "Confinement cost", "Kos berpantang", "💰", "t-cost"),
    ("#new", "New mum", "Ibu baharu", "👶", ""),
    ("pantang.html", "Pantang planner", "Perancang pantang", "🍲", "t-pantang"),
    ("vaccines.html", "Vaccination dates", "Jadual imunisasi", "💉", "t-vax"),
    ("breastmilk.html", "Breast milk storage", "Simpan susu ibu", "🤱", "t-milk"),
    ("newborn.html", "Newborn essentials", "Barang bayi baru lahir", "🧺", "t-kit"),
    ("leave.html", "Maternity leave", "Cuti bersalin", "🗓️", "t-leave"),
    ("#kids", "Mum & kids", "Ibu & anak", "🧒", ""),
    ("prices.html", "Milk & diaper prices", "Harga susu & lampin", "🍼", "t-prices"),
    ("nursery.html", "Taska & tadika", "Taska & tadika", "🧸", "t-nursery"),
]

# Product groups on the prices page (icon, English, Malay) - also listed in the "Prices" drop-down.
GROUPS = {
    "mum": ("🤰", "Milk for mums", "Susu untuk ibu"),
    "infant": ("🍼", "Infant formula (Step 1)", "Rumusan bayi (Langkah 1)"),
    "followon": ("🍼", "Follow-on formula (Step 2)", "Rumusan susulan (Langkah 2)"),
    "growing": ("🥛", "Growing-up milk (1 year +)", "Susu pertumbuhan (1 tahun +)"),
    "diaper": ("🧷", "Diapers", "Lampin pakai buang"),
    "food": ("🥣", "Baby food", "Makanan bayi"),
}


def _price_groups():
    """Groups that actually have prices this month (so the drop-down never links to an empty section)."""
    try:
        with open(os.path.join(HERE, "site-data", "prices-summary.json"), encoding="utf-8") as f:
            have = {it["g"] for it in json.load(f)["items"].values()}
    except (OSError, ValueError, KeyError):
        have = set(GROUPS)
    return [g for g in GROUPS if g in have]


PRICE_GROUPS = _price_groups()

# Strings used by assets/app.js
JS_STR = {
    "en": {
        "pickDate": "Please choose a date first.",
        "badDate": "That date doesn't look right - please check it.",
        "weeksDays": "You are {w} weeks {d} days pregnant",
        "early": "Our week-by-week guide starts at week 4 - come back soon!",
        "tri": "Trimester {t}",
        "sizeOf": "Your baby is about the size of {size}.",
        "daysToGo": "{n} days to go · due {date}",
        "readWeek": "Read week {w}",
        "passed": "Your due date has passed. If your baby has arrived - congratulations! Plan your recovery with the pantang planner.",
        "openPantang": "Open pantang planner",
        "youAreHere": "You are here",
        "pBefore": "Before the birth", "pAfter": "After the birth", "pToday": "Today",
        "pShortlist": "Start shortlisting confinement centres or nannies",
        "pBook": "Book your confinement centre or nanny and pay the deposit",
        "pBuy": "Buy pantang food, herbs and supplies",
        "pBag": "Hospital bag packed - confirm dates with your centre or nanny",
        "pDue": "Due date", "pBirth": "Baby's birthday",
        "pVacc": "Baby's first vaccines (BCG and Hepatitis B) are usually given at birth",
        "pMilk": "Breast milk usually 'comes in' between day 2 and day 5. Watch for yellow skin or eyes (jaundice) and get your baby checked.",
        "pPat": "Last day of paternity leave (7 days, if it started on the birth day)",
        "pCheck": "Postnatal check-up for mum (around 6 weeks)",
        "pEnd": "Last day of pantang ({n} days)",
        "pReg": "Last day to register the birth with JPN (Peninsular Malaysia: within 60 days)",
        "pMat": "Last day of maternity leave (98 days, if it started on the birth day)",
        "pNoteDue": "Dates after the birth are counted from your due date - most babies come a little earlier or later.",
        "qHead": ["Quote", "Total", "Days", "Per day", "Babies per nurse", "Extras"],
        "qQuote": "Quote {n}", "qLowest": "Lowest per day",
        "qWarn": "More than 4 babies per nurse - ask how they cope at night",
        "qNone": "Fill in a price for at least one quote to compare.",
        "bagProgress": "{n} of {t} packed", "bagDone": "All packed - well done!",
        "lvNeed": "Please enter the birth date.",
        "lvMat": "Maternity leave (98 days)", "lvPat": "Paternity leave (7 days)", "lvMatEnds": "Maternity leave ends", "lvPatEnds": "Paternity leave ends", "lvStarts": "Starts {a} · {n} days", "lvBackLbl": "Back at work", "lvBackNote": "or your next working day",
        "lvRange": "{a} to {b}", "lvBack": "Back at work on {d} (or your next working day).",
        "lvEarly": "Note: under the Employment Act, maternity leave can't start more than 30 days before the birth.",
        "grp": {"mum": "Milk for mums (pregnancy & breastfeeding)", "infant": "Infant formula (Step 1)",
                "followon": "Follow-on formula (Step 2)", "growing": "Growing-up milk (1 year and above)",
                "diaper": "Diapers", "food": "Baby food"},
        "cProduct": "Product", "cTypical": "Typical", "cFrom": "From", "cUnit": "Per unit",
        "cShops": "Shops", "per100": "/100 g", "perPiece": "/diaper (M)",
        "tape": "tape", "pants": "pants", "where": "Cheapest shops", "hide": "Hide",
        "chooseState": "Choose your state above to see the cheapest shops.",
        "noShops": "No shop prices for this area yet.",
        "updated": "Prices collected {a} to {b} from {n} shops across Malaysia.",
        "allMy": "All Malaysia", "allDist": "All districts",
        "loading": "Loading prices...", "loadFail": "Couldn't load the prices. Check your connection and refresh the page.",
        "showing": "Showing prices for: {area}", "fewShops": "Few shops in this area - prices may not be typical.",
        "nuTaska": "Taska in {area}", "nuTadika": "Tadika in {area}",
        "nuArea": "your area",
        "qDays": "days", "qPerDay": "/day", "qOneMore": "Add one more quote to compare.",
        "wcWeek": "Week {w}", "wcDays": "+ {d} days",
        "pEndsLbl": "Pantang ends", "pDaysN": "{n}-day pantang", "pTodayLbl": "Today", "pDayOf": "Day {d} of {n}",
        "pStartsLbl": "Pantang starts", "pInDays": "in {n} days", "pCheckLbl": "Postnatal check-up", "pCheckSmall": "around 6 weeks after birth", "pNext": "Next",
        "vaxBirth": "At birth", "vaxMonths": "{m} months",
        "milkUseBy": "Use by", "milkLabel": "Write on the bag: expressed {a}",
        "nmFav": "Save to favourites", "nmNone": "No names match.",
        "fWindow": "Most fertile days", "fWindowSmall": "best chance of pregnancy", "fOv": "Likely ovulation", "fNext": "Next period",
        "fDue": "If you conceive this cycle, due around {d}",
        "kickIdle": "Tap each time you feel a movement.", "kickRunning": "{m} min since your first tap", "kickDone": "10 movements in {m} min",
        "conStart": "Start contraction", "conStop": "Stop", "conLasts": "lasts", "conApart": "apart",
        "conAvg": "Last few: about {gap} apart, lasting {len}.", "conHint": "Tap Start when a contraction begins and Stop when it ends.",
        "nuOneMore": "Add one more taska or tadika to compare.", "nuYear": "first year", "nuMonth": "/month",
        "nuNotReg": "Not ticked as registered - ask to see the JKM / KPM certificate",
        "nuOption": "Option {n}", "nuCheapest": "Lowest first-year cost",
        "promoEnded": "(This promotion may have ended - check the current price.)", "moreInfo": "More info",
        "bfNote": "Breast milk is the best food for babies - the Ministry of Health and WHO recommend only breast milk for the first 6 months. If you use formula, ask your doctor or nurse which type suits your baby. We don't sell or advertise infant formula.",
        "online": "Check online prices (Google Shopping)",
        "noMatch": "No products match \"{q}\" here.", "clearSearch": "Show all products",
        "preTypical": "Typical packages (anywhere in Malaysia)", "preCentres": "Confinement centres - {state}", "qFrom": "from",
        "preCentreNote": "Published price for {d} days: {price}. Checked {date}. Prices change - confirm with the centre.",
        "preSource": "Centre's website", "preTypicalNote": "Typical price - change it to match your quote.",
        "preCentreNoteNoDays": "Published price: {price} (stay length not stated). Checked {date}. Prices change - confirm with the centre.",
    },
    "ms": {
        "pickDate": "Sila pilih tarikh dahulu.",
        "badDate": "Tarikh itu nampak tidak betul - sila semak semula.",
        "weeksDays": "Anda hamil {w} minggu {d} hari",
        "early": "Panduan minggu demi minggu kami bermula pada minggu ke-4 - datang lagi nanti!",
        "tri": "Trimester {t}",
        "sizeOf": "Saiz bayi anda lebih kurang {size}.",
        "daysToGo": "{n} hari lagi · jangkaan {date}",
        "readWeek": "Baca minggu {w}",
        "passed": "Tarikh jangkaan bersalin sudah berlalu. Jika bayi sudah lahir - tahniah! Rancang tempoh berpantang dengan perancang pantang.",
        "openPantang": "Buka perancang pantang",
        "youAreHere": "Anda di sini",
        "pBefore": "Sebelum bersalin", "pAfter": "Selepas bersalin", "pToday": "Hari ini",
        "pShortlist": "Mula senarai pendek pusat berpantang atau pengasuh",
        "pBook": "Tempah pusat berpantang atau pengasuh dan bayar deposit",
        "pBuy": "Beli bahan makanan, herba dan keperluan berpantang",
        "pBag": "Beg hospital siap - sahkan tarikh dengan pusat atau pengasuh",
        "pDue": "Tarikh jangkaan bersalin", "pBirth": "Hari lahir bayi",
        "pVacc": "Vaksin pertama bayi (BCG dan Hepatitis B) biasanya diberi semasa lahir",
        "pMilk": "Susu ibu biasanya mula banyak antara hari ke-2 hingga ke-5. Perhatikan kulit atau mata kuning (jaundis) dan bawa bayi untuk pemeriksaan.",
        "pPat": "Hari terakhir cuti paterniti (7 hari, jika bermula pada hari lahir)",
        "pCheck": "Pemeriksaan postnatal ibu (sekitar 6 minggu)",
        "pEnd": "Hari terakhir berpantang ({n} hari)",
        "pReg": "Hari terakhir mendaftar kelahiran di JPN (Semenanjung: dalam tempoh 60 hari)",
        "pMat": "Hari terakhir cuti bersalin (98 hari, jika bermula pada hari lahir)",
        "pNoteDue": "Tarikh selepas bersalin dikira dari tarikh jangkaan - kebanyakan bayi lahir lebih awal atau lewat sedikit.",
        "qHead": ["Sebut harga", "Jumlah", "Hari", "Sehari", "Bayi setiap jururawat", "Tambahan"],
        "qQuote": "Sebut harga {n}", "qLowest": "Paling murah sehari",
        "qWarn": "Lebih daripada 4 bayi setiap jururawat - tanya bagaimana mereka menjaga pada waktu malam",
        "qNone": "Isi harga untuk sekurang-kurangnya satu sebut harga untuk dibandingkan.",
        "bagProgress": "{n} daripada {t} siap", "bagDone": "Semua siap - syabas!",
        "lvNeed": "Sila masukkan tarikh lahir.",
        "lvMat": "Cuti bersalin (98 hari)", "lvPat": "Cuti paterniti (7 hari)", "lvMatEnds": "Cuti bersalin tamat", "lvPatEnds": "Cuti paterniti tamat", "lvStarts": "Bermula {a} · {n} hari", "lvBackLbl": "Kembali bekerja", "lvBackNote": "atau hari bekerja berikutnya",
        "lvRange": "{a} hingga {b}", "lvBack": "Kembali bekerja pada {d} (atau hari bekerja berikutnya).",
        "lvEarly": "Nota: di bawah Akta Kerja, cuti bersalin tidak boleh bermula lebih awal daripada 30 hari sebelum bersalin.",
        "grp": {"mum": "Susu untuk ibu (hamil & menyusu)", "infant": "Rumusan bayi (Langkah 1)",
                "followon": "Rumusan susulan (Langkah 2)", "growing": "Susu pertumbuhan (1 tahun ke atas)",
                "diaper": "Lampin pakai buang", "food": "Makanan bayi"},
        "cProduct": "Produk", "cTypical": "Biasa", "cFrom": "Dari", "cUnit": "Seunit",
        "cShops": "Kedai", "per100": "/100 g", "perPiece": "/helai (M)",
        "tape": "pita", "pants": "seluar", "where": "Kedai termurah", "hide": "Tutup",
        "chooseState": "Pilih negeri anda di atas untuk melihat kedai termurah.",
        "noShops": "Belum ada harga kedai untuk kawasan ini.",
        "updated": "Harga dikumpul {a} hingga {b} dari {n} kedai di seluruh Malaysia.",
        "allMy": "Seluruh Malaysia", "allDist": "Semua daerah",
        "loading": "Memuatkan harga...", "loadFail": "Harga tidak dapat dimuatkan. Semak sambungan internet dan muat semula halaman.",
        "showing": "Harga untuk: {area}", "fewShops": "Sedikit kedai di kawasan ini - harga mungkin tidak mewakili.",
        "nuTaska": "Taska di {area}", "nuTadika": "Tadika di {area}",
        "nuArea": "kawasan anda",
        "qDays": "hari", "qPerDay": "/hari", "qOneMore": "Tambah satu lagi sebut harga untuk dibandingkan.",
        "wcWeek": "Minggu {w}", "wcDays": "+ {d} hari",
        "pEndsLbl": "Pantang tamat", "pDaysN": "Pantang {n} hari", "pTodayLbl": "Hari ini", "pDayOf": "Hari {d} / {n}",
        "pStartsLbl": "Pantang bermula", "pInDays": "{n} hari lagi", "pCheckLbl": "Pemeriksaan postnatal", "pCheckSmall": "lebih kurang 6 minggu selepas bersalin", "pNext": "Seterusnya",
        "vaxBirth": "Semasa lahir", "vaxMonths": "{m} bulan",
        "milkUseBy": "Guna sebelum", "milkLabel": "Tulis pada beg: diperah {a}",
        "nmFav": "Simpan sebagai kegemaran", "nmNone": "Tiada nama sepadan.",
        "fWindow": "Hari paling subur", "fWindowSmall": "peluang hamil paling tinggi", "fOv": "Ovulasi dijangka", "fNext": "Haid seterusnya",
        "fDue": "Jika hamil kitaran ini, jangkaan lahir sekitar {d}",
        "kickIdle": "Tekan setiap kali anda rasa bayi bergerak.", "kickRunning": "{m} minit sejak tekanan pertama", "kickDone": "10 gerakan dalam {m} minit",
        "conStart": "Mula kontraksi", "conStop": "Berhenti", "conLasts": "tempoh", "conApart": "jarak",
        "conAvg": "Beberapa terakhir: jarak lebih kurang {gap}, tempoh {len}.", "conHint": "Tekan Mula apabila kontraksi bermula dan Berhenti apabila tamat.",
        "nuOneMore": "Tambah satu lagi taska atau tadika untuk dibandingkan.", "nuYear": "tahun pertama", "nuMonth": "/bulan",
        "nuNotReg": "Tidak ditanda berdaftar - minta untuk melihat sijil JKM / KPM",
        "nuOption": "Pilihan {n}", "nuCheapest": "Kos tahun pertama paling rendah",
        "promoEnded": "(Promosi ini mungkin sudah tamat - semak harga terkini.)", "moreInfo": "Maklumat lanjut",
        "bfNote": "Susu ibu ialah makanan terbaik untuk bayi - Kementerian Kesihatan dan WHO mengesyorkan susu ibu sahaja untuk 6 bulan pertama. Jika anda menggunakan susu formula, tanya doktor atau jururawat jenis yang sesuai. Kami tidak menjual atau mengiklankan susu formula bayi.",
        "online": "Semak harga dalam talian (Google Shopping)",
        "noMatch": "Tiada produk sepadan dengan \"{q}\" di sini.", "clearSearch": "Tunjuk semua produk",
        "preTypical": "Pakej biasa (seluruh Malaysia)", "preCentres": "Pusat berpantang - {state}", "qFrom": "dari",
        "preCentreNote": "Harga yang diterbitkan untuk {d} hari: {price}. Disemak {date}. Harga boleh berubah - sahkan dengan pusat.",
        "preSource": "Laman web pusat", "preTypicalNote": "Harga biasa - ubah supaya sama dengan sebut harga anda.",
        "preCentreNoteNoDays": "Harga yang diterbitkan: {price} (tempoh tidak dinyatakan). Disemak {date}. Harga boleh berubah - sahkan dengan pusat.",
    },
}

# ---------------------------------------------------------------- helper bot (no AI: keyword matching)
# Keywords work in both languages. A keyword starting with "=" must match a whole word
# (so "hi" doesn't match "which"); others match the start of a word or a phrase.
BOT_KW = {
    "danger": ["bleed", "blood", "darah", "pendarahan", "emergency", "kecemasan", "999", "waters broke", "water broke",
               "air ketuban", "ketuban pecah", "pecah ketuban", "not moving", "less movement", "kurang bergerak",
               "tak bergerak", "tidak bergerak", "fits", "seizure", "sawan", "fever", "demam", "faint", "pengsan",
               "severe pain", "sakit teruk", "sakit perut", "headache", "sakit kepala", "blurred", "kabur", "swollen",
               "bengkak", "warning sign", "tanda bahaya", "danger"],
    "week": ["which week", "what week", "minggu ke berapa", "minggu berapa", "due date", "tarikh jangkaan", "=edd",
             "hamil berapa", "how far along", "kira minggu", "week calculator"],
    "pantang": ["pantang", "confinement period", "confinement food", "44 hari", "44 days", "urut", "bertungku", "tungku",
                "bengkung", "barut", "zuo yue", "jamu", "after birth", "lepas bersalin", "selepas bersalin", "postnatal",
                "postpartum"],
    "cost": ["confinement centre", "confinement center", "pusat berpantang", "nanny", "pengasuh", "confinement cost",
             "kos berpantang", "deposit", "confinement lady", "mak bidan"],
    "bag": ["hospital bag", "beg hospital", "what to bring", "what to pack", "apa nak bawa", "apa perlu bawa",
            "barang hospital", "bawa ke hospital", "=pack"],
    "leave": ["maternity leave", "cuti bersalin", "paternity", "paterniti", "cuti", "98 days", "98 hari", "=leave",
              "employer", "majikan", "=hr"],
    "prices": ["milk", "susu", "formula", "diaper", "lampin", "pampers", "drypers", "huggies", "petpet", "mamypoko",
               "price", "harga", "murah", "cheap", "cerelac", "kedai"],
    "nursery": ["taska", "tadika", "nursery", "kindergarten", "childcare", "child care", "daycare", "day care",
                "prasekolah", "preschool", "tabika", "kemas", "babysit"],
    "breastfeed": ["breastfeed", "breast feed", "breastmilk", "breast milk", "susu ibu", "menyusu", "penyusuan",
                   "lactation", "pam susu", "breast pump", "nipple", "puting"],
    "vaccine": ["vaccin", "vaksin", "imunisasi", "immunis", "immuniz", "=jab", "suntikan", "=bcg", "hepatitis"],
    "birthreg": ["register", "daftar", "birth certificate", "sijil lahir", "sijil kelahiran", "=jpn", "mykid"],
    "feedback": ["feedback", "cadangan", "suggest", "improve", "tambah baik", "complain", "aduan", "contact", "hubungi",
                 "=bug", "salah", "wrong"],
    "milkstore": ["simpan susu", "susu perah", "susu perahan", "=ebm", "freezer", "peti sejuk", "breast milk storage", "store breast milk",
                  "expressed milk", "tahan berapa lama", "how long breast milk"],
    "names": ["nama bayi", "nama anak", "baby name", "nama lelaki", "nama perempuan", "maksud nama", "name meaning"],
    "fertile": ["hari subur", "ovulasi", "ovulation", "subur", "nak hamil", "cuba hamil", "trying to conceive", "=ttc", "fertile"],
    "kicks": ["tendangan", "kick count", "kick counter", "kira tendangan", "kontraksi", "contraction", "sakit nak bersalin", "labour pain", "labor"],
    "essentials": ["barang bayi", "barang baby", "newborn essentials", "what to buy", "beli apa", "baby list", "persediaan bayi"],
    "hello": ["=hi", "=hello", "=hai", "=helo", "=hey", "salam", "assalamualaikum", "good morning", "selamat pagi"],
    "thanks": ["thank", "terima kasih", "=tq", "=tqvm", "=ty"],
}
BOT_ANS = {  # id: (page or "", English answer, Malay answer, English link text, Malay link text)
    "danger": ("", "If you have bleeding, leaking fluid, a bad headache or blurred vision, sudden swelling, severe tummy pain, fever, fits, or your baby is moving less than usual - go to the nearest clinic or hospital now, or call 999. I can't give medical advice.",
               "Jika anda mengalami pendarahan, air keluar dari faraj, sakit kepala teruk atau pandangan kabur, bengkak mengejut, sakit perut teruk, demam, sawan, atau bayi kurang bergerak - pergi segera ke klinik atau hospital terdekat, atau hubungi 999. Saya tidak boleh memberi nasihat perubatan.", "", ""),
    "week": ("index.html", "Enter your due date (or the first day of your last period) on the home page and I'll show your week.",
             "Masukkan tarikh jangkaan bersalin (atau hari pertama haid terakhir) di halaman utama untuk melihat minggu anda.",
             "Open the week calculator", "Buka kalkulator minggu"),
    "pantang": ("pantang.html", "The pantang planner gives you a dated timeline for Malay (44 days), Chinese (30) or Indian (40) traditions, plus safety tips.",
                "Perancang pantang memberi jadual bertarikh untuk tradisi Melayu (44 hari), Cina (30) atau India (40), serta tip keselamatan.",
                "Open pantang planner", "Buka perancang pantang"),
    "cost": ("confinement-cost.html", "Confinement nannies are about RM5,000-9,000 for 28 days; mid-range centres about RM12,000-18,000. You can compare your quotes per day here.",
             "Pengasuh berpantang lebih kurang RM5,000-9,000 untuk 28 hari; pusat pertengahan lebih kurang RM12,000-18,000. Anda boleh banding sebut harga sehari di sini.",
             "Compare confinement costs", "Banding kos berpantang"),
    "bag": ("hospital-bag.html", "Pack by about 36 weeks. Our checklist covers documents, mum, baby and your partner, and saves your ticks on this phone.",
            "Siapkan sebelum lebih kurang 36 minggu. Senarai semak kami merangkumi dokumen, ibu, bayi dan pasangan, dan menyimpan tanda anda dalam telefon ini.",
            "Open hospital bag checklist", "Buka senarai semak beg hospital"),
    "leave": ("leave.html", "Mothers get 98 days of paid maternity leave and married fathers 7 days of paternity leave under the Employment Act. The calculator works out your dates.",
              "Ibu layak 98 hari cuti bersalin bergaji dan bapa yang berkahwin 7 hari cuti paterniti di bawah Akta Kerja. Kalkulator mengira tarikh anda.",
              "Open leave calculator", "Buka kalkulator cuti"),
    "prices": ("prices.html", "See typical baby milk, diaper and baby food prices for your state and district, and the cheapest shops, from the government's price survey.",
               "Lihat harga biasa susu bayi, lampin dan makanan bayi di negeri dan daerah anda, serta kedai termurah, daripada tinjauan harga kerajaan.",
               "See milk & diaper prices", "Lihat harga susu & lampin"),
    "nursery": ("nursery.html", "Find a taska (under 4) or tadika (4-6) near you on Google Maps, plus the questions to ask before you choose.",
                "Cari taska (bawah 4 tahun) atau tadika (4-6 tahun) berhampiran di Google Maps, serta soalan yang perlu ditanya sebelum memilih.",
                "Find taska & tadika", "Cari taska & tadika"),
    "breastfeed": ("hospital-bag.html", "Breast milk is the best food for babies - the Ministry of Health recommends only breast milk for the first 6 months. For latching or supply worries, ask your clinic's or hospital's lactation nurse.",
                   "Susu ibu ialah makanan terbaik untuk bayi - Kementerian Kesihatan mengesyorkan susu ibu sahaja untuk 6 bulan pertama. Jika ada masalah penyusuan, tanya jururawat laktasi di klinik atau hospital.",
                   "Breastfeeding items for your bag", "Barang penyusuan untuk beg anda"),
    "vaccine": ("vaccines.html", "Babies usually get their first vaccines (BCG and Hepatitis B) at birth. After that, follow the schedule in your baby's health book at your klinik kesihatan.",
                "Bayi biasanya menerima vaksin pertama (BCG dan Hepatitis B) semasa lahir. Selepas itu, ikut jadual dalam buku kesihatan bayi di klinik kesihatan.",
                "See your baby's vaccine dates", "Lihat tarikh vaksin bayi"),
    "birthreg": ("pantang.html", "Register the birth with JPN - in Peninsular Malaysia within 60 days (many hospitals have a JPN counter). Bring both parents' MyKad and your marriage certificate.",
                 "Daftar kelahiran di JPN - di Semenanjung dalam tempoh 60 hari (banyak hospital ada kaunter JPN). Bawa MyKad kedua-dua ibu bapa dan sijil nikah.",
                 "See your after-birth timeline", "Lihat jadual selepas bersalin"),
    "feedback": ("feedback.html", "Thank you! Tell us what to fix or add - it takes a minute.",
                 "Terima kasih! Beritahu kami apa yang perlu dibaiki atau ditambah - hanya seminit.",
                 "Suggest an improvement", "Hantar cadangan"),
    "milkstore": ("breastmilk.html", "KKM says expressed milk keeps 4 hours at room temperature, 8 hours in an air-conditioned room, 3-5 days in the fridge and 6 months in a deep freezer.",
                  "KKM: susu perahan tahan 4 jam pada suhu bilik, 8 jam dalam bilik berhawa dingin, 3-5 hari dalam peti sejuk dan 6 bulan dalam peti sejuk beku.",
                  "Breast milk storage guide", "Panduan simpan susu ibu"),
    "names": ("names.html", "Browse Malay and Islamic baby names with their meanings, and save your favourites.",
              "Lihat nama bayi Melayu dan Islam beserta maksud, dan simpan pilihan kegemaran anda.", "Browse baby names", "Lihat nama bayi"),
    "fertile": ("fertility.html", "Ovulation is usually about 14 days before your next period. The calculator shows your likely fertile days.",
                "Ovulasi biasanya lebih kurang 14 hari sebelum haid seterusnya. Kalkulator menunjukkan hari subur anda.", "Find your fertile days", "Cari hari subur anda"),
    "kicks": ("labour.html", "Count your baby's kicks or time your contractions. If movements slow down, or contractions come regularly and get stronger, call your hospital.",
              "Kira tendangan bayi atau masa kontraksi. Jika gerakan berkurang, atau kontraksi datang secara tetap dan semakin kuat, hubungi hospital.",
              "Open kick counter & contraction timer", "Buka pengira tendangan & kontraksi"),
    "essentials": ("newborn.html", "Our newborn checklist covers sleeping, feeding, bathing, diapers, clothes and going out.",
                   "Senarai semak bayi baru lahir merangkumi tidur, menyusu, mandi, lampin, pakaian dan keluar rumah.",
                   "Open newborn checklist", "Buka senarai barang bayi"),
    "hello": ("", "Hi! Ask me about your pregnancy week, pantang, confinement costs, maternity leave, milk prices or taska.",
              "Hai! Tanya saya tentang minggu kehamilan, pantang, kos berpantang, cuti bersalin, harga susu atau taska.", "", ""),
    "thanks": ("", "You're welcome! Take care.", "Sama-sama! Jaga diri.", "", ""),
}
BOT_UI = {
    "en": {"open": "Ask Teman", "title": "Teman helper", "close": "Close", "placeholder": "Type a question...",
           "send": "Send", "greet": "Hi! I'm a simple helper (not a doctor). Ask me about your pregnancy week, pantang, confinement costs, maternity leave, milk prices or taska.",
           "fallback": "Sorry, I didn't understand - I'm a simple helper. Try one of these topics, or tell us what's missing.",
           "note": "Not medical advice. Emergency: 999.",
           "weekAns": "At week {w}, your baby is about the size of {size}.", "weekLink": "Read week {w}",
           "myWeek": "From your saved due date, you are {w} weeks {d} days pregnant.",
           "chips": [["Which week am I?", "which week"], ["Pantang", "pantang"], ["Confinement cost", "confinement cost"],
                     ["Hospital bag", "hospital bag"], ["Maternity leave", "maternity leave"], ["Milk & diaper prices", "milk price"],
                     ["Taska & tadika", "taska"], ["Warning signs", "warning sign"], ["Suggest an idea", "feedback"]]},
    "ms": {"open": "Tanya Teman", "title": "Pembantu Teman", "close": "Tutup", "placeholder": "Taip soalan...",
           "send": "Hantar", "greet": "Hai! Saya pembantu ringkas (bukan doktor). Tanya saya tentang minggu kehamilan, pantang, kos berpantang, cuti bersalin, harga susu atau taska.",
           "fallback": "Maaf, saya kurang faham - saya hanya pembantu ringkas. Cuba salah satu topik ini, atau beritahu kami apa yang tiada.",
           "note": "Bukan nasihat perubatan. Kecemasan: 999.",
           "weekAns": "Pada minggu ke-{w}, saiz bayi anda lebih kurang {size}.", "weekLink": "Baca minggu {w}",
           "myWeek": "Berdasarkan tarikh jangkaan yang disimpan, anda hamil {w} minggu {d} hari.",
           "chips": [["Minggu ke berapa?", "minggu ke berapa"], ["Pantang", "pantang"], ["Kos berpantang", "pusat berpantang"],
                     ["Beg hospital", "beg hospital"], ["Cuti bersalin", "cuti bersalin"], ["Harga susu & lampin", "harga susu"],
                     ["Taska & tadika", "taska"], ["Tanda bahaya", "tanda bahaya"], ["Beri cadangan", "cadangan"]]},
}
for _lang in ("en", "ms"):
    _ui = dict(BOT_UI[_lang])
    _ui["intents"] = [{"id": i, "k": BOT_KW[i], "p": BOT_ANS[i][0],
                       "a": BOT_ANS[i][2 if _lang == "ms" else 1], "lt": BOT_ANS[i][4 if _lang == "ms" else 3]}
                      for i in BOT_KW]
    JS_STR[_lang]["bot"] = _ui

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
        "%3Ctext y='.9em' font-size='90'%3E%F0%9F%A4%B0%3C/text%3E%3C/svg%3E")


# ---------------------------------------------------------------- helpers

def ad(name, x):
    if config.ADSENSE_CLIENT:
        slot = config.AD_SLOTS.get(name)
        if not slot:
            return ""  # Auto ads decide placement
        return (f'<div class="ad"><span class="ad-label">{x("Advertisement", "Iklan")}</span>'
                f'<ins class="adsbygoogle" style="display:block" data-ad-client="{esc(config.ADSENSE_CLIENT)}" '
                f'data-ad-slot="{esc(slot)}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
                f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>')
    if AD_PREVIEW:
        return f'<div class="ad ad-preview">{x("Advertisement space", "Ruang iklan")} ({name})</div>'
    return ""


def tip(text, x, html_text=False):
    """Small ⓘ that shows extra details on hover (computers) or tap (phones) - keeps pages uncluttered."""
    body = text if html_text else esc(text)
    return (f'<span class="tip"><button type="button" class="tip-btn" aria-label="{x("More info", "Maklumat lanjut")}" aria-expanded="false">i</button>'
            f'<span class="tip-bubble" role="tooltip">{body}</span></span>')


def page_head(x, ico, cls, eyebrow, title, lead="", extra="", lead_id=""):
    """Modern page header: coloured icon tile, small section label, title, one-line intro."""
    lid = f' id="{lead_id}"' if lead_id else ""
    lead_html = f'<p class="lead"{lid}>{lead}</p>' if lead or lead_id else ""
    return (f'<header class="page-head {cls}"><span class="ph-ico" aria-hidden="true">{ico}</span>'
            f'<div class="ph-text"><p class="ph-eyebrow">{esc(eyebrow)}</p><h1>{title}{(" " + extra) if extra else ""}</h1>{lead_html}</div></header>')


def shop(key, q, x):
    url = config.AFFILIATE_LINKS.get(key) or config.SHOP_SEARCH_URL.format(q=quote_plus(q))
    return (f'<a class="shop" href="{esc(url)}" target="_blank" rel="sponsored nofollow noopener">'
            f'{x("Shop", "Beli")}<span aria-hidden="true"> ↗</span></a>')


def danger(x):
    items_en = ["Bleeding from the vagina", "Fluid leaking from the vagina",
                "A bad headache, blurred vision, or sudden swelling of the face or hands",
                "Severe tummy pain", "Fever", "Your baby moving less than usual (after 28 weeks)", "Fits"]
    items_ms = ["Pendarahan dari faraj", "Air keluar dari faraj",
                "Sakit kepala teruk, pandangan kabur, atau bengkak mengejut pada muka atau tangan",
                "Sakit perut yang teruk", "Demam", "Bayi kurang bergerak daripada biasa (selepas 28 minggu)", "Sawan"]
    lis = "".join(f"<li>{esc(i)}</li>" for i in (items_ms if x("", "x") else items_en))
    return (f'<aside class="box danger"><h2>{x("Go to a clinic or hospital straight away if you have:", "Pergi segera ke klinik atau hospital jika anda mengalami:")}</h2>'
            f'<ul>{lis}</ul><p><strong>{x("Emergency: call 999.", "Kecemasan: hubungi 999.")}</strong></p></aside>')


def contact_cta(x, what_en, what_ms):
    if not config.CONTACT_EMAIL:
        return ""
    return (f'<aside class="box cta"><p>{x(what_en, what_ms)}</p>'
            f'<a class="btn ghost" href="mailto:{esc(config.CONTACT_EMAIL)}">{x("Email us", "E-mel kami")}</a></aside>')


def write_page(lang, path, title, desc, body, data=None):
    x = tr(lang)
    depth = path.count("/")
    root = "../" * (depth + 1)
    lroot = "../" * depth
    other = "ms" if lang == "en" else "en"
    site = config.SITE_NAME
    full_title = f"{title} | {site}" if path != "index.html" else f"{site} - {title}"

    seo = ""
    if config.BASE_URL:
        def url(lg):
            u = f"{config.BASE_URL}/{lg}/{path}"
            return u[:-len("index.html")] if u.endswith("index.html") else u
        seo = (f'<link rel="canonical" href="{url(lang)}">'
               f'<link rel="alternate" hreflang="en" href="{url("en")}">'
               f'<link rel="alternate" hreflang="ms" href="{url("ms")}">'
               f'<link rel="alternate" hreflang="x-default" href="{url("en")}">'
               f'<meta property="og:url" content="{url(lang)}">')
    ads = ""
    if config.ADSENSE_CLIENT:
        ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='
               f'{esc(config.ADSENSE_CLIENT)}" crossorigin="anonymous"></script>')

    # Menu: one button on the left that drops down the list of sections (built on <details>, works without JS).
    items, current = [], x("Menu", "Menu")
    for href, en, ms, ico, cls in NAV:
        if href.startswith("#"):
            items.append(f'<li class="menu-group"><span aria-hidden="true">{ico}</span> {esc(x(en, ms))}</li>')
            continue
        active = href == path or (href == "weeks/index.html" and path.startswith("weeks/"))
        label = x(en, ms) if href != "prices.html" else x("Prices", "Harga")
        if active and href != "index.html":
            current = label
        cur = ' aria-current="page"' if active else ""
        if href == "prices.html":  # "Prices" opens its own list of product groups + a search box
            subs = "".join(
                f'<li><a href="{lroot}prices.html#grp-{g}"><span class="mi-ico" aria-hidden="true">{GROUPS[g][0]}</span>'
                f'{esc(x(GROUPS[g][1], GROUPS[g][2]))}</a></li>' for g in PRICE_GROUPS)
            items.append(f"""<li><details class="menu-sub"{" open" if active else ""}>
  <summary class="mi {cls}"{cur}><span class="mi-ico" aria-hidden="true">{ico}</span>{esc(label)}<span class="chev" aria-hidden="true"></span></summary>
  <ul>
    <li><a href="{lroot}prices.html"><span class="mi-ico" aria-hidden="true">📋</span>{x("All prices", "Semua harga")}</a></li>{subs}
    <li><form class="search-row" action="{lroot}prices.html" method="get" role="search">
      <input type="search" name="q" placeholder="{x("Search, e.g. Drypers", "Cari, cth. Drypers")}" aria-label="{x("Search products", "Cari produk")}">
      <button type="submit" class="btn">{x("Search", "Cari")}</button></form></li>
  </ul></details></li>""")
            continue
        items.append(f'<li><a class="mi {cls}" href="{lroot}{href}"{cur}><span class="mi-ico" aria-hidden="true">{ico}</span>{esc(label)}</a></li>')
    extra = (f'<li class="menu-foot"><a href="{lroot}feedback.html">💬 {x("Suggest an improvement", "Hantar cadangan")}</a></li>'
             if config.FEEDBACK_FORM_URL else "")
    menu = f"""<details class="menu">
      <summary class="menu-btn" aria-label="{x("Open menu", "Buka menu")}"><span class="burger" aria-hidden="true"><i></i><i></i><i></i></span><span class="menu-label">{esc(current)}</span></summary>
      <nav class="menu-panel" aria-label="{x("Main", "Utama")}"><ul>{"".join(items)}{extra}</ul></nav>
    </details>"""

    tm = {"lang": lang, "root": root, "s": JS_STR[lang], "ver": VER,
          "wk": {n: wk.get(n, lang)["size"] for n in wk.W}}  # for the helper bot's week answers
    if data:
        tm.update(data)
    tm_json = json.dumps(tm, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    page = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#c2416b">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{ICON}">
<link rel="stylesheet" href="{root}assets/style.css?v={VER}">
{seo}{ads}
</head>
<body>
<a class="skip" href="#main">{x("Skip to content", "Langkau ke kandungan")}</a>
<header class="top">
  <div class="wrap top-row">
    {menu}
    <a class="brand" href="{lroot}index.html"><span class="logo" aria-hidden="true">🤰</span><span>{esc(site)}</span></a>
    <a class="lang" href="{root}{other}/{path}" hreflang="{other}" lang="{other}" title="{"Bahasa Melayu" if other == "ms" else "English"}">{"BM" if other == "ms" else "EN"}</a>
  </div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap">
  <p class="foot-links"><a href="{lroot}about.html">{x("About", "Tentang kami")}</a><a href="{lroot}privacy.html">{x("Privacy", "Privasi")}</a>{f'<a href="{lroot}feedback.html">{x("Suggest an improvement", "Hantar cadangan")}</a>' if config.FEEDBACK_FORM_URL else ""}</p>
  <p class="small">{x("General information only - not medical advice.", "Maklumat umum sahaja - bukan nasihat perubatan.")}
  {tip(x("Always follow your doctor, nurse or midwife. Some shop links are affiliate links: we may earn a small commission at no extra cost to you. We never earn from infant formula.",
         "Sentiasa ikut nasihat doktor, jururawat atau bidan anda. Sesetengah pautan kedai ialah pautan afiliasi: kami mungkin mendapat komisen kecil tanpa kos tambahan kepada anda. Kami tidak pernah mendapat komisen daripada susu formula bayi."), x)}
  · © {TODAY.year} {esc(site)}</p>
</div></footer>
<script>window.TM={tm_json}</script>
<script src="{root}assets/app.js?v={VER}" defer></script>
</body>
</html>
"""
    dest = os.path.join(OUT, lang, *path.split("/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    WRITTEN.append((lang, path))


# Home page picture: baby clothes on a washing line with bunga raya. Drawn here (no licence issues),
# colours follow the light/dark theme.
HERO_SVG = """<svg class="hero-art" viewBox="0 0 640 200" role="img" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">
  <rect width="640" height="200" rx="18" style="fill:var(--brand-soft)"/>
  <circle cx="566" cy="46" r="24" fill="#ffcf6e" opacity=".9"/>
  <path d="M0 158 Q120 122 240 150 T480 140 T640 148 V200 H0 Z" style="fill:var(--accent-soft)"/>
  <path d="M0 176 Q160 142 320 170 T640 164 V200 H0 Z" style="fill:var(--accent)" opacity=".22"/>
  <line x1="40" y1="50" x2="40" y2="168" style="stroke:var(--muted)" stroke-width="4" stroke-linecap="round"/>
  <line x1="600" y1="50" x2="600" y2="168" style="stroke:var(--muted)" stroke-width="4" stroke-linecap="round"/>
  <path d="M40 52 Q320 92 600 52" fill="none" style="stroke:var(--muted)" stroke-width="2"/>
  <g transform="translate(150 64)">
    <path d="M-14 0 Q0 10 14 0 L34 8 L44 26 L30 32 L24 24 L24 58 Q24 66 14 68 L6 70 L-6 70 L-14 68 Q-24 66 -24 58 L-24 24 L-30 32 L-44 26 L-34 8 Z" fill="#f7a8c4"/>
    <circle cx="-5" cy="63" r="2.2" fill="#fff"/><circle cx="5" cy="63" r="2.2" fill="#fff"/>
    <path d="M0 34 l-6 -6 a4 4 0 0 1 6 -5 a4 4 0 0 1 6 5 z" fill="#fff" opacity=".85"/>
    <rect x="-17" y="-5" width="6" height="12" rx="2" fill="#c98b5e"/><rect x="11" y="-5" width="6" height="12" rx="2" fill="#c98b5e"/>
  </g>
  <g transform="translate(232 70)">
    <path d="M0 0 H16 V30 Q16 38 24 40 L32 42 Q40 44 38 52 Q36 58 28 57 L8 54 Q0 52 0 44 Z" fill="#7fd1c3"/>
    <rect x="0" y="0" width="16" height="7" fill="#fff" opacity=".6"/><rect x="5" y="-5" width="6" height="11" rx="2" fill="#c98b5e"/>
  </g>
  <g transform="translate(262 71) rotate(6)">
    <path d="M0 0 H16 V30 Q16 38 24 40 L32 42 Q40 44 38 52 Q36 58 28 57 L8 54 Q0 52 0 44 Z" fill="#7fd1c3"/>
    <rect x="0" y="0" width="16" height="7" fill="#fff" opacity=".6"/><rect x="5" y="-5" width="6" height="11" rx="2" fill="#c98b5e"/>
  </g>
  <g transform="translate(345 70)">
    <path d="M-26 44 Q-26 8 0 6 Q26 8 26 44 Z" fill="#ffd36e"/>
    <rect x="-28" y="40" width="56" height="11" rx="5" fill="#f4b942"/>
    <circle cx="0" cy="5" r="7" fill="#fff3c4"/>
    <rect x="-3" y="-4" width="6" height="10" rx="2" fill="#c98b5e"/>
  </g>
  <g transform="translate(418 68)">
    <rect x="0" y="4" width="20" height="34" rx="10" fill="#c7b6f2"/><rect x="14" y="14" width="11" height="14" rx="5.5" fill="#c7b6f2"/>
    <rect x="0" y="4" width="20" height="7" rx="3" fill="#fff" opacity=".55"/><rect x="7" y="-4" width="6" height="11" rx="2" fill="#c98b5e"/>
  </g>
  <g transform="translate(448 67)">
    <rect x="0" y="4" width="20" height="34" rx="10" fill="#c7b6f2"/><rect x="-5" y="14" width="11" height="14" rx="5.5" fill="#c7b6f2"/>
    <rect x="0" y="4" width="20" height="7" rx="3" fill="#fff" opacity=".55"/><rect x="7" y="-4" width="6" height="11" rx="2" fill="#c98b5e"/>
  </g>
  <g transform="translate(522 60)">
    <path d="M0 4 Q-24 6 -24 32 Q-24 58 0 58 Q24 58 24 32 Q24 6 0 4 Z" fill="#9cc8f2"/>
    <path d="M0 40 l-8 -8 a5.5 5.5 0 0 1 8 -7 a5.5 5.5 0 0 1 8 7 z" fill="#fff" opacity=".9"/>
    <rect x="-3" y="-4" width="6" height="11" rx="2" fill="#c98b5e"/>
  </g>
  <g transform="translate(86 150)">
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#e2445c"/>
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#e2445c" transform="rotate(72)"/>
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#e2445c" transform="rotate(144)"/>
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#e2445c" transform="rotate(216)"/>
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#e2445c" transform="rotate(288)"/>
    <circle r="6" fill="#b0213a"/>
    <path d="M0 0 L12 -26" stroke="#ffd36e" stroke-width="3" stroke-linecap="round"/>
    <circle cx="12" cy="-27" r="3" fill="#ffd36e"/><circle cx="16" cy="-23" r="2.4" fill="#ffd36e"/><circle cx="8" cy="-30" r="2.4" fill="#ffd36e"/>
    <ellipse cx="-30" cy="18" rx="16" ry="7" fill="#4caf7d" transform="rotate(-25 -30 18)"/>
  </g>
  <g transform="translate(600 172) scale(.65)">
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#f06b80"/>
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#f06b80" transform="rotate(72)"/>
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#f06b80" transform="rotate(144)"/>
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#f06b80" transform="rotate(216)"/>
    <ellipse cx="0" cy="-18" rx="14" ry="20" fill="#f06b80" transform="rotate(288)"/>
    <circle r="6" fill="#b0213a"/>
  </g>
  <path d="M300 30 l-7 -7 a5 5 0 0 1 7 -6 a5 5 0 0 1 7 6 z" style="fill:var(--brand)" opacity=".45"/>
  <path d="M478 22 l-5 -5 a3.6 3.6 0 0 1 5 -4.3 a3.6 3.6 0 0 1 5 4.3 z" style="fill:var(--brand)" opacity=".4"/>
  <path d="M96 34 l-5 -5 a3.6 3.6 0 0 1 5 -4.3 a3.6 3.6 0 0 1 5 4.3 z" style="fill:var(--brand)" opacity=".35"/>
</svg>"""


# ---------------------------------------------------------------- pages

def p_fertility(lang):
    x = tr(lang)
    body = f"""
{page_head(x, "🌸", "t-fert", x("Trying for a baby", "Merancang kehamilan"), x("Fertile days calculator", "Kalkulator hari subur"),
           x("Find the days you're most likely to conceive.", "Cari hari peluang hamil paling tinggi."), extra=tip(x("Ovulation usually happens about 14 days before your next period. Your fertile window is the 5 days before ovulation and the day after. Cycles vary - this is an estimate, not contraception.",
                                                                                                                  "Ovulasi biasanya berlaku lebih kurang 14 hari sebelum haid seterusnya. Tempoh subur ialah 5 hari sebelum ovulasi dan sehari selepasnya. Kitaran berbeza - ini anggaran, bukan kaedah perancang keluarga."), x))}
<section class="card" id="fert-tool">
  <div class="q-fields fert-fields">
    <label class="field">{x("First day of your last period", "Hari pertama haid terakhir")}<input type="date" id="fert-lmp"></label>
    <label class="field">{x("Cycle length (days)", "Panjang kitaran (hari)")}<input type="number" id="fert-cycle" min="21" max="40" value="28" inputmode="numeric"></label>
  </div>
  <div id="fert-result" aria-live="polite"></div>
</section>
{ad("in_content", x)}
<details class="acc"><summary>{x("Tips when trying to conceive", "Tip ketika merancang kehamilan")}</summary><ul>
<li>{x("Start folic acid before you conceive - ask your pharmacist or klinik kesihatan.", "Mulakan asid folik sebelum hamil - tanya ahli farmasi atau klinik kesihatan.")}</li>
<li>{x("Track a few cycles: if yours vary a lot, the dates here will too.", "Catat beberapa kitaran: jika kitaran anda banyak berubah, tarikh di sini juga berubah.")}</li>
<li>{x("See a doctor if you haven't conceived after a year of trying (or 6 months if you're 35 or older).", "Jumpa doktor jika belum hamil selepas setahun mencuba (atau 6 bulan jika berumur 35 tahun ke atas).")}</li>
</ul></details>
"""
    write_page(lang, "fertility.html", x("Fertile days & ovulation calculator", "Kalkulator hari subur & ovulasi"),
               x("Free fertile days and ovulation calculator: find your most fertile days, likely ovulation and next period.",
                 "Kalkulator hari subur dan ovulasi percuma: cari hari paling subur, tarikh ovulasi dan haid seterusnya."), body)


def p_names(lang):
    x = tr(lang)
    data = [[n, g, (mm if lang == "ms" else me)] for n, g, me, mm in extra.NAMES]
    body = f"""
{page_head(x, "✨", "t-names", x("Pregnant", "Sedang hamil"), x("Baby names", "Nama bayi"),
           x("Malay and Islamic names with their meanings.", "Nama Melayu dan Islam beserta maksudnya."), extra=tip(x("Meanings are common interpretations - many names have more than one. Check with a trusted source or ustaz/ustazah before deciding.",
                                                                                                                        "Maksud ialah tafsiran biasa - banyak nama mempunyai lebih daripada satu maksud. Semak dengan sumber dipercayai atau ustaz/ustazah sebelum memutuskan."), x))}
<section class="card" id="names-tool">
  <div class="search-row"><input type="search" id="nm-q" placeholder="{x("Search a name or meaning, e.g. light", "Cari nama atau maksud, cth. cahaya")}" aria-label="{x("Search names", "Cari nama")}"></div>
  <div class="seg nm-seg">
    <button type="button" data-f="all" aria-pressed="true">{x("All", "Semua")}</button>
    <button type="button" data-f="m" aria-pressed="false">{x("Boys", "Lelaki")}</button>
    <button type="button" data-f="f" aria-pressed="false">{x("Girls", "Perempuan")}</button>
    <button type="button" data-f="fav" aria-pressed="false">♥ {x("Saved", "Disimpan")}</button>
  </div>
  <ul class="nm-list" id="nm-list"></ul>
</section>
{ad("bottom", x)}
"""
    write_page(lang, "names.html", x("Malay & Islamic baby names with meanings", "Nama bayi Melayu & Islam beserta maksud"),
               x("Browse Malay and Islamic baby names for boys and girls with their meanings, and save your favourites.",
                 "Senarai nama bayi lelaki dan perempuan Melayu dan Islam beserta maksud - simpan nama kegemaran anda."), body, {"names": data})


def p_labour(lang):
    x = tr(lang)
    body = f"""
{page_head(x, "⏱️", "t-labour", x("Third trimester", "Trimester ketiga"), x("Kick counter & contraction timer", "Pengira tendangan & masa kontraksi"),
           x("Simple tools for the last weeks. Saved only on this phone.", "Alat mudah untuk minggu-minggu terakhir. Disimpan dalam telefon ini sahaja."))}
<div class="info-grid">
<section class="card" id="kick-tool">
  <h2><span aria-hidden="true">👣</span> {x("Kick counter", "Pengira tendangan")} {tip(x("From about 28 weeks, get to know your baby's usual pattern. Pick a time when baby is usually active and count movements. If movements slow down or change, go to your clinic or hospital the same day - don't wait.",
                                                                                     "Dari lebih kurang 28 minggu, kenali corak biasa bayi. Pilih waktu bayi biasanya aktif dan kira gerakan. Jika gerakan berkurang atau berubah, pergi ke klinik atau hospital pada hari yang sama - jangan tunggu."), x)}</h2>
  <button type="button" class="kick-btn" id="kick-btn"><span id="kick-count">0</span><small>{x("tap for each movement", "tekan setiap gerakan")}</small></button>
  <p class="hint center" id="kick-time"></p>
  <p class="center"><button type="button" class="link-btn muted" id="kick-reset">{x("Start again", "Mula semula")}</button></p>
</section>
<section class="card" id="con-tool">
  <h2><span aria-hidden="true">⏱️</span> {x("Contraction timer", "Pemasa kontraksi")} {tip(x("Time from the start of one contraction to the start of the next. Contractions that come regularly, get stronger and closer together may mean labour is starting - call your hospital for advice. Go straight away if your waters break, you bleed, or baby moves less.",
                                                                                        "Kira dari permulaan satu kontraksi ke permulaan kontraksi seterusnya. Kontraksi yang datang secara tetap, semakin kuat dan rapat mungkin tanda bersalin bermula - hubungi hospital untuk nasihat. Pergi segera jika air ketuban pecah, berdarah, atau bayi kurang bergerak."), x)}</h2>
  <button type="button" class="btn con-btn" id="con-btn">{x("Start contraction", "Mula kontraksi")}</button>
  <p class="hint" id="con-sum"></p>
  <ol class="con-log" id="con-log"></ol>
  <p><button type="button" class="link-btn muted" id="con-reset">{x("Clear", "Padam")}</button></p>
</section>
</div>
{danger(x)}
{ad("in_content", x)}
"""
    write_page(lang, "labour.html", x("Kick counter & contraction timer", "Pengira tendangan & pemasa kontraksi"),
               x("Free baby kick counter and contraction timer for the last weeks of pregnancy.", "Pengira tendangan bayi dan pemasa kontraksi percuma untuk minggu-minggu akhir kehamilan."), body)


def p_vaccines(lang):
    x = tr(lang)
    vax = [[m, (vm if lang == "ms" else ve), (nm if lang == "ms" else ne)] for m, ve, vm, ne, nm in extra.VACCINES]
    body = f"""
{page_head(x, "💉", "t-vax", x("New mum", "Ibu baharu"), x("Vaccination dates", "Jadual imunisasi"),
           x("Your baby's free KKM vaccines, with dates.", "Vaksin percuma KKM untuk bayi anda, beserta tarikh."), extra=tip(x("Based on KKM's National Immunisation Programme. Ages can differ by state and clinic, so always follow your baby's health record book and your klinik kesihatan. Vaccines in the programme are free at government clinics.",
                                                                                                                                  "Berdasarkan Program Imunisasi Kebangsaan KKM. Umur boleh berbeza mengikut negeri dan klinik, jadi sentiasa ikut buku rekod kesihatan bayi dan klinik kesihatan anda. Vaksin dalam program ini percuma di klinik kerajaan."), x))}
<section class="card" id="vax-tool">
  <div class="due-row"><label class="field grow">{x("Baby's birth date", "Tarikh lahir bayi")}<input type="date" id="vax-birth"></label></div>
  <div id="vax-result" aria-live="polite"></div>
  <p class="hint">{x("Tick each vaccine when it's done - saved on this phone.", "Tandakan setiap vaksin yang sudah diambil - disimpan dalam telefon ini.")}</p>
</section>
{ad("in_content", x)}
<details class="acc"><summary>{x("After a vaccine", "Selepas vaksin")}</summary><ul>
<li>{x("A little fever, fussiness or a sore spot is common for a day or two.", "Demam sedikit, meragam atau bengkak di tempat suntikan adalah biasa selama sehari dua.")}</li>
<li>{x("Get medical help straight away for a high fever, fits, a floppy or unusually sleepy baby, or trouble breathing.", "Dapatkan rawatan segera jika demam tinggi, sawan, bayi lembik atau terlalu mengantuk, atau sukar bernafas.")}</li>
<li>{x("Missed a date? Go to your klinik kesihatan - they will catch your baby up.", "Terlepas tarikh? Pergi ke klinik kesihatan - mereka akan menyusun semula jadual.")}</li>
</ul></details>
"""
    write_page(lang, "vaccines.html", x("Baby vaccination schedule Malaysia (KKM)", "Jadual imunisasi bayi Malaysia (KKM)"),
               x("Malaysia's baby vaccination schedule (KKM National Immunisation Programme) with your baby's dates - BCG, Hepatitis B, 6-in-1, pneumococcal and MMR.",
                 "Jadual imunisasi bayi Malaysia (Program Imunisasi Kebangsaan KKM) beserta tarikh bayi anda - BCG, Hepatitis B, 6-dalam-1, pneumokokal dan MMR."), body, {"vax": vax})


def p_breastmilk(lang):
    x = tr(lang)
    rows = "".join(f'<li><span class="ms-ico" aria-hidden="true">{ic}</span><div><strong>{esc(x(pe, pm))}</strong>{f" <span class=muted>{t}</span>" if t else ""}</div>'
                   f'<span class="ms-time">{esc(x(he, hm))}</span></li>' for k, ic, pe, pm, t, h, he, hm in extra.MILK)
    opts = "".join(f'<option value="{k}" data-h="{h}">{esc(x(pe, pm))}{(" (" + t + ")") if t else ""}</option>' for k, ic, pe, pm, t, h, he, hm in extra.MILK)
    body = f"""
{page_head(x, "🤱", "t-milk", x("New mum", "Ibu baharu"), x("Breast milk storage", "Simpan susu ibu"),
           x("How long expressed milk keeps, from KKM's guide.", "Berapa lama susu perahan tahan, mengikut panduan KKM."), extra=tip(x("Times from the Ministry of Health's nutrition division poster for working mothers (Penyusuan Susu Ibu - Ibu Bekerja). Ask your clinic if your baby is premature or unwell - times can be shorter.",
                                                                                                                                         "Tempoh daripada poster Bahagian Pemakanan KKM untuk ibu bekerja (Penyusuan Susu Ibu - Ibu Bekerja). Tanya klinik jika bayi pramatang atau kurang sihat - tempohnya mungkin lebih singkat."), x))}
<ul class="milk-list">{rows}</ul>
<section class="card" id="milk-tool">
  <h2><span aria-hidden="true">🏷️</span> {x("Label calculator", "Kalkulator label")}</h2>
  <div class="q-fields fert-fields">
    <label class="field">{x("Expressed at", "Diperah pada")}<input type="datetime-local" id="milk-when"></label>
    <label class="field">{x("Stored in", "Disimpan di")}<select id="milk-where">{opts}</select></label>
  </div>
  <div id="milk-result" aria-live="polite"></div>
</section>
{ad("in_content", x)}
<details class="acc"><summary>{x("Good habits", "Amalan baik")}</summary><ul>
<li>{x("Store milk in a clean, closed container or bag and label it with the date and time.", "Simpan susu dalam bekas atau beg yang bersih dan bertutup, dan labelkan dengan tarikh dan masa.")}</li>
<li>{x("Use the oldest milk first.", "Guna susu yang paling lama dahulu.")}</li>
<li>{x("Thaw frozen milk in the chiller overnight. Once thawed, don't freeze it again.", "Cairkan susu beku dalam bahagian dingin semalaman. Susu yang sudah cair tidak boleh dibekukan semula.")}</li>
<li>{x("Warm it in a bowl of warm water - never in a microwave - and test it on your wrist.", "Panaskan dalam mangkuk air suam - jangan guna ketuhar gelombang mikro - dan uji pada pergelangan tangan.")}</li>
</ul></details>
"""
    write_page(lang, "breastmilk.html", x("Breast milk storage guide (KKM)", "Panduan simpan susu ibu (KKM)"),
               x("How long expressed breast milk lasts at room temperature, in the fridge and freezer, from Malaysia's Ministry of Health guide.",
                 "Berapa lama susu ibu perahan tahan pada suhu bilik, dalam peti sejuk dan peti sejuk beku, mengikut panduan KKM."), body)


def p_newborn(lang):
    x = tr(lang)
    secs = []
    for te, tm, items in extra.ESSENTIALS:
        lis = "".join(
            f'<li><label class="check"><input type="checkbox" data-key="nb_{k}"> {esc(x(en, ms))}</label>'
            f'{shop(aff, en, x) if aff else ""}</li>' for k, en, ms, aff in items)
        secs.append(f'<section class="card"><h2>{esc(x(te, tm))}</h2><ul class="checklist">{lis}</ul></section>')
    body = f"""
<div data-store="tm_newborn"></div>
{page_head(x, "🧺", "t-kit", x("New mum", "Ibu baharu"), x("Newborn essentials", "Barang bayi baru lahir"), extra=tip(x("A starting list - you won't need everything at once. 'Shop' links open Shopee; some are affiliate links, so we may earn a small commission at no extra cost to you.",
                                                                                                                    "Senarai permulaan - anda tidak perlukan semuanya sekali gus. Pautan 'Beli' membuka Shopee; sesetengahnya pautan afiliasi, jadi kami mungkin mendapat komisen kecil tanpa kos tambahan kepada anda."), x))}
<div class="bag-progress card"><div class="bp-top"><strong id="bag-progress" aria-live="polite"></strong><button type="button" class="link-btn muted" id="bag-reset">{x("Untick everything", "Buang semua tanda")}</button></div>
<div class="progress"><span id="bag-bar" style="width:0%"></span></div></div>
<div class="check-grid">{"".join(secs)}</div>
{ad("in_content", x)}
"""
    write_page(lang, "newborn.html", x("Newborn baby checklist Malaysia", "Senarai barang bayi baru lahir"),
               x("What to buy before your baby arrives: sleeping, feeding, bathing, diapers, clothes and car seat - a free checklist saved on your phone.",
                 "Apa perlu dibeli sebelum bayi lahir: tidur, menyusu, mandi, lampin, pakaian dan kerusi kereta - senarai semak percuma."), body)


def p_feedback(lang):
    x = tr(lang)
    url = config.FEEDBACK_FORM_URL
    body = f"""
{page_head(x, "💬", "t-home", x("Feedback", "Maklum balas"), x("Help us improve", "Bantu kami menambah baik"))}
<p class="muted">{x("Something missing, wrong or confusing? Tell us - every idea is read. Please don't share medical details here.",
                   "Ada yang tiada, salah atau mengelirukan? Beritahu kami - setiap cadangan dibaca. Jangan kongsi butiran perubatan di sini.")}</p>
<div class="form-frame"><iframe src="{esc(url)}?embedded=true" title="{x("Feedback form", "Borang cadangan")}">{x("Loading...", "Memuatkan...")}</iframe></div>
<p class="small muted">{x("Form not showing?", "Borang tidak keluar?")} <a href="{esc(url)}" target="_blank" rel="noopener">{x("Open it in a new tab", "Buka dalam tab baharu")} ↗</a></p>
"""
    write_page(lang, "feedback.html", x("Help us improve", "Bantu kami menambah baik"),
               x("Send ideas to improve this free pregnancy and pantang site.", "Hantar cadangan untuk menambah baik laman kehamilan dan pantang percuma ini."),
               body)


def p_home(lang):
    x = tr(lang)
    weeks_js = {n: [wk.W[n][0], wk.get(n, lang)["size"]] for n in wk.W}
    tools = [
        ("weeks/index.html", "📅", "Week by week", "Minggu demi minggu", "Baby's size and growth", "Saiz dan perkembangan bayi", "t-weeks"),
        ("pantang.html", "🍲", "Pantang planner", "Perancang pantang", "Your dated timeline", "Jadual bertarikh anda", "t-pantang"),
        ("confinement-cost.html", "💰", "Confinement cost", "Kos berpantang", "Compare centres & nannies", "Banding pusat & pengasuh", "t-cost"),
        ("hospital-bag.html", "👜", "Hospital bag", "Beg hospital", "What to pack", "Apa yang perlu dibawa", "t-bag"),
        ("leave.html", "🗓️", "Maternity leave", "Cuti bersalin", "98 + 7 days, worked out", "98 + 7 hari, dikira", "t-leave"),
        ("prices.html", "🍼", "Milk & diaper prices", "Harga susu & lampin", "Cheapest shops near you", "Kedai termurah berhampiran", "t-prices"),
        ("nursery.html", "🧸", "Taska & tadika", "Taska & tadika", "Childcare near you", "Penjagaan anak berhampiran", "t-nursery"),
    ]
    desc = {h: (de, dm) for h, i, te, tm, de, dm, c in tools}
    desc.update({
        "fertility.html": ("When you're most likely to conceive", "Bila peluang hamil paling tinggi"),
        "names.html": ("Malay & Islamic names with meanings", "Nama Melayu & Islam beserta maksud"),
        "labour.html": ("Count kicks, time contractions", "Kira tendangan, masa kontraksi"),
        "vaccines.html": ("Your baby's KKM vaccine dates", "Tarikh vaksin bayi (KKM)"),
        "breastmilk.html": ("How long it keeps (KKM)", "Berapa lama tahan (KKM)"),
        "newborn.html": ("What to buy before baby", "Apa perlu dibeli sebelum bayi"),
    })
    stages, cur_stage = [], None
    for h, en, ms, ico, cls in NAV:
        if h.startswith("#"):
            cur_stage = [h[1:], ico, x(en, ms), []]
            stages.append(cur_stage)
        elif cur_stage:
            de, dm = desc.get(h, ("", ""))
            cur_stage[3].append(f'<a class="tool-card {cls}" href="{h}"><span class="tool-ico" aria-hidden="true">{ico}</span>'
                                f'<span><strong>{esc(x(en, ms))}</strong><span class="muted">{esc(x(de, dm))}</span></span></a>')
    stage_tabs = "".join(f'<button type="button" class="stage-tab" role="tab" data-stage="{k}" aria-selected="false"><span aria-hidden="true">{ic}</span> {esc(lbl)}</button>'
                         for k, ic, lbl, _ in stages)
    stage_panels = "".join(f'<div class="stage-panel tools" role="tabpanel" data-stage="{k}">{"".join(cs)}</div>' for k, ic, lbl, cs in stages)
    body = f"""
<section class="hero2">
  <div class="hero-text">
    <p class="eyebrow">{x("Free · No sign-up · English & BM", "Percuma · Tanpa daftar · BM & English")}</p>
    <h1>{x("Your pregnancy &amp; <span class=\"hl\">pantang</span> companion", "Teman kehamilan &amp; <span class=\"hl\">berpantang</span> anda")}</h1>
    <p class="lead">{x("Follow your baby week by week, plan pantang, compare confinement costs and find the cheapest milk and diapers near you.",
                       "Ikuti bayi minggu demi minggu, rancang pantang, banding kos berpantang dan cari susu serta lampin paling murah berhampiran.")}</p>
    <div class="due-box" id="due-tool">
      <div class="due-top">
        <span class="due-q">{x("Which week am I?", "Minggu ke berapa saya?")}</span>
        {tip(x("Your date is saved only on this phone. No sign-up.", "Tarikh anda disimpan dalam telefon ini sahaja. Tiada pendaftaran."), x)}
      </div>
      <div class="seg" role="group" aria-label="{x("I know my", "Saya tahu")}">
        <button type="button" data-mode="due" aria-pressed="true">{x("Due date", "Tarikh jangkaan")}</button>
        <button type="button" data-mode="lmp" aria-pressed="false">{x("Last period", "Haid terakhir")}</button>
      </div>
      <span id="due-label" class="sr-only" data-due="{x("My due date", "Tarikh jangkaan bersalin saya")}" data-lmp="{x("First day of my last period", "Hari pertama haid terakhir saya")}">{x("My due date", "Tarikh jangkaan bersalin saya")}</span>
      <div class="due-row">
        <input type="date" id="due-input" aria-labelledby="due-label">
        <button type="button" class="btn" id="due-go">{x("Show my week", "Tunjuk minggu saya")}</button>
      </div>
    </div>
  </div>
  <div class="hero-visual">{HERO_SVG}</div>
</section>
<div id="due-result" aria-live="polite"></div>
<section class="stages">
  <div class="stage-tabs" role="tablist" aria-label="{x("Your stage", "Peringkat anda")}">{stage_tabs}</div>
  {stage_panels}
</section>
<ul class="trust">
  <li><span aria-hidden="true">📊</span>{x("Official shop prices from the government's KPDN survey", "Harga kedai rasmi daripada tinjauan KPDN kerajaan")}</li>
  <li><span aria-hidden="true">🔒</span>{x("What you type stays on your phone", "Apa yang anda taip kekal dalam telefon anda")}</li>
  <li><span aria-hidden="true">💗</span>{x("Made for Malaysian families", "Dibina untuk keluarga Malaysia")}</li>
</ul>
{ad("in_content", x)}
"""
    write_page(lang, "index.html", x("Pregnancy & pantang companion", "Teman kehamilan & berpantang"),
               x("Free week-by-week pregnancy guide, pantang planner, confinement cost comparer and baby milk prices for Malaysian families.",
                 "Panduan kehamilan minggu demi minggu, perancang pantang, perbandingan kos berpantang dan harga susu bayi untuk keluarga Malaysia - percuma."),
               body, {"weeks": weeks_js})


def p_weeks_index(lang):
    x = tr(lang)
    parts = []
    for t, (a, b) in enumerate([(4, 13), (14, 27), (28, 40)], start=1):
        lis = "".join(
            f'<li data-week="{n}"><a href="{n}.html"><span class="wk-n">{x("Week", "Minggu")} {n}</span>'
            f'<span class="wk-s"><span aria-hidden="true">{wk.W[n][0]}</span> {esc(wk.get(n, lang)["size"])}</span></a></li>'
            for n in range(a, b + 1))
        parts.append(f'<section><h2>{x("Trimester", "Trimester")} {t}</h2><ul class="week-list">{lis}</ul></section>')
    body = f"""
{page_head(x, "📅", "t-weeks", x("Week by week", "Minggu demi minggu"), x("Pregnancy week by week", "Kehamilan minggu demi minggu"),
             x("Your baby's size, growth and one useful thing to do - weeks 4 to 40.", "Saiz bayi, perkembangan dan satu perkara berguna - minggu 4 hingga 40."))}
{"".join(parts[:1])}
{ad("in_content", x)}
{"".join(parts[1:])}
"""
    write_page(lang, "weeks/index.html", x("Pregnancy week by week", "Kehamilan minggu demi minggu"),
               x("Week-by-week pregnancy guide for Malaysian mums: baby size, development and a to-do for every week.",
                 "Panduan kehamilan minggu demi minggu untuk ibu di Malaysia: saiz bayi, perkembangan dan tugasan setiap minggu."),
               body)


def p_week(lang, n):
    x = tr(lang)
    d = wk.get(n, lang)
    stats = " · ".join(s for s in (d["length"], d["weight"]) if s)
    def pg(m, arrow_left):
        if m < wk.FIRST or m > wk.LAST:
            return "<span></span>"
        lbl = f'{x("Week", "Minggu")} {m}'
        sub = f'<small>{wk.W[m][0]} {esc(wk.get(m, lang)["size"])}</small>'
        return (f'<a class="pg {"pg-prev" if arrow_left else "pg-next"}" href="{m}.html"><span>{"← " if arrow_left else ""}{lbl}{"" if arrow_left else " →"}</span>{sub}</a>')
    prev_l, next_l = pg(n - 1, True), pg(n + 1, False)
    chips = "".join(f'<span class="chip-static">{esc(c)}</span>' for c in
                    [x(f"Trimester {d['tri']}", f"Trimester {d['tri']}"), d["length"], d["weight"]] if c)
    body = f"""
<p class="crumbs"><a href="index.html">{x("Week by week", "Minggu demi minggu")}</a> › {x("Trimester", "Trimester")} {d["tri"]}</p>
<header class="week-hero">
  <div class="wh-emoji" aria-hidden="true">{d["emoji"]}</div>
  <div>
    <p class="ph-eyebrow">{x(f"Week {n} of 40", f"Minggu {n} daripada 40")} <span id="you-here" class="pill" hidden>{x("You are here", "Anda di sini")}</span></p>
    <h1>{x(f"Week {n}: baby is the size of {d['size']}", f"Minggu {n}: bayi sebesar {d['size']}")}</h1>
    <div class="chips-static">{chips}</div>
  </div>
</header>
<div class="progress wk-progress" role="progressbar" aria-valuemin="0" aria-valuemax="40" aria-valuenow="{n}"><span style="width:{round(n / 40 * 100)}%"></span></div>
<div class="info-grid">
  <section class="card"><h2><span aria-hidden="true">👶</span> {x("Your baby this week", "Bayi anda minggu ini")}</h2><p>{esc(d["baby"])}</p></section>
  <section class="card"><h2><span aria-hidden="true">🤰</span> {x("Your body", "Badan anda")}</h2><p>{esc(d["mum"])}</p></section>
</div>
<section class="card todo-card"><h2><span aria-hidden="true">✅</span> {x("To do this week", "Perlu dibuat minggu ini")}</h2><p>{esc(d["todo"])}</p></section>
{ad("in_content", x)}
{danger(x)}
<nav class="pager" aria-label="{x("Weeks", "Minggu")}">{prev_l}{next_l}</nav>
"""
    write_page(lang, f"weeks/{n}.html", x(f"Pregnancy week {n}: baby the size of {d['size']}", f"Kehamilan minggu ke-{n}: bayi sebesar {d['size']}"),
               x(f"Week {n} of pregnancy: your baby is about the size of {d['size']}. {d['baby']}",
                 f"Kehamilan minggu ke-{n}: saiz bayi lebih kurang {d['size']}. {d['baby']}")[:300],
               body, {"week": n})


def p_pantang(lang):
    x = tr(lang)
    trads = [
        ("Malay tradition (often 44 days)", "Tradisi Melayu (biasanya 44 hari)",
         "Common practices: urut (traditional massage), bertungku (warm compress), barut or bengkung (tummy binder), mandi herba (herbal bath), jamu, and warm, simple food. Many families avoid 'cold' foods.",
         "Amalan biasa: urut, bertungku, barut atau bengkung, mandi herba, jamu, dan makanan panas yang ringkas. Ramai keluarga mengelak makanan 'sejuk'."),
        ("Chinese tradition (30 days, some 40)", "Tradisi Cina (30 hari, ada yang 40)",
         "Known as zuo yue zi (坐月子). Common practices: warming food such as ginger, sesame oil and red dates, nourishing soups, avoiding cold drinks and wind, and resting at home for the month.",
         "Dikenali sebagai zuo yue zi (坐月子). Amalan biasa: makanan 'panas' seperti halia, minyak bijan dan kurma merah, sup berkhasiat, mengelak minuman sejuk dan angin, serta berehat di rumah sebulan."),
        ("Indian tradition (about 40 days)", "Tradisi India (lebih kurang 40 hari)",
         "Common practices: warm home-cooked food with garlic and spices, herbal drinks, oil massage and herbal baths, and plenty of rest.",
         "Amalan biasa: makanan panas masakan rumah dengan bawang putih dan rempah, minuman herba, urutan minyak dan mandi herba, serta banyak berehat."),
    ]
    ticons = ["🌙", "🏮", "🪔"]
    cards = "".join(f'<div class="trad-card"><span class="trad-ico" aria-hidden="true">{ticons[i]}</span><h3>{esc(x(a, b))}</h3><p>{esc(x(c, d))}</p></div>'
                    for i, (a, b, c, d) in enumerate(trads))
    body = f"""
{page_head(x, "🍲", "t-pantang", x("Pantang", "Pantang"), x("Pantang planner", "Perancang pantang"),
             x("A dated timeline for before and after the birth.", "Jadual bertarikh sebelum dan selepas bersalin."))}
<section class="card" id="pantang-tool">
  <p class="field-label">{x("Your tradition", "Tradisi anda")}</p>
  <div class="pill-group" role="group" aria-label="{x("Tradition", "Tradisi")}">
    <button type="button" class="pill-opt" data-v="44"><span aria-hidden="true">🌙</span> {x("Malay", "Melayu")} <small>44 {x("days", "hari")}</small></button>
    <button type="button" class="pill-opt" data-v="30"><span aria-hidden="true">🏮</span> {x("Chinese", "Cina")} <small>30 {x("days", "hari")}</small></button>
    <button type="button" class="pill-opt" data-v="40"><span aria-hidden="true">🪔</span> {x("Indian", "India")} <small>40 {x("days", "hari")}</small></button>
    <button type="button" class="pill-opt" data-v="custom"><span aria-hidden="true">✏️</span> {x("Other", "Lain-lain")}</button>
  </div>
  <label class="sr-only">{x("Tradition", "Tradisi")}
    <select id="p-trad" tabindex="-1">
      <option value="44">{x("Malay - 44 days", "Melayu - 44 hari")}</option>
      <option value="30">{x("Chinese - 30 days", "Cina - 30 hari")}</option>
      <option value="40">{x("Indian - 40 days", "India - 40 hari")}</option>
      <option value="custom">{x("Other - choose the number of days", "Lain-lain - pilih bilangan hari")}</option>
    </select></label>
  <label class="field" id="p-days-wrap" hidden>{x("Number of days", "Bilangan hari")}
    <input type="number" id="p-days" min="7" max="120" value="40" inputmode="numeric"></label>
  <div class="seg seg-radio" role="radiogroup" aria-label="{x("I know my baby's", "Saya tahu")}">
    <label><input type="radio" name="p-kind" value="due" checked><span>{x("Due date", "Tarikh jangkaan")}</span></label>
    <label><input type="radio" name="p-kind" value="birth"><span>{x("Baby is born", "Bayi sudah lahir")}</span></label>
  </div>
  <div class="due-row">
    <input type="date" id="p-date" aria-label="{x("Date", "Tarikh")}">
    <button type="button" class="btn" id="p-go">{x("Make my timeline", "Buat jadual saya")}</button>
  </div>
  <div id="p-result" aria-live="polite"></div>
</section>
{ad("in_content", x)}
<section><h2>{x("Pantang traditions in Malaysia", "Tradisi berpantang di Malaysia")} {tip(x("Every family is different - these are common practices, not rules.", "Setiap keluarga berbeza - ini amalan biasa, bukan peraturan."), x)}</h2>
<div class="trad-grid">{cards}</div></section>
<aside class="box note"><h2>{x("Stay safe during pantang", "Berpantang dengan selamat")}</h2><ul>
<li>{x("Ask your doctor before urut, bertungku or a tight binder - especially after a caesarean, when the wound needs to heal first.",
       "Tanya doktor sebelum berurut, bertungku atau memakai bengkung yang ketat - terutama selepas pembedahan caesarean, kerana luka perlu sembuh dahulu.")}</li>
<li>{x("Keep eating a variety of food and drink enough water - your body needs it to recover and to make milk. If your family's food rules cut out a lot, ask your doctor or a dietitian.",
       "Teruskan makan pelbagai jenis makanan dan minum air secukupnya - badan memerlukannya untuk pulih dan menghasilkan susu. Jika pantang makanan keluarga terlalu ketat, tanya doktor atau pakar diet.")}</li>
<li>{x("Go to hospital straight away for heavy bleeding, fever, smelly discharge, a painful swollen leg, chest pain or trouble breathing.",
       "Pergi segera ke hospital jika pendarahan banyak, demam, lelehan berbau, kaki bengkak dan sakit, sakit dada atau sukar bernafas.")}</li>
<li>{x("Feeling low for more than two weeks, or having thoughts of harming yourself or your baby? Talk to your doctor - postnatal depression is common and treatable. You can also call Talian HEAL 15555.",
       "Berasa sedih lebih daripada dua minggu, atau terfikir untuk mencederakan diri atau bayi? Berbincang dengan doktor - kemurungan selepas bersalin adalah biasa dan boleh dirawat. Anda juga boleh menghubungi Talian HEAL 15555.")}</li>
</ul></aside>
<p><a class="btn ghost" href="confinement-cost.html">{x("Compare confinement costs →", "Banding kos berpantang →")}</a></p>
"""
    write_page(lang, "pantang.html", x("Pantang planner", "Perancang pantang"),
               x("Free pantang (confinement) planner for Malay, Chinese and Indian traditions: what to do before and after the birth, with dates.",
                 "Perancang pantang percuma untuk tradisi Melayu, Cina dan India: perkara yang perlu dibuat sebelum dan selepas bersalin, dengan tarikh."),
               body)


def p_cost(lang):
    x = tr(lang)
    extras = [("care24", "24-hour baby care", "Jagaan bayi 24 jam"),
              ("lact", "Breastfeeding help", "Bantuan penyusuan"),
              ("massage", "Massage for mum", "Urutan untuk ibu"),
              ("partner", "Partner can stay", "Pasangan boleh tinggal"),
              ("laundry", "Laundry", "Dobi")]
    quotes = []
    for i in range(1, 5):
        chips = "".join(f'<label class="chip"><input type="checkbox" name="inc" value="{k}"><span>{esc(x(en, ms))}</span></label>'
                        for k, en, ms in extras)
        quotes.append(f"""<div class="quote" data-q="{i}"{" hidden" if i > 2 else ""}>
  <div class="q-head"><span class="q-num">{i}</span>
    <select name="preset" aria-label="{x("Choose a centre or package", "Pilih pusat atau pakej")} {i}">
      <option value="">{x("Choose a centre or package...", "Pilih pusat atau pakej...")}</option></select>
    <span class="q-tip"></span></div>
  <p class="q-sum" hidden></p>
  <details class="q-edit"><summary>{x("Edit / enter your own", "Ubah / isi sendiri")}</summary>
    <div class="q-fields">
      <label class="field q-name">{x("Name", "Nama")}<input type="text" name="name" maxlength="60" autocomplete="off"></label>
      <label class="field">{x("Total (RM)", "Jumlah (RM)")}<input type="number" name="price" min="0" step="1" inputmode="decimal"></label>
      <label class="field">{x("Days", "Hari")}<input type="number" name="days" min="1" max="120" value="28" inputmode="numeric"></label>
      <label class="field">{x("Babies per nurse", "Bayi/jururawat")}<input type="number" name="ratio" min="1" max="20" inputmode="numeric"></label>
    </div>
    <div class="chips">{chips}</div>
  </details>
</div>""")
    questions_en = [
        "Is the centre registered with the authorities? Ask to see the licence.",
        "How many babies does each nurse look after - during the day and at night?",
        "Are the nurses trained? What happens if a baby or mum falls ill, and how far is the nearest hospital?",
        "What is included: meals, laundry, massage, baby supplies, partner's stay?",
        "What if your baby comes early or late, or you need to stay longer in hospital? Is the deposit refundable?",
        "Can family visit, and when?",
        "For a nanny: does she live in, how many hours does she work, and does she cook pantang meals?",
    ]
    questions_ms = [
        "Adakah pusat ini berdaftar dengan pihak berkuasa? Minta untuk melihat lesennya.",
        "Berapa bayi yang dijaga oleh setiap jururawat - pada waktu siang dan malam?",
        "Adakah jururawat terlatih? Apa berlaku jika bayi atau ibu sakit, dan berapa jauh hospital terdekat?",
        "Apa yang termasuk: makanan, dobi, urutan, barang bayi, penginapan pasangan?",
        "Bagaimana jika bayi lahir awal atau lewat, atau anda perlu tinggal lebih lama di hospital? Adakah deposit boleh dipulangkan?",
        "Bolehkah keluarga melawat, dan bila?",
        "Untuk pengasuh: adakah dia tinggal bersama, berapa jam bekerja, dan adakah dia memasak makanan pantang?",
    ]
    qs = "".join(f"<li>{esc(q)}</li>" for q in (questions_ms if lang == "ms" else questions_en))
    maps_q = quote_plus(x("confinement centre near me", "pusat berpantang berhampiran"))
    body = f"""
{page_head(x, "💰", "t-cost", x("Confinement", "Berpantang"), x("Confinement cost", "Kos berpantang"),
             x("Compare centres and nannies by price per day.", "Banding pusat dan pengasuh mengikut harga sehari."))}
<section class="card" id="quote-tool">
  <h2>{x("Compare quotes", "Banding sebut harga")} {tip(x("Pick a centre or a typical package and the rest fills in. Change anything to match what you were offered. Saved only on this phone.",
                                                        "Pilih pusat atau pakej biasa dan yang lain diisi sendiri. Ubah apa-apa supaya sama dengan tawaran anda. Disimpan dalam telefon ini sahaja."), x)}</h2>
  <div class="quotes">{"".join(quotes)}</div>
  <div class="q-actions">
    <button type="button" class="link-btn" id="q-add">+ {x("Add another quote", "Tambah sebut harga")}</button>
    <button type="button" class="link-btn muted" id="q-clear">{x("Clear all", "Padam semua")}</button>
  </div>
  <div id="q-result" aria-live="polite"></div>
</section>
<p class="maps-row"><a class="btn ghost" href="https://www.google.com/maps/search/?api=1&amp;query={maps_q}" target="_blank" rel="noopener">🔎 {x("More centres near you (Google Maps)", "Lagi pusat berhampiran (Google Maps)")} ↗</a>
{tip(x("Smaller local centres are often cheaper but don't publish prices online. Ask them for a quote, then choose 'Edit / enter your own' above.",
       "Pusat kecil berhampiran selalunya lebih murah tetapi tidak menerbitkan harga dalam talian. Minta sebut harga, kemudian pilih 'Ubah / isi sendiri' di atas."), x)}</p>
{ad("in_content", x)}
<section><h2>{x("Typical prices for 28 days", "Harga biasa untuk 28 hari")} {tip(x("Rough 2026 ranges from price guides (malaysia4u.com). Prices differ a lot by city and by what's included - always get a written quote.",
                                                                              "Anggaran julat 2026 daripada panduan harga (malaysia4u.com). Harga sangat berbeza mengikut bandar dan apa yang termasuk - sentiasa minta sebut harga bertulis."), x)}</h2>
<ul class="price-list">
  <li><span>{x("Live-in nanny", "Pengasuh tinggal bersama")}</span><strong>RM5,000 – 9,000</strong></li>
  <li><span>{x("Centre - mid-range", "Pusat - pertengahan")}</span><strong>RM12,000 – 18,000</strong></li>
  <li><span>{x("Centre - luxury", "Pusat - mewah")}</span><strong>{x("RM20,000 – 40,000+", "RM20,000 – 40,000+")}</strong></li>
</ul></section>
<details class="acc"><summary>{x("Ask before you pay a deposit", "Tanya sebelum membayar deposit")}</summary><ol>{qs}</ol></details>
{contact_cta(x, "Run a confinement centre or work as a confinement nanny? Ask us about being listed here.",
             "Mengusahakan pusat berpantang atau bekerja sebagai pengasuh berpantang? Tanya kami tentang penyenaraian di sini.")}
"""
    write_page(lang, "confinement-cost.html", x("Confinement centre & nanny cost in Malaysia", "Kos pusat berpantang & pengasuh di Malaysia"),
               x("How much a confinement centre or confinement nanny costs in Malaysia, questions to ask, and a free tool to compare quotes per day.",
                 "Berapa kos pusat berpantang atau pengasuh berpantang di Malaysia, soalan yang perlu ditanya, dan alat percuma membandingkan sebut harga sehari."),
               body)


BAG = [
    ("Documents", "Dokumen", [
        ("ic", "MyKad (IC) - both parents", "MyKad - kedua-dua ibu bapa", None),
        ("pinkbook", "Pink book or antenatal card", "Buku pink atau kad antenatal", None),
        ("marriage", "Marriage certificate (for birth registration)", "Sijil nikah (untuk pendaftaran kelahiran)", None),
        ("insurance", "Insurance card or guarantee letter (GL)", "Kad insurans atau surat jaminan (GL)", None),
        ("forms", "Hospital admission letter or forms", "Surat atau borang kemasukan hospital", None),
        ("cash", "Some cash and a bank card", "Sedikit wang tunai dan kad bank", None),
    ]),
    ("For mum", "Untuk ibu", [
        ("nursing_tops", "2-3 loose tops that open at the front for breastfeeding", "2-3 baju longgar berbutang depan untuk menyusu", "baju menyusu"),
        ("nursing_bra", "2 nursing bras", "2 coli menyusu", "nursing bra"),
        ("maternity_pads", "Maternity pads (1-2 packs)", "Tuala wanita bersalin (1-2 bungkus)", "maternity pad"),
        ("disposable_underwear", "Disposable or old underwear", "Seluar dalam pakai buang atau lama", "disposable underwear maternity"),
        ("nipple_cream", "Nipple cream", "Krim puting", "nipple cream"),
        ("straw_bottle", "Water bottle with a straw", "Botol air berstraw", "botol air straw"),
        ("slippers", "Slippers and socks", "Selipar dan stokin", None),
        ("toiletries", "Toiletries, toothbrush and towel", "Kelengkapan mandi, berus gigi dan tuala", None),
        ("going_home", "Comfortable clothes to go home in", "Pakaian selesa untuk pulang", None),
        ("snacks", "Snacks", "Makanan ringan", None),
    ]),
    ("For baby", "Untuk bayi", [
        ("newborn_clothes", "2-3 newborn outfits", "2-3 pasang baju bayi baru lahir", "baju bayi newborn"),
        ("swaddle", "Swaddles (kain bedung)", "Kain bedung", "kain bedung bayi"),
        ("newborn_diapers", "Newborn diapers (1 pack)", "Lampin bayi baru lahir (1 bungkus)", "lampin bayi newborn"),
        ("wipes", "Baby wipes or cotton wool", "Tisu basah bayi atau kapas", "baby wipes"),
        ("mittens", "Mittens, socks and a cap", "Sarung tangan, stokin dan topi", "sarung tangan kaki bayi"),
        ("blanket", "Baby blanket", "Selimut bayi", "selimut bayi"),
        ("baby_bottles", "Baby feeding bottles (if you plan to use them)", "Botol susu bayi (jika perlu)", "botol susu bayi"),
        ("car_seat", "Infant car seat, fitted before the birth", "Kerusi keselamatan kereta bayi, dipasang sebelum bersalin", "infant car seat"),
    ]),
    ("For your partner", "Untuk pasangan", [
        ("powerbank", "Phone charger and power bank", "Pengecas telefon dan power bank", "power bank"),
        ("partner_clothes", "Change of clothes and toiletries", "Pakaian salin dan kelengkapan mandi", None),
        ("partner_snacks", "Snacks and drinks", "Makanan ringan dan minuman", None),
        ("contacts", "List of important phone numbers", "Senarai nombor telefon penting", None),
    ]),
]


def p_bag(lang):
    x = tr(lang)
    secs = []
    for te, tm, items in BAG:
        lis = "".join(
            f'<li><label class="check"><input type="checkbox" data-key="{k}"> {esc(x(en, ms))}</label>'
            f'{shop(k, q, x) if q else ""}</li>' for k, en, ms, q in items)
        secs.append(f'<section class="card"><h2>{esc(x(te, tm))}</h2><ul class="checklist">{lis}</ul></section>')
    body = f"""
{page_head(x, "👜", "t-bag", x("Before the birth", "Sebelum bersalin"), x("Hospital bag checklist", "Senarai semak beg hospital"), extra=tip(x("Pack by about 36 weeks. Your ticks are saved on this phone. 'Shop' links open Shopee - some are affiliate links, so we may earn a small commission at no extra cost to you.",
                                                                       "Siapkan sebelum lebih kurang 36 minggu. Tanda anda disimpan dalam telefon ini. Pautan 'Beli' membuka Shopee - sesetengahnya pautan afiliasi, jadi kami mungkin mendapat komisen kecil tanpa kos tambahan kepada anda."), x))}
<div class="bag-progress card"><div class="bp-top"><strong id="bag-progress" aria-live="polite"></strong><button type="button" class="link-btn muted" id="bag-reset">{x("Untick everything", "Buang semua tanda")}</button></div>
<div class="progress"><span id="bag-bar" style="width:0%"></span></div></div>
{secs[0]}
{ad("in_content", x)}
{"".join(secs[1:])}
"""
    write_page(lang, "hospital-bag.html", x("Hospital bag checklist for Malaysian mums", "Senarai semak beg hospital untuk ibu"),
               x("What to pack in your hospital bag for giving birth in Malaysia: documents, mum, baby and partner - a free checklist that saves on your phone.",
                 "Apa yang perlu dibawa ke hospital untuk bersalin: dokumen, barang ibu, bayi dan pasangan - senarai semak percuma yang disimpan dalam telefon."),
               body)


def p_leave(lang):
    x = tr(lang)
    body = f"""
{page_head(x, "🗓️", "t-leave", x("Work", "Kerja"), x("Maternity leave", "Cuti bersalin"),
             x("When your 98 days (and dad's 7 days) start and end.", "Bila 98 hari anda (dan 7 hari bapa) bermula dan berakhir."))}
<section class="card" id="leave-tool">
  <label class="field">{x("Baby's birth date (or due date)", "Tarikh lahir bayi (atau tarikh jangkaan)")}<input type="date" id="lv-birth"></label>
  <label class="field">{x("Maternity leave starts on (leave empty = birth date)", "Cuti bersalin bermula pada (biar kosong = tarikh lahir)")}<input type="date" id="lv-mstart"></label>
  <label class="field">{x("Paternity leave starts on (leave empty = birth date)", "Cuti paterniti bermula pada (biar kosong = tarikh lahir)")}<input type="date" id="lv-pstart"></label>
  <button type="button" class="btn" id="lv-go">{x("Calculate", "Kira")}</button>
  <div id="lv-result" aria-live="polite"></div>
</section>
{ad("in_content", x)}
<details class="acc"><summary>{x("The rules in short", "Peraturan secara ringkas")}</summary><ul>
<li>{x("Under the Employment Act 1955 (as amended in 2023), mothers get 98 consecutive days of paid maternity leave.",
       "Di bawah Akta Kerja 1955 (dipinda pada 2023), ibu layak mendapat 98 hari berturut-turut cuti bersalin bergaji.")}</li>
<li>{x("Maternity leave can start up to 30 days before the birth, and no later than the day after.",
       "Cuti bersalin boleh bermula sehingga 30 hari sebelum bersalin, dan tidak lewat daripada sehari selepas bersalin.")}</li>
<li>{x("Married fathers get 7 consecutive days of paid paternity leave. Conditions apply - for example, at least 12 months with the employer and telling them early.",
       "Bapa yang berkahwin layak mendapat 7 hari berturut-turut cuti paterniti bergaji. Syarat dikenakan - contohnya, bekerja sekurang-kurangnya 12 bulan dengan majikan dan memaklumkan awal.")}</li>
<li>{x("Civil servants, and workers in Sabah and Sarawak, have their own rules. Check with your HR department.",
       "Penjawat awam, serta pekerja di Sabah dan Sarawak, mempunyai peraturan sendiri. Semak dengan bahagian sumber manusia (HR).")}</li>
</ul></details>
"""
    write_page(lang, "leave.html", x("Maternity leave calculator Malaysia (98 days)", "Kalkulator cuti bersalin Malaysia (98 hari)"),
               x("Calculate your 98 days of maternity leave and 7 days of paternity leave under Malaysia's Employment Act.",
                 "Kira 98 hari cuti bersalin dan 7 hari cuti paterniti di bawah Akta Kerja Malaysia."),
               body)


def p_prices(lang):
    x = tr(lang)
    body = f"""
{page_head(x, "🍼", "t-prices", x("Prices", "Harga"), x("Milk & diaper prices", "Harga susu & lampin"), lead=x("Official shop prices near you.", "Harga kedai rasmi berhampiran anda."), lead_id="pr-updated", extra=tip(x("Shop prices from the government's price survey: PriceCatcher by KPDN, published on data.gov.my. Typical = the middle price across shops. From = 1 in 10 shops charge this or less. Prices change often - check in store.",
                                                                         "Harga kedai daripada tinjauan harga kerajaan: PriceCatcher oleh KPDN, diterbitkan di data.gov.my. Biasa = harga pertengahan di semua kedai. Dari = 1 daripada 10 kedai mengenakan harga ini atau lebih rendah. Harga sering berubah - semak di kedai."), x))}
<section class="filters">
  <form class="search-row" id="pr-search" role="search">
    <input type="search" id="pr-q" placeholder="{x("Search, e.g. Drypers or Dutch Lady", "Cari, cth. Drypers atau Dutch Lady")}" aria-label="{x("Search products", "Cari produk")}">
    <button type="submit" class="btn">{x("Search", "Cari")}</button>
  </form>
  <div class="filter-row">
    <select id="pr-group" aria-label="{x("Product type", "Jenis produk")}">
      <option value="">{x("All products", "Semua produk")}</option>
      {"".join(f'<option value="{g}">{GROUPS[g][0]} {esc(x(GROUPS[g][1], GROUPS[g][2]))}</option>' for g in PRICE_GROUPS)}
    </select>
    <select id="pr-state" aria-label="{x("State", "Negeri")}"></select>
    <select id="pr-district" aria-label="{x("District", "Daerah")}" disabled></select>
  </div>
</section>
<div id="pr-tables" aria-live="polite"><p class="muted">{x("Loading prices...", "Memuatkan harga...")}</p></div>
{ad("bottom", x)}
"""
    write_page(lang, "prices.html", x("Baby milk & diaper prices in Malaysia", "Harga susu bayi & lampin di Malaysia"),
               x("Compare baby milk, formula and diaper prices by state and district in Malaysia, from the government's PriceCatcher survey. Find the cheapest shops near you.",
                 "Banding harga susu bayi, susu formula dan lampin mengikut negeri dan daerah, daripada tinjauan PriceCatcher kerajaan. Cari kedai paling murah berhampiran anda."),
               body)


def p_nursery(lang):
    x = tr(lang)
    kinds = [
        ("Taska (childcare centre)", "Taska (taman asuhan kanak-kanak)",
         "For babies and children under 4. Every taska must be registered with the Social Welfare Department (JKM).",
         "Untuk bayi dan kanak-kanak bawah 4 tahun. Setiap taska wajib berdaftar dengan Jabatan Kebajikan Masyarakat (JKM)."),
        ("Tadika (kindergarten)", "Tadika",
         "For children aged 4 to 6. Private tadika register with the Ministry of Education (KPM).",
         "Untuk kanak-kanak berumur 4 hingga 6 tahun. Tadika swasta berdaftar dengan Kementerian Pendidikan (KPM)."),
        ("Government preschools", "Prasekolah kerajaan",
         "KEMAS and PERPADUAN tabika, and preschool classes (prasekolah) in government schools - usually with low fees.",
         "Tabika KEMAS dan PERPADUAN, serta kelas prasekolah di sekolah kerajaan - biasanya yuran rendah."),
    ]
    cards = "".join(f'<details class="acc"><summary>{esc(x(a, b))}</summary><p>{esc(x(c, d))}</p></details>' for a, b, c, d in kinds)
    # Compare tool: mums type in the taska/tadika they visit; ranked by first-year cost.
    nu_extras = [("reg", "Registered (JKM / KPM)", "Berdaftar (JKM / KPM)"), ("cctv", "CCTV for parents", "CCTV untuk ibu bapa"),
                 ("meals", "Meals included", "Makanan termasuk"), ("halal", "Halal food", "Makanan halal"),
                 ("near", "Near home / work", "Dekat rumah / tempat kerja"), ("transport", "Transport", "Pengangkutan")]
    nu_cards = []
    for i in range(1, 5):
        chips = "".join(f'<label class="chip"><input type="checkbox" name="inc" value="{k}"><span>{esc(x(en, ms))}</span></label>'
                        for k, en, ms in nu_extras)
        nu_cards.append(f"""<div class="quote" data-q="{i}"{" hidden" if i > 2 else ""}>
  <div class="q-head"><span class="q-num">{i}</span>
    <input type="text" name="name" maxlength="60" autocomplete="off" placeholder="{x("Name of taska / tadika", "Nama taska / tadika")}" aria-label="{x("Name", "Nama")} {i}"></div>
  <div class="q-fields">
    <label class="field">{x("Monthly fee (RM)", "Yuran bulanan (RM)")}<input type="number" name="fee" min="0" inputmode="decimal"></label>
    <label class="field">{x("Registration + deposit (RM)", "Pendaftaran + deposit (RM)")}<input type="number" name="reg_fee" min="0" inputmode="decimal"></label>
    <label class="field">{x("Opens", "Buka")}<input type="time" name="open"></label>
    <label class="field">{x("Closes", "Tutup")}<input type="time" name="close"></label>
    <label class="field">{x("Children per carer", "Kanak-kanak/pengasuh")}<input type="number" name="ratio" min="1" max="30" inputmode="numeric"></label>
  </div>
  <p class="q-sum" hidden></p>
  <div class="chips">{chips}</div>
</div>""")
    nu_compare = f"""<section class="card" id="nu-compare">
  <h2>{x("Compare taska & tadika", "Banding taska & tadika")} {tip(x("Visit a few places, then type in what they told you. We rank them by first-year cost (12 months of fees plus registration and deposit). Saved only on this phone.",
                                                                   "Lawat beberapa tempat, kemudian masukkan apa yang mereka beritahu. Kami susun mengikut kos tahun pertama (12 bulan yuran serta pendaftaran dan deposit). Disimpan dalam telefon ini sahaja."), x)}</h2>
  <div class="quotes">{"".join(nu_cards)}</div>
  <div class="q-actions">
    <button type="button" class="link-btn" id="nu-add">+ {x("Add another", "Tambah lagi")}</button>
    <button type="button" class="link-btn muted" id="nu-clear">{x("Clear all", "Padam semua")}</button>
  </div>
  <div id="nu-result" aria-live="polite"></div>
</section>"""
    type_rows = [
        ("🧸", "Taska", "Taska", "Under 4", "Bawah 4 tahun", "JKM", "JKM", "Private: varies by area", "Swasta: berbeza ikut kawasan"),
        ("🎒", "Tadika", "Tadika", "4 - 6", "4 - 6 tahun", "KPM", "KPM", "Private: varies by area", "Swasta: berbeza ikut kawasan"),
        ("🏫", "Government preschool", "Prasekolah kerajaan", "4 - 6", "4 - 6 tahun", "KEMAS · PERPADUAN · KPM", "KEMAS · PERPADUAN · KPM",
         "Usually low", "Biasanya rendah"),
    ]
    type_table = ('<div class="table-wrap"><table class="types"><thead><tr><th>' + x("Type", "Jenis") + "</th><th>" + x("Ages", "Umur") +
                  "</th><th>" + x("Registered with", "Berdaftar dengan") + '</th><th class="hide-sm">' + x("Fees", "Yuran") + "</th></tr></thead><tbody>" +
                  "".join(f'<tr><td><span aria-hidden="true">{ic}</span> <strong>{esc(x(te, tm))}</strong></td><td>{esc(x(ae, am))}</td>'
                          f'<td>{esc(x(re, rm_))}</td><td class="hide-sm">{esc(x(fe, fm))}</td></tr>'
                          for ic, te, tm, ae, am, re, rm_, fe, fm in type_rows) + "</tbody></table></div>")
    checks_en = [
        "Is it registered? A registered taska shows its JKM certificate and registration plaque - ask to see them.",
        "Are the carers trained (for example JKM's basic childcare course, KAAK)?",
        "How many children does each carer look after?",
        "Is there CCTV, and can parents view it?",
        "What food is served (halal?), and where do the children nap?",
        "What happens when a child is sick?",
        "Do the opening hours fit your working hours? Is there a late fee?",
        "Fees, deposit and extra charges - get them in writing.",
        "What is the emergency plan, and where is the nearest clinic?",
    ]
    checks_ms = [
        "Adakah ia berdaftar? Taska berdaftar mempamerkan sijil JKM dan plak berdaftar - minta untuk melihatnya.",
        "Adakah pengasuh terlatih (contohnya Kursus Asas Asuhan Kanak-Kanak, KAAK, oleh JKM)?",
        "Berapa kanak-kanak yang dijaga oleh setiap pengasuh?",
        "Adakah CCTV, dan bolehkah ibu bapa melihatnya?",
        "Apakah makanan yang disediakan (halal?), dan di mana kanak-kanak tidur?",
        "Apa berlaku jika anak sakit?",
        "Adakah waktu operasi sesuai dengan waktu kerja anda? Adakah caj lewat?",
        "Yuran, deposit dan caj tambahan - minta secara bertulis.",
        "Apakah pelan kecemasan, dan di mana klinik terdekat?",
    ]
    ql = "".join(f"<li>{esc(q)}</li>" for q in (checks_ms if lang == "ms" else checks_en))
    near_taska = "https://www.google.com/maps/search/?api=1&query=" + quote_plus("taska near me")
    near_tadika = "https://www.google.com/maps/search/?api=1&query=" + quote_plus("tadika near me")
    body = f"""
{page_head(x, "🧸", "t-nursery", x("After the birth", "Selepas bersalin"), x("Taska & tadika", "Taska & tadika"),
             x("Find, check and compare childcare near you.", "Cari, semak dan banding penjagaan anak berhampiran anda."))}
<section class="card" id="nursery-tool">
  <div class="btn-row">
    <a class="btn" id="nu-near-taska" href="{near_taska}" target="_blank" rel="noopener">📍 {x("Taska near me", "Taska berhampiran")}</a>
    <a class="btn" id="nu-near-tadika" href="{near_tadika}" target="_blank" rel="noopener">📍 {x("Tadika near me", "Tadika berhampiran")}</a>
    {tip(x("Opens Google Maps, which uses your phone's location.", "Membuka Google Maps, yang menggunakan lokasi telefon anda."), x)}
  </div>
  <div class="filter-row">
    <select id="nu-state" aria-label="{x("State", "Negeri")}"></select>
    <select id="nu-district" aria-label="{x("District", "Daerah")}" disabled></select>
  </div>
  <div class="btn-row" id="nu-area-links" hidden>
    <a class="btn ghost" id="nu-taska" href="#" target="_blank" rel="noopener"></a>
    <a class="btn ghost" id="nu-tadika" href="#" target="_blank" rel="noopener"></a>
  </div>
</section>
{nu_compare}
<h2>{x("Taska, tadika or preschool?", "Taska, tadika atau prasekolah?")}</h2>
{type_table}
{ad("in_content", x)}
<div class="acc-list">
<details class="acc"><summary>{x("Check before you choose", "Semak sebelum memilih")}</summary><ol>{ql}</ol></details>
<details class="acc"><summary>{x("Registration, complaints & tax relief", "Pendaftaran, aduan & pelepasan cukai")}</summary><ul>
<li>{x("The government's official list of registered taska:", "Senarai rasmi taska berdaftar:")}
<a href="https://www.malaysia.gov.my/my/personas/ibu-bapa-kepada-anak-kecil-0-6-tahun/menghantar-anak-ke-pusat-jagaan/taman-asuhan-kanak-kanak-taska" target="_blank" rel="noopener">MyGOV</a>.</li>
<li>{x("To report an unregistered taska, call Talian Kasih 15999 or your nearest welfare office.",
       "Untuk melaporkan taska tidak berdaftar, hubungi Talian Kasih 15999 atau pejabat kebajikan masyarakat terdekat.")}</li>
<li>{x("Fees paid to a registered taska or tadika for a child aged 6 or below can get income tax relief (up to RM3,000 a year - check LHDN for the current rules).",
       "Yuran taska atau tadika berdaftar untuk anak berumur 6 tahun ke bawah boleh mendapat pelepasan cukai pendapatan (sehingga RM3,000 setahun - semak peraturan terkini dengan LHDN).")}</li>
</ul></details>
</div>
{contact_cta(x, "Run a taska or tadika? Ask us about being listed here.", "Mengusahakan taska atau tadika? Tanya kami tentang penyenaraian di sini.")}
"""
    write_page(lang, "nursery.html", x("Find a taska or tadika near you", "Cari taska atau tadika berhampiran"),
               x("Find a taska (childcare centre) or tadika (kindergarten) near you in Malaysia, and the questions to ask before you choose.",
                 "Cari taska atau tadika berhampiran anda, dan soalan yang perlu ditanya sebelum memilih."),
               body)


def p_privacy(lang):
    x = tr(lang)
    email = (f'<a href="mailto:{esc(config.CONTACT_EMAIL)}">{esc(config.CONTACT_EMAIL)}</a>'
             if config.CONTACT_EMAIL else x("the email on our About page", "e-mel di halaman Tentang kami"))
    body = f"""
{page_head(x, "🔒", "t-leave", x("Your data", "Data anda"), x("Privacy", "Privasi"))}
<p class="small muted">{x("Last updated", "Kemas kini terakhir")}: {TODAY.isoformat()}</p>
<h2>{x("What you type stays on your phone", "Apa yang anda taip kekal dalam telefon anda")}</h2>
<p>{x("There are no accounts. Your due date, checklists, quotes and area choices are saved only in your own browser (local storage) so the tools remember them. They are never sent to us. To delete them, clear this site's data in your browser settings.",
       "Tiada akaun. Tarikh jangkaan, senarai semak, sebut harga dan pilihan kawasan anda disimpan dalam pelayar anda sahaja (local storage) supaya alat boleh mengingatinya. Data ini tidak dihantar kepada kami. Untuk memadamnya, kosongkan data laman ini dalam tetapan pelayar.")}</p>
<h2>{x("Advertising", "Pengiklanan")}</h2>
<p>{x("This site may show ads from Google AdSense. Google and its partners use cookies to show ads based on your visits to this and other websites.",
       "Laman ini mungkin memaparkan iklan daripada Google AdSense. Google dan rakan kongsinya menggunakan kuki untuk memaparkan iklan berdasarkan lawatan anda ke laman ini dan laman lain.")}
<a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">{x("How Google uses this information", "Cara Google menggunakan maklumat ini")}</a>.
{x("You can turn off personalised ads in", "Anda boleh mematikan iklan yang diperibadikan di")} <a href="https://myadcenter.google.com" target="_blank" rel="noopener">My Ad Center</a>.</p>
<h2>{x("Shop links", "Pautan kedai")}</h2>
<p>{x("Some shop links are affiliate links. If you buy through them we may earn a small commission, at no extra cost to you. We never earn from infant formula.",
       "Sesetengah pautan kedai ialah pautan afiliasi. Jika anda membeli melaluinya, kami mungkin mendapat komisen kecil tanpa kos tambahan kepada anda. Kami tidak pernah mendapat komisen daripada susu formula bayi.")}</p>
<h2>{x("Feedback form", "Borang cadangan")}</h2>
<p>{x("Ideas you send through our feedback form are collected by Google Forms. Only leave your email if you want a reply, and please don't share medical details there.",
       "Cadangan yang dihantar melalui borang kami dikumpul oleh Google Forms. Tinggalkan e-mel hanya jika mahu balasan, dan jangan kongsi butiran perubatan di sana.")}</p>
<h2>{x("Other sites", "Laman lain")}</h2>
<p>{x("Product pictures on the prices page load from Shopee's image servers. Links to Google Maps, Shopee and government sites follow those sites' own privacy policies.",
       "Gambar produk di halaman harga dimuatkan dari pelayan gambar Shopee. Pautan ke Google Maps, Shopee dan laman kerajaan tertakluk kepada dasar privasi laman tersebut.")}</p>
<h2>{x("Contact", "Hubungi")}</h2>
<p>{x("Questions about privacy? Write to", "Soalan tentang privasi? Tulis kepada")} {email}.</p>
"""
    write_page(lang, "privacy.html", x("Privacy policy", "Dasar privasi"),
               x("How this site handles your information: no accounts, your data stays on your phone.",
                 "Cara laman ini mengendalikan maklumat anda: tiada akaun, data kekal dalam telefon anda."),
               body)


def p_about(lang):
    x = tr(lang)
    email = (f'<p>{x("Contact us:", "Hubungi kami:")} <a href="mailto:{esc(config.CONTACT_EMAIL)}">{esc(config.CONTACT_EMAIL)}</a></p>'
             if config.CONTACT_EMAIL else "")
    body = f"""
{page_head(x, "🤰", "t-home", x("About", "Tentang kami"), esc(config.SITE_NAME))}
<p class="muted">{x("Free, simple tools for Malaysian families expecting a baby - in English and Bahasa Melayu.",
                   "Alat percuma dan mudah untuk keluarga Malaysia yang menantikan bayi - dalam Bahasa Melayu dan English.")}</p>
<p>{x("We bring together the things parents-to-be in Malaysia ask about most: how the baby is growing, pantang, confinement costs, maternity leave, baby milk prices and childcare.",
       "Kami menghimpunkan perkara yang paling kerap ditanya oleh bakal ibu bapa di Malaysia: perkembangan bayi, pantang, kos berpantang, cuti bersalin, harga susu bayi dan penjagaan anak.")}</p>
<h2>{x("Not medical advice", "Bukan nasihat perubatan")}</h2>
<p>{x("Everything here is general information. Every pregnancy is different - always follow your doctor, nurse or midwife, and go to a clinic or hospital if you are worried.",
       "Semua di sini ialah maklumat umum. Setiap kehamilan berbeza - sentiasa ikut nasihat doktor, jururawat atau bidan, dan pergi ke klinik atau hospital jika anda risau.")}</p>
<h2>{x("Where our information comes from", "Sumber maklumat kami")}</h2>
<ul>
<li>{x("Prices: PriceCatcher by KPDN, published on data.gov.my.", "Harga: PriceCatcher oleh KPDN, diterbitkan di data.gov.my.")}</li>
<li>{x("Leave rules: Employment Act 1955 (amended 2023).", "Peraturan cuti: Akta Kerja 1955 (dipinda 2023).")}</li>
<li>{x("Baby sizes are rough averages from common pregnancy references.", "Saiz bayi ialah anggaran purata daripada rujukan kehamilan biasa.")}</li>
<li>{x("Vaccination dates: KKM National Immunisation Programme.", "Tarikh vaksin: Program Imunisasi Kebangsaan KKM.")}</li>
<li>{x("Breast milk storage: KKM nutrition division (Bahagian Pemakanan) poster for working mothers.", "Simpan susu ibu: poster Bahagian Pemakanan KKM untuk ibu bekerja.")}</li>
</ul>
{email}
"""
    write_page(lang, "about.html", x("About", "Tentang kami"),
               x("About this free pregnancy and pantang site for Malaysian families.", "Tentang laman kehamilan dan pantang percuma untuk keluarga Malaysia."),
               body)


# ---------------------------------------------------------------- build

def root_files():
    chooser = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(config.SITE_NAME)}</title><link rel="icon" href="{ICON}">
<link rel="stylesheet" href="assets/style.css?v={VER}">
<script>var l;try{{l=localStorage.getItem('tm_lang')}}catch(e){{}}
if(l!=='en'&&l!=='ms'){{l=(navigator.language||'').toLowerCase().indexOf('ms')===0?'ms':'en'}}location.replace(l+'/index.html');</script>
</head><body><main class="wrap"><h1>{esc(config.SITE_NAME)}</h1>
<p><a class="btn" href="ms/index.html">Bahasa Melayu</a> <a class="btn ghost" href="en/index.html">English</a></p></main></body></html>
"""
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(chooser)
    # Pages check this on load and reload themselves if the browser showed an old saved copy.
    with open(os.path.join(OUT, "version.json"), "w", encoding="utf-8") as f:
        json.dump({"v": VER}, f)
    robots = "User-agent: *\nAllow: /\n"
    if config.BASE_URL:
        robots += f"Sitemap: {config.BASE_URL}/sitemap.xml\n"
        urls = []
        for lang, path in WRITTEN:
            u = f"{config.BASE_URL}/{lang}/{path}"
            u = u[:-len("index.html")] if u.endswith("index.html") else u
            urls.append(f"<url><loc>{esc(u)}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>")
        with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    + "".join(urls) + "</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(robots)
    if config.ADSENSE_CLIENT:
        pub = config.ADSENSE_CLIENT.replace("ca-", "")
        with open(os.path.join(OUT, "ads.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")


def main():
    global AD_PREVIEW
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad-preview", action="store_true")
    AD_PREVIEW = ap.parse_args().ad_preview

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(HERE, "static"), os.path.join(OUT, "assets"))
    # Files that must sit at the site root, e.g. Google Search Console's verification file. Keep them.
    shutil.copytree(os.path.join(HERE, "root-files"), OUT, dirs_exist_ok=True)
    data_src = os.path.join(HERE, "site-data")
    if os.path.isdir(data_src):
        shutil.copytree(data_src, os.path.join(OUT, "data"))
    else:
        print("warning: site-data/ missing - run scripts/update_prices.py first; prices page will be empty")

    for lang in LANGS:
        p_home(lang)
        p_weeks_index(lang)
        for n in range(wk.FIRST, wk.LAST + 1):
            p_week(lang, n)
        p_pantang(lang)
        p_cost(lang)
        p_bag(lang)
        p_leave(lang)
        p_prices(lang)
        p_nursery(lang)
        p_privacy(lang)
        p_about(lang)
        if config.FEEDBACK_FORM_URL:
            p_feedback(lang)
        p_fertility(lang)
        p_names(lang)
        p_labour(lang)
        p_vaccines(lang)
        p_breastmilk(lang)
        p_newborn(lang)
    root_files()
    print(f"built {len(WRITTEN)} pages into {OUT}" + (" (ad preview)" if AD_PREVIEW else ""))


if __name__ == "__main__":
    main()
