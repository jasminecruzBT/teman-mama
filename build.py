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
from content import topics as tp
from content import topics2 as t2

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
    ("#before", "Before pregnancy", "Sebelum hamil", "🌱", ""),
    ("fertility.html", "Fertile days", "Hari subur", "🌸", "t-fert"),
    ("planning.html", "Planning a pregnancy", "Persediaan hamil", "📝", "t-plan"),
    ("#preg", "Pregnant", "Sedang hamil", "🤰", ""),
    ("weeks/index.html", "Week by week", "Minggu demi minggu", "📅", "t-weeks"),
    ("antenatal.html", "Antenatal check-ups", "Pemeriksaan antenatal", "🩺", "t-ante"),
    ("healthy-pregnancy.html", "Healthy pregnancy", "Penjagaan kesihatan semasa hamil", "🥗", "t-healthy"),
    ("pregnancy-body.html", "Body changes & symptoms", "Perubahan badan & simptom", "🤰", "t-body"),
    ("names.html", "Baby names", "Nama bayi", "✨", "t-names"),
    ("labour.html", "Kicks & contractions", "Tendangan & kontraksi", "⏱️", "t-labour"),
    ("hospital-bag.html", "Hospital bag", "Beg hospital", "👜", "t-bag"),
    ("delivery-cost.html", "Delivery cost", "Kos bersalin", "🏥", "t-deliv"),
    ("confinement-cost.html", "Confinement cost", "Kos berpantang", "💰", "t-cost"),
    ("budget.html", "Baby's first-year budget", "Anggaran belanja tahun pertama bayi", "🧾", "t-budget"),
    ("#new", "New mum", "Ibu baharu", "👶", ""),
    ("pantang.html", "Pantang planner", "Perancang pantang", "🍲", "t-pantang"),
    ("recovery.html", "Recovering after birth", "Pemulihan selepas bersalin", "🌷", "t-recover"),
    ("feelings.html", "How are you feeling?", "Kesihatan emosi ibu", "💛", "t-mind"),
    ("after-birth.html", "Documents & savings", "Dokumen & simpanan", "📄", "t-docs"),
    ("aqiqah.html", "Aqiqah & cukur jambul", "Aqiqah & cukur jambul", "🐐", "t-aqiqah"),
    ("vaccines.html", "Vaccination dates", "Jadual imunisasi", "💉", "t-vax"),
    ("jaundice.html", "Jaundice & G6PD", "Kuning (jaundis) & G6PD", "🟡", "t-jaun"),
    ("breastmilk.html", "Breastfeeding guide", "Panduan penyusuan", "🤱", "t-milk"),
    ("newborn.html", "Newborn essentials", "Barang bayi baru lahir", "🧺", "t-kit"),
    ("leave.html", "Maternity leave", "Cuti bersalin", "🗓️", "t-leave"),
    ("#kids", "Mum & kids", "Ibu & anak", "🧒", ""),
    ("growth.html", "Baby's growth", "Tumbesaran bayi", "📈", "t-growth"),
    ("baby-health.html", "Baby health: when to see the klinik", "Kesihatan bayi: bila ke klinik", "🩺", "t-bhealth"),
    ("solids.html", "Baby's first foods", "Pengenalan makanan pejal", "🥣", "t-solids"),
    ("baby-log.html", "Baby's daily log", "Rekod harian bayi", "📝", "t-log"),
    ("safety.html", "Child safety", "Keselamatan kanak-kanak", "🛡️", "t-safety"),
    ("prices.html", "Prices: milk, diapers & essentials", "Harga barang keperluan", "🍼", "t-prices"),
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
    "essentials": ("🧴", "Mum & home essentials", "Barang keperluan ibu & rumah"),
    "pantang": ("🍲", "Pantang cooking basics", "Bahan masakan pantang"),
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
                "diaper": "Diapers", "food": "Baby food", "essentials": "Mum & home essentials (laundry, bath, dishes)",
                "pantang": "Pantang cooking basics (ginger, chicken, fish, eggs, rice)"},
        "sortUnit": "Cheapest per unit", "sortTypical": "Cheapest typical price", "sortFrom": "Cheapest 'from' price", "sortAz": "Name A-Z", "sortShops": "Most shops",
        "cProduct": "Product", "cTypical": "Typical", "cFrom": "From", "cUnit": "Per unit",
        "cShops": "Shops", "per100": "/100 g", "perPiece": "/diaper (M)",
        "tape": "tape", "pants": "pants", "where": "Cheapest shops", "hide": "Hide",
        "chooseState": "Choose your state above to see the cheapest shops.",
        "noShops": "No shop prices for this area yet.",
        "updated": "Prices collected {a} to {b} from {n} shops across Malaysia.",
        "allMy": "All Malaysia", "allDist": "All districts",
        "cmpBtn": "Compare states", "cmpTitle": "Usual price in each state, cheapest first", "cmpRank": "{s} is number {r} cheapest of {n} states.",
        "cmpMy": "All Malaysia: {p}", "cmpShops": "{n} shops", "cmpCheapest": "Cheapest: {s}, {d} less than {me}.", "cmpPick": "Pick your state above to see where it ranks.",
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
        "nmFav": "Save to favourites", "nmNone": "No names match.", "nmUni": "Boy or girl", "nmCount": "{n} names",
        "fWindow": "Most fertile days", "fWindowSmall": "best chance of pregnancy", "fOv": "Likely ovulation", "fNext": "Next period",
        "fDue": "If you conceive this cycle, due around {d}",
        "kickIdle": "Tap each time you feel a movement.", "kickRunning": "{m} min since your first tap", "kickDone": "10 movements in {m} min",
        "conStart": "Start contraction", "conStop": "Stop", "conLasts": "lasts", "conApart": "apart",
        "conAvg": "Last few: about {gap} apart, lasting {len}.", "conHint": "Tap Start when a contraction begins and Stop when it ends.",
        "nuOneMore": "Add one more taska or tadika to compare.", "nuYear": "first year", "nuMonth": "/month",
        "nuNotReg": "Not ticked as registered - ask to see the JKM / KPM certificate",
        "nuOption": "Option {n}", "nuCheapest": "Lowest first-year cost", "nuFree": "Free",
        "promoEnded": "(This promotion may have ended - check the current price.)", "moreInfo": "More info",
        "bfNote": "Breast milk is the best food for babies - the Ministry of Health and WHO recommend only breast milk for the first 6 months. If you use formula, ask your doctor or nurse which type suits your baby. We don't sell or advertise infant formula.",
        "online": "Check online prices (Google Shopping)",
        "noMatch": "No products match \"{q}\" here.", "clearSearch": "Show all products", "noMatchFeed": "Bottles, teats and breast pumps (e.g. Philips Avent, Pigeon, Medela, Spectra) aren't in the government price survey, so we can't show shop prices for them.",
        "preTypical": "Typical packages (anywhere in Malaysia)", "preCentres": "Confinement centres - {state}", "qFrom": "from",
        "preCentreNote": "Published price for {d} days: {price}. Checked {date}. Prices change - confirm with the centre.",
        "preSource": "Centre's website", "preTypicalNote": "Typical price - change it to match your quote.",
        "preCentreNoteNoDays": "Published price: {price} (stay length not stated). Checked {date}. Prices change - confirm with the centre.", "qAdded": "Added ✓",
        "dRegBy": "Register the birth by", "dLeft": "{n} days left · free", "dLastDay": "Today is the last day · free",
        "dLatePen": "Now a late registration - go to your nearest JPN office soon (RM50 fee in Peninsular Malaysia).",
        "dLateSS": "Past 14 days - go to JPN as soon as you can. After 42 days it becomes a late registration with extra steps.",
        "dMyKad": "Apply for MyKad", "dMyKadSmall": "compulsory at age 12",
        "dEpf": "EPF account", "dEpfSmall": "earliest date (age 14)", "dEpfFrom": "Your child can open one from {d}.",
        "gvEstimate": "Estimated bill for mum", "gvFee": "Delivery fee", "gvWard": "Ward ({n} days)", "gvCare": "Treatment ({n} days)",
        "gvRoom": "Delivery room (1st class)", "gvTheatre": "Operating theatre (1st class)", "gvFree": "Free",
        "toDark": "Switch to dark mode", "toLight": "Switch to light mode",
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
                "diaper": "Lampin pakai buang", "food": "Makanan bayi", "essentials": "Barang keperluan ibu & rumah (dobi, mandi, pinggan)",
                "pantang": "Bahan masakan pantang (halia, ayam, ikan, telur, beras)"},
        "sortUnit": "Seunit paling murah", "sortTypical": "Harga biasa paling murah", "sortFrom": "Harga 'dari' paling murah", "sortAz": "Nama A-Z", "sortShops": "Paling banyak kedai",
        "cProduct": "Produk", "cTypical": "Biasa", "cFrom": "Dari", "cUnit": "Seunit",
        "cShops": "Kedai", "per100": "/100 g", "perPiece": "/helai (M)",
        "tape": "pita", "pants": "seluar", "where": "Kedai termurah", "hide": "Tutup",
        "chooseState": "Pilih negeri anda di atas untuk melihat kedai termurah.",
        "noShops": "Belum ada harga kedai untuk kawasan ini.",
        "updated": "Harga dikumpul {a} hingga {b} dari {n} kedai di seluruh Malaysia.",
        "allMy": "Seluruh Malaysia", "allDist": "Semua daerah",
        "cmpBtn": "Banding negeri", "cmpTitle": "Harga biasa di setiap negeri, paling murah dahulu", "cmpRank": "{s} ke-{r} paling murah daripada {n} negeri.",
        "cmpMy": "Seluruh Malaysia: {p}", "cmpShops": "{n} kedai", "cmpCheapest": "Paling murah: {s}, {d} lebih rendah daripada {me}.", "cmpPick": "Pilih negeri anda di atas untuk melihat kedudukannya.",
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
        "nmFav": "Simpan sebagai kegemaran", "nmNone": "Tiada nama sepadan.", "nmUni": "Lelaki atau perempuan", "nmCount": "{n} nama",
        "fWindow": "Hari paling subur", "fWindowSmall": "peluang hamil paling tinggi", "fOv": "Ovulasi dijangka", "fNext": "Haid seterusnya",
        "fDue": "Jika hamil kitaran ini, jangkaan lahir sekitar {d}",
        "kickIdle": "Tekan setiap kali anda rasa bayi bergerak.", "kickRunning": "{m} minit sejak tekanan pertama", "kickDone": "10 gerakan dalam {m} minit",
        "conStart": "Mula kontraksi", "conStop": "Berhenti", "conLasts": "tempoh", "conApart": "jarak",
        "conAvg": "Beberapa terakhir: jarak lebih kurang {gap}, tempoh {len}.", "conHint": "Tekan Mula apabila kontraksi bermula dan Berhenti apabila tamat.",
        "nuOneMore": "Tambah satu lagi taska atau tadika untuk dibandingkan.", "nuYear": "tahun pertama", "nuMonth": "/bulan",
        "nuNotReg": "Tidak ditanda berdaftar - minta untuk melihat sijil JKM / KPM",
        "nuOption": "Pilihan {n}", "nuCheapest": "Kos tahun pertama paling rendah", "nuFree": "Percuma",
        "promoEnded": "(Promosi ini mungkin sudah tamat - semak harga terkini.)", "moreInfo": "Maklumat lanjut",
        "bfNote": "Susu ibu ialah makanan terbaik untuk bayi - Kementerian Kesihatan dan WHO mengesyorkan susu ibu sahaja untuk 6 bulan pertama. Jika anda menggunakan susu formula, tanya doktor atau jururawat jenis yang sesuai. Kami tidak menjual atau mengiklankan susu formula bayi.",
        "online": "Semak harga dalam talian (Google Shopping)",
        "noMatch": "Tiada produk sepadan dengan \"{q}\" di sini.", "clearSearch": "Tunjuk semua produk", "noMatchFeed": "Botol susu, puting botol dan pam susu (cth. Philips Avent, Pigeon, Medela, Spectra) tiada dalam tinjauan harga kerajaan, jadi kami tidak dapat menunjukkan harga kedai.",
        "preTypical": "Pakej biasa (seluruh Malaysia)", "preCentres": "Pusat berpantang - {state}", "qFrom": "dari",
        "preCentreNote": "Harga yang diterbitkan untuk {d} hari: {price}. Disemak {date}. Harga boleh berubah - sahkan dengan pusat.",
        "preSource": "Laman web pusat", "preTypicalNote": "Harga biasa - ubah supaya sama dengan sebut harga anda.",
        "preCentreNoteNoDays": "Harga yang diterbitkan: {price} (tempoh tidak dinyatakan). Disemak {date}. Harga boleh berubah - sahkan dengan pusat.", "qAdded": "Ditambah ✓",
        "dRegBy": "Daftar kelahiran sebelum", "dLeft": "{n} hari lagi · percuma", "dLastDay": "Hari ini hari terakhir · percuma",
        "dLatePen": "Kini pendaftaran lewat - pergi ke pejabat JPN terdekat segera (bayaran RM50 di Semenanjung).",
        "dLateSS": "Sudah lebih 14 hari - pergi ke JPN secepat mungkin. Selepas 42 hari ia menjadi pendaftaran lewat dengan langkah tambahan.",
        "dMyKad": "Mohon MyKad", "dMyKadSmall": "wajib pada umur 12 tahun",
        "dEpf": "Akaun KWSP", "dEpfSmall": "tarikh paling awal (umur 14)", "dEpfFrom": "Anak anda boleh membukanya mulai {d}.",
        "gvEstimate": "Anggaran bil ibu", "gvFee": "Caj bersalin", "gvWard": "Wad ({n} hari)", "gvCare": "Rawatan ({n} hari)",
        "gvRoom": "Bilik bersalin (kelas 1)", "gvTheatre": "Dewan bedah (kelas 1)", "gvFree": "Percuma",
        "toDark": "Tukar ke mod gelap", "toLight": "Tukar ke mod cerah",
    },
}


JS_STR["en"].update({
    "anteWeeks": "Weeks {a}-{b}", "anteWeek": "Week {a}", "anteBeforeWk": "Before week {b}", "anteBefore": "before {d}",
    "antePost": "About 6 weeks after birth", "anteOpen": "Open", "anteMissed": "Missed it? Tell your klinik at your next visit.",
    "budDeliv": "Giving birth", "budConf": "Confinement", "budDiaper": "Diapers ({n} a day for a year)", "budMilk": "Formula milk (12 months)",
    "budItems": "Baby items", "budCare": "Childcare ({m} months)", "budVax": "Vaccines at klinik kesihatan", "budFree": "Free",
    "budTotal": "First year, about", "budMonth": "about {rm} a month",
    "epdsDone": "Answered {n} of 10 - your result shows when all 10 are answered.",
    "epdsScore": "Your score: {s} out of 30",
    "epdsLow": "Your score is below the level that usually needs follow-up. If you still feel low, or it lasts more than two weeks, talk to your klinik or doctor - and check again in two weeks.",
    "epdsHigh": "Your score suggests you may have depression. Please see your klinik kesihatan or doctor soon and tell them your score. It's common and it can be treated - you're not alone.",
    "epdsUrgent": "You said you've had thoughts of harming yourself. Please get help today: go to the nearest hospital emergency department, call 999, or call Talian HEAL 15555.",
    "epdsPrivate": "This score is not saved anywhere. You can take a screenshot to show your nurse or doctor.",
    "aq7": "7th day", "aq14": "14th day", "aq21": "21st day", "aqLeft": "in {n} days", "aqToday": "today", "aqPassed": "passed",
    "solSix": "6 months old - first foods", "solStarted": "time to start (if your klinik agrees)", "solOne": "1 year old",
    "solOneSmall": "until then: no salt, sugar, juice or honey",
    "grPctW": "Heavier than about {p} in 100 babies of the same age and sex.", "grPctL": "Longer than about {p} in 100 babies of the same age and sex.",
    "grOk": "Within the usual range.", "grLow": "Below the usual range - ask your klinik to check.", "grHigh": "Above the usual range - ask your klinik to check.",
    "grMed": "Middle (median) for this age: {w} kg · {l} cm", "grAge": "{m} months old", "grHist": "Saved measurements", "grDel": "Delete",
    "grWhen": "Date", "grW": "Weight", "grL": "Length",
    "grNeed": "Enter the birth date, the date measured and the weight or length.", "grOld": "This WHO chart covers birth to 2 years. For older children, use the chart in your child's health book.",
})
JS_STR["ms"].update({
    "anteWeeks": "Minggu {a}-{b}", "anteWeek": "Minggu {a}", "anteBeforeWk": "Sebelum minggu {b}", "anteBefore": "sebelum {d}",
    "antePost": "Lebih kurang 6 minggu selepas bersalin", "anteOpen": "Buka", "anteMissed": "Terlepas? Beritahu klinik pada lawatan seterusnya.",
    "budDeliv": "Bersalin", "budConf": "Berpantang", "budDiaper": "Lampin ({n} sehari selama setahun)", "budMilk": "Susu formula (12 bulan)",
    "budItems": "Barang bayi", "budCare": "Taska ({m} bulan)", "budVax": "Vaksin di klinik kesihatan", "budFree": "Percuma",
    "budTotal": "Tahun pertama, lebih kurang", "budMonth": "lebih kurang {rm} sebulan",
    "epdsDone": "Dijawab {n} daripada 10 - keputusan dipaparkan selepas kesemua 10 dijawab.",
    "epdsScore": "Skor anda: {s} daripada 30",
    "epdsLow": "Skor anda di bawah tahap yang biasanya perlu susulan. Jika anda masih berasa sedih, atau ia berlarutan lebih dua minggu, berbincang dengan klinik atau doktor - dan semak semula dalam dua minggu.",
    "epdsHigh": "Skor anda menunjukkan anda mungkin mengalami kemurungan. Sila jumpa klinik kesihatan atau doktor secepat mungkin dan beritahu skor anda. Ia biasa berlaku dan boleh dirawat - anda tidak keseorangan.",
    "epdsUrgent": "Anda menyatakan pernah terfikir untuk mencederakan diri. Sila dapatkan bantuan hari ini: pergi ke jabatan kecemasan hospital terdekat, hubungi 999, atau Talian HEAL 15555.",
    "epdsPrivate": "Skor ini tidak disimpan di mana-mana. Anda boleh mengambil tangkapan skrin untuk ditunjukkan kepada jururawat atau doktor.",
    "aq7": "Hari ke-7", "aq14": "Hari ke-14", "aq21": "Hari ke-21", "aqLeft": "lagi {n} hari", "aqToday": "hari ini", "aqPassed": "sudah lepas",
    "solSix": "Umur 6 bulan - makanan pertama", "solStarted": "masa untuk mula (jika klinik bersetuju)", "solOne": "Umur 1 tahun",
    "solOneSmall": "sebelum itu: tiada garam, gula, jus atau madu",
    "grPctW": "Lebih berat daripada lebih kurang {p} daripada 100 bayi sebaya dan sama jantina.", "grPctL": "Lebih panjang daripada lebih kurang {p} daripada 100 bayi sebaya dan sama jantina.",
    "grOk": "Dalam julat biasa.", "grLow": "Di bawah julat biasa - minta klinik menyemak.", "grHigh": "Di atas julat biasa - minta klinik menyemak.",
    "grMed": "Nilai tengah (median) untuk umur ini: {w} kg · {l} cm", "grAge": "Umur {m} bulan", "grHist": "Ukuran yang disimpan", "grDel": "Padam",
    "grWhen": "Tarikh", "grW": "Berat", "grL": "Panjang",
    "grNeed": "Masukkan tarikh lahir, tarikh diukur dan berat atau panjang.", "grOld": "Carta WHO ini untuk lahir hingga 2 tahun. Untuk kanak-kanak lebih besar, guna carta dalam buku kesihatan anak.",
})


JS_STR["en"].update({
    "log_fl": "Breastfeed - left", "log_fr": "Breastfeed - right", "log_fb": "Bottle feed", "log_wet": "Wet nappy", "log_dirty": "Dirty nappy",
    "log_sleep": "Fell asleep", "log_wake": "Woke up", "logToday": "Today", "logYesterday": "Yesterday", "logFeeds": "Feeds", "logWet": "Wet nappies",
    "logDirty": "Dirty nappies", "logSleep": "Sleep", "logH": "h", "logDel": "Remove", "logEmpty": "Nothing recorded on this day yet.",
    "logSince": "Last feed {t} ago", "logJustNow": "Last feed just now", "logAsleep": "asleep since {t}",
})
JS_STR["ms"].update({
    "log_fl": "Menyusu - kiri", "log_fr": "Menyusu - kanan", "log_fb": "Susu botol", "log_wet": "Lampin basah", "log_dirty": "Lampin kotor",
    "log_sleep": "Mula tidur", "log_wake": "Bangun", "logToday": "Hari ini", "logYesterday": "Semalam", "logFeeds": "Susuan", "logWet": "Lampin basah",
    "logDirty": "Lampin kotor", "logSleep": "Tidur", "logH": "j", "logDel": "Buang", "logEmpty": "Belum ada rekod pada hari ini.",
    "logSince": "Susuan terakhir {t} yang lalu", "logJustNow": "Susuan terakhir baru sahaja", "logAsleep": "tidur sejak {t}",
})

JS_STR["en"].update({
    "wgBmi": "Your BMI before pregnancy", "wgCat_under": "underweight", "wgCat_normal": "normal", "wgCat_over": "overweight", "wgCat_obese": "obese",
    "wgTotal": "Healthy total gain", "wgWholePreg": "over the whole pregnancy", "wgWeekly": "From week 13", "wgPerWeek": "per week",
    "wgSoFar": "So far: {g} kg at week {w}.", "wgExpect": "The usual range by now is about {lo} - {hi} kg.",
    "wgOk": "That's within the usual range.", "wgBelow": "That's a little below - mention it at your next klinik visit.", "wgAbove": "That's a little above - mention it at your next klinik visit.",
})
JS_STR["ms"].update({
    "wgBmi": "BMI anda sebelum hamil", "wgCat_under": "kurang berat badan", "wgCat_normal": "normal", "wgCat_over": "lebih berat badan", "wgCat_obese": "obes",
    "wgTotal": "Jumlah kenaikan sihat", "wgWholePreg": "sepanjang kehamilan", "wgWeekly": "Dari minggu 13", "wgPerWeek": "seminggu",
    "wgSoFar": "Setakat ini: {g} kg pada minggu {w}.", "wgExpect": "Julat biasa pada tahap ini lebih kurang {lo} - {hi} kg.",
    "wgOk": "Itu dalam julat biasa.", "wgBelow": "Itu sedikit rendah - beritahu klinik pada lawatan seterusnya.", "wgAbove": "Itu sedikit tinggi - beritahu klinik pada lawatan seterusnya.",
})

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
               "price", "harga", "murah", "cheap", "cerelac", "kedai", "tuala wanita", "=pad", "panadol", "detergen", "sabun",
               "halia", "ayam", "telur", "ikan haruan", "barang dapur", "barang keperluan", "groceries"],
    "nursery": ["taska", "tadika", "nursery", "kindergarten", "childcare", "child care", "daycare", "day care",
                "prasekolah", "preschool", "tabika", "kemas", "babysit"],
    "breastfeed": ["breastfeed", "breast feed", "breastmilk", "breast milk", "susu ibu", "menyusu", "penyusuan",
                   "lactation", "pam susu", "breast pump", "nipple", "puting"],
    "vaccine": ["vaccin", "vaksin", "imunisasi", "immunis", "immuniz", "=jab", "suntikan", "=bcg", "hepatitis"],
    "birthreg": ["register", "daftar", "birth certificate", "sijil lahir", "sijil kelahiran", "=jpn", "mykid", "dokumen",
                 "document", "passport", "pasport", "=str", "mystr"],
    "savings": ["=asb", "asnb", "amanah saham", "=asm", "=epf", "kwsp", "sspn", "ptptn", "tabung haji", "simpanan anak",
                "savings for baby", "save for baby", "baby savings", "akaun anak", "child account", "account for baby",
                "akaun bayi", "simpan duit", "invest for", "pelaburan anak"],
    "feedback": ["feedback", "cadangan", "suggest", "improve", "tambah baik", "complain", "aduan", "contact", "hubungi",
                 "=bug", "salah", "wrong"],
    "milkstore": ["simpan susu", "susu perah", "susu perahan", "=ebm", "freezer", "peti sejuk", "breast milk storage", "store breast milk",
                  "expressed milk", "tahan berapa lama", "how long breast milk"],
    "names": ["nama bayi", "nama anak", "baby name", "nama lelaki", "nama perempuan", "maksud nama", "name meaning",
              "nama cina", "nama india", "chinese name", "indian name", "tamil name", "nama tamil"],
    "fertile": ["hari subur", "ovulasi", "ovulation", "subur", "nak hamil", "cuba hamil", "trying to conceive", "=ttc", "fertile"],
    "kicks": ["tendangan", "kick count", "kick counter", "kira tendangan", "kontraksi", "contraction", "sakit nak bersalin", "labour pain", "labor"],
    "essentials": ["barang bayi", "barang baby", "newborn essentials", "what to buy", "beli apa", "baby list", "persediaan bayi"],
    "delivery": ["kos bersalin", "harga bersalin", "pakej bersalin", "bil bersalin", "delivery cost", "delivery package",
                 "maternity package", "cost to give birth", "cost of giving birth", "hospital kerajaan", "government hospital",
                 "hospital swasta", "private hospital", "caesarean", "czer", "=fpp", "ppum", "hukm", "hctm", "=kelas"],
    "planning": ["asid folik", "folic", "sebelum hamil", "before pregnancy", "pre-pregnancy", "prakehamilan", "plan pregnancy",
                 "planning pregnancy", "rancang hamil", "ujian hamil", "pregnancy test", "test hamil", "=upt", "=ivf", "=iui",
                 "infertil", "kesuburan", "tak hamil", "susah hamil", "not getting pregnant", "lppkn"],
    "antenatal": ["antenatal", "check-up", "checkup", "pemeriksaan", "buku pink", "pink book", "=ogtt", "glukosa", "kencing manis hamil",
                  "gestational diabetes", "diabetes hamil", "=tdap", "batuk kokol", "whooping", "klinik ibu", "booking"],
    "healthy": ["makan apa", "what to eat", "pantang makan hamil", "boleh makan", "can i eat", "food to avoid", "makanan hamil",
                "puasa", "fasting", "ramadan", "ramadhan", "fidyah", "qada", "terbang", "flight", "=fly", "flying", "kapal terbang", "airasia",
                "malaysia airlines", "kafein", "caffeine", "kopi", "durian", "nanas", "pineapple", "sushi"],
    "budget": ["bajet", "budget", "belanja bayi", "cost of baby", "kos bayi", "kos anak", "how much does a baby cost", "first year", "tahun pertama"],
    "feelings": ["sedih selepas bersalin", "rasa sedih", "kemurungan selepas bersalin", "postnatal depression", "postpartum depression", "sad after", "feel sad", "feeling low", "sedih", "=sad", "murung", "depress", "kemurungan", "baby blues", "stress", "tertekan", "anxious",
                 "cemas", "=epds", "mental", "emosi", "lonely", "sunyi", "tak larat"],
    "aqiqah": ["aqiqah", "akikah", "aqikah", "cukur jambul", "cukur rambut", "kambing", "goat", "zakat rambut"],
    "jaundice": ["kuning", "jaundice", "jaundis", "=g6pd", "bilirubin", "phototherapy", "fototerapi", "jemur", "ubat gegat", "mothball"],
    "growth": ["berat bayi", "baby weight", "tinggi bayi", "panjang bayi", "growth", "tumbesaran", "percentile", "persentil", "milestone",
               "perkembangan", "merangkak", "crawl", "first steps", "mula berjalan", "mula bercakap", "first words", "tidur bayi", "baby sleep", "how much sleep"],
    "solids": ["makanan pejal", "solid food", "solids", "first food", "makanan pertama", "=mpasi", "bubur bayi", "baby porridge", "puree",
               "madu", "honey"],
    "feedgear": ["avent", "philips avent", "pigeon", "tommee", "medela", "spectra", "botol susu", "baby bottle", "feeding bottle",
                 "steriliser", "sterilizer", "steril", "puting botol", "teat"],
    "babylog": ["rekod susuan", "rekod bayi", "log bayi", "baby log", "baby tracker", "feeding log", "track feeds", "kira lampin", "berapa kali menyusu",
                "nappy count", "diaper count", "sleep log", "jejak tidur"],
    "symptoms": ["alahan", "morning sickness", "loya", "muntah", "pedih ulu hati", "heartburn", "sakit belakang", "back pain", "kejang kaki",
                 "leg cramp", "sembelit", "constipation", "bengkak kaki", "swollen feet", "keputihan", "discharge", "tompok darah", "spotting",
                 "kerap kencing", "hb rendah", "kurang darah", "anemia", "anaemia", "berat badan hamil", "weight gain", "naik berat", "normal ke"],
    "recovery": ["darah nifas", "nifas", "lochia", "jahitan", "stitches", "luka caesar", "luka bedah", "pelvic floor", "senaman kegel", "kegel",
                 "perancang keluarga", "contraception", "family planning", "bila boleh bersama", "selepas bersalin pemeriksaan", "postnatal check"],
    "babyhealth": ["demam bayi", "bayi demam", "baby fever", "suhu bayi", "kolik", "colic", "menangis tak berhenti", "crying a lot", "najis pucat",
                   "pale poo", "ruam lampin", "nappy rash", "diaper rash", "tumbuh gigi", "teething", "muntah hijau", "goncang bayi", "shaken baby"],
    "safety": ["car seat", "kerusi keselamatan", "kerusi kereta", "=crs", "tercekik", "choking", "keselamatan rumah", "baby proof", "babyproof",
               "tinggal dalam kereta", "left in car", "bateri butang", "button battery"],
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
    "breastfeed": ("breastmilk.html", "Breast milk is the best food for babies - the Ministry of Health recommends only breast milk for the first 6 months. For latching or supply worries, ask your clinic's or hospital's lactation nurse.",
                   "Susu ibu ialah makanan terbaik untuk bayi - Kementerian Kesihatan mengesyorkan susu ibu sahaja untuk 6 bulan pertama. Jika ada masalah penyusuan, tanya jururawat laktasi di klinik atau hospital.",
                   "Open the breastfeeding guide", "Buka panduan penyusuan"),
    "vaccine": ("vaccines.html", "Babies usually get their first vaccines (BCG and Hepatitis B) at birth. After that, follow the schedule in your baby's health book at your klinik kesihatan.",
                "Bayi biasanya menerima vaksin pertama (BCG dan Hepatitis B) semasa lahir. Selepas itu, ikut jadual dalam buku kesihatan bayi di klinik kesihatan.",
                "See your baby's vaccine dates", "Lihat tarikh vaksin bayi"),
    "birthreg": ("after-birth.html", "Register the birth with JPN - within 60 days in Peninsular Malaysia, 14 days in Sabah and Sarawak. Bring both parents' MyKad, your marriage certificate and the hospital's birth confirmation form.",
                 "Daftar kelahiran di JPN - dalam tempoh 60 hari di Semenanjung, 14 hari di Sabah dan Sarawak. Bawa MyKad kedua-dua ibu bapa, sijil nikah dan borang pengesahan kelahiran daripada hospital.",
                 "Open the after-birth checklist", "Buka senarai semak selepas bersalin"),
    "savings": ("after-birth.html#savings", "Bumiputera babies can have an ASB account from birth (RM10 to start), and ASM, SSPN and Tabung Haji also take babies. An EPF account can only be opened from age 14.",
                "Bayi Bumiputera boleh ada akaun ASB dari lahir (RM10 untuk mula), dan ASM, SSPN serta Tabung Haji juga menerima bayi. Akaun KWSP hanya boleh dibuka dari umur 14 tahun.",
                "See savings for your baby", "Lihat simpanan untuk bayi"),
    "feedback": ("feedback.html", "Thank you! Tell us what to fix or add - it takes a minute.",
                 "Terima kasih! Beritahu kami apa yang perlu dibaiki atau ditambah - hanya seminit.",
                 "Suggest an improvement", "Hantar cadangan"),
    "milkstore": ("breastmilk.html", "KKM says expressed milk keeps 4 hours at room temperature, 8 hours in an air-conditioned room, 3-5 days in the fridge and 6 months in a deep freezer.",
                  "KKM: susu perahan tahan 4 jam pada suhu bilik, 8 jam dalam bilik berhawa dingin, 3-5 hari dalam peti sejuk dan 6 bulan dalam peti sejuk beku.",
                  "Breast milk storage guide", "Panduan simpan susu ibu"),
    "names": ("names.html", "Browse Malay, Chinese and Indian baby names with their meanings, and save your favourites.",
              "Lihat nama bayi Melayu, Cina dan India beserta maksud, dan simpan pilihan kegemaran anda.", "Browse baby names", "Lihat nama bayi"),
    "fertile": ("fertility.html", "Ovulation is usually about 14 days before your next period. The calculator shows your likely fertile days.",
                "Ovulasi biasanya lebih kurang 14 hari sebelum haid seterusnya. Kalkulator menunjukkan hari subur anda.", "Find your fertile days", "Cari hari subur anda"),
    "kicks": ("labour.html", "Count your baby's kicks or time your contractions. If movements slow down, or contractions come regularly and get stronger, call your hospital.",
              "Kira tendangan bayi atau masa kontraksi. Jika gerakan berkurang, atau kontraksi datang secara tetap dan semakin kuat, hubungi hospital.",
              "Open kick counter & contraction timer", "Buka pengira tendangan & kontraksi"),
    "essentials": ("newborn.html", "Our newborn checklist covers sleeping, feeding, bathing, diapers, clothes and going out.",
                   "Senarai semak bayi baru lahir merangkumi tidur, menyusu, mandi, lampin, pakaian dan keluar rumah.",
                   "Open newborn checklist", "Buka senarai barang bayi"),
    "delivery": ("delivery-cost.html", "In a government hospital a normal delivery in a 3rd-class ward costs Malaysians about RM16 for 2 days. Private hospital packages are about RM2,300-5,500 for a normal delivery and RM5,700-12,000 for a caesarean.",
                 "Di hospital kerajaan, bersalin normal di wad kelas 3 berharga lebih kurang RM16 untuk 2 hari bagi warganegara. Pakej hospital swasta lebih kurang RM2,300-5,500 untuk bersalin normal dan RM5,700-12,000 untuk caesarean.",
                 "Compare delivery costs", "Banding kos bersalin"),
    "planning": ("planning.html", "Planning a baby? KKM advises starting folic acid 3 months before pregnancy and a pre-pregnancy check at your klinik kesihatan. Most home pregnancy tests work from the day your period is due.",
                 "Merancang untuk hamil? KKM menasihatkan mula mengambil asid folik 3 bulan sebelum hamil dan pemeriksaan prakehamilan di klinik kesihatan. Kebanyakan ujian kehamilan di rumah boleh dibuat mulai hari haid dijangka.",
                 "Open the planning checklist", "Buka senarai persediaan"),
    "antenatal": ("antenatal.html", "Register at your klinik kesihatan before 12 weeks. You'll have a glucose test (OGTT) at 24-28 weeks and a free Tdap vaccine at 28-32 weeks. Enter your due date to see your own dates.",
                  "Daftar di klinik kesihatan sebelum 12 minggu. Anda akan menjalani ujian glukosa (OGTT) pada 24-28 minggu dan menerima vaksin Tdap percuma pada 28-32 minggu. Masukkan tarikh jangkaan untuk melihat tarikh anda.",
                  "See your check-up dates", "Lihat tarikh pemeriksaan anda"),
    "healthy": ("healthy-pregnancy.html", "Eat a variety, drink plain water, and avoid raw or undercooked food, unpasteurised milk and too much caffeine. We also cover fasting in Ramadan and airline rules for flying while pregnant.",
                "Makan pelbagai, minum air kosong, dan elakkan makanan mentah atau separa masak, susu tidak dipasteur dan kafein berlebihan. Kami juga menerangkan puasa Ramadan dan peraturan syarikat penerbangan untuk ibu hamil.",
                "Food, fasting & flying", "Makanan, puasa & terbang"),
    "budget": ("budget.html", "Add up delivery, confinement, diapers, milk, baby items and childcare for baby's first year - every number can be changed.",
               "Kira kos bersalin, berpantang, lampin, susu, barang bayi dan taska untuk tahun pertama bayi - setiap angka boleh diubah.",
               "Open the budget calculator", "Buka kalkulator anggaran belanja"),
    "feelings": ("feelings.html", "Feeling low after having a baby is common, and it can be treated. Try our private 10-question check, and talk to your klinik. If you're thinking of harming yourself, call 999 or Talian HEAL 15555 now.",
                 "Berasa sedih selepas bersalin adalah biasa, dan boleh dirawat. Cuba semakan peribadi 10 soalan kami, dan berbincang dengan klinik. Jika terfikir untuk mencederakan diri, hubungi 999 atau Talian HEAL 15555 sekarang.",
                 "Open the feelings check", "Buka semakan emosi"),
    "aqiqah": ("aqiqah.html", "Aqiqah and cukur jambul are sunnah on the 7th day (or the 14th or 21st). Enter baby's birth date to see the dates.",
               "Aqiqah dan cukur jambul sunat pada hari ketujuh (atau ke-14 atau ke-21). Masukkan tarikh lahir bayi untuk melihat tarikhnya.",
               "See aqiqah dates", "Lihat tarikh aqiqah"),
    "jaundice": ("jaundice.html", "Yellow skin in the first 24 hours, a baby who is very yellow, drowsy or not feeding well, or pale stools need a klinik straight away. Don't 'sun' your baby - KKM says it can harm them.",
                 "Kulit kuning dalam 24 jam pertama, bayi sangat kuning, lemah atau tidak mahu menyusu, atau najis pucat perlu ke klinik segera. Jangan 'jemur' bayi - KKM menyatakan ia boleh membahayakan.",
                 "Jaundice & G6PD guide", "Panduan kuning & G6PD"),
    "growth": ("growth.html", "Check your baby's weight and length on the WHO chart (0-2 years), see milestones by month and how much sleep babies need.",
               "Semak berat dan panjang bayi pada carta WHO (0-2 tahun), perkembangan mengikut bulan dan berapa banyak tidur yang bayi perlukan.",
               "Open baby's growth", "Buka tumbesaran bayi"),
    "solids": ("solids.html", "KKM: start other food at 6 months and keep breastfeeding to 2 years. No salt, sugar, juice or honey before 1 year.",
               "KKM: mula beri makanan lain pada 6 bulan dan teruskan menyusu hingga 2 tahun. Tiada garam, gula, jus atau madu sebelum 1 tahun.",
               "Baby's first foods", "Pengenalan makanan pejal"),
    "feedgear": ("breastmilk.html#pump", "Philips Avent is a baby-feeding brand - bottles, teats, breast pumps and sterilisers (Pigeon, Medela and Spectra are others). KKM recommends only breast milk for the first 6 months; if you express milk or use bottles, wash and sterilise every part before use.",
                 "Philips Avent ialah jenama barang penyusuan bayi - botol, puting botol, pam susu dan pensteril (Pigeon, Medela dan Spectra juga). KKM mengesyorkan susu ibu sahaja untuk 6 bulan pertama; jika anda memerah susu atau menggunakan botol, cuci dan steril setiap bahagian sebelum digunakan.",
                 "Pumping & bottles guide", "Panduan pam & botol"),
    "babylog": ("baby-log.html", "Tap to log each feed (left, right or bottle), wet and dirty nappies, and sleep - you'll see the day's totals. It's saved only on your phone.",
                "Tekan untuk merekod setiap susuan (kiri, kanan atau botol), lampin basah dan kotor, serta tidur - anda akan nampak jumlah sehari. Disimpan dalam telefon anda sahaja.",
                "Open the baby log", "Buka rekod harian bayi"),
    "symptoms": ("pregnancy-body.html", "Most pregnancy aches are normal - our guide has self-care tips for 13 common symptoms and the signs that mean you should see your klinik. It also shows your healthy weight-gain range and what low HB means.",
                 "Kebanyakan ketidakselesaan semasa hamil adalah normal - panduan kami ada tip penjagaan diri untuk 13 simptom biasa dan tanda yang perlu ke klinik. Ia juga menunjukkan julat kenaikan berat sihat dan maksud HB rendah.",
                 "Is this normal?", "Normalkah ini?"),
    "recovery": ("recovery.html", "Bleeding after birth usually stops by 6-8 weeks. KKM: you can get pregnant again before your first period, so get family-planning advice within a month. Heavy bleeding, fever, calf pain or chest pain: go to hospital.",
                 "Darah nifas biasanya berhenti dalam 6-8 minggu. KKM: anda boleh hamil semula sebelum haid pertama, jadi dapatkan nasihat perancang keluarga dalam sebulan. Pendarahan banyak, demam, sakit betis atau sakit dada: pergi ke hospital.",
                 "Recovering after birth", "Pemulihan selepas bersalin"),
    "babyhealth": ("baby-health.html", "A baby under 3 months with a temperature of 38°C or more needs a klinik or hospital now. Our guide covers fever, colic, pale poo, nappy rash and teething - and never shake a baby.",
                   "Bayi bawah 3 bulan dengan suhu 38°C atau lebih perlu ke klinik atau hospital sekarang. Panduan kami merangkumi demam, kolik, najis pucat, ruam lampin dan tumbuh gigi - dan jangan sekali-kali menggoncang bayi.",
                   "When to see the klinik", "Bila perlu ke klinik"),
    "safety": ("safety.html", "Since 2020, children under 12, under 36 kg and under 136 cm must use a car seat (JPJ). Never leave a child alone in a car. Our page also covers home safety and choking first aid.",
               "Sejak 2020, kanak-kanak bawah 12 tahun, kurang 36 kg dan kurang 136 cm wajib menggunakan kerusi keselamatan (JPJ). Jangan tinggalkan anak seorang diri dalam kereta. Halaman kami juga merangkumi keselamatan rumah dan pertolongan cemas tercekik.",
               "Child safety", "Keselamatan kanak-kanak"),
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

GLOBE_ICON = ('<svg class="globe" viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>')
THEME_ICONS = ('<svg class="ic-moon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/></svg>'
               '<svg class="ic-sun" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')

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


def tabbar(x, group, items, hash_ok=False, prompt=""):
    """Big tappable tabs; only the chosen panel shows (less scrolling). Each item:
    (key, icon, label_en, label_ms, big_html, small_en, small_ms, count). count=True -> JS shows ticked/total
    for the checkboxes in that panel. app.js tabGroups() remembers the choice per group (tm_tab_<group>)."""
    btns = []
    for i, (k, ico, le, lm, big, se, sm, count) in enumerate(items):
        btns.append(
            f'<button type="button" class="dtab" role="tab" id="tb-{group}-{k}" aria-controls="tp-{group}-{k}" '
            f'aria-selected="{"true" if i == 0 else "false"}" data-tab="{k}"{" data-count" if count else ""}>'
            f'<span class="dt-lbl"><span aria-hidden="true">{ico}</span> {esc(x(le, lm))}</span>'
            + (f'<span class="dt-big">{big}</span>' if big else "")
            + (f'<span class="dt-small">{esc(x(se, sm))}</span>' if se else "") + "</button>")
    q = f'<p class="dtabs-q">{prompt}</p>' if prompt else ""
    return (f'{q}<div class="dtabs n{len(items)}" role="tablist" data-group="{group}"{" data-hash" if hash_ok else ""} '
            f'aria-label="{esc(prompt or x("Sections", "Bahagian"))}">{"".join(btns)}</div>')


def tabpanel(group, key, html):
    return (f'<div class="dpanel" role="tabpanel" id="tp-{group}-{key}" aria-labelledby="tb-{group}-{key}" '
            f'data-group="{group}" data-tab="{key}">{html}</div>')


def pcard(x, kind, ico, name, loc, meta, price_html, body, state="", extra_cls="", sort=None):
    """Listing card like a directory: name, place, 'from' price; tap opens the details underneath."""
    sk = "".join(f' data-s-{k}="{esc(v)}"' for k, v in (sort or {}).items())
    return (f'<details class="pcard{(" " + extra_cls) if extra_cls else ""}" data-state="{esc(state)}"{sk}><summary>'
            f'<span class="pc-band" aria-hidden="true">{ico}</span>'
            f'<span class="pc-kind">{esc(kind)}</span><strong class="pc-name">{esc(name)}</strong>'
            f'<span class="pc-loc">📍 {esc(loc)}</span>'
            f'<span class="pc-foot"><span class="pc-meta">{meta}</span><span class="pc-price">{price_html}</span></span>'
            f'<span class="pc-more"><span class="pc-open">{x("View details", "Lihat butiran")}</span><span class="pc-close">{x("Hide details", "Tutup butiran")}</span></span>'
            f'</summary><div class="pc-body">{body}</div></details>')


def sort_select(x, target, options):
    """A 'Sort by' drop-down that reorders the cards inside #target by their data-s-<key>.
    options: [(value 'key:asc|desc', English, Malay)]; the first one is the default."""
    opts = "".join(f'<option value="{v}">{esc(x(en, ms))}</option>' for v, en, ms in options)
    return (f'<label class="sort-row card-sort"><span>⇅ {x("Sort by", "Susun ikut")}</span>'
            f'<select data-sort-for="{target}">{opts}</select></label>')


def state_chips(x, target, states):
    return (f'<div class="nm-origin state-chips" role="group" data-for="{target}" aria-label="{x("State", "Negeri")}">'
            f'<button type="button" class="chip-btn" data-state="" aria-pressed="true">{x("All states", "Semua negeri")}</button>'
            + "".join(f'<button type="button" class="chip-btn" data-state="{esc(s)}" aria-pressed="false">{esc(s)}</button>' for s in states)
            + "</div>")


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
    # Sections (Before pregnancy, Pregnant, ...) are collapsible: only their titles show until tapped;
    # the section holding the current page starts open.
    current = x("Menu", "Menu")
    top, sections = [], []

    def add(html, act):
        if sections:
            sections[-1][2].append(html)
            sections[-1][3] = sections[-1][3] or act
        else:
            top.append(html)
    for href, en, ms, ico, cls in NAV:
        if href.startswith("#"):
            sections.append([ico, x(en, ms), [], False])
            continue
        active = href == path or (href == "weeks/index.html" and path.startswith("weeks/"))
        label = x(en, ms) if href != "prices.html" else x("Prices", "Harga barang keperluan")
        if active and href != "index.html":
            current = label
        cur = ' aria-current="page"' if active else ""
        if href == "prices.html":  # "Prices" opens its own list of product groups + a search box
            subs = "".join(
                f'<li><a href="{lroot}prices.html#grp-{g}"><span class="mi-ico" aria-hidden="true">{GROUPS[g][0]}</span>'
                f'{esc(x(GROUPS[g][1], GROUPS[g][2]))}</a></li>' for g in PRICE_GROUPS)
            add(f"""<li><details class="menu-sub"{" open" if active else ""}>
  <summary class="mi {cls}"{cur}><span class="mi-ico" aria-hidden="true">{ico}</span>{esc(label)}<span class="chev" aria-hidden="true"></span></summary>
  <ul>
    <li><a href="{lroot}prices.html"><span class="mi-ico" aria-hidden="true">📋</span>{x("All prices", "Semua harga")}</a></li>{subs}
    <li><form class="search-row" action="{lroot}prices.html" method="get" role="search">
      <input type="search" name="q" placeholder="{x("Search, e.g. Drypers", "Cari, cth. Drypers")}" aria-label="{x("Search products", "Cari produk")}">
      <button type="submit" class="btn">{x("Search", "Cari")}</button></form></li>
  </ul></details></li>""", active)
            continue
        add(f'<li><a class="mi {cls}" href="{lroot}{href}"{cur}><span class="mi-ico" aria-hidden="true">{ico}</span>{esc(label)}</a></li>', active)
    items = top + [
        f'<li class="menu-sec"><details class="menu-grp" name="menu-grp"{" open" if act else ""}>'
        f'<summary class="menu-group"><span aria-hidden="true">{gico}</span> {esc(title)}<span class="chev" aria-hidden="true"></span></summary>'
        f'<ul>{"".join(its)}</ul></details></li>' for gico, title, its, act in sections]
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
<script>try{{var t=JSON.parse(localStorage.getItem("tm_theme"));if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<link rel="stylesheet" href="{root}assets/style.css?v={VER}">
{seo}{ads}
</head>
<body>
<a class="skip" href="#main">{x("Skip to content", "Langkau ke kandungan")}</a>
<header class="top">
  <div class="wrap top-row">
    {menu}
    <a class="brand" href="{lroot}index.html"><span class="logo" aria-hidden="true">🤰</span><span>{esc(site)}</span></a>
    <button type="button" class="theme-btn" id="theme-btn" aria-label="{x("Switch light or dark mode", "Tukar mod cerah atau gelap")}">{THEME_ICONS}</button>
    <a class="lang" href="{root}{other}/{path}" hreflang="{other}" lang="{other}" title="{"Tukar ke Bahasa Melayu" if other == "ms" else "Switch to English"}">{GLOBE_ICON}<span>{"BM" if other == "ms" else "EN"}</span></a>
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
    data = [[n, g, (mm if lang == "ms" else me), o] for n, g, me, mm, o in extra.NAMES]
    body = f"""
{page_head(x, "✨", "t-names", x("Pregnant", "Sedang hamil"), x("Baby names", "Nama bayi"),
           x("Names from Malaysia's many communities - Malay, Chinese, Indian, Punjabi, Sabah and Sarawak peoples, Orang Asli, Siamese and Kristang - plus English, Japanese and Korean, with their meanings.", "Nama daripada pelbagai kaum di Malaysia - Melayu, Cina, India, Punjabi, kaum Sabah dan Sarawak, Orang Asli, Siam dan Kristang - serta Inggeris, Jepun dan Korea, beserta maksudnya."), extra=tip(x("Meanings are common interpretations - many names have more than one. For Chinese, Japanese and Korean names the meaning depends on the characters you choose. Punjabi, Iban, Kadazan-Dusun, English, Japanese and Korean meanings were checked in name references and dictionaries (Behind the Name; Richards' Iban-English Dictionary; Borneo Dictionary; SIL dictionaries on Webonary; the Austronesian Basic Vocabulary Database). Most Sabah, Sarawak and Orang Asli names are words with lovely meanings in that language - the language is shown after each meaning. Check with family, a trusted source or your religious teacher before deciding.",
                                                                                                                        "Maksud ialah tafsiran biasa - banyak nama mempunyai lebih daripada satu maksud. Untuk nama Cina, Jepun dan Korea, maksudnya bergantung pada aksara yang dipilih. Maksud nama Punjabi, Iban, Kadazan-Dusun, Inggeris, Jepun dan Korea disemak dalam rujukan nama dan kamus (Behind the Name; Kamus Iban-Inggeris Richards; Borneo Dictionary; kamus SIL di Webonary; Pangkalan Data Kosa Kata Asas Austronesia). Kebanyakan nama Sabah, Sarawak dan Orang Asli ialah perkataan yang bermaksud indah dalam bahasa itu - bahasanya ditunjukkan selepas setiap maksud. Semak dengan keluarga, sumber dipercayai atau guru agama anda sebelum memutuskan."), x))}
<section class="card" id="names-tool">
  <div class="search-row"><input type="search" id="nm-q" placeholder="{x("Search a name or meaning, e.g. light", "Cari nama atau maksud, cth. cahaya")}" aria-label="{x("Search names", "Cari nama")}"></div>
  <div class="chips nm-origin" role="group" aria-label="{x("Origin", "Asal")}">
    <button type="button" class="chip-btn" data-o="all" aria-pressed="true">{x("All", "Semua")}</button>
    <button type="button" class="chip-btn" data-o="malay" aria-pressed="false">🌙 {x("Malay & Islamic", "Melayu & Islam")}</button>
    <button type="button" class="chip-btn" data-o="chinese" aria-pressed="false">🏮 {x("Chinese", "Cina")}</button>
    <button type="button" class="chip-btn" data-o="indian" aria-pressed="false">🪔 {x("Indian", "India")}</button>
    <button type="button" class="chip-btn" data-o="punjabi" aria-pressed="false">☬ {x("Punjabi & Sikh", "Punjabi & Sikh")}</button>
    <button type="button" class="chip-btn" data-o="borneo" aria-pressed="false">🦜 {x("Sabah & Sarawak", "Sabah & Sarawak")}</button>
    <button type="button" class="chip-btn" data-o="orangasli" aria-pressed="false">🌿 {x("Orang Asli", "Orang Asli")}</button>
    <button type="button" class="chip-btn" data-o="siam" aria-pressed="false">🐘 {x("Siamese", "Siam")}</button>
    <button type="button" class="chip-btn" data-o="kristang" aria-pressed="false">⛵ {x("Kristang (Portuguese-Eurasian)", "Kristang (Serani)")}</button>
    <button type="button" class="chip-btn" data-o="english" aria-pressed="false">📖 {x("English & biblical", "Inggeris & Alkitab")}</button>
    <button type="button" class="chip-btn" data-o="japanese" aria-pressed="false">🌸 {x("Japanese", "Jepun")}</button>
    <button type="button" class="chip-btn" data-o="korean" aria-pressed="false">🎎 {x("Korean", "Korea")}</button>
  </div>
  <div class="seg nm-seg">
    <button type="button" data-f="all" aria-pressed="true">{x("All", "Semua")}</button>
    <button type="button" data-f="m" aria-pressed="false">{x("Boys", "Lelaki")}</button>
    <button type="button" data-f="f" aria-pressed="false">{x("Girls", "Perempuan")}</button>
    <button type="button" data-f="fav" aria-pressed="false">♥ {x("Saved", "Disimpan")}</button>
  </div>
  <div class="az-bar" id="nm-az" role="group" aria-label="{x("First letter", "Huruf pertama")}">
    <button type="button" data-l="all" aria-pressed="true">{x("A-Z", "A-Z")}</button>{"".join(f'<button type="button" data-l="{l}" aria-pressed="false">{l}</button>' for l in sorted({n[0][0].upper() for n in extra.NAMES}))}
  </div>
  <p class="hint" id="nm-count" aria-live="polite"></p>
  <ul class="nm-list" id="nm-list"></ul>
</section>
{ad("bottom", x)}
"""
    write_page(lang, "names.html", x("Baby names with meanings from every Malaysian community", "Nama bayi beserta maksud daripada pelbagai kaum di Malaysia"),
               x("Browse Malay, Islamic, Chinese, Indian (Tamil, Telugu, Malayalam), Punjabi, Iban, Kadazan-Dusun, Bidayuh, Melanau, Kenyah, Kelabit, Bajau, Murut, Rungus, Orang Asli, Siamese, Kristang, English, Japanese and Korean baby names with their meanings, and save your favourites.",
                 "Senarai nama bayi lelaki dan perempuan Melayu, Islam, Cina, India (Tamil, Telugu, Malayalam), Punjabi, Iban, Kadazan-Dusun, Bidayuh, Melanau, Kenyah, Kelabit, Bajau, Murut, Rungus, Orang Asli, Siam, Kristang, Inggeris, Jepun dan Korea beserta maksud - simpan nama kegemaran anda."), body, {"names": data})


def p_labour(lang):
    x = tr(lang)
    body = f"""
{page_head(x, "⏱️", "t-labour", x("Third trimester", "Trimester ketiga"), x("Kick counter & contraction timer", "Pengira tendangan & masa kontraksi"),
           x("Simple tools for the last weeks. Saved only on this phone.", "Alat mudah untuk minggu-minggu terakhir. Disimpan dalam telefon ini sahaja."))}
{tabbar(x, "lb", [("kick", "👣", "Kick counter", "Pengira tendangan", x("Count 10 moves", "Kira 10 gerakan"), "from about 28 weeks", "dari lebih kurang 28 minggu", False),
                    ("con", "⏱️", "Contractions", "Kontraksi", x("How far apart?", "Berapa jarak?"), "time each one", "kira setiap satu", False)],
                prompt=x("Which tool?", "Alat yang mana?"))}
<div class="lb-grid">
<div class="dpanel" role="tabpanel" id="tp-lb-kick" aria-labelledby="tb-lb-kick" data-group="lb" data-tab="kick">
<section class="card" id="kick-tool">
  <h2><span aria-hidden="true">👣</span> {x("Kick counter", "Pengira tendangan")} {tip(x("From about 28 weeks, get to know your baby's usual pattern. Pick a time when baby is usually active and count movements. If movements slow down or change, go to your clinic or hospital the same day - don't wait.",
                                                                                     "Dari lebih kurang 28 minggu, kenali corak biasa bayi. Pilih waktu bayi biasanya aktif dan kira gerakan. Jika gerakan berkurang atau berubah, pergi ke klinik atau hospital pada hari yang sama - jangan tunggu."), x)}</h2>
  <button type="button" class="kick-btn" id="kick-btn"><span id="kick-count">0</span><small>{x("tap for each movement", "tekan setiap gerakan")}</small></button>
  <p class="hint center" id="kick-time"></p>
  <p class="center"><button type="button" class="link-btn muted" id="kick-reset">{x("Start again", "Mula semula")}</button></p>
</section>
</div>
<div class="dpanel" role="tabpanel" id="tp-lb-con" aria-labelledby="tb-lb-con" data-group="lb" data-tab="con">
<section class="card" id="con-tool">
  <h2><span aria-hidden="true">⏱️</span> {x("Contraction timer", "Pemasa kontraksi")} {tip(x("Time from the start of one contraction to the start of the next. Contractions that come regularly, get stronger and closer together may mean labour is starting - call your hospital for advice. Go straight away if your waters break, you bleed, or baby moves less.",
                                                                                        "Kira dari permulaan satu kontraksi ke permulaan kontraksi seterusnya. Kontraksi yang datang secara tetap, semakin kuat dan rapat mungkin tanda bersalin bermula - hubungi hospital untuk nasihat. Pergi segera jika air ketuban pecah, berdarah, atau bayi kurang bergerak."), x)}</h2>
  <button type="button" class="btn con-btn" id="con-btn">{x("Start contraction", "Mula kontraksi")}</button>
  <p class="hint" id="con-sum"></p>
  <ol class="con-log" id="con-log"></ol>
  <p><button type="button" class="link-btn muted" id="con-reset">{x("Clear", "Padam")}</button></p>
</section>
</div>
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
    tabs = tabbar(x, "bf", [
        ("start", "🤱", "Getting started", "Mula menyusu", x("Latch & enough milk", "Pelekapan & susu cukup"), "", "", False),
        ("problems", "🩹", "Common problems", "Masalah biasa", x("Sore nipples, mastitis", "Puting luka, mastitis"), "", "", False),
        ("pump", "🍼", "Pumping & bottles", "Pam & botol", x("Expressing, sterilising", "Memerah, mensteril"), "", "", False),
        ("work", "💼", "Back to work", "Kembali bekerja", x("Keep breastfeeding", "Teruskan menyusu"), "", "", False),
        ("store", "🧊", "Storing milk", "Simpan susu", x("How long it keeps", "Berapa lama tahan"), "", "", False),
    ], hash_ok=True, prompt=x("What do you need help with?", "Apa yang anda perlukan bantuan?"))
    body = f"""
{page_head(x, "🤱", "t-milk", x("New mum", "Ibu baharu"), x("Breastfeeding guide", "Panduan penyusuan susu ibu"),
           x("From the first feeds to going back to work - from KKM's guidance.", "Dari susuan pertama hingga kembali bekerja - berdasarkan panduan KKM."))}
{tabs}
{tabpanel("bf", "start", f'''<section class="card"><h2>{x("Breast milk is all your baby needs", "Susu ibu sudah mencukupi untuk bayi")}</h2>
<p>{x("KKM strongly recommends only breast milk for the first 6 months - your baby doesn't need water, other drinks or food. Keep breastfeeding after 6 months alongside other food, up to 2 years.", "KKM sangat mengesyorkan susu ibu sahaja untuk 6 bulan pertama - bayi tidak memerlukan air, minuman lain atau makanan. Teruskan menyusu selepas 6 bulan bersama makanan lain, sehingga 2 tahun.")}</p></section>
<section class="card"><h2>{x("How often", "Berapa kerap")}</h2><ul>
<li>{x("Feed whenever your baby shows hunger cues - no limits on how often or how long, including at night.", "Susukan bila-bila bayi menunjukkan tanda lapar - tiada had kekerapan atau tempoh, termasuk waktu malam.")}</li>
<li>{x("In the first weeks that's usually at least 8 times in 24 hours. Feeding often keeps your milk supply up.", "Pada minggu-minggu awal biasanya sekurang-kurangnya 8 kali dalam 24 jam. Menyusu dengan kerap mengekalkan bekalan susu.")}</li>
<li>{x("Crying is a late sign of hunger - look for earlier cues like rooting and sucking on hands.", "Menangis ialah tanda lapar yang lewat - perhatikan tanda awal seperti mencari puting dan menghisap tangan.")}</li></ul></section>
<section class="card"><h2>{x("A good latch", "Pelekapan yang betul")}</h2><ul>
<li>{x("Baby's mouth is wide open, chin touching your breast, cheeks rounded.", "Mulut bayi terbuka luas, dagu menyentuh payudara, pipi membulat.")}</li>
<li>{x("You can see more of the dark skin around your nipple above baby's top lip than below the bottom lip.", "Lebih banyak kulit gelap sekeliling puting kelihatan di atas bibir atas bayi berbanding di bawah bibir bawah.")}</li>
<li>{x("You can hear swallowing, and it doesn't hurt after the first few sucks.", "Anda boleh dengar bayi menelan, dan tidak sakit selepas beberapa hisapan pertama.")}</li></ul></section>
<section class="card"><h2>{x("Is my baby getting enough?", "Adakah bayi mendapat susu yang cukup?")}</h2><ul>
<li>{x("6 to 8 wet nappies a day, with clear (not dark) urine.", "6 hingga 8 lampin basah sehari, dengan air kencing yang jernih (tidak pekat).")}</li>
<li>{x("Several soft yellow poos a day in the early weeks.", "Beberapa kali najis kuning yang lembut sehari pada minggu-minggu awal.")}</li>
<li>{x("Baby is alert, shows hunger at times and seems satisfied after feeds.", "Bayi cergas, menunjukkan lapar sekali-sekala dan nampak puas selepas menyusu.")}</li>
<li>{x("Losing a little weight in the first 3-4 days is normal. KKM: if baby has lost 5-10% of birth weight by day 5-6, see the klinik doctor; more than 10%, go to hospital.", "Turun sedikit berat badan dalam 3-4 hari pertama adalah normal. KKM: jika bayi turun 5-10% berat lahir pada hari ke-5 hingga 6, jumpa doktor klinik; lebih 10%, pergi ke hospital.")}</li></ul>
<a class="btn ghost" href="baby-log.html">📝 {x("Count feeds & nappies", "Kira susuan & lampin")} →</a></section>''')}
{tabpanel("bf", "problems", f'''<section class="card"><h2>{x("Sore or cracked nipples", "Puting sakit atau merekah")}</h2>
<p>{x("Usually caused by the baby not being positioned or attached well. If every feed hurts, or your nipples crack or bleed, get help from your klinik nurse soon.", "Biasanya kerana kedudukan atau pelekapan bayi kurang betul. Jika setiap kali menyusu terasa sakit, atau puting merekah atau berdarah, dapatkan bantuan jururawat klinik segera.")}</p></section>
<section class="card"><h2>{x("Engorgement (overfull breasts)", "Payudara bengkak (terlalu penuh)")}</h2>
<p>{x("Feed often, express just enough to feel comfortable, and use cold and warm compresses.", "Susukan dengan kerap, perah sekadar untuk rasa selesa, dan gunakan tuaman sejuk dan suam.")}</p></section>
<section class="card"><h2>{x("Mastitis", "Mastitis (radang payudara)")}</h2>
<p>{x("A breast that's hot, red and tender, and feeling like you have the flu. Keep the milk flowing - if feeding is too painful, express that side. See a doctor if you feel worse, or aren't better within 12-24 hours. If an abscess forms, keep feeding from the other breast.", "Payudara panas, merah dan sakit, serta rasa seperti demam selsema. Pastikan susu terus keluar - jika menyusu terlalu sakit, perah susu di sebelah itu. Jumpa doktor jika semakin teruk, atau tidak pulih dalam 12-24 jam. Jika ada abses, teruskan menyusu dari payudara sebelah lagi.")}</p></section>''')}
{tabpanel("bf", "pump", f'''<section class="card"><h2>{x("Expressing by hand", "Memerah dengan tangan")}</h2><ol>
<li>{x("Get comfortable somewhere warm and quiet.", "Duduk dengan selesa di tempat yang hangat dan tenang.")}</li>
<li>{x("Cup your breast in a C-shape with your thumb and finger, 2-3 cm back from the nipple.", "Pegang payudara dalam bentuk C dengan ibu jari dan jari, 2-3 cm dari puting.")}</li>
<li>{x("Gently press together, release, and repeat in a rhythm. Then do the other breast.", "Tekan perlahan, lepaskan, dan ulang secara berirama. Kemudian buat pada payudara sebelah lagi.")}</li></ol></section>
<section class="card"><h2>{x("Breast pumps", "Pam susu")}</h2>
<p>{x("Manual pumps are cheaper, lighter and quieter; electric pumps do the work for you and are quicker. Common brands in Malaysia include Philips Avent, Medela, Spectra and Pigeon.", "Pam manual lebih murah, ringan dan senyap; pam elektrik lebih mudah dan cepat. Jenama biasa di Malaysia termasuk Philips Avent, Medela, Spectra dan Pigeon.")}</p></section>
<section class="card"><h2>{x("Cleaning & sterilising", "Mencuci & mensteril")}</h2><ul>
<li>{x("Wash pump parts, bottles and teats in hot soapy water as soon as possible after use.", "Basuh bahagian pam, botol dan puting botol dengan air sabun panas secepat mungkin selepas digunakan.")}</li>
<li>{x("Then sterilise: boil them for at least 10 minutes, fully under the water - or use a sterilising solution (at least 30 minutes) or a steam steriliser, following its instructions.", "Kemudian steril: rebus sekurang-kurangnya 10 minit, tenggelam sepenuhnya dalam air - atau guna larutan pensteril (sekurang-kurangnya 30 minit) atau pensteril wap, ikut arahannya.")}</li></ul></section>''')}
{tabpanel("bf", "work", f'''<section class="card"><ul>
<li>{x("Start expressing and storing milk a few weeks before you go back, so there's a supply ready.", "Mula memerah dan menyimpan susu beberapa minggu sebelum kembali bekerja, supaya ada bekalan.")}</li>
<li>{x("Malaysia's Employment Act has no rule on breastfeeding breaks - talk to your employer early about time and a clean, private place to express.", "Akta Kerja Malaysia tiada peruntukan rehat menyusu - bincang awal dengan majikan tentang masa dan tempat yang bersih dan tertutup untuk memerah.")}</li>
<li>{x("Ask your klinik for advice before you return - KKM's klinik kesihatan counsel mums on going back to work.", "Minta nasihat klinik sebelum kembali bekerja - klinik kesihatan KKM memberi kaunseling kepada ibu yang akan kembali bekerja.")}</li></ul>
<a class="btn ghost" href="leave.html">🗓️ {x("Maternity leave dates", "Tarikh cuti bersalin")} →</a></section>''')}
{tabpanel("bf", "store", f'''<p class="dp-intro">{x("How long expressed milk keeps, from KKM's nutrition division poster for working mothers.", "Berapa lama susu perahan tahan, daripada poster Bahagian Pemakanan KKM untuk ibu bekerja.")}
{tip(x("Ask your klinik if your baby is premature or unwell - times can be shorter.", "Tanya klinik jika bayi pramatang atau kurang sihat - tempohnya mungkin lebih singkat."), x)}</p>
<ul class="milk-list">{rows}</ul>
<section class="card" id="milk-tool">
  <h2><span aria-hidden="true">🏷️</span> {x("Label calculator", "Kalkulator label")}</h2>
  <div class="q-fields fert-fields">
    <label class="field">{x("Expressed at", "Diperah pada")}<input type="datetime-local" id="milk-when"></label>
    <label class="field">{x("Stored in", "Disimpan di")}<select id="milk-where">{opts}</select></label>
  </div>
  <div id="milk-result" aria-live="polite"></div>
</section>
<details class="acc"><summary>{x("Good habits", "Amalan baik")}</summary><ul>
<li>{x("Store milk in a clean, closed container or bag and label it with the date and time.", "Simpan susu dalam bekas atau beg yang bersih dan bertutup, dan labelkan dengan tarikh dan masa.")}</li>
<li>{x("Use the oldest milk first.", "Guna susu yang paling lama dahulu.")}</li>
<li>{x("Thaw frozen milk in the chiller overnight. Once thawed, don't freeze it again.", "Cairkan susu beku dalam bahagian dingin semalaman. Susu yang sudah cair tidak boleh dibekukan semula.")}</li>
<li>{x("Warm it in a bowl of warm water - never in a microwave - and test it on your wrist.", "Panaskan dalam mangkuk air suam - jangan guna ketuhar gelombang mikro - dan uji pada pergelangan tangan.")}</li>
</ul></details>''')}
{ad("in_content", x)}
{src_line(x, [(x("KKM Perinatal Care Manual", "Manual Penjagaan Perinatal KKM"), t2.PCM),
              (x("KKM breastfeeding poster (working mums)", "Poster penyusuan KKM (ibu bekerja)"), "https://hq.moh.gov.my/nutrition/wp-content/uploads/2023/12/Poster-Penyusuan-Susu-Ibu-Ibu-Bekerja-1-1.pdf"),
              ("NHS: breastfeeding", "https://www.nhs.uk/baby/breastfeeding-and-bottle-feeding/breastfeeding/"), ("NHS: sterilising", "https://www.nhs.uk/baby/breastfeeding-and-bottle-feeding/bottle-feeding/sterilising-baby-bottles/")])}
"""
    write_page(lang, "breastmilk.html", x("Breastfeeding guide: latch, supply, pumping & storage (KKM)", "Panduan penyusuan susu ibu: pelekapan, bekalan, memerah & simpanan (KKM)"),
               x("Breastfeeding help for Malaysian mums: how often to feed, a good latch, signs of enough milk, sore nipples and mastitis, pumping and sterilising, going back to work, and KKM's milk storage times.",
                 "Bantuan penyusuan untuk ibu di Malaysia: kekerapan menyusu, pelekapan yang betul, tanda susu cukup, puting luka dan mastitis, memerah dan mensteril, kembali bekerja, dan tempoh simpanan susu KKM."),
               body)


def p_newborn(lang):
    x = tr(lang)
    secs = []
    for te, tm, items in extra.ESSENTIALS:
        lis = "".join(
            f'<li><label class="check"><input type="checkbox" data-key="nb_{k}"> {esc(x(en, ms))}</label>'
            f'{shop(aff, en, x) if aff else ""}</li>' for k, en, ms, aff in items)
        secs.append(f'<section class="card"><h2>{esc(x(te, tm))}</h2><ul class="checklist">{lis}</ul></section>')
    icons = ["🛏️", "🍼", "🛁", "🧷", "👕", "🚗"]
    nb_tabs = tabbar(x, "nb", [(f"s{i}", icons[i % len(icons)], te, tm, f"0 / {len(items)}", "", "", True) for i, (te, tm, items) in enumerate(extra.ESSENTIALS)],
                     prompt=x("Pick a category:", "Pilih kategori:"))
    nb_panels = "".join(tabpanel("nb", f"s{i}", sec) for i, sec in enumerate(secs))
    body = f"""
<div data-store="tm_newborn"></div>
{page_head(x, "🧺", "t-kit", x("New mum", "Ibu baharu"), x("Newborn essentials", "Barang bayi baru lahir"), extra=tip(x("A starting list - you won't need everything at once. 'Shop' links open Shopee; some are affiliate links, so we may earn a small commission at no extra cost to you.",
                                                                                                                    "Senarai permulaan - anda tidak perlukan semuanya sekali gus. Pautan 'Beli' membuka Shopee; sesetengahnya pautan afiliasi, jadi kami mungkin mendapat komisen kecil tanpa kos tambahan kepada anda."), x))}
<div class="bag-progress card"><div class="bp-top"><strong id="bag-progress" aria-live="polite"></strong><button type="button" class="link-btn muted" id="bag-reset">{x("Untick everything", "Buang semua tanda")}</button></div>
<div class="progress"><span id="bag-bar" style="width:0%"></span></div></div>
{nb_tabs}
{nb_panels}
{ad("in_content", x)}
"""
    write_page(lang, "newborn.html", x("Newborn baby checklist Malaysia", "Senarai barang bayi baru lahir"),
               x("What to buy before your baby arrives: sleeping, feeding, bathing, diapers, clothes and car seat - a free checklist saved on your phone.",
                 "Apa perlu dibeli sebelum bayi lahir: tidur, menyusu, mandi, lampin, pakaian dan kerusi kereta - senarai semak percuma."), body)


def p_afterbirth(lang):
    x = tr(lang)
    secs = []
    for te, tm, ico, items in extra.AFTER_BIRTH:
        lis = "".join(
            f'<li><label class="check"><input type="checkbox" data-key="ab_{k}"> {esc(x(en, ms))}</label>'
            f'{tip(x(te_, tm_), x) if te_ else ""}</li>' for k, en, ms, te_, tm_ in items)
        secs.append(f'<section class="card"><h2><span aria-hidden="true">{ico}</span> {esc(x(te, tm))}</h2><ul class="checklist">{lis}</ul></section>')
    cards = []
    SAVE_START = {"th": 2, "asb": 10, "asm": 10, "sspn": 20, "epf": 999}  # RM to open; EPF only from age 14, so last
    for k, ico, ne, nm, we, wm, se, sm, be, bm, he, hm, url in extra.SAVINGS:
        epf = k == "epf"
        cards.append(
            f'<article class="save-card{" save-later" if epf else ""}" id="sv-{k}" data-s-start="{SAVE_START[k]}" data-s-name="{esc(x(ne, nm).lower())}"><div class="sv-top"><span class="sv-ico" aria-hidden="true">{ico}</span>'
            f'<div><h3>{esc(x(ne, nm))}</h3><span class="sv-who">{esc(x(we, wm))}</span></div></div>'
            f'<dl><dt>{x("Start", "Mula")}</dt><dd>{esc(x(se, sm))}</dd>'
            f'<dt>{x("Bring", "Bawa")}</dt><dd>{esc(x(be, bm))}</dd>'
            f'<dt>{x("Where", "Di mana")}</dt><dd>{esc(x(he, hm))}</dd></dl>'
            + (f'<p class="sv-date" id="sv-epf-date" hidden></p>' if epf else "")
            + f'<a class="sv-link" href="{esc(url)}" target="_blank" rel="noopener">{x("Official site", "Laman rasmi")} ↗</a></article>')
    body = f"""
<div data-store="tm_docs" data-progress="{x("{n} of {t} done", "{n} daripada {t} selesai")}" data-done="{x("All done - well done!", "Semua selesai - syabas!")}"></div>
{page_head(x, "📄", "t-docs", x("New mum", "Ibu baharu"), x("Documents &amp; savings after birth", "Dokumen &amp; simpanan selepas bersalin"),
           x("Register the birth on time, sort out baby's papers, and see which savings accounts your baby can have.",
             "Daftar kelahiran tepat pada masanya, uruskan dokumen bayi, dan lihat akaun simpanan yang boleh dibuka untuk bayi."),
           extra=tip(x("Checked on the official JPN, ASNB, PTPTN, Tabung Haji and EPF websites in November 2026. Rules and fees can change - check with the office before you go.",
                       "Disemak di laman rasmi JPN, ASNB, PTPTN, Tabung Haji dan KWSP pada November 2026. Peraturan dan bayaran boleh berubah - semak dengan pejabat berkenaan sebelum pergi."), x))}
<section class="card" id="docs-tool">
  <p class="field-label">{x("Where was baby born?", "Di mana bayi dilahirkan?")}</p>
  <div class="pill-group" role="group" aria-label="{x("Where was baby born?", "Di mana bayi dilahirkan?")}">
    <button type="button" class="pill-opt" data-r="pen" aria-pressed="true">{x("Peninsular", "Semenanjung")} <small>60 {x("days", "hari")}</small></button>
    <button type="button" class="pill-opt" data-r="sbh" aria-pressed="false">Sabah <small>14 {x("days", "hari")}</small></button>
    <button type="button" class="pill-opt" data-r="swk" aria-pressed="false">Sarawak <small>14 {x("days", "hari")}</small></button>
  </div>
  <div class="due-row"><label class="field grow">{x("Baby's birth date", "Tarikh lahir bayi")}<input type="date" id="docs-birth"></label></div>
  <div id="docs-result" aria-live="polite"></div>
  <p class="hint">{x("Registering within the time limit is free. Some hospitals have a JPN counter - ask before you go home.",
                     "Pendaftaran dalam tempoh yang ditetapkan adalah percuma. Sesetengah hospital ada kaunter JPN - tanya sebelum pulang.")}</p>
</section>
{tabbar(x, "ab", [("docs", "📝", "Documents", "Dokumen", "0 / " + str(sum(len(it) for _, _, _, it in extra.AFTER_BIRTH)), "birth cert, MyKid, STR...", "sijil lahir, MyKid, STR...", True),
                    ("savings", "🐷", "Savings for baby", "Simpanan bayi", x(f"{len(extra.SAVINGS)} accounts", f"{len(extra.SAVINGS)} akaun"), "ASB, SSPN, Tabung Haji, EPF", "ASB, SSPN, Tabung Haji, KWSP", False)],
                hash_ok=True, prompt=x("What do you want to sort out?", "Apa yang anda mahu uruskan?"))}
<div class="dpanel" role="tabpanel" id="tp-ab-docs" aria-labelledby="tb-ab-docs" data-group="ab" data-tab="docs">
<div class="bag-progress card"><div class="bp-top"><strong id="bag-progress" aria-live="polite"></strong><button type="button" class="link-btn muted" id="bag-reset">{x("Untick everything", "Buang semua tanda")}</button></div>
<div class="progress"><span id="bag-bar" style="width:0%"></span></div></div>
<div class="check-grid">{"".join(secs)}</div>
</div>
<div class="dpanel" role="tabpanel" id="tp-ab-savings" aria-labelledby="tb-ab-savings" data-group="ab" data-tab="savings">
<section id="savings">
<h2 class="sv-head sv-first"><span aria-hidden="true">🐷</span> {x("Start saving for baby", "Mula menyimpan untuk bayi")}</h2>
<p class="muted">{x("Once you have the birth certificate, you can open these for your baby. They're all optional - pick what suits your family.",
                    "Selepas mendapat sijil kelahiran, anda boleh membuka akaun ini untuk bayi. Semuanya pilihan - pilih yang sesuai untuk keluarga anda.")}</p>
{sort_select(x, "save-list", [("start:asc", "Cheapest to open", "Paling murah untuk dibuka"), ("name:asc", "Name A-Z", "Nama A-Z")])}
<div class="save-grid" id="save-list">{"".join(cards)}</div>
<p class="small muted">{x("General information only, not financial advice. Limits, fees and returns change, and past dividends don't promise future ones - check with ASNB, PTPTN, Tabung Haji or EPF before you open an account.",
                          "Maklumat umum sahaja, bukan nasihat kewangan. Had, bayaran dan pulangan boleh berubah, dan dividen lalu tidak menjamin dividen akan datang - semak dengan ASNB, PTPTN, Tabung Haji atau KWSP sebelum membuka akaun.")}</p>
</section>
</div>
{ad("in_content", x)}
<p><a class="btn ghost" href="vaccines.html">{x("Baby's vaccine dates →", "Tarikh vaksin bayi →")}</a> <a class="btn ghost" href="leave.html">{x("Maternity leave →", "Cuti bersalin →")}</a></p>
"""
    write_page(lang, "after-birth.html", x("Documents after birth & savings for baby (Malaysia)", "Dokumen selepas bersalin & simpanan bayi (Malaysia)"),
               x("What to do after your baby is born in Malaysia: register the birth with JPN (60 days, or 14 in Sabah and Sarawak), MyKid, STR, and opening ASB, SSPN or Tabung Haji for your baby.",
                 "Perkara selepas bayi lahir di Malaysia: daftar kelahiran di JPN (60 hari, atau 14 hari di Sabah dan Sarawak), MyKid, STR, dan membuka ASB, SSPN atau Tabung Haji untuk bayi."),
               body)


def _rm(n):
    return f"RM{n:,}"


def _dmy(iso_date, lang):
    d = datetime.date.fromisoformat(iso_date)
    months = (["Jan", "Feb", "Mac", "Apr", "Mei", "Jun", "Jul", "Ogo", "Sep", "Okt", "Nov", "Dis"] if lang == "ms"
              else ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    return f"{d.day} {months[d.month - 1]} {d.year}"


def p_delivery(lang):
    x = tr(lang)
    with open(os.path.join(HERE, "site-data", "delivery.json"), encoding="utf-8") as f:
        D = json.load(f)
    gov, fpp, priv = D["gov"], D["fpp"], sorted(D["private"], key=lambda h: (h["price_from_rm"], h["name"]))
    today_iso = TODAY.isoformat()
    lo_n, hi_n = min(h["price_from_rm"] for h in priv), max(h["price_from_rm"] for h in priv)
    cs = [h["csec_rm"] for h in priv if h.get("csec_rm")]
    gov_min = gov["delivery"]["normal"]["c3"] + 2 * gov["ward_per_day"]["c3"][0]
    hctm = next(u for u in D["university"] if u.get("fees"))
    uni_min = hctm["fees"]["normal"] + 2 * (hctm["fees"]["ward_per_day"] + hctm["fees"]["care_per_day"])

    def opt(group, v, en, ms, small_en="", small_ms="", on=False):
        sm = f' <small>{esc(x(small_en, small_ms))}</small>' if small_en else ""
        return f'<button type="button" class="pill-opt" data-g="{group}" data-v="{v}" aria-pressed="{"true" if on else "false"}">{esc(x(en, ms))}{sm}</button>'

    cls_opts = "".join([opt("cls", "c3", "Class 3", "Kelas 3", "open ward", "wad terbuka", True), opt("cls", "c2", "Class 2", "Kelas 2"),
                        opt("cls", "c1_3", "Class 1", "Kelas 1", "3+ beds", "3+ katil"), opt("cls", "c1_2", "Class 1", "Kelas 1", "2 beds", "2 katil"),
                        opt("cls", "c1_1", "Class 1", "Kelas 1", "single", "seorang")])
    type_opts = "".join([opt("type", "normal", "Normal", "Normal", on=True), opt("type", "assisted", "Vacuum / forceps / breech", "Vakum / forsep / songsang"),
                         opt("type", "twins", "Twins", "Kembar"), opt("type", "csec", "Caesarean", "Caesarean")])

    states = sorted({h["state"] for h in priv})
    cards = []
    for h in priv:
        ended = h.get("valid_until") and today_iso > h["valid_until"]
        frm = x("from ", "dari ")
        normal = (frm if h.get("from") else "") + _rm(h["price_from_rm"])
        csec = ((frm if h.get("csec_from") else "") + _rm(h["csec_rm"])) if h.get("csec_rm") else x("ask the hospital", "tanya hospital")
        stay = x(h.get("stay_en", ""), h.get("stay_ms", ""))
        valid = (f' · {x("offer ends", "tawaran tamat")} {_dmy(h["valid_until"], lang)}' if h.get("valid_until") and not ended else "")
        body_ = (f'<div class="pc-rows"><div>{x("Normal delivery", "Bersalin normal")}<strong>{normal}</strong></div>'
                 f'<div>{x("Caesarean", "Caesarean")}<strong>{csec}</strong></div></div>'
                 + (f'<p><strong>{esc(stay)}</strong></p>' if stay else "")
                 + f'<p>{esc(x(h["note_en"], h["note_ms"]))}</p>'
                 + (f'<p class="hosp-ended">{x("This offer may have ended - check the current price.", "Tawaran ini mungkin sudah tamat - semak harga terkini.")}</p>' if ended else "")
                 + f'<p class="pc-actions"><a class="btn" href="{esc(h["source_url"])}" target="_blank" rel="noopener">{x("Hospital page", "Laman hospital")} ↗</a>'
                   f'<span class="small muted">{x("checked", "disemak")} {_dmy(h["checked"], lang)}{valid}</span></p>')
        price = (f'{x("Normal", "Normal")} {normal}' + (f'<small>{x("Caesarean", "Caesarean")} {csec}</small>' if h.get("csec_rm") else ""))
        hsort = {"normal": h["price_from_rm"], "csec": h.get("csec_rm") or 999999, "name": h["name"].lower(), "state": h["state"].lower()}
        cards.append(pcard(x, x("Private hospital", "Hospital swasta"), "🏥", h["name"], h["state"], esc(stay.split(" · ")[0]) if stay else "",
                           price, body_, state=h["state"], sort=hsort))

    hasa = next(u for u in D["university"] if u.get("exec_normal_rm"))
    f_ = hctm["fees"]
    hasa_body = (f'<div class="pc-rows"><div>{x("Normal - standard ward", "Normal - wad biasa")}<strong>{_rm(hasa["standard_normal_rm"])}</strong></div>'
                 f'<div>{x("Normal - Executive", "Normal - Executive")}<strong>{_rm(hasa["exec_normal_rm"])}</strong></div>'
                 f'<div>{x("Caesarean - Executive", "Caesarean - Executive")}<strong>{_rm(hasa["exec_csec_rm"])}</strong></div></div>'
                 f'<p>{esc(x(hasa["standard_note_en"], hasa["standard_note_ms"]))}</p><p>{esc(x(hasa["exec_note_en"], hasa["exec_note_ms"]))}</p>'
                 f'<p class="pc-actions"><a class="btn" href="{esc(hasa["source_url"])}" target="_blank" rel="noopener">{x("Standard price", "Harga biasa")} ↗</a>'
                 f'<a class="btn ghost" href="{esc(hasa["exec_url"])}" target="_blank" rel="noopener">HASA Executive ↗</a>'
                 f'<span class="small muted">{x("checked", "disemak")} {_dmy(hasa["checked"], lang)}</span></p>')
    hctm_body = (f'<div class="pc-rows"><div>{x("Normal delivery fee", "Caj bersalin normal")}<strong>{_rm(f_["normal"])}</strong></div>'
                 f'<div>{x("Forceps / vacuum", "Forsep / vakum")}<strong>{_rm(f_["forceps"])} / {_rm(f_["vacuum"])}</strong></div>'
                 f'<div>{x("Caesarean fee", "Caj caesarean")}<strong>{_rm(f_["csec"])}</strong></div>'
                 f'<div>{x("Normal, 2 days (mum)", "Normal, 2 hari (ibu)")}<strong>~{_rm(uni_min)}</strong></div></div>'
                 f'<p>{esc(x(hctm["note_en"], hctm["note_ms"]))}</p>'
                 f'<p class="pc-actions"><a class="btn" href="{esc(hctm["source_url"])}" target="_blank" rel="noopener">{x("Charge book (PDF, p. 37-38)", "Buku Caj (PDF, ms 37-38)")} ↗</a>'
                 f'<span class="small muted">{x("checked", "disemak")} {_dmy(hctm["checked"], lang)}</span></p>')
    uni_cards = (pcard(x, x("University hospital", "Hospital universiti"), "🎓", hasa["name"], hasa["state"], x("standard ward", "wad biasa"),
                       f'{x("from", "dari")} {_rm(hasa["standard_normal_rm"])}<small>Executive {_rm(hasa["exec_normal_rm"])}</small>', hasa_body)
                 + pcard(x, x("University hospital", "Hospital universiti"), "🎓", hctm["name"], hctm["state"], x("public ward, 2 days", "wad awam, 2 hari"),
                         f'~{_rm(uni_min)}<small>{x("caesarean fee", "caj caesarean")} {_rm(f_["csec"])}</small>', hctm_body))
    ask = "".join(f'<li><a href="{esc(u["url"])}" target="_blank" rel="noopener">{esc(u["name"])}</a> <span class="muted">· {esc(u["state"])}</span></li>' for u in D["university_ask"])
    pask = D.get("private_ask", [])
    priv_ask_html = ""
    if pask:
        pstates = sorted({u["state"] for u in pask})
        lis = "".join(f'<li data-state="{esc(u["state"])}"><a href="{esc(u["url"])}" target="_blank" rel="noopener">{esc(u["name"])}</a> <span class="muted">· {esc(u["state"])}</span></li>' for u in pask)
        priv_ask_html = (f'<details class="acc" id="priv-ask"><summary>{x(f"{len(pask)} more hospitals with no package price online - call them", f"{len(pask)} lagi hospital tanpa harga pakej dalam talian - hubungi mereka")}</summary>'
                         f'<p class="small muted">{x("Some only offer a discount on the final bill.", "Sesetengahnya hanya menawarkan diskaun pada bil akhir.")}</p><ul>{lis}</ul></details>')

    chips_html = state_chips(x, "hosp-list", states).replace('data-for="hosp-list"', 'data-for="hosp-list" data-ask="priv-ask"')
    deliv_tabs = tabbar(x, "deliv", [
        ("gov", "🏛️", "Government", "Kerajaan", f'{x("from", "dari")} {_rm(gov_min)}', "normal, class 3 ward, 2 days", "normal, wad kelas 3, 2 hari", False),
        ("uni", "🎓", "University", "Universiti", f'{_rm(uni_min)} – {_rm(hasa["exec_normal_rm"])}', "normal: public ward to private wing", "normal: wad biasa hingga wad swasta", False),
        ("private", "🏥", "Private", "Swasta", f'{_rm(lo_n)} – {_rm(hi_n)}', f"normal packages · {len(priv)} hospitals", f"pakej normal · {len(priv)} hospital", False),
    ], hash_ok=True, prompt=x("Where do you plan to give birth? Tap one:", "Di mana anda merancang untuk bersalin? Pilih satu:"))
    body = f"""
{page_head(x, "🏥", "t-deliv", x("Pregnant", "Sedang hamil"), x("Delivery cost", "Kos bersalin"),
           x("What giving birth costs in government, university and private hospitals - from their own price lists.",
             "Kos bersalin di hospital kerajaan, universiti dan swasta - daripada senarai harga mereka sendiri."),
           extra=tip(x("Prices for Malaysian citizens, checked on each hospital's or the Ministry of Health's own website. Prices change and packages have conditions - always confirm with the hospital.",
                       "Harga untuk warganegara Malaysia, disemak di laman web hospital atau Kementerian Kesihatan sendiri. Harga boleh berubah dan pakej ada syarat - sentiasa sahkan dengan hospital."), x))}
{deliv_tabs}

<div class="dpanel" role="tabpanel" id="tp-deliv-gov" aria-labelledby="tb-deliv-gov" data-group="deliv" data-tab="gov">
<section class="card" id="gov-tool">
  <h2><span aria-hidden="true">🏛️</span> {x("Government hospital bill estimate", "Anggaran bil hospital kerajaan")}</h2>
  <p class="field-label">{x("Ward class", "Kelas wad")}</p>
  <div class="pill-group">{cls_opts}</div>
  <p class="field-label">{x("Delivery", "Cara bersalin")}</p>
  <div class="pill-group">{type_opts}</div>
  <div class="gv-row">
    <label class="field">{x("Days in ward", "Hari di wad")}<input type="number" id="gv-days" min="1" max="14" value="2" inputmode="numeric"></label>
    <label class="check gv-ac"><input type="checkbox" id="gv-ac" checked> {x("Air-conditioned ward", "Wad berhawa dingin")}</label>
  </div>
  <div id="gv-result" aria-live="polite"></div>
  <p class="hint">{x("Ministry of Health rates for Malaysians (updated", "Kadar Kementerian Kesihatan untuk warganegara (dikemas kini")} {_dmy(gov["updated"], lang)}). {x("Lab tests, scans, some medicines and your baby's own charges are extra. Civil servants and government pensioners: ask the hospital about your entitlement.",
     "Ujian makmal, imbasan, sesetengah ubat dan caj bayi adalah tambahan. Penjawat awam dan pesara kerajaan: tanya hospital tentang kelayakan anda.")}
     <a href="{esc(gov["source_url"])}" target="_blank" rel="noopener">{x("Delivery rates", "Kadar bersalin")} ↗</a> · <a href="{esc(gov["ward_url"])}" target="_blank" rel="noopener">{x("Ward rates", "Kadar wad")} ↗</a></p>
</section>

<aside class="box note fpp-box"><h2>{x("Want your own specialist in a government hospital?", "Mahu pakar pilihan sendiri di hospital kerajaan?")}</h2>
<p>{x("Some government hospitals run a Full Paying Patient (FPP) service: you choose the specialist and pay private-style fees at lower prices. Example - "+fpp["name"]+":",
      "Sesetengah hospital kerajaan ada Perkhidmatan Pesakit Bayar Penuh (FPP): anda pilih pakar dan bayar yuran gaya swasta pada harga lebih rendah. Contoh - "+fpp["name"]+":")}</p>
<ul class="fpp-list"><li>{x("Normal", "Normal")} <strong>{_rm(fpp["normal"][0])} – {_rm(fpp["normal"][1])}</strong></li>
<li>{x("Vacuum / forceps", "Vakum / forsep")} <strong>{_rm(fpp["assisted"][0])} – {_rm(fpp["assisted"][1])}</strong></li>
<li>{x("Caesarean", "Caesarean")} <strong>{_rm(fpp["csec"][0])} – {_rm(fpp["csec"][1])}</strong></li></ul>
<p class="small">{x("Estimates from the hospital's FPP brochure; bed RM160-180 and care RM100 a day.", "Anggaran daripada brosur FPP hospital; katil RM160-180 dan rawatan RM100 sehari.")} <a href="{esc(fpp["source_url"])}" target="_blank" rel="noopener">{x("Brochure (PDF)", "Brosur (PDF)")} ↗</a></p></aside>
</div>

<div class="dpanel" role="tabpanel" id="tp-deliv-uni" aria-labelledby="tb-deliv-uni" data-group="deliv" data-tab="uni">
<p class="dp-intro">{x("University hospitals are half government, half private. Their normal wards charge low fixed fees. Some also have a private wing (for example HASA Executive), where you pay more for a single room and your own specialist.",
                       "Hospital universiti separuh kerajaan, separuh swasta. Wad biasa mengenakan caj tetap yang rendah. Ada juga yang mempunyai wad swasta (contohnya HASA Executive) - bayar lebih untuk bilik seorang dan pakar pilihan sendiri.")}</p>
<div class="pgrid">{uni_cards}</div>
<details class="acc"><summary>{x("Other university hospitals (no prices online - call them)", "Hospital universiti lain (tiada harga dalam talian - hubungi mereka)")}</summary><ul>{ask}</ul></details>
</div>

<div class="dpanel" role="tabpanel" id="tp-deliv-private" aria-labelledby="tb-deliv-private" data-group="deliv" data-tab="private">
<p class="dp-intro">{x(f"Hospitals that publish a price on their own website, cheapest first. Caesarean packages: {_rm(min(cs))} – {_rm(max(cs))}.",
                       f"Hospital yang menyiarkan harga di laman web sendiri, paling murah dahulu. Pakej caesarean: {_rm(min(cs))} – {_rm(max(cs))}.")}</p>
{chips_html}
{sort_select(x, "hosp-list", [("normal:asc", "Normal: cheapest", "Normal: paling murah"),
                               ("normal:desc", "Normal: most expensive", "Normal: paling mahal"),
                               ("csec:asc", "Caesarean: cheapest", "Caesarean: paling murah"),
                               ("name:asc", "Name A-Z", "Nama A-Z"), ("state:asc", "State", "Negeri")])}
<div class="pgrid" id="hosp-list">{"".join(cards)}</div>
{priv_ask_html}
<details class="acc"><summary>{x("What packages usually don't include", "Apa yang biasanya tidak termasuk dalam pakej")}</summary><ul>
<li>{x("Epidural or other pain relief, induction of labour, and often vacuum or forceps.", "Epidural atau ubat tahan sakit lain, induksi bersalin, dan selalunya vakum atau forsep.")}</li>
<li>{x("Complications or an emergency caesarean - you're then charged normal hospital rates.", "Komplikasi atau caesarean kecemasan - anda akan dicaj kadar biasa hospital.")}</li>
<li>{x("Extra nights, and your baby's special care (for example jaundice treatment or the NICU).", "Malam tambahan, dan rawatan khas bayi (contohnya rawatan kuning atau NICU).")}</li>
<li>{x("At some hospitals, deliveries after office hours, at weekends or on public holidays.", "Di sesetengah hospital, bersalin selepas waktu pejabat, hujung minggu atau cuti umum.")}</li>
<li>{x("Many packages need a full deposit around week 36, and some need a few antenatal visits with their doctors first.", "Banyak pakej memerlukan deposit penuh sekitar minggu ke-36, dan ada yang memerlukan beberapa lawatan antenatal dengan doktor mereka dahulu.")}</li>
</ul></details>
</div>
{ad("in_content", x)}
<p><a class="btn ghost" href="hospital-bag.html">{x("Hospital bag checklist →", "Senarai beg hospital →")}</a> <a class="btn ghost" href="confinement-cost.html">{x("Confinement cost →", "Kos berpantang →")}</a></p>
"""
    gov_js = {"d": gov["delivery"], "w": gov["ward_per_day"], "t": gov["treatment_per_day"], "room": gov["room_c1"]}
    write_page(lang, "delivery-cost.html", x("Delivery cost in Malaysia: government, university & private hospitals", "Kos bersalin di Malaysia: hospital kerajaan, universiti & swasta"),
               x("How much giving birth costs in Malaysia: government hospital rates by ward class, FPP, university hospitals (UiTM, HCTM UKM) and private hospital maternity packages, from official price lists.",
                 "Berapa kos bersalin di Malaysia: kadar hospital kerajaan mengikut kelas wad, FPP, hospital universiti (UiTM, HCTM UKM) dan pakej bersalin hospital swasta, daripada senarai harga rasmi."),
               body, {"gov": gov_js})


def p_planning(lang):
    x = tr(lang)
    items = [
        ("folic", "Start folic acid about 3 months before you try, and keep taking it until the end of the first trimester",
         "Mula ambil asid folik lebih kurang 3 bulan sebelum mencuba, dan teruskan hingga akhir trimester pertama",
         "KKM's pre-pregnancy guideline. It helps prevent spine and brain defects in the baby. Ask your klinik for the right dose - it's higher if you have diabetes, epilepsy or had a baby with a neural tube defect.",
         "Garis panduan prakehamilan KKM. Ia membantu mencegah kecacatan tulang belakang dan otak bayi. Tanya klinik untuk dos yang sesuai - dos lebih tinggi jika anda menghidap diabetes, epilepsi atau pernah melahirkan bayi dengan kecacatan tiub neural."),
        ("ppc", "Get a pre-pregnancy check (Penjagaan Prakehamilan) at your klinik kesihatan",
         "Buat pemeriksaan prakehamilan (Penjagaan Prakehamilan) di klinik kesihatan",
         "Especially important if you have diabetes, high blood pressure, heart, thyroid or kidney disease, epilepsy, or take long-term medicine.",
         "Sangat penting jika anda menghidap diabetes, darah tinggi, penyakit jantung, tiroid atau buah pinggang, epilepsi, atau mengambil ubat jangka panjang."),
        ("meds", "Ask your doctor or pharmacist about every medicine and supplement you take - don't stop any on your own",
         "Tanya doktor atau ahli farmasi tentang setiap ubat dan suplemen yang anda ambil - jangan berhenti sendiri", "", ""),
        ("rubella", "Check you're protected against rubella (German measles)",
         "Pastikan anda dilindungi daripada rubela (campak Jerman)",
         "If you need the vaccine, have it before pregnancy - your doctor will tell you how long to wait before trying.",
         "Jika perlu vaksin, ambil sebelum hamil - doktor akan memberitahu berapa lama perlu menunggu sebelum mencuba."),
        ("thal", "Know your thalassaemia carrier status - and your partner's", "Ketahui status pembawa talasemia anda - dan pasangan",
         "Thalassaemia is common in Malaysia. If you both carry it, ask your klinik about counselling before pregnancy.",
         "Talasemia biasa di Malaysia. Jika kedua-duanya pembawa, tanya klinik tentang kaunseling sebelum hamil."),
        ("teeth", "See a dentist", "Jumpa doktor gigi", "", ""),
        ("weight", "Eat well, stay active and aim for a healthy weight", "Makan seimbang, kekal aktif dan capai berat badan sihat", "", ""),
        ("smoke", "Stop smoking, vaping and alcohol - and keep your home smoke-free", "Berhenti merokok, vape dan alkohol - dan pastikan rumah bebas asap rokok", "", ""),
        ("money", "Check your insurance or takaful: many plans only cover pregnancy after a waiting period",
         "Semak insurans atau takaful: banyak pelan hanya melindungi kehamilan selepas tempoh menunggu",
         "Also look at delivery costs and start a small savings fund.", "Lihat juga kos bersalin dan mula simpanan kecil."),
    ]
    lis = "".join(
        f'<li><label class="check"><input type="checkbox" data-key="pl_{k}"> {esc(x(en, ms))}</label>{tip(x(te, tm), x) if te else ""}</li>'
        for k, en, ms, te, tm in items)
    body = f"""
<div data-store="tm_plan" data-progress="{x("{n} of {t} done", "{n} daripada {t} selesai")}" data-done="{x("All done - good luck!", "Semua selesai - semoga dipermudahkan!")}"></div>
{page_head(x, "📝", "t-plan", x("Before pregnancy", "Sebelum hamil"), x("Planning a pregnancy", "Persediaan sebelum hamil"),
           x("What to do in the months before you try for a baby.", "Perkara yang perlu dibuat beberapa bulan sebelum mencuba untuk hamil."))}
{tabbar(x, "pl", [("check", "✅", "Checklist", "Senarai semak", f"0 / {len(items)}", "before you try", "sebelum mencuba", True),
                    ("test", "🧪", "Test & signs", "Ujian & tanda", x("When to test?", "Bila boleh uji?"), "", "", False),
                    ("help", "💬", "Not pregnant yet?", "Belum hamil?", "LPPKN · KWSP", "", "", False)],
                prompt=x("Tap what you need:", "Pilih apa yang anda perlukan:"))}
<div class="dpanel" role="tabpanel" id="tp-pl-check" aria-labelledby="tb-pl-check" data-group="pl" data-tab="check">
<div class="bag-progress card"><div class="bp-top"><strong id="bag-progress" aria-live="polite"></strong><button type="button" class="link-btn muted" id="bag-reset">{x("Untick everything", "Buang semua tanda")}</button></div>
<div class="progress"><span id="bag-bar" style="width:0%"></span></div></div>
<section class="card"><h2><span aria-hidden="true">✅</span> {x("Before you try", "Sebelum mencuba")}</h2><ul class="checklist">{lis}</ul></section>
<div class="tool-row">
  <a class="tool-card t-fert" href="fertility.html"><span class="tool-ico" aria-hidden="true">🌸</span><span><strong>{x("Fertile days", "Hari subur")}</strong><span class="muted">{x("Find your best days to try", "Cari hari terbaik untuk mencuba")}</span></span></a>
  <a class="tool-card t-deliv" href="delivery-cost.html"><span class="tool-ico" aria-hidden="true">🏥</span><span><strong>{x("Delivery cost", "Kos bersalin")}</strong><span class="muted">{x("Budget for the birth", "Bajet untuk bersalin")}</span></span></a>
</div>
</div>
<div class="dpanel" role="tabpanel" id="tp-pl-test" aria-labelledby="tb-pl-test" data-group="pl" data-tab="test">
<details class="acc" open><summary>{x("When can I take a pregnancy test?", "Bila boleh buat ujian kehamilan?")}</summary>
<p>{x("Most home pregnancy tests work from the day your period is due. Testing earlier can show a negative even if you are pregnant - if your period still doesn't come, test again a few days later. The fertile-days calculator shows when your next period is due.",
     "Kebanyakan ujian kehamilan di rumah berkesan mulai hari haid dijangka. Ujian lebih awal boleh menunjukkan negatif walaupun anda hamil - jika haid masih belum datang, uji semula beberapa hari kemudian. Kalkulator hari subur menunjukkan bila haid seterusnya dijangka.")}</p></details>
<details class="acc" open><summary>{x("Early signs of pregnancy", "Tanda awal kehamilan")}</summary><ul>
<li>{x("A missed period", "Haid tidak datang")}</li><li>{x("Feeling sick or vomiting (morning sickness)", "Loya atau muntah (alahan)")}</li>
<li>{x("Sore or swollen breasts", "Payudara sakit atau membengkak")}</li><li>{x("Feeling very tired", "Sangat letih")}</li>
<li>{x("Needing to pee more often", "Kerap buang air kecil")}</li></ul>
<p class="small muted">{x("Once a test is positive, register at your klinik kesihatan for antenatal care as early as you can.", "Selepas ujian positif, daftar di klinik kesihatan untuk penjagaan antenatal secepat mungkin.")}</p></details>
</div>
<div class="dpanel" role="tabpanel" id="tp-pl-help" aria-labelledby="tb-pl-help" data-group="pl" data-tab="help">
<aside class="box note"><h2>{x("Not pregnant yet?", "Belum hamil lagi?")}</h2><ul>
<li>{x("See a doctor if you've tried for a year - or after 6 months if you're 35 or older, or sooner if your periods are irregular. Your klinik kesihatan can refer you.",
       "Jumpa doktor jika sudah mencuba setahun - atau selepas 6 bulan jika berumur 35 tahun ke atas, atau lebih awal jika haid tidak teratur. Klinik kesihatan boleh merujuk anda.")}</li>
<li>{x("LPPKN's fertility programme subsidises IUI treatment for eligible couples (both Malaysian, household income below RM10,000 a month, wife under 37).",
       "Program kesuburan LPPKN memberi subsidi rawatan IUI kepada pasangan layak (kedua-duanya warganegara, pendapatan isi rumah bawah RM10,000 sebulan, isteri bawah 37 tahun).")}
    <a href="https://www.lppkn.gov.my/lppkngateway/frontend/web/index.php?r=portal/article2&amp;menu=46&amp;id=MzZWR0JhNFZJbU9lbjNIZU9Rc1E2QT09" target="_blank" rel="noopener">LPPKN ↗</a></li>
<li>{x("You can withdraw from your EPF Akaun Sejahtera to pay for fertility treatment (IVF, IUI, ICSI).", "Anda boleh mengeluarkan wang daripada Akaun Sejahtera KWSP untuk rawatan kesuburan (IVF, IUI, ICSI).")}
    <a href="https://www.kwsp.gov.my/en/member/healthcare/fertility" target="_blank" rel="noopener">KWSP ↗</a></li>
<li>{x("IVF and IUI costs for you or your spouse count towards the medical expenses income tax relief (up to RM10,000).", "Kos IVF dan IUI untuk anda atau pasangan boleh dituntut di bawah pelepasan cukai perbelanjaan perubatan (sehingga RM10,000).")}</li>
</ul></aside>
</div>
{ad("in_content", x)}
<p class="small muted">{x("Sources: KKM Pre-pregnancy Care guideline (Dec 2023), LPPKN, KWSP and LHDN websites, checked November 2026. General information only - follow your doctor's advice.",
                          "Sumber: Garis Panduan Perkhidmatan Prakehamilan KKM (Dis 2023), laman LPPKN, KWSP dan LHDN, disemak November 2026. Maklumat umum sahaja - ikut nasihat doktor anda.")}</p>
"""
    write_page(lang, "planning.html", x("Planning a pregnancy: checklist for Malaysian mums", "Persediaan sebelum hamil: senarai semak"),
               x("Before you try for a baby: folic acid, pre-pregnancy check at the klinik kesihatan, rubella and thalassaemia, when to test, and fertility help from LPPKN and EPF.",
                 "Sebelum mencuba untuk hamil: asid folik, pemeriksaan prakehamilan di klinik kesihatan, rubela dan talasemia, bila boleh uji, dan bantuan kesuburan LPPKN dan KWSP."),
               body)


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
        ("prices.html", "🍼", "Milk, diapers & essentials", "Harga barang keperluan", "Cheapest shops near you", "Kedai termurah berhampiran", "t-prices"),
        ("nursery.html", "🧸", "Taska & tadika", "Taska & tadika", "Childcare near you", "Penjagaan anak berhampiran", "t-nursery"),
    ]
    desc = {h: (de, dm) for h, i, te, tm, de, dm, c in tools}
    desc.update({
        "fertility.html": ("When you're most likely to conceive", "Bila peluang hamil paling tinggi"),
        "names.html": ("From every Malaysian community", "Daripada pelbagai kaum di Malaysia"),
        "labour.html": ("Count kicks, time contractions", "Kira tendangan, masa kontraksi"),
        "after-birth.html": ("Birth cert, MyKid, ASB & savings", "Sijil lahir, MyKid, ASB & simpanan"),
        "planning.html": ("Folic acid, checks & fertility help", "Asid folik, saringan & bantuan kesuburan"),
        "delivery-cost.html": ("Government, university & private", "Kerajaan, universiti & swasta"),
        "vaccines.html": ("Your baby's KKM vaccine dates", "Tarikh vaksin bayi (KKM)"),
        "breastmilk.html": ("Latch, supply, pumping & storage", "Pelekapan, bekalan, memerah & simpanan"),
        "newborn.html": ("What to buy before baby", "Apa perlu dibeli sebelum bayi"),
        "antenatal.html": ("Klinik visits, tests & Tdap - dated", "Lawatan klinik, ujian & Tdap - bertarikh"),
        "healthy-pregnancy.html": ("Food, fasting & flying", "Makanan, puasa & terbang"),
        "budget.html": ("Add up baby's first year", "Kira kos tahun pertama bayi"),
        "feelings.html": ("Private postnatal depression check", "Semakan kemurungan selepas bersalin"),
        "aqiqah.html": ("7th, 14th & 21st day dates", "Tarikh hari ke-7, 14 & 21"),
        "jaundice.html": ("Warning signs & what to avoid", "Tanda bahaya & apa perlu dielak"),
        "growth.html": ("WHO chart, milestones & sleep", "Carta WHO, perkembangan & tidur"),
        "solids.html": ("Starting food at 6 months", "Mula makanan pada 6 bulan"),
        "baby-log.html": ("Tap to log feeds, nappies & sleep", "Rekod susuan, lampin & tidur"),
        "pregnancy-body.html": ("Is it normal? Symptoms, weight, HB", "Normalkah? Simptom, berat, HB"),
        "recovery.html": ("Bleeding, stitches & check-ups", "Darah nifas, jahitan & pemeriksaan"),
        "baby-health.html": ("Fever, crying, poo & rashes", "Demam, tangisan, najis & ruam"),
        "safety.html": ("Car seats, home & choking", "Kerusi kereta, rumah & tercekik"),
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
        parts.append(tabpanel("tri", f"t{t}", f'<ul class="week-list">{lis}</ul>'))
    tri_tabs = tabbar(x, "tri", [("t1", "🌱", "Trimester 1", "Trimester 1", x("Weeks 4–13", "Minggu 4–13"), "", "", False),
                                 ("t2", "🌷", "Trimester 2", "Trimester 2", x("Weeks 14–27", "Minggu 14–27"), "", "", False),
                                 ("t3", "🌻", "Trimester 3", "Trimester 3", x("Weeks 28–40", "Minggu 28–40"), "", "", False)])
    body = f"""
{page_head(x, "📅", "t-weeks", x("Week by week", "Minggu demi minggu"), x("Pregnancy week by week", "Kehamilan minggu demi minggu"),
             x("Your baby's size, growth and one useful thing to do - weeks 4 to 40.", "Saiz bayi, perkembangan dan satu perkara berguna - minggu 4 hingga 40."))}
{tri_tabs}
{"".join(parts)}
{ad("in_content", x)}
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
{tabbar(x, "wk", [("baby", "👶", "Your baby", "Bayi anda", "", "", "", False), ("mum", "🤰", "Your body", "Badan anda", "", "", "", False),
                    ("todo", "✅", "To do", "Perlu buat", "", "", "", False)])}
{tabpanel("wk", "baby", f'<section class="card"><h2><span aria-hidden="true">👶</span> {x("Your baby this week", "Bayi anda minggu ini")}</h2><p>{esc(d["baby"])}</p></section>')}
{tabpanel("wk", "mum", f'<section class="card"><h2><span aria-hidden="true">🤰</span> {x("Your body", "Badan anda")}</h2><p>{esc(d["mum"])}</p></section>')}
{tabpanel("wk", "todo", f'<section class="card todo-card"><h2><span aria-hidden="true">✅</span> {x("To do this week", "Perlu dibuat minggu ini")}</h2><p>{esc(d["todo"])}</p></section>')}
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
{tabbar(x, "pt", [("plan", "📅", "My timeline", "Jadual saya", x("44 · 30 · 40 days", "44 · 30 · 40 hari"), "dates for before and after", "tarikh sebelum & selepas", False),
                    ("trad", "🌙", "Traditions", "Tradisi", x("Malay · Chinese · Indian", "Melayu · Cina · India"), "", "", False),
                    ("help", "🏠", "Help at home", "Bantuan di rumah", x("Carers & meals", "Penjaga & makanan"), "", "", False)],
                prompt=x("Tap what you need:", "Pilih apa yang anda perlukan:"))}
<div class="dpanel" role="tabpanel" id="tp-pt-plan" aria-labelledby="tb-pt-plan" data-group="pt" data-tab="plan">
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
</div>
<div class="dpanel" role="tabpanel" id="tp-pt-trad" aria-labelledby="tb-pt-trad" data-group="pt" data-tab="trad">
<section><h2>{x("Pantang traditions in Malaysia", "Tradisi berpantang di Malaysia")} {tip(x("Every family is different - these are common practices, not rules.", "Setiap keluarga berbeza - ini amalan biasa, bukan peraturan."), x)}</h2>
<div class="trad-grid">{cards}</div></section>
</div>
<div class="dpanel" role="tabpanel" id="tp-pt-help" aria-labelledby="tb-pt-help" data-group="pt" data-tab="help">
<section><h2>{x("Help at home after the birth", "Bantuan di rumah selepas bersalin")} {tip(x("Links open HappyPreggie, a Malaysian directory of pregnancy and confinement providers. Most list 'contact for price' - ask for a written quote, and compare it in our confinement cost tool.", "Pautan membuka HappyPreggie, direktori penyedia khidmat kehamilan dan berpantang di Malaysia. Kebanyakannya 'hubungi untuk harga' - minta sebut harga bertulis, dan bandingkan dalam alat kos berpantang kami."), x)}</h2>
<div class="help-grid">
  <a class="help-card" href="https://www.happypreggie.com/listing/pantang" target="_blank" rel="noopener"><span aria-hidden="true">💆‍♀️</span><strong>{x("Pantang carers & urut", "Penjaga pantang & urut")}</strong><span class="muted">{x("Home visits for mum and baby", "Lawatan ke rumah untuk ibu dan bayi")} ↗</span></a>
  <a class="help-card" href="https://www.happypreggie.com/listing/confinement-food" target="_blank" rel="noopener"><span aria-hidden="true">🍱</span><strong>{x("Confinement meals", "Makanan pantang")}</strong><span class="muted">{x("Delivered daily", "Dihantar setiap hari")} ↗</span></a>
  <a class="help-card" href="https://www.happypreggie.com/listing/confinement-centre" target="_blank" rel="noopener"><span aria-hidden="true">🏨</span><strong>{x("Confinement centres", "Pusat berpantang")}</strong><span class="muted">{x("300+ centres listed", "300+ pusat disenaraikan")} ↗</span></a>
  <a class="help-card" href="https://www.happypreggie.com/listing/antenatal-education" target="_blank" rel="noopener"><span aria-hidden="true">🤱</span><strong>{x("Breastfeeding help", "Bantuan penyusuan")}</strong><span class="muted">{x("Lactation consultants and classes", "Kaunselor laktasi dan kelas")} ↗</span></a>
</div></section>
</div>
{ad("in_content", x)}
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
    with open(os.path.join(HERE, "site-data", "confinement.json"), encoding="utf-8") as f:
        CD = json.load(f)
    today_iso = TODAY.isoformat()
    inc_names = {k: (en, ms) for k, en, ms in extras}
    centre_cards = []
    order = sorted(range(len(CD["centres"])), key=lambda i: CD["centres"][i]["price_from_rm"])
    for i in order:
        c = CD["centres"][i]
        ended = c.get("valid_until") and today_iso > c["valid_until"]
        days = c.get("days") or 28
        per_day = round(c["price_from_rm"] / days)
        price_rng = _rm(c["price_from_rm"]) + (f' – {_rm(c["price_to_rm"])}' if c.get("price_to_rm") else "")
        incs = "".join(
            f'<li class="{"yes" if v is True else "no" if v is False else "ask"}">{"✓ " if v is True else "✗ " if v is False else "? "}{esc(x(*inc_names[k]))}</li>'
            for k, v in c.get("includes", {}).items() if k in inc_names)
        rows = (f'<div>{x("Price", "Harga")}<strong>{price_rng}</strong></div>'
                f'<div>{x("Stay", "Tempoh")}<strong>{x("not stated", "tidak dinyatakan") if c.get("days_unstated") else str(days) + " " + x("days", "hari")}</strong></div>'
                f'<div>{x("Per day from", "Sehari dari")}<strong>{_rm(per_day)}</strong></div>'
                + (f'<div>{x("Babies per nurse", "Bayi setiap jururawat")}<strong>{c["babies_per_nurse"]}</strong></div>' if c.get("babies_per_nurse") else "")
                + (f'<div>{x("Food", "Makanan")}<strong>{x("Halal", "Halal") if c["halal"] else x("Not halal", "Tidak halal")}</strong></div>' if c.get("halal") is not None else ""))
        body_ = (f'<div class="pc-rows">{rows}</div>'
                 f'<p class="small muted">{x("Included (✓ yes · ✗ no · ? ask the centre):", "Termasuk (✓ ya · ✗ tidak · ? tanya pusat):")}</p><ul class="inc-list">{incs}</ul>'
                 + (f'<p>{esc(x(c.get("caveat_en", ""), c.get("caveat_ms", "")))}</p>' if c.get("caveat_en") else "")
                 + (f'<p class="hosp-ended">{x("This promotion may have ended - check the current price.", "Promosi ini mungkin sudah tamat - semak harga terkini.")}</p>' if ended else "")
                 + f'<p class="pc-actions"><button type="button" class="btn" data-compare="c{i}">+ {x("Add to comparison", "Tambah ke perbandingan")}</button>'
                   f'<a class="btn ghost" href="{esc(c["source_url"])}" target="_blank" rel="noopener">{x("Centre website", "Laman pusat")} ↗</a>'
                   f'<span class="small muted">{x("checked", "disemak")} {_dmy(c["checked"], lang)}</span></p>')
        csort = {"price": c["price_from_rm"], "perday": per_day, "name": c["name"].lower(), "state": c["state"].lower()}
        centre_cards.append(pcard(x, x("Confinement centre", "Pusat berpantang"), "🏨", c["name"], f'{c["area"]}, {c["state"]}',
                                  x("days not stated", "tempoh tidak dinyatakan") if c.get("days_unstated") else f'{days} {x("days", "hari")}',
                                  f'{x("From", "Dari")} {_rm(c["price_from_rm"])}<small>{_rm(per_day)}{x("/day", "/hari")}</small>', body_, state=c["state"], sort=csort))
    c_ask = CD.get("centres_ask", [])
    c_states = sorted({c["state"] for c in CD["centres"]} | {a["state"] for a in c_ask})
    c_ask_html = ""
    if c_ask:
        lis = "".join(f'<li data-state="{esc(a["state"])}"><a href="{esc(a["url"])}" target="_blank" rel="noopener">{esc(a["name"])}</a> '
                      f'<span class="muted">· {esc(a["area"])}, {esc(a["state"])}</span></li>' for a in c_ask)
        c_ask_html = (f'<details class="acc" id="centre-ask"><summary>{x(f"{len(c_ask)} more centres with no price online - call them", f"{len(c_ask)} lagi pusat tanpa harga dalam talian - hubungi mereka")}</summary>'
                      f'<ul>{lis}</ul></details>')
    c_min = min(c["price_from_rm"] for c in CD["centres"])
    typ = {t["id"]: t for t in CD["typical"]}
    def typ_row(tid, en, ms, rng):
        return (f'<li><span>{esc(x(en, ms))}</span><strong>{rng}</strong>'
                f'<button type="button" class="link-btn" data-compare="{tid}">+ {x("Compare", "Banding")}</button></li>')
    home_cards = []
    for h in CD.get("home_care", []):
        per = h.get("per_days", 7)
        body_ = (f'<div class="pc-rows"><div>{x("Price", "Harga")}<strong>{x("from", "dari")} {_rm(h["price_from_rm"])}</strong></div>'
                 f'<div>{x("For", "Untuk")}<strong>{per} {x("days", "hari")}</strong></div>'
                 + ("" if per == 28 else f'<div>{x("28 days", "28 hari")}<strong>{_rm(h["p28_rm"])}</strong></div>' if h.get("p28_rm")
                    else f'<div>{x("28 days at this rate", "28 hari pada kadar ini")}<strong>~{_rm(round(h["price_from_rm"] * 28 / per))}</strong></div>') + '</div>'
                 f'<p>{esc(x(h["note_en"], h["note_ms"]))}</p>'
                 f'<p class="pc-actions"><a class="btn" href="{esc(h["source_url"])}" target="_blank" rel="noopener">{x("Their website", "Laman web mereka")} ↗</a>'
                 f'<span class="small muted">{x("checked", "disemak")} {_dmy(h["checked"], lang)}</span></p>')
        home_cards.append(pcard(x, x("Pantang carer at home", "Penjaga pantang di rumah"), "👩‍🍼", x(h["name"], h.get("name_ms", h["name"])), x(h["area_en"], h["area_ms"]),
                                f'{per} {x("days", "hari")}', f'{x("From", "Dari")} {_rm(h["price_from_rm"])}<small>{x("per", "untuk")} {per} {x("days", "hari")}</small>', body_))
    home_html = (f'<h2 class="sv-head">{x("Home pantang services with a published price", "Perkhidmatan pantang di rumah dengan harga diterbitkan")}</h2>'
                 f'<div class="pgrid">{"".join(home_cards)}</div>') if home_cards else ""
    cost_tabs = tabbar(x, "cost", [
        ("centres", "🏨", "Centres", "Pusat berpantang", f'{x("from", "dari")} {_rm(c_min)}', f"{len(CD['centres'])} centres with published prices", f"{len(CD['centres'])} pusat dengan harga diterbitkan", False),
        ("nanny", "👩‍🍼", "Nanny at home", "Pengasuh di rumah", "RM5,000 – 9,000", "typical, live-in, 28 days", "biasa, tinggal bersama, 28 hari", False),
        ("compare", "⚖️", "Compare quotes", "Banding sebut harga", x("Price per day", "Harga sehari"), "rank your own quotes", "susun sebut harga anda", False),
    ], hash_ok=True, prompt=x("What are you looking for? Tap one:", "Apa yang anda cari? Pilih satu:"))
    nanny_qs = [
        (x("Does she live in with you, and how many hours does she work each day?", "Adakah dia tinggal bersama, dan berapa jam dia bekerja sehari?")),
        (x("Does she cook pantang meals, and who buys the ingredients?", "Adakah dia memasak makanan pantang, dan siapa yang membeli bahan?")),
        (x("Does she look after the baby at night so you can sleep?", "Adakah dia menjaga bayi pada waktu malam supaya anda boleh tidur?")),
        (x("Can she give herbal baths, urut or bertungku - and has your doctor said it's safe?", "Bolehkah dia memandikan herba, mengurut atau bertungku - dan adakah doktor kata selamat?")),
        (x("What happens on public holidays, and is there a replacement if she falls ill?", "Bagaimana pada cuti umum, dan adakah pengganti jika dia sakit?")),
        (x("How much is the deposit, and is it refundable if the baby comes early or late?", "Berapa deposit, dan adakah ia dipulangkan jika bayi lahir awal atau lewat?")),
    ]
    body = f"""
{page_head(x, "💰", "t-cost", x("Confinement", "Berpantang"), x("Confinement cost", "Kos berpantang"),
             x("Compare centres and nannies by price per day.", "Banding pusat dan pengasuh mengikut harga sehari."))}
{cost_tabs}
{tabpanel("cost", "centres", f"""
<p class="dp-intro">{x("Centres that publish a price on their own website, cheapest first. Tap a card for details, or add it to your comparison.",
                       "Pusat yang menyiarkan harga di laman web sendiri, paling murah dahulu. Tekan kad untuk butiran, atau tambah ke perbandingan anda.")}</p>
{state_chips(x, "centre-list", c_states).replace('data-for="centre-list"', 'data-for="centre-list" data-ask="centre-ask"')}
{sort_select(x, "centre-list", [("price:asc", "Cheapest first", "Paling murah dahulu"), ("price:desc", "Most expensive first", "Paling mahal dahulu"),
                                 ("perday:asc", "Cheapest per day", "Sehari paling murah"), ("name:asc", "Name A-Z", "Nama A-Z"), ("state:asc", "State", "Negeri")])}
<div class="pgrid" id="centre-list">{"".join(centre_cards)}</div>
{c_ask_html}
<aside class="box note"><p>{x("In other states (Kedah, Perlis, Perak, Kelantan, Terengganu, Pahang, Negeri Sembilan, Melaka, Sabah, Sarawak) we checked again in November 2026: no confinement centre publishes its price online. Home pantang services with published prices do cover several of these states -",
                            "Di negeri lain (Kedah, Perlis, Perak, Kelantan, Terengganu, Pahang, Negeri Sembilan, Melaka, Sabah, Sarawak) kami menyemak semula pada November 2026: tiada pusat berpantang yang menyiarkan harga dalam talian. Perkhidmatan pantang di rumah dengan harga diterbitkan meliputi beberapa negeri ini -")}
<a href="#nanny">{x("see Nanny at home", "lihat Pengasuh di rumah")} →</a></p></aside>
<section><h2>{x("Typical prices for 28 days", "Harga biasa untuk 28 hari")} {tip(x("Rough 2026 ranges from price guides (malaysia4u.com). Prices differ a lot by city and by what's included - always get a written quote.",
                                                                              "Anggaran julat 2026 daripada panduan harga (malaysia4u.com). Harga sangat berbeza mengikut bandar dan apa yang termasuk - sentiasa minta sebut harga bertulis."), x)}</h2>
<ul class="price-list typ-list">
  {typ_row("t-budget", "Centre - budget (outside central KL)", "Pusat - bajet (luar pusat KL)", "RM9,000 – 12,000")}
  {typ_row("t-mid", "Centre - mid-range", "Pusat - pertengahan", "RM12,000 – 18,000")}
  {typ_row("t-lux", "Centre - luxury", "Pusat - mewah", "RM20,000 – 40,000+")}
</ul></section>
<p class="maps-row"><a class="btn ghost" href="https://www.google.com/maps/search/?api=1&amp;query={maps_q}" target="_blank" rel="noopener">🔎 {x("More centres near you (Google Maps)", "Lagi pusat berhampiran (Google Maps)")} ↗</a>
<a class="btn ghost" href="https://www.happypreggie.com/listing/confinement-centre" target="_blank" rel="noopener">📋 {x("300+ centres on HappyPreggie", "300+ pusat di HappyPreggie")} ↗</a>
{tip(x("Smaller local centres are often cheaper but don't publish prices online. Ask them for a quote, then add it in 'Compare quotes'.",
       "Pusat kecil berhampiran selalunya lebih murah tetapi tidak menerbitkan harga dalam talian. Minta sebut harga, kemudian masukkan dalam 'Banding sebut harga'."), x)}</p>
""")}
{tabpanel("cost", "nanny", f"""
<div class="card nanny-card"><div class="pc-rows">
  <div>{x("Live-in confinement nanny", "Pengasuh berpantang tinggal bersama")}<strong>RM5,000 – 9,000</strong></div>
  <div>{x("Usual length", "Tempoh biasa")}<strong>28 {x("days", "hari")}</strong></div>
  <div>{x("Per day", "Sehari")}<strong>~RM179 – 321</strong></div></div>
  <p class="small muted">{x("Typical 2026 range from price guides (malaysia4u.com) - agencies and freelance nannies vary a lot.", "Julat biasa 2026 daripada panduan harga (malaysia4u.com) - agensi dan pengasuh bebas sangat berbeza.")}</p>
  <p class="pc-actions"><button type="button" class="btn" data-compare="t-nanny">+ {x("Add a typical nanny to comparison", "Tambah pengasuh biasa ke perbandingan")}</button>
  <a class="btn ghost" href="https://www.happypreggie.com/listing/pantang" target="_blank" rel="noopener">{x("Find pantang carers (HappyPreggie)", "Cari penjaga pantang (HappyPreggie)")} ↗</a></p></div>
{home_html}
<details class="acc" open><summary>{x("Ask a nanny before you book", "Tanya pengasuh sebelum menempah")}</summary><ol>{"".join(f"<li>{esc(q)}</li>" for q in nanny_qs)}</ol></details>
""")}
{tabpanel("cost", "compare", f"""
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
<details class="acc"><summary>{x("Ask before you pay a deposit", "Tanya sebelum membayar deposit")}</summary><ol>{qs}</ol></details>
""")}
{ad("in_content", x)}
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
    icons = ["📄", "🤰", "👶", "👨"]
    bag_tabs = tabbar(x, "bag", [(f"s{i}", icons[i], te, tm, f"0 / {len(items)}", "", "", True) for i, (te, tm, items) in enumerate(BAG)],
                      prompt=x("Pack one part at a time:", "Kemas satu bahagian pada satu masa:"))
    bag_panels = "".join(tabpanel("bag", f"s{i}", sec) for i, sec in enumerate(secs))
    body = f"""
{page_head(x, "👜", "t-bag", x("Before the birth", "Sebelum bersalin"), x("Hospital bag checklist", "Senarai semak beg hospital"), extra=tip(x("Pack by about 36 weeks. Your ticks are saved on this phone. 'Shop' links open Shopee - some are affiliate links, so we may earn a small commission at no extra cost to you.",
                                                                       "Siapkan sebelum lebih kurang 36 minggu. Tanda anda disimpan dalam telefon ini. Pautan 'Beli' membuka Shopee - sesetengahnya pautan afiliasi, jadi kami mungkin mendapat komisen kecil tanpa kos tambahan kepada anda."), x))}
<div class="bag-progress card"><div class="bp-top"><strong id="bag-progress" aria-live="polite"></strong><button type="button" class="link-btn muted" id="bag-reset">{x("Untick everything", "Buang semua tanda")}</button></div>
<div class="progress"><span id="bag-bar" style="width:0%"></span></div></div>
{bag_tabs}
{bag_panels}
{ad("in_content", x)}
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
{page_head(x, "🍼", "t-prices", x("Prices", "Harga"), x("Milk, diapers & essentials", "Harga susu, lampin & barang keperluan"), lead=x("Official shop prices near you.", "Harga kedai rasmi berhampiran anda."), lead_id="pr-updated", extra=tip(x("Shop prices from the government's price survey: PriceCatcher by KPDN, published on data.gov.my. Typical = the middle price across shops. From = 1 in 10 shops charge this or less. Prices change often - check in store.",
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
  <div class="chip-scroll" id="pr-chips" role="group" aria-label="{x("Your state", "Negeri anda")}"></div>
  <label class="sort-row"><span>⇅ {x("Sort by", "Susun ikut")}</span>
    <select id="pr-sort">
      <option value="unit">{x("Cheapest per unit", "Seunit paling murah")}</option>
      <option value="typical">{x("Cheapest typical price", "Harga biasa paling murah")}</option>
      <option value="from">{x("Cheapest 'from' price", "Harga 'dari' paling murah")}</option>
      <option value="az">{x("Name A-Z", "Nama A-Z")}</option>
      <option value="shops">{x("Most shops", "Paling banyak kedai")}</option>
    </select></label>
</section>
<div id="pr-tables" aria-live="polite"><p class="muted">{x("Loading prices...", "Memuatkan harga...")}</p></div>
{ad("bottom", x)}
"""
    write_page(lang, "prices.html", x("Baby milk, diaper & essentials prices in Malaysia", "Harga susu bayi, lampin & barang keperluan di Malaysia"),
               x("Compare baby milk, formula, diaper, maternity pad, laundry and pantang food prices by state and district in Malaysia, from the government's PriceCatcher survey. Find the cheapest shops near you.",
                 "Banding harga susu bayi, susu formula, lampin, tuala wanita, barang dobi dan bahan masakan pantang mengikut negeri dan daerah, daripada tinjauan PriceCatcher kerajaan. Cari kedai paling murah berhampiran anda."),
               body, {"grpOrder": list(GROUPS)})


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
    with open(os.path.join(HERE, "site-data", "nursery.json"), encoding="utf-8") as f:
        NUD = json.load(f)
    NU = NUD["options"]
    def nu_fee(o):
        return x(o["fee_en"], o["fee_ms"])
    nu_opts = "".join(
        '<optgroup label="' + esc(lbl) + '">'
        + "".join(f'<option value="{esc(o["id"])}">{esc(o["name"])} · {esc(nu_fee(o))}</option>' for o in NU if o.get("sector", "gov") == sec) + "</optgroup>"
        for sec, lbl in (("gov", x("Government (fees published)", "Kerajaan (yuran diterbitkan)")),
                         ("private", x("Private chains (fees published)", "Rangkaian swasta (yuran diterbitkan)"))))
    nu_cards = []
    for i in range(1, 5):
        chips = "".join(f'<label class="chip"><input type="checkbox" name="inc" value="{k}"><span>{esc(x(en, ms))}</span></label>'
                        for k, en, ms in nu_extras)
        nu_cards.append(f"""<div class="quote" data-q="{i}"{" hidden" if i > 2 else ""}>
  <div class="q-head"><span class="q-num">{i}</span>
    <select name="preset" aria-label="{x("Choose a taska or tadika", "Pilih taska atau tadika")} {i}">
      <option value="">{x("Choose, or enter your own...", "Pilih, atau isi sendiri...")}</option>{nu_opts}</select></div>
  <p class="q-sum" hidden></p>
  <details class="q-edit"><summary>{x("Edit / enter your own", "Ubah / isi sendiri")}</summary>
  <div class="q-fields">
    <label class="field q-name">{x("Name", "Nama")}<input type="text" name="name" maxlength="60" autocomplete="off" placeholder="{x("Name of taska / tadika", "Nama taska / tadika")}"></label>
    <label class="field">{x("Monthly fee (RM)", "Yuran bulanan (RM)")}<input type="number" name="fee" min="0" inputmode="decimal"></label>
    <label class="field">{x("Registration + deposit (RM)", "Pendaftaran + deposit (RM)")}<input type="number" name="reg_fee" min="0" inputmode="decimal"></label>
    <label class="field">{x("Opens", "Buka")}<input type="time" name="open"></label>
    <label class="field">{x("Closes", "Tutup")}<input type="time" name="close"></label>
    <label class="field">{x("Children per carer", "Kanak-kanak/pengasuh")}<input type="number" name="ratio" min="1" max="30" inputmode="numeric"></label>
  </div>
  <div class="chips">{chips}</div>
  </details>
</div>""")
    nu_dir = []
    for o in NU:
        rows = (f'<div>{x("Monthly", "Sebulan")}<strong>{esc(nu_fee(o))}</strong></div>'
                f'<div>{x("Registration", "Pendaftaran")}<strong>{x("Free", "Percuma") if o["reg"] == 0 else (_rm(o["reg"]) if o["reg"] else x("Ask", "Tanya"))}</strong></div>'
                f'<div>{x("Ages", "Umur")}<strong>{esc(o["ages"])} {x("years", "tahun")}</strong></div>')
        body_ = (f'<div class="pc-rows">{rows}</div><p>{esc(x(o["note_en"], o["note_ms"]))}</p>'
                 f'<p class="pc-actions"><button type="button" class="btn" data-nu-add="{esc(o["id"])}">+ {x("Add to comparison", "Tambah ke perbandingan")}</button>'
                 f'<a class="btn ghost" href="{esc(o["source_url"])}" target="_blank" rel="noopener">{x("Official page", "Laman rasmi")} ↗</a>'
                 + (f'<a class="btn ghost" href="{esc(o["apply_url"])}" target="_blank" rel="noopener">{x("Apply", "Mohon")} ↗</a>' if o.get("apply_url") else "")
                 + f'<span class="small muted">{x("checked", "disemak")} {_dmy(o["checked"], lang)}</span></p>')
        if o.get("sector") == "private":
            kind = x("Private tadika (chain)", "Tadika swasta (rangkaian)") if o["kind"] == "tadika" else x("Private playschool (chain)", "Playschool swasta (rangkaian)")
        else:
            kind = x("Government tadika", "Tadika kerajaan") if o["kind"] == "tadika" else x("Government taska", "Taska kerajaan")
        year = (o["fee"] * 12 + (o["reg"] or 0)) if o["fee"] is not None else 999999
        nsort = {"year": year, "name": o["name"].lower(), "age": int(o["ages"].split("-")[0])}
        nu_dir.append(pcard(x, kind, o["icon"], o["name"], x(o["area_en"], o["area_ms"]) if o.get("area_en") else x("All over Malaysia", "Seluruh Malaysia"),
                            f'{x("Ages", "Umur")} {esc(o["ages"])}', esc(nu_fee(o)) + (f'<small>{x("a month", "sebulan")}</small>' if o["fee"] else ""), body_,
                            sort=nsort))
    gask = NUD.get("gov_ask", [])
    gask_html = ("" if not gask else
                 f'<details class="acc"><summary>{x("State-run taska with no fee online - call them", "Taska kerajaan negeri tanpa yuran dalam talian - hubungi mereka")}</summary><ul>'
                 + "".join(f'<li><a href="{esc(a["url"])}" target="_blank" rel="noopener">{esc(a["name"])}</a> <span class="muted">· {esc(a["state"])}</span><br>'
                           f'<span class="small">{esc(x(a["note_en"], a["note_ms"]))}</span></li>' for a in gask) + "</ul></details>")
    help_cards = []
    for h in NUD.get("help", []):
        loc = x("All over Malaysia", "Seluruh Malaysia") if h["state"] == "*" else h["state"]
        hb = (f'<p>{esc(x(h["note_en"], h["note_ms"]))}</p>'
              f'<p class="pc-actions"><a class="btn" href="{esc(h["source_url"])}" target="_blank" rel="noopener">{x("Official page", "Laman rasmi")} ↗</a>'
              f'<span class="small muted">{x("checked", "disemak")} {_dmy(h["checked"], lang)}</span></p>')
        help_cards.append(pcard(x, x("Help with fees", "Bantuan yuran"), h["icon"], x(h["name_en"], h["name_ms"]), loc,
                                esc(x(h["who_en"], h["who_ms"])), esc(x(h["amount_en"], h["amount_ms"])), hb, state=h["state"]))
    help_states = sorted({h["state"] for h in NUD.get("help", []) if h["state"] != "*"})
    nu_help = f"""<p class="dp-intro">{x("Official help with taska and tadika fees. Tap your state to see what you may get there - the ones marked 'All over Malaysia' apply everywhere.",
                                       "Bantuan rasmi untuk yuran taska dan tadika. Pilih negeri anda - yang bertanda 'Seluruh Malaysia' terpakai di semua negeri.")}</p>
{state_chips(x, "help-list", help_states)}
<div class="pgrid" id="help-list">{"".join(help_cards)}</div>
<aside class="box note"><p>{x("We checked every state in November 2026. Only Selangor and Sarawak publish their own fee help online; elsewhere, use the national subsidy and tax relief above, and ask your state assemblyman's (ADUN) office about local aid.",
                            "Kami menyemak setiap negeri pada November 2026. Hanya Selangor dan Sarawak menyiarkan bantuan yuran negeri dalam talian; di negeri lain, gunakan subsidi kebangsaan dan pelepasan cukai di atas, dan tanya pejabat ADUN anda tentang bantuan setempat.")}</p></aside>"""
    nu_compare = f"""<p class="dp-intro">{x("Government taska and tadika - and a few private chains - publish their fees, so you can add them straight to your comparison. Most private ones don't - visit them, then enter their quote.",
                                         "Taska dan tadika kerajaan - serta beberapa rangkaian swasta - menyiarkan yuran mereka, jadi anda boleh terus menambahnya ke perbandingan. Kebanyakan yang swasta tidak - lawat dahulu, kemudian masukkan sebut harga mereka.")}</p>
{sort_select(x, "nu-list", [("year:asc", "Cheapest first", "Paling murah dahulu"), ("age:asc", "Youngest age first", "Umur paling muda dahulu"),
                            ("name:asc", "Name A-Z", "Nama A-Z")])}
<div class="pgrid" id="nu-list">{"".join(nu_dir)}</div>
{gask_html}
<section class="card" id="nu-compare">
  <h2>{x("Compare taska & tadika", "Banding taska & tadika")} {tip(x("Pick a government option or enter what a centre told you. We rank them by first-year cost (12 months of fees plus registration and deposit). Saved only on this phone.",
                                                                   "Pilih pilihan kerajaan atau masukkan apa yang pusat beritahu anda. Kami susun mengikut kos tahun pertama (12 bulan yuran serta pendaftaran dan deposit). Disimpan dalam telefon ini sahaja."), x)}</h2>
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
{tabbar(x, "nu", [("find", "📍", "Find near you", "Cari berhampiran", "Google Maps", "taska & tadika", "taska & tadika", False),
                    ("compare", "⚖️", "Compare", "Banding", x("Free – RM900 a month", "Percuma – RM900 sebulan"), "published fees + your quotes", "yuran diterbitkan + sebut harga anda", False),
                    ("help", "💸", "Help with fees", "Bantuan yuran", x("Up to RM180 a month", "Sehingga RM180 sebulan"), "subsidies & tax relief", "subsidi & pelepasan cukai", False),
                    ("guide", "📚", "Types & checks", "Jenis & semakan", x("Taska · Tadika", "Taska · Tadika"), "what to ask", "apa perlu ditanya", False)],
                prompt=x("Tap what you need:", "Pilih apa yang anda perlukan:"))}
<div class="dpanel" role="tabpanel" id="tp-nu-find" aria-labelledby="tb-nu-find" data-group="nu" data-tab="find">
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
</div>
<div class="dpanel" role="tabpanel" id="tp-nu-compare" aria-labelledby="tb-nu-compare" data-group="nu" data-tab="compare">
{nu_compare}
</div>
<div class="dpanel" role="tabpanel" id="tp-nu-help" aria-labelledby="tb-nu-help" data-group="nu" data-tab="help">
{nu_help}
</div>
<div class="dpanel" role="tabpanel" id="tp-nu-guide" aria-labelledby="tb-nu-guide" data-group="nu" data-tab="guide">
<h2>{x("Taska, tadika or preschool?", "Taska, tadika atau prasekolah?")}</h2>
{type_table}
<div class="acc-list">
<details class="acc"><summary>{x("Check before you choose", "Semak sebelum memilih")}</summary><ol>{ql}</ol></details>
<details class="acc"><summary>{x("Registration, complaints & tax relief", "Pendaftaran, aduan & pelepasan cukai")}</summary><ul>
<li>{x("The government's official list of registered taska:", "Senarai rasmi taska berdaftar:")}
<a href="https://www.malaysia.gov.my/my/personas/ibu-bapa-kepada-anak-kecil-0-6-tahun/menghantar-anak-ke-pusat-jagaan/taman-asuhan-kanak-kanak-taska" target="_blank" rel="noopener">MyGOV</a>.</li>
<li>{x("To report an unregistered taska, call Talian Kasih 15999 or your nearest welfare office.",
       "Untuk melaporkan taska tidak berdaftar, hubungi Talian Kasih 15999 atau pejabat kebajikan masyarakat terdekat.")}</li>
<li>{x("Fees paid to a registered taska or tadika for a child aged 6 or below get income tax relief of up to RM3,000 a year (Year of Assessment 2025) - see 'Help with fees'.",
       "Yuran taska atau tadika berdaftar untuk anak berumur 6 tahun ke bawah layak pelepasan cukai pendapatan sehingga RM3,000 setahun (Tahun Taksiran 2025) - lihat 'Bantuan yuran'.")}</li>
</ul></details>
</div>
</div>
{ad("in_content", x)}
{contact_cta(x, "Run a taska or tadika? Ask us about being listed here.", "Mengusahakan taska atau tadika? Tanya kami tentang penyenaraian di sini.")}
"""
    write_page(lang, "nursery.html", x("Find a taska or tadika near you", "Cari taska atau tadika berhampiran"),
               x("Find a taska (childcare centre) or tadika (kindergarten) near you in Malaysia, and the questions to ask before you choose.",
                 "Cari taska atau tadika berhampiran anda, dan soalan yang perlu ditanya sebelum memilih."),
               body, {"nu": NU})


def src_line(x, items):
    """'Sources:' line with links. items: [(label, url)]"""
    return (f'<p class="small muted src-line">{x("Sources", "Sumber")}: '
            + " · ".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(l)}</a>' for l, u in items)
            + f'. {x("General information only - follow your doctor or klinik.", "Maklumat umum sahaja - ikut nasihat doktor atau klinik anda.")}</p>')


def p_antenatal(lang):
    x = tr(lang)
    items = [[k, a, b, ico, x(en, ms), x(te, tm), ln] for k, a, b, ico, en, ms, te, tm, ln in tp.ANTENATAL]
    body = f"""
{page_head(x, "🩺", "t-ante", x("Pregnant", "Sedang hamil"), x("Antenatal check-ups", "Pemeriksaan antenatal"),
           x("Your klinik visits, tests and vaccines - with dates.", "Lawatan klinik, ujian dan vaksin anda - beserta tarikh."))}
<section class="card" id="ante-tool">
  <div class="due-row"><label class="field grow">{x("Your due date", "Tarikh jangkaan bersalin")}<input type="date" id="ante-due"></label></div>
  <div id="ante-result" aria-live="polite"></div>
  <p class="hint">{x("How often: once a month until 28 weeks, every 2 weeks from 28 to 35 weeks, then every week from 36 weeks. Tick each one when it's done - saved on this phone.",
                     "Kekerapan: sebulan sekali sehingga 28 minggu, setiap 2 minggu dari 28 hingga 35 minggu, kemudian setiap minggu dari 36 minggu. Tandakan setiap satu apabila selesai - disimpan dalam telefon ini.")}</p>
</section>
{danger(x)}
{ad("in_content", x)}
{src_line(x, [("KKM Perinatal Care Manual", "https://hq.moh.gov.my/bpkk/images/PERINATAL_CARE_MANUAL_4th_Edition_2020_11Mei2023.pdf"),
              ("MyHEALTH", "http://www.myhealth.gov.my/en/antenal-care/"),
              (x("KKM Tdap vaccine", "Vaksin Tdap KKM"), "https://www.moh.gov.my/images/kenyataan-media/2023/KENYATAAN_MEDIA_KKM_28_OGOS_2023_-_VAKSIN_TDAP_UNTUK_IBU_HAMIL.pdf")])}
"""
    write_page(lang, "antenatal.html", x("Antenatal check-up schedule Malaysia (KKM)", "Jadual pemeriksaan antenatal (KKM)"),
               x("When to see your klinik kesihatan in pregnancy: booking before 12 weeks, glucose test at 24-28 weeks, free Tdap vaccine at 28-32 weeks and more - with your dates.",
                 "Bila perlu ke klinik kesihatan semasa hamil: daftar sebelum 12 minggu, ujian glukosa 24-28 minggu, vaksin Tdap percuma 28-32 minggu dan lain-lain - beserta tarikh anda."),
               body, {"ante": items})


def p_healthy(lang):
    x = tr(lang)
    avoid = "".join(f"<li>{esc(x(e, m))}</li>" for e, m in tp.FOOD_AVOID)
    do = "".join(f"<li>{esc(x(e, m))}</li>" for e, m in tp.FOOD_DO)
    brk = "".join(f"<li>{esc(x(e, m))}</li>" for e, m in tp.FAST_BREAK)
    air = "".join(
        f'<article class="card air-card"><h3>✈️ {esc(n)}</h3><p><strong>{x("One baby", "Seorang bayi")}:</strong> {esc(x(se, sm))}</p>'
        f'<p><strong>{x("Twins or more", "Kembar atau lebih")}:</strong> {esc(x(me, mm))}</p><p>{esc(x(le, lm))}</p>'
        f'<p class="small muted"><a href="{esc(u)}" target="_blank" rel="noopener">{x("Airline page", "Laman syarikat penerbangan")} ↗</a> · {x("checked", "disemak")} {_dmy(c, lang)}</p></article>'
        for n, se, sm, me, mm, le, lm, u, c in tp.AIRLINES)
    tabs = tabbar(x, "hp", [
        ("food", "🥗", "Food", "Makanan", x("Eat & avoid", "Makan & elak"), "", "", False),
        ("fast", "🌙", "Fasting", "Puasa", x("Ramadan", "Ramadan"), "pregnant & breastfeeding", "hamil & menyusu", False),
        ("fly", "✈️", "Flying", "Terbang", x("Airline rules", "Peraturan"), "by week", "ikut minggu", False),
    ], hash_ok=True, prompt=x("What do you want to know?", "Apa yang anda mahu tahu?"))
    body = f"""
{page_head(x, "🥗", "t-healthy", x("Pregnant", "Sedang hamil"), x("Healthy pregnancy", "Penjagaan kesihatan semasa hamil"),
           x("Food, fasting and flying while you're pregnant.", "Makanan, puasa dan menaiki kapal terbang semasa hamil."))}
{tabs}
{tabpanel("hp", "food", f'''<section class="card"><h2>✅ {x("Do", "Amalkan")}</h2><ul>{do}</ul></section>
<section class="card"><h2>🚫 {x("Avoid or limit", "Elakkan atau hadkan")}</h2><ul>{avoid}</ul></section>
{src_line(x, [("MyHEALTH", "http://www.myhealth.gov.my/pemakanan-semasa-mengandung/"), (x("MyHEALTH cravings", "MyHEALTH mengidam"), "http://www.myhealth.gov.my/mengidam-semasa-mengandung/")])}''')}
{tabpanel("hp", "fast", f'''<section class="card"><h2>🩺 {x("Your health", "Kesihatan anda")}</h2>
<p>{x("Talk to your doctor before you fast - especially if you have diabetes, anaemia or another health problem. Between iftar and sahur, drink enough plain water.",
     "Berbincang dengan doktor sebelum berpuasa - terutama jika anda menghidap diabetes, anemia atau masalah kesihatan lain. Antara berbuka dan sahur, minum air kosong secukupnya.")}</p>
<p><strong>{x("Break your fast straight away if you have:", "Berbuka segera jika anda mengalami:")}</strong></p><ul>{brk}</ul></section>
<section class="card"><h2>🕌 {x("The ruling (Mufti of the Federal Territories)", "Hukum (Mufti Wilayah Persekutuan)")}</h2><ul>
<li>{x("Pregnant and breastfeeding mothers may skip fasting if they worry about their own health or their baby's.", "Ibu hamil dan menyusu boleh tidak berpuasa jika bimbang akan kesihatan diri atau bayi.")}</li>
<li>{x("Worried about yourself (or yourself and baby): replace the fast later (qada) - no fidyah.", "Bimbang akan diri sendiri (atau diri dan bayi): ganti puasa (qada) sahaja - tanpa fidyah.")}</li>
<li>{x("Worried about the baby only: qada and fidyah (the main Syafi'i view).", "Bimbang akan bayi sahaja: qada dan fidyah (pandangan muktamad mazhab Syafi'i).")}</li>
<li>{x("If pregnancy or breastfeeding delays your qada past next Ramadan, there's no extra fidyah for the delay.", "Jika hamil atau menyusu menyebabkan qada tertangguh melepasi Ramadan berikutnya, tiada fidyah tambahan kerana kelewatan itu.")}</li>
</ul><p class="small muted">{x("Scholars differ on some points - ask your state mufti or ustaz/ustazah.", "Terdapat perbezaan pandangan ulama - rujuk mufti negeri atau ustaz/ustazah anda.")}</p></section>
{src_line(x, [("MyHEALTH", "http://www.myhealth.gov.my/puasa-dan-ubat/"), ("Mufti WP Irsyad 31", "https://www.muftiwp.gov.my/ms/artikel/irsyad-hukum/umum/1969-31"),
              ("Mufti WP Irsyad 232", "https://www.muftiwp.gov.my/ms/artikel/irsyad-hukum/edisi-ramadhan/5594-irsyad-fatwa-edisi-khas-ramadhan-siri-ke-232-siapakah-golongan-yang-wajib-membayar-fidyah-puasa")])}''')}
{tabpanel("hp", "fly", f'''<p class="dp-intro">{x("Each airline has its own rules - check yours before you book, and carry your pink book.", "Setiap syarikat penerbangan ada peraturan sendiri - semak sebelum menempah, dan bawa buku pink anda.")}</p>
<div class="info-grid">{air}</div>
<p class="small muted">{x("Ask your doctor whether flying is safe for you, especially with complications or twins.", "Tanya doktor sama ada selamat untuk anda terbang, terutama jika ada komplikasi atau kembar.")}</p>''')}
{danger(x)}
{ad("in_content", x)}
"""
    write_page(lang, "healthy-pregnancy.html", x("Healthy pregnancy: food, fasting & flying", "Penjagaan kesihatan semasa hamil: makanan, puasa & terbang"),
               x("What to eat and avoid in pregnancy (KKM), fasting in Ramadan while pregnant or breastfeeding, and AirAsia and Malaysia Airlines rules for flying while pregnant.",
                 "Makanan yang perlu diambil dan dielak semasa hamil (KKM), puasa Ramadan ketika hamil atau menyusu, dan peraturan AirAsia serta Malaysia Airlines untuk ibu hamil."),
               body)


def p_budget(lang):
    x = tr(lang)
    with open(os.path.join(HERE, "site-data", "delivery.json"), encoding="utf-8") as f:
        DD = json.load(f)
    gov_min = DD["gov"]["delivery"]["normal"]["c3"] + 2 * DD["gov"]["ward_per_day"]["c3"][0]
    privs = sorted(h["price_from_rm"] for h in DD["private"])
    priv_mid = privs[len(privs) // 2]
    hctm = next(u for u in DD["university"] if u.get("fees"))
    uni = hctm["fees"]["normal"] + 2 * (hctm["fees"]["ward_per_day"] + hctm["fees"]["care_per_day"])
    try:
        with open(os.path.join(HERE, "site-data", "prices-summary.json"), encoding="utf-8") as f:
            PS = json.load(f)
        my = PS["areas"]["MY"]
        dp = sorted(my[c][0] / it["pc"] for c, it in PS["items"].items() if it["g"] == "diaper" and it.get("pc") and c in my)
        per_diaper = round(dp[len(dp) // 2], 2) if dp else 0.5
        tins = sorted(my[c][0] for c, it in PS["items"].items() if it["g"] == "infant" and c in my)
    except (OSError, ValueError, KeyError):
        per_diaper, tins = 0.5, []
    tin_hint = (x(f"A tin of Step 1 formula costs about {_rm(round(tins[0]))}-{_rm(round(tins[-1]))} in shops (KPDN survey).",
                  f"Setin susu formula Langkah 1 berharga lebih kurang {_rm(round(tins[0]))}-{_rm(round(tins[-1]))} di kedai (tinjauan KPDN).") if tins else "")
    def opt(v, en, ms):
        return f'<option value="{v}">{esc(x(en, ms))}</option>'
    body = f"""
{page_head(x, "🧾", "t-budget", x("Pregnant", "Sedang hamil"), x("Baby's first-year budget", "Anggaran belanja tahun pertama bayi"),
           x("Add up the big costs of baby's first year. Change any number - saved on this phone.", "Kira kos besar tahun pertama bayi. Ubah mana-mana angka - disimpan dalam telefon ini."))}
<section class="card" id="bud-tool">
  <div class="bud-grid">
    <label class="field">{x("Giving birth", "Bersalin")}<select name="deliv">
      {opt(gov_min, f"Government hospital, 3rd class - {_rm(gov_min)}", f"Hospital kerajaan, kelas 3 - {_rm(gov_min)}")}
      {opt(uni, f"University hospital, public ward - about {_rm(uni)}", f"Hospital universiti, wad awam - lebih kurang {_rm(uni)}")}
      {opt(priv_mid, f"Private hospital package - about {_rm(priv_mid)}", f"Pakej hospital swasta - lebih kurang {_rm(priv_mid)}")}
      {opt("custom", "My own amount", "Jumlah sendiri")}</select></label>
    <label class="field">{x("Confinement", "Berpantang")}<select name="conf">
      {opt(0, "At home with family - RM0", "Di rumah dengan keluarga - RM0")}
      {opt(7000, "Live-in nanny - about RM7,000", "Pengasuh tinggal bersama - lebih kurang RM7,000")}
      {opt(10500, "Budget centre - about RM10,500", "Pusat bajet - lebih kurang RM10,500")}
      {opt(15000, "Mid-range centre - about RM15,000", "Pusat pertengahan - lebih kurang RM15,000")}
      {opt("custom", "My own amount", "Jumlah sendiri")}</select></label>
    <label class="field bud-custom" data-for="deliv" hidden>{x("Birth cost (RM)", "Kos bersalin (RM)")}<input type="number" name="deliv_rm" min="0" inputmode="decimal"></label>
    <label class="field bud-custom" data-for="conf" hidden>{x("Confinement cost (RM)", "Kos berpantang (RM)")}<input type="number" name="conf_rm" min="0" inputmode="decimal"></label>
    <label class="field">{x("Diapers a day", "Lampin sehari")}<input type="number" name="dpd" min="0" max="15" value="6" inputmode="numeric"></label>
    <label class="field">{x("Price per diaper (RM)", "Harga selampin (RM)")}<input type="number" name="dprice" min="0" step="0.01" value="{per_diaper}" inputmode="decimal"></label>
    <label class="field">{x("Formula milk per month (RM, 0 if breastfeeding)", "Susu formula sebulan (RM, 0 jika menyusu badan)")}<input type="number" name="milk" min="0" value="0" inputmode="decimal"></label>
    <label class="field">{x("Baby items - cot, car seat, clothes (RM)", "Barang bayi - katil, kerusi kereta, pakaian (RM)")}<input type="number" name="items" min="0" value="0" inputmode="decimal"></label>
    <label class="field">{x("Childcare per month (RM)", "Taska sebulan (RM)")}<input type="number" name="care" min="0" value="0" inputmode="decimal"></label>
    <label class="field">{x("Months of childcare in year 1", "Bulan taska dalam tahun pertama")}<input type="number" name="care_m" min="0" max="12" value="9" inputmode="numeric"></label>
  </div>
  <p class="hint">{x(f"Diaper price {_rm(per_diaper)} = middle price per size-M diaper in Malaysian shops (KPDN survey). Vaccines are free at klinik kesihatan.",
                     f"Harga lampin {_rm(per_diaper)} = harga pertengahan selampin saiz M di kedai Malaysia (tinjauan KPDN). Vaksin percuma di klinik kesihatan.")} {esc(tin_hint)}</p>
  <div id="bud-result" aria-live="polite"></div>
</section>
<p class="tool-links"><a class="btn ghost" href="delivery-cost.html">🏥 {x("Delivery cost", "Kos bersalin")} →</a> <a class="btn ghost" href="confinement-cost.html">💰 {x("Confinement cost", "Kos berpantang")} →</a>
<a class="btn ghost" href="newborn.html">🧺 {x("Newborn essentials", "Barang bayi")} →</a> <a class="btn ghost" href="nursery.html">🧸 {x("Taska & tadika", "Taska & tadika")} →</a></p>
{ad("in_content", x)}
"""
    write_page(lang, "budget.html", x("Baby first-year budget calculator Malaysia", "Kalkulator anggaran belanja tahun pertama bayi"),
               x("How much does a baby cost in the first year in Malaysia? Add up delivery, confinement, diapers, milk, baby items and childcare - with real prices.",
                 "Berapa kos bayi pada tahun pertama di Malaysia? Kira kos bersalin, berpantang, lampin, susu, barang bayi dan taska - dengan harga sebenar."),
               body)


def p_feelings(lang):
    x = tr(lang)
    qs = []
    for i, (q, qms, ans) in enumerate(tp.EPDS, start=1):
        opts = "".join(
            f'<label class="epds-opt"><input type="radio" name="q{i}" value="{sc}"><span>{esc(a)}'
            + (f'<small>{esc(tp.EPDS_ANS_MS.get(a, ""))}</small>' if lang == "ms" else "") + "</span></label>"
            for a, sc in ans)
        qs.append(f'<fieldset class="epds-q"><legend><span class="epds-n">{i}</span> {esc(q)}'
                  + (f'<small>{esc(qms)}</small>' if lang == "ms" else "") + f"</legend>{opts}</fieldset>")
    body = f"""
{page_head(x, "💛", "t-mind", x("New mum", "Ibu baharu"), x("How are you feeling?", "Bagaimana perasaan anda?"),
           x("A short private check for postnatal depression. Nothing you tick is saved or sent anywhere.", "Semakan ringkas dan peribadi untuk kemurungan selepas bersalin. Apa yang anda tanda tidak disimpan atau dihantar ke mana-mana."))}
<aside class="box note"><p>{x("Feeling weepy or up and down in the first two weeks ('baby blues') is common. If it lasts longer than two weeks, or feels heavy, it may be postnatal depression - which is common and treatable.",
                              "Mudah menangis atau emosi turun naik dalam dua minggu pertama ('baby blues') adalah biasa. Jika lebih lama daripada dua minggu, atau terasa berat, ia mungkin kemurungan selepas bersalin - yang biasa dan boleh dirawat.")}</p></aside>
<form class="card" id="epds" onsubmit="return false">
  <p class="field-label">{x("Think about the past 7 days, not just today.", "Fikirkan tentang 7 hari yang lalu, bukan hari ini sahaja.")}
  {tip(x("These are the 10 questions of the Edinburgh Postnatal Depression Scale, used by KKM clinics. Questions are in the original English.", "Ini 10 soalan Skala Kemurungan Postnatal Edinburgh (EPDS) yang digunakan di klinik KKM. Soalan dalam Bahasa Inggeris asal, dengan maksud ringkas dalam BM."), x)}</p>
  {"".join(qs)}
  <div id="epds-result" aria-live="polite"></div>
</form>
<aside class="box danger"><h2>{x("Need help now?", "Perlukan bantuan sekarang?")}</h2><ul>
<li>{x("Thoughts of harming yourself or your baby: go to the nearest hospital emergency department or call 999.", "Terfikir untuk mencederakan diri atau bayi: pergi ke jabatan kecemasan hospital terdekat atau hubungi 999.")}</li>
<li>{x("Talk to someone: Talian HEAL 15555 (Ministry of Health).", "Bercakap dengan seseorang: Talian HEAL 15555 (Kementerian Kesihatan).")}</li>
<li>{x("Or see your klinik kesihatan or doctor - say how you've been feeling.", "Atau jumpa klinik kesihatan atau doktor - ceritakan perasaan anda.")}</li></ul></aside>
<p class="small muted">EPDS: Cox JL, Holden JM, Sagovsky R. Detection of postnatal depression: development of the 10-item Edinburgh Postnatal Depression Scale. British Journal of Psychiatry 1987;150:782-786.
{x("Score guide per KKM's depression guideline (2019).", "Panduan skor mengikut garis panduan kemurungan KKM (2019).")} <a href="https://www.moh.gov.my/images/04-penerbitan/penerbitan-klinikal/panduan-amalan-klinikal/CPG_Management_of_MDD_Second_Edition_04092020.pdf" target="_blank" rel="noopener">KKM CPG ↗</a>.
{x("This check is not a diagnosis.", "Semakan ini bukan diagnosis.")}</p>
"""
    write_page(lang, "feelings.html", x("Postnatal depression check (EPDS)", "Semakan kemurungan selepas bersalin (EPDS)"),
               x("A free, private 10-question check for postnatal depression (Edinburgh Postnatal Depression Scale), with where to get help in Malaysia.",
                 "Semakan 10 soalan percuma dan peribadi untuk kemurungan selepas bersalin (EPDS), serta tempat mendapatkan bantuan di Malaysia."),
               body)


def p_aqiqah(lang):
    x = tr(lang)
    steps = "".join(
        f'<li><label class="check"><input type="checkbox" data-key="aq_{k}"> {esc(x(en, ms))}</label>{tip(x(te, tm), x) if te else ""}</li>'
        for k, en, ms, te, tm in tp.AQIQAH_STEPS)
    body = f"""
<div data-store="tm_aqiqah" data-progress="{x("{n} of {t} done", "{n} daripada {t} selesai")}" data-done="{x("All done - alhamdulillah!", "Semua selesai - alhamdulillah!")}"></div>
{page_head(x, "🐐", "t-aqiqah", x("New mum", "Ibu baharu"), x("Aqiqah & cukur jambul", "Aqiqah & cukur jambul"),
           x("The dates, and what to prepare - for Muslim families.", "Tarikh dan persediaan - untuk keluarga Muslim."))}
<section class="card" id="aq-tool">
  <div class="due-row"><label class="field grow">{x("Baby's birth date", "Tarikh lahir bayi")}<input type="date" id="aq-birth"></label></div>
  <div id="aq-result" aria-live="polite"></div>
  <p class="hint">{x("The 7th day counts the day of birth as day 1. If you can't do it on the 7th day, the 14th or 21st day is fine.",
                     "Hari ketujuh dikira dengan hari lahir sebagai hari pertama. Jika tidak mampu pada hari ketujuh, boleh pada hari ke-14 atau ke-21.")}
  {tip(x("Some scholars count differently for a baby born at night - ask your local mosque or ustaz.", "Sesetengah ulama mengira berbeza bagi bayi yang lahir pada waktu malam - tanya masjid atau ustaz berhampiran."), x)}</p>
</section>
<div class="bag-progress card"><div class="bp-top"><strong id="bag-progress" aria-live="polite"></strong><button type="button" class="link-btn muted" id="bag-reset">{x("Untick everything", "Buang semua tanda")}</button></div>
<div class="progress"><span id="bag-bar" style="width:0%"></span></div></div>
<section class="card"><h2>🕌 {x("On the day", "Pada hari itu")}</h2><ul class="checklist">{steps}</ul></section>
{ad("in_content", x)}
{src_line(x, [("Mufti WP Irsyad 128", "https://www.muftiwp.gov.my/ms/artikel/irsyad-hukum/umum/1237-irsyad-al-fatwa-ke-128-adakah-cukup-aqiqah-seekor-kambing-bagi-bayi-lelaki"),
              ("Al-Kafi #1646", "https://muftiwp.gov.my/ms/artikel/al-kafi-li-al-fatawi/4292-al-kafi-1646-adakah-boleh-melakukan-aqiqah-pada-hari-ke-5-kelahiran-bayi"),
              ("Al-Kafi #1668", "https://www.muftiwp.gov.my/ms/artikel/al-kafi-li-al-fatawi/4346-al-kafi-1668-adakah-wujud-zakat-rambut-bayi"),
              ("Al-Kafi #1746", "https://muftiwp.gov.my/ms/artikel/al-kafi-li-al-fatawi/4590-al-kafi-1746-bolehkah-cukur-rambut-bayi-terlebih-dahulu-sebelum-melakukan-aqiqah")])}
"""
    write_page(lang, "aqiqah.html", x("Aqiqah & cukur jambul: dates and checklist", "Aqiqah & cukur jambul: tarikh dan senarai semak"),
               x("When to do aqiqah and cukur jambul (7th, 14th or 21st day), how many goats, and the gold or silver charity - from the Federal Territory Mufti's office.",
                 "Bila buat aqiqah dan cukur jambul (hari ke-7, 14 atau 21), berapa ekor kambing, dan sedekah emas atau perak - daripada Jabatan Mufti Wilayah Persekutuan."),
               body)


def p_jaundice(lang):
    x = tr(lang)
    urgent = "".join(f"<li>{esc(x(e, m))}</li>" for e, m in tp.JAUNDICE_URGENT)
    avoid = "".join(f"<li>{esc(x(e, m))}</li>" for e, m in tp.G6PD_AVOID)
    body = f"""
{page_head(x, "🟡", "t-jaun", x("New mum", "Ibu baharu"), x("Jaundice (kuning) & G6PD", "Kuning (jaundis) & G6PD"),
           x("What's normal, when to go back to the klinik, and what to avoid if your baby has G6PD deficiency.", "Apa yang normal, bila perlu ke klinik semula, dan apa yang perlu dielak jika bayi kekurangan G6PD."))}
<aside class="box danger"><h2>{x("Take your baby to a klinik or hospital straight away if:", "Bawa bayi ke klinik atau hospital segera jika:")}</h2><ul>{urgent}</ul>
<p>{x("Your risk is higher if an older child had severe jaundice - tell the nurse.", "Risiko lebih tinggi jika anak sebelum ini pernah kuning teruk - beritahu jururawat.")}</p></aside>
<section class="card"><h2>☀️ {x("Don't 'sun' your baby to treat jaundice", "Jangan 'jemur' bayi untuk merawat kuning")}</h2>
<p>{x("The Ministry of Health warns that keeping a baby out in the morning sun can harm them. Jaundice that needs treatment is treated in hospital under a special blue light (phototherapy).",
     "Kementerian Kesihatan mengingatkan bahawa mendedahkan bayi kepada cahaya matahari pagi secara berterusan boleh membahayakan bayi. Kuning yang perlu dirawat akan dirawat di hospital di bawah cahaya biru khas (fototerapi).")}</p></section>
<section class="card"><h2>🧬 G6PD</h2>
<p>{x("Every baby born in Malaysia is tested for G6PD deficiency using blood from the umbilical cord. It's lifelong but doesn't affect growth - your child just needs to avoid some things that can break down red blood cells:",
     "Setiap bayi yang lahir di Malaysia diuji untuk kekurangan G6PD menggunakan darah tali pusat. Ia kekal seumur hidup tetapi tidak menjejaskan tumbesaran - anak hanya perlu mengelakkan beberapa perkara yang boleh memecahkan sel darah merah:")}</p>
<ul>{avoid}</ul>
<p>{x("Keep breastfeeding - but if you're breastfeeding, avoid these things too, as small amounts can pass into breast milk.", "Teruskan menyusu - tetapi jika anda menyusu, elakkan juga perkara ini kerana sedikit boleh masuk ke dalam susu ibu.")}</p></section>
{ad("in_content", x)}
{src_line(x, [(x("MyHEALTH: jaundice", "MyHEALTH: kekuningan"), "http://www.myhealth.gov.my/kekuningan-pada-bayi-baru-lahir/"),
              (x("MyHEALTH: G6PD screening", "MyHEALTH: saringan G6PD"), "http://www.myhealth.gov.my/en/g6pd-screening-newborn/"),
              (x("MyHEALTH: G6PD deficiency", "MyHEALTH: kekurangan G6PD"), "http://myhealth.moh.gov.my/en/g6pd-deficiency-2/")])}
"""
    write_page(lang, "jaundice.html", x("Newborn jaundice (kuning) & G6PD in Malaysia", "Kuning (jaundis) bayi & G6PD"),
               x("Newborn jaundice: warning signs that need a klinik straight away, why sunbathing isn't a treatment, and what babies with G6PD deficiency must avoid - from KKM's MyHEALTH.",
                 "Kuning pada bayi baru lahir: tanda bahaya yang perlu ke klinik segera, mengapa menjemur bayi bukan rawatan, dan apa yang perlu dielak oleh bayi kekurangan G6PD - daripada MyHEALTH KKM."),
               body)


def p_growth(lang):
    x = tr(lang)
    with open(os.path.join(HERE, "site-data", "who-growth.json"), encoding="utf-8") as f:
        W = json.load(f)
    ms = "".join(
        f'<details class="acc"{" open" if i == 0 else ""}><summary>{m} {x("months", "bulan")}' + (f' ({m // 12} {x("year", "tahun") if m == 12 else x("years", "tahun")})' if m % 12 == 0 else "")
        + "</summary><ul>" + "".join(f"<li>{esc(x(e, mm))}</li>" for e, mm in its) + "</ul></details>"
        for i, (m, its) in enumerate(tp.MILESTONES))
    sleep_rows = "".join(f'<li><span>{esc(x(a, b))}</span><strong>{h} {x("hours", "jam")}</strong></li>' for a, b, h in tp.SLEEP)
    safe = "".join(f"<li>{esc(x(e, m))}</li>" for e, m in tp.SAFE_SLEEP)
    tabs = tabbar(x, "gr", [
        ("measure", "📏", "Weight & length", "Berat & panjang", x("WHO chart", "Carta WHO"), "0-2 years", "0-2 tahun", False),
        ("milestones", "🧩", "Milestones", "Perkembangan", x("2-24 months", "2-24 bulan"), "", "", False),
        ("sleep", "😴", "Sleep", "Tidur", x("Hours & safe sleep", "Jam & tidur selamat"), "", "", False),
    ], hash_ok=True, prompt=x("What do you want to check?", "Apa yang anda mahu semak?"))
    body = f"""
{page_head(x, "📈", "t-growth", x("Mum & kids", "Ibu & anak"), x("Baby's growth", "Tumbesaran bayi"),
           x("Weight and length on the WHO chart, milestones and sleep.", "Berat dan panjang pada carta WHO, perkembangan dan tidur."))}
{tabs}
{tabpanel("gr", "measure", f'''<section class="card" id="gr-tool">
  <p class="field-label">{x("Baby is a", "Bayi ialah")}</p>
  <div class="pill-group"><button type="button" class="pill-opt" data-sex="b" aria-pressed="true">👦 {x("Boy", "Lelaki")}</button><button type="button" class="pill-opt" data-sex="g" aria-pressed="false">👧 {x("Girl", "Perempuan")}</button></div>
  <div class="q-fields gr-fields">
    <label class="field">{x("Birth date", "Tarikh lahir")}<input type="date" id="gr-birth"></label>
    <label class="field">{x("Measured on", "Diukur pada")}<input type="date" id="gr-date"></label>
    <label class="field">{x("Weight (kg)", "Berat (kg)")}<input type="number" id="gr-w" min="1" max="25" step="0.01" inputmode="decimal" placeholder="7.5"></label>
    <label class="field">{x("Length (cm)", "Panjang (cm)")}<input type="number" id="gr-l" min="40" max="100" step="0.1" inputmode="decimal" placeholder="68"></label>
  </div>
  <button type="button" class="btn" id="gr-add">{x("Check and save", "Semak dan simpan")}</button>
  <div id="gr-result" aria-live="polite"></div>
  <p class="hint">{x("Compares with the WHO Child Growth Standards (birth to 2 years) - the same charts as your child's health book. Saved only on this phone.",
                     "Dibandingkan dengan Piawaian Tumbesaran Kanak-kanak WHO (lahir hingga 2 tahun) - carta yang sama dalam buku kesihatan anak anda. Disimpan dalam telefon ini sahaja.")}</p>
</section>''')}
{tabpanel("gr", "milestones", f'''<p class="dp-intro">{x("Things most children (3 in 4) can do by each age. If your child can't, has lost skills they had, or you're worried - don't wait: talk to your klinik or doctor.",
                                                    "Perkara yang kebanyakan kanak-kanak (3 daripada 4) boleh buat pada setiap umur. Jika anak anda belum boleh, hilang kemahiran yang pernah ada, atau anda risau - jangan tunggu: berbincang dengan klinik atau doktor.")}</p>
<div class="acc-list">{ms}</div>
{src_line(x, [("CDC Learn the Signs. Act Early.", "https://www.cdc.gov/act-early/milestones/index.html")])}''')}
{tabpanel("gr", "sleep", f'''<section class="card"><h2>🕒 {x("Sleep in 24 hours (including naps)", "Tidur dalam 24 jam (termasuk tidur siang)")}</h2><ul class="price-list">{sleep_rows}</ul>
<p class="small muted">{x("Recommended ranges - every baby is different.", "Julat yang disyorkan - setiap bayi berbeza.")}</p></section>
<section class="card"><h2>🛏️ {x("Safe sleep", "Tidur selamat")}</h2><ul>{safe}</ul></section>
{src_line(x, [("AASM 2016", "https://jcsm.aasm.org/doi/10.5664/jcsm.5866"), ("National Sleep Foundation", "https://www.thensf.org/how-many-hours-of-sleep-do-you-really-need/"),
              (x("MyHEALTH: baby sleep", "MyHEALTH: gaya tidur bayi"), "http://www.myhealth.gov.my/gaya-tidur-bayi/")])}''')}
{ad("in_content", x)}
"""
    write_page(lang, "growth.html", x("Baby growth chart (WHO), milestones & sleep", "Carta tumbesaran bayi (WHO), perkembangan & tidur"),
               x("Check your baby's weight and length on the WHO growth chart (0-2 years), see milestones by month, and how much sleep babies need.",
                 "Semak berat dan panjang bayi pada carta tumbesaran WHO (0-2 tahun), perkembangan mengikut bulan, dan berapa banyak tidur yang bayi perlukan."),
               body, {"who": {"w": W["weight"], "l": W["length"]}})


def p_solids(lang):
    x = tr(lang)
    rules = "".join(f"<li>{esc(x(e, m))}</li>" for e, m in tp.SOLIDS)
    body = f"""
{page_head(x, "🥣", "t-solids", x("Mum & kids", "Ibu & anak"), x("Baby's first foods", "Pengenalan makanan pejal"),
           x("Starting solids at 6 months - how much, what texture, and what to avoid.", "Mula makanan pejal pada 6 bulan - berapa banyak, tekstur dan apa yang perlu dielak."))}
<section class="card" id="sol-tool">
  <div class="due-row"><label class="field grow">{x("Baby's birth date", "Tarikh lahir bayi")}<input type="date" id="sol-birth"></label></div>
  <div id="sol-result" aria-live="polite"></div>
</section>
<section class="card"><h2>📋 {x("The basics (KKM)", "Asas (KKM)")}</h2><ul>{rules}</ul></section>
<p class="tool-links"><a class="btn ghost" href="prices.html#grp-food">🥣 {x("Baby food prices", "Harga makanan bayi")} →</a> <a class="btn ghost" href="growth.html">📈 {x("Baby's growth", "Tumbesaran bayi")} →</a></p>
{ad("in_content", x)}
{src_line(x, [(x("KKM infant feeding guideline", "Garis panduan pemakanan bayi KKM"), "https://hq.moh.gov.my/nutrition/wp-content/uploads/2023/12/GP_Baby_Book-1.pdf"),
              (x("KKM diet guide for children 2026", "Panduan diet kanak-kanak KKM 2026"), "https://hq.moh.gov.my/nutrition/wp-content/uploads/2026/09/4.-NOTA-POKET-PANDUAN-DIET-MALAYSIA-UNTUK-KANAK-KANAK-DAN-REMAJA-2026.pdf")])}
"""
    write_page(lang, "solids.html", x("Starting solids at 6 months (KKM guide)", "Pengenalan makanan pejal pada 6 bulan (panduan KKM)"),
               x("When and how to start solid food: 6 months, portions for 6-8 months, textures, and no salt, sugar, juice or honey before 1 year - from Malaysia's Ministry of Health.",
                 "Bila dan bagaimana mula makanan pejal: 6 bulan, sukatan untuk 6-8 bulan, tekstur, dan tiada garam, gula, jus atau madu sebelum 1 tahun - daripada Kementerian Kesihatan."),
               body)


def p_babylog(lang):
    x = tr(lang)
    btn = lambda k, ico, en, ms, cls="": f'<button type="button" class="log-btn {cls}" data-k="{k}"><span aria-hidden="true">{ico}</span>{esc(x(en, ms))}</button>'
    body = f"""
{page_head(x, "📝", "t-log", x("Mum & kids", "Ibu & anak"), x("Baby's daily log", "Rekod harian bayi"),
           x("Tap to record feeds, nappies and sleep. Saved only on this phone.", "Tekan untuk merekod susuan, lampin dan tidur. Disimpan dalam telefon ini sahaja."))}
<section class="card" id="log-tool">
  <p class="field-label">{x("Feed", "Susuan")}</p>
  <div class="log-grid">{btn("fl", "🤱", "Left breast", "Payudara kiri")}{btn("fr", "🤱", "Right breast", "Payudara kanan")}{btn("fb", "🍼", "Bottle", "Botol")}</div>
  <p class="field-label">{x("Nappy", "Lampin")}</p>
  <div class="log-grid">{btn("wet", "💧", "Wet", "Basah")}{btn("dirty", "💩", "Dirty", "Kotor (najis)")}</div>
  <p class="field-label">{x("Sleep", "Tidur")}</p>
  <div class="log-grid">{btn("sleep", "😴", "Fell asleep", "Mula tidur")}{btn("wake", "🌤️", "Woke up", "Bangun")}</div>
  <p class="hint" id="log-since" aria-live="polite"></p>
  <div class="log-nav"><button type="button" class="link-btn" id="log-prev" aria-label="{x("Previous day", "Hari sebelumnya")}">‹</button>
    <strong id="log-day"></strong><button type="button" class="link-btn" id="log-next" aria-label="{x("Next day", "Hari berikutnya")}">›</button></div>
  <div class="stats log-stats" id="log-sum"></div>
  <ul class="log-list" id="log-list"></ul>
  <p class="hint">{x("Tap ✕ to remove a mistake. Records older than 60 days are cleared automatically.", "Tekan ✕ untuk membuang kesilapan. Rekod lebih 60 hari dipadam secara automatik.")}</p>
</section>
<p class="tool-links"><a class="btn ghost" href="breastmilk.html">🤱 {x("Breastfeeding guide", "Panduan penyusuan")} →</a>
<a class="btn ghost" href="baby-health.html">🩺 {x("When to see the klinik", "Bila perlu ke klinik")} →</a></p>
{ad("in_content", x)}
"""
    write_page(lang, "baby-log.html", x("Baby feeding, nappy & sleep log", "Rekod susuan, lampin & tidur bayi"),
               x("A free baby tracker: tap to log breastfeeds, bottles, wet and dirty nappies and sleep - saved on your phone, no sign-up.",
                 "Penjejak bayi percuma: tekan untuk merekod susuan, botol, lampin basah dan kotor serta tidur - disimpan dalam telefon, tanpa daftar."),
               body)


def p_body(lang):
    x = tr(lang)
    sym = "".join(
        f'<details class="acc sym{" sym-urgent" if urg else ""}"><summary><span aria-hidden="true">{ico}</span> {esc(x(ne, nm))}</summary>'
        f'<p>{esc(x(te, tm))}</p><p class="sym-when"><strong>{x("See your klinik if:", "Jumpa klinik jika:")}</strong> {esc(x(we, wm))}</p></details>'
        for ico, ne, nm, te, tm, we, wm, urg in t2.SYMPTOMS)
    wg_rows = "".join(
        f'<tr><td>{x(lab_en, lab_ms)}</td><td>{band}</td><td class="num">{lo:g}–{hi:g} kg</td><td class="num">{wl:g}–{wh:g} kg</td></tr>'
        for (up, lo, hi, wl, wh, k), (lab_en, lab_ms, band) in zip(t2.WEIGHT_GAIN, [
            ("Underweight", "Kurang berat badan", "&lt;18.5"), ("Normal", "Normal", "18.5–24.9"),
            ("Overweight", "Lebih berat badan", "25.0–29.9"), ("Obese", "Obes", "≥30.0")]))
    food = "".join(f"<li>{esc(x(e, m))}</li>" for e, m in t2.IRON_FOOD)
    tabs = tabbar(x, "bd", [
        ("sym", "🤔", "Is this normal?", "Normalkah ini?", x("13 common symptoms", "13 simptom biasa"), "", "", False),
        ("weight", "⚖️", "Weight gain", "Kenaikan berat", x("Your healthy range", "Julat sihat anda"), "", "", False),
        ("hb", "🩸", "Low HB (anaemia)", "HB rendah (anemia)", x("Below 11 g/dL", "Bawah 11 g/dL"), "", "", False),
    ], hash_ok=True, prompt=x("What do you want to check?", "Apa yang anda mahu semak?"))
    body = f"""
{page_head(x, "🤰", "t-body", x("Pregnant", "Sedang hamil"), x("Body changes & symptoms", "Perubahan badan & simptom"),
           x("What's normal in pregnancy, and when to see your klinik.", "Apa yang normal semasa hamil, dan bila perlu ke klinik."))}
{tabs}
{tabpanel("bd", "sym", f'''<p class="dp-intro">{x("Tap a symptom for self-care tips and the signs that mean you should see your klinik. Red ones can be serious.", "Tekan simptom untuk tip penjagaan diri dan tanda yang perlu ke klinik. Yang merah boleh menjadi serius.")}</p>
<div class="acc-list">{sym}</div>
<p class="tool-links"><a class="btn ghost" href="labour.html">⏱️ {x("Kick counter", "Pengira tendangan")} →</a> <a class="btn ghost" href="antenatal.html">🩺 {x("Antenatal check-ups", "Pemeriksaan antenatal")} →</a></p>''')}
{tabpanel("bd", "weight", f'''<section class="card" id="wg-tool">
  <div class="q-fields gr-fields">
    <label class="field">{x("Height (cm)", "Tinggi (cm)")}<input type="number" id="wg-h" min="120" max="220" inputmode="decimal" placeholder="158"></label>
    <label class="field">{x("Weight before pregnancy (kg)", "Berat sebelum hamil (kg)")}<input type="number" id="wg-w0" min="30" max="200" step="0.1" inputmode="decimal" placeholder="55"></label>
    <label class="field">{x("Week now", "Minggu sekarang")}<input type="number" id="wg-wk" min="4" max="42" inputmode="numeric"></label>
    <label class="field">{x("Weight now (kg)", "Berat sekarang (kg)")}<input type="number" id="wg-w1" min="30" max="220" step="0.1" inputmode="decimal"></label>
  </div>
  <div id="wg-result" aria-live="polite"></div>
  <p class="hint">{x("Saved only on this phone. Your klinik weighs you at each visit - follow their advice.", "Disimpan dalam telefon ini sahaja. Klinik menimbang anda pada setiap lawatan - ikut nasihat mereka.")}</p>
</section>
<div class="table-wrap"><table class="wg-table"><thead><tr><th>{x("BMI before pregnancy", "BMI sebelum hamil")}</th><th></th><th class="num">{x("Whole pregnancy", "Sepanjang kehamilan")}</th><th class="num">{x("Per week (from week 13)", "Seminggu (dari minggu 13)")}</th></tr></thead><tbody>{wg_rows}</tbody></table></div>
<p class="small muted">{x("First 12 weeks: 0.5 - 2.0 kg for everyone. From KKM's Rekod Kesihatan Ibu (pink book), which uses the US Institute of Medicine 2009 guide.", "12 minggu pertama: 0.5 - 2.0 kg untuk semua. Daripada Rekod Kesihatan Ibu KKM (buku pink), berdasarkan panduan Institute of Medicine (AS) 2009.")}
<a href="{t2.KIK}" target="_blank" rel="noopener">KKM ↗</a></p>''')}
{tabpanel("bd", "hb", f'''<section class="card"><h2>{x("What the numbers mean", "Maksud bacaan HB")}</h2>
<ul class="price-list hb-list">
<li><span>{x("11 g/dL or more", "11 g/dL ke atas")}</span><strong>{x("Normal", "Normal")}</strong></li>
<li><span>9 – {x("below", "bawah")} 11</span><strong>{x("Mild anaemia", "Anemia ringan")}</strong></li>
<li><span>7 – {x("below", "bawah")} 9</span><strong>{x("Moderate", "Sederhana")}</strong></li>
<li><span>{x("Below 7", "Bawah 7")}</span><strong>{x("Severe - needs urgent care", "Teruk - perlu rawatan segera")}</strong></li></ul>
<p class="small muted">{x("From the HB chart in your pink book.", "Daripada carta HB dalam buku pink anda.")}</p></section>
<section class="card"><h2>{x("Signs", "Tanda-tanda")}</h2><p>{x("Feeling tired or weak, breathless, heart racing, light-headed, looking pale. Some mums have no signs - that's why the klinik checks your blood.",
                                                                                 "Letih atau lemah, sesak nafas, jantung berdebar, pening, kelihatan pucat. Sesetengah ibu tiada tanda - sebab itu klinik memeriksa darah anda.")}</p></section>
<section class="card"><h2>{x("What helps", "Apa yang membantu")}</h2><ul>
<li>{x("KKM recommends iron tablets for all pregnant mums - take them as your klinik tells you. If you're anaemic, your dose will be higher.", "KKM mengesyorkan pil zat besi untuk semua ibu hamil - ambil seperti yang diarahkan klinik. Jika anda anemia, dosnya lebih tinggi.")}</li>
<li>{x("Take iron tablets with or after food to reduce stomach upset. A glass of orange juice may help you absorb it.", "Ambil pil zat besi bersama atau selepas makan untuk mengurangkan rasa tidak selesa. Segelas jus oren boleh membantu penyerapan.")}</li>
<li>{x("Large amounts of tea, coffee and milk make iron harder to absorb - have them away from meals and tablets.", "Teh, kopi dan susu yang banyak menyukarkan penyerapan zat besi - ambil jauh dari waktu makan dan pil.")}</li>
<li>{x("Eat iron-rich food:", "Makan makanan kaya zat besi:")}<ul>{food}</ul></li></ul></section>''')}
{danger(x)}
{ad("in_content", x)}
{src_line(x, [(x("KKM Perinatal Care Manual", "Manual Penjagaan Perinatal KKM"), t2.PCM), (x("KKM pink book", "Buku pink KKM"), t2.KIK),
              ("NHS: common symptoms", "https://www.nhs.uk/pregnancy/common-symptoms/"), ("NHS: anaemia", "https://www.nhs.uk/conditions/iron-deficiency-anaemia/")])}
"""
    write_page(lang, "pregnancy-body.html", x("Pregnancy symptoms, weight gain & low HB", "Simptom kehamilan, kenaikan berat badan & HB rendah"),
               x("Is it normal? Morning sickness, heartburn, back pain, swelling, bleeding and more - with when to see your klinik. Plus KKM's healthy weight-gain ranges and what low HB means.",
                 "Normalkah? Alahan, pedih ulu hati, sakit belakang, bengkak, pendarahan dan lain-lain - serta bila perlu ke klinik. Juga julat kenaikan berat badan sihat KKM dan maksud HB rendah."),
               body, {"wg": [list(r) for r in t2.WEIGHT_GAIN]})


def p_recovery(lang):
    x = tr(lang)
    red = "".join(f"<li>{esc(x(e, m))}</li>" for e, m in t2.POSTNATAL_RED)
    tabs = tabbar(x, "rc", [
        ("body", "🩹", "Your body", "Badan anda", x("Bleeding, stitches, pelvic floor", "Darah nifas, jahitan, otot pelvis"), "", "", False),
        ("visits", "🏥", "Check-ups", "Pemeriksaan", x("Home visits & 1 month", "Lawatan rumah & 1 bulan"), "", "", False),
        ("family", "💞", "Sex & family planning", "Hubungan & perancang keluarga", x("You can get pregnant again soon", "Anda boleh hamil semula dengan cepat"), "", "", False),
    ], hash_ok=True, prompt=x("What do you want to know?", "Apa yang anda mahu tahu?"))
    body = f"""
{page_head(x, "🌷", "t-recover", x("New mum", "Ibu baharu"), x("Recovering after birth", "Pemulihan selepas bersalin"),
           x("How your body heals, your check-ups, and planning your family.", "Bagaimana badan pulih, pemeriksaan anda, dan merancang keluarga."))}
<aside class="box danger"><h2>{x("Go to hospital straight away if you have:", "Pergi ke hospital segera jika anda mengalami:")}</h2><ul>{red}</ul>
<p>{x("Feeling very low, or thoughts of harming yourself or your baby:", "Berasa sangat sedih, atau terfikir untuk mencederakan diri atau bayi:")} <a href="feelings.html">{x("get help now", "dapatkan bantuan sekarang")}</a> · <strong>999</strong> · Talian HEAL 15555</p></aside>
{tabs}
{tabpanel("rc", "body", f'''<section class="card"><h2>🩸 {x("Bleeding after birth (nifas)", "Darah nifas")}</h2>
<p>{x("Bleeding carries on for a few weeks, gradually turns brownish and gets less until it stops - usually by 6 to 8 weeks. Tell your nurse if you pass large clots.", "Pendarahan berterusan selama beberapa minggu, beransur-ansur menjadi keperangan dan berkurang sehingga berhenti - biasanya dalam 6 hingga 8 minggu. Beritahu jururawat jika keluar ketulan darah yang besar.")}</p></section>
<section class="card"><h2>✂️ {x("Caesarean wound", "Luka pembedahan caesarean")}</h2>
<p>{x("Gently clean and dry the wound every day. Take things slowly - lifting heavy things and driving may need to wait about 6 weeks. See your klinik straight away if the wound gets redder, more painful or swollen, or leaks pus or bad-smelling fluid.", "Bersihkan dan keringkan luka dengan lembut setiap hari. Bertenang - mengangkat barang berat dan memandu mungkin perlu ditangguh lebih kurang 6 minggu. Jumpa klinik segera jika luka semakin merah, sakit atau bengkak, atau mengeluarkan nanah atau cecair berbau busuk.")}</p></section>
<section class="card"><h2>💪 {x("Pelvic floor exercises", "Senaman otot pelvis")}</h2><ol>
<li>{x("Squeeze the muscles you'd use to stop a wee - try not to pull your tummy in.", "Kemut otot yang digunakan untuk menahan kencing - cuba jangan tarik perut ke dalam.")}</li>
<li>{x("Hold for 2 seconds, then relax. Repeat 10 times, breathing normally.", "Tahan 2 saat, kemudian lepaskan. Ulang 10 kali sambil bernafas seperti biasa.")}</li>
<li>{x("Slowly build up to holding for 10 seconds. It can take a few months to help.", "Tingkatkan perlahan-lahan sehingga dapat menahan 10 saat. Ia mungkin mengambil masa beberapa bulan untuk membantu.")}</li></ol>
<p class="small muted">{x("Still leaking urine? Tell the doctor at your postnatal check.", "Masih terkencing? Beritahu doktor semasa pemeriksaan selepas bersalin.")}</p></section>''')}
{tabpanel("rc", "visits", f'''<section class="card"><h2>{x("Your postnatal care", "Penjagaan selepas bersalin anda")}</h2>
<p>{x("A nurse from the klinik kesihatan visits you at home regularly after you give birth. You also need a check-up at the klinik kesihatan one month after the birth.", "Jururawat klinik kesihatan akan membuat lawatan ke rumah secara berkala selepas anda bersalin. Anda juga perlu membuat pemeriksaan di klinik kesihatan sebulan selepas bersalin.")}</p>
<p>{x("At the visits they check your bleeding, your blood pressure, your wound and stitches, breastfeeding and how you're feeling - and look at your baby too.", "Semasa lawatan, mereka memeriksa darah nifas, tekanan darah, luka dan jahitan, penyusuan dan perasaan anda - serta bayi anda.")}</p>
<p>{x("Tell them about anything that worries you - even if it seems small.", "Beritahu mereka apa sahaja yang membimbangkan anda - walaupun nampak kecil.")}</p></section>''')}
{tabpanel("rc", "family", f'''<section class="card"><h2>{x("You can get pregnant before your first period", "Anda boleh hamil sebelum haid pertama")}</h2>
<p>{x("KKM says mums can become pregnant again even before their first period, and breastfeeding is not a reliable form of birth control. Get advice on family planning within one month of the birth at your klinik.", "KKM menyatakan ibu boleh hamil semula walaupun sebelum haid pertama, dan penyusuan susu ibu bukan cara mencegah kehamilan yang boleh dipercayai. Dapatkan nasihat perancang keluarga dalam masa sebulan selepas bersalin di klinik.")}</p>
<p>{x("Sex can start again once the bleeding has stopped and any stitches have healed - usually 4 to 6 weeks after the birth.", "Hubungan suami isteri boleh disambung semula selepas darah nifas berhenti dan jahitan sembuh - biasanya 4 hingga 6 minggu selepas bersalin.")}</p></section>
<section class="card"><h2>{x("Where to get help", "Di mana mendapatkan bantuan")}</h2>
<p>{x("Your klinik kesihatan, or LPPKN (National Population and Family Development Board), offers family planning advice and methods such as pills, injections, implants and IUDs.", "Klinik kesihatan, atau LPPKN (Lembaga Penduduk dan Pembangunan Keluarga Negara), menawarkan nasihat perancang keluarga dan kaedah seperti pil, suntikan, implan dan IUD.")}</p>
<a class="btn ghost" href="https://www.malaysia.gov.my/en/categories/family-institution/-family-planning" target="_blank" rel="noopener">MyGOV ↗</a></section>''')}
{ad("in_content", x)}
{src_line(x, [(x("KKM Perinatal Care Manual", "Manual Penjagaan Perinatal KKM"), t2.PCM), ("MyGOV", t2.MYGOV_POSTNATAL),
              ("NHS: your body after birth", "https://www.nhs.uk/pregnancy/labour-and-birth/your-body/"), ("NHS: caesarean recovery", "https://www.nhs.uk/tests-and-treatments/caesarean-section/recovery/")])}
"""
    write_page(lang, "recovery.html", x("Recovering after birth: bleeding, stitches & check-ups", "Pemulihan selepas bersalin: darah nifas, jahitan & pemeriksaan"),
               x("How long bleeding lasts after birth, caesarean wound care, pelvic floor exercises, KKM postnatal visits, family planning - and the warning signs that need a hospital.",
                 "Berapa lama darah nifas, penjagaan luka caesarean, senaman otot pelvis, lawatan postnatal KKM, perancang keluarga - dan tanda bahaya yang perlu ke hospital."),
               body)


def _lis(x, items):
    return "".join(f"<li>{esc(x(e, m))}</li>" for e, m in items)


def p_babyhealth(lang):
    x = tr(lang)
    urgent = _lis(x, [
        ("Blue, grey or very pale lips or tongue", "Bibir atau lidah biru, kelabu atau sangat pucat"),
        ("A fit (seizure)", "Sawan"),
        ("Very sleepy, floppy or hard to wake", "Sangat mengantuk, lembik atau susah dikejutkan"),
        ("Breathing very fast or struggling to breathe", "Bernafas sangat laju atau susah bernafas"),
        ("Not feeding, or vomiting green fluid, or a swollen tummy", "Tidak mahu menyusu, muntah cecair hijau, atau perut kembung"),
        ("A rash that doesn't fade when you press a glass on it", "Ruam yang tidak hilang apabila ditekan dengan gelas"),
        ("Dry nappies, sunken eyes or no tears when crying", "Lampin kering, mata cengkung atau menangis tanpa air mata"),
        ("Under 3 months old with a temperature of 38°C or higher", "Bayi bawah 3 bulan dengan suhu 38°C atau lebih"),
    ])
    tabs = tabbar(x, "bh", [
        ("fever", "🌡️", "Fever", "Demam", "38°C+", "", "", False),
        ("cry", "😭", "Crying & colic", "Menangis & kolik", x("Never shake", "Jangan goncang"), "", "", False),
        ("poo", "💩", "Poo & pee", "Najis & air kencing", x("Pale poo = klinik", "Najis pucat = klinik"), "", "", False),
        ("rash", "🧷", "Nappy rash", "Ruam lampin", x("Zinc cream", "Krim zink"), "", "", False),
        ("teeth", "🦷", "Teething", "Tumbuh gigi", x("Around 6 months", "Sekitar 6 bulan"), "", "", False),
    ], hash_ok=True, prompt=x("What's worrying you?", "Apa yang membimbangkan anda?"))
    body = f"""
{page_head(x, "🩺", "t-bhealth", x("Mum & kids", "Ibu & anak"), x("Baby health: when to see the klinik", "Kesihatan bayi: bila perlu ke klinik"),
           x("Fever, crying, poo, rashes and teething - what's normal and what isn't.", "Demam, menangis, najis, ruam dan tumbuh gigi - apa yang normal dan apa yang tidak."))}
<aside class="box danger"><h2>{x("Go to hospital now, or call 999, if your baby has:", "Pergi ke hospital sekarang, atau hubungi 999, jika bayi anda:")}</h2><ul>{urgent}</ul>
<p>{x("Trust your instinct - if you feel something is seriously wrong, get help.", "Percayai naluri anda - jika anda rasa ada sesuatu yang tidak kena, dapatkan bantuan.")}</p></aside>
{tabs}
{tabpanel("bh", "fever", f'''<section class="card"><ul>
<li>{x("A high temperature is 38°C or more. Measure it under the armpit with a digital thermometer.", "Suhu tinggi ialah 38°C atau lebih. Ukur di bawah ketiak dengan termometer digital.")}</li>
<li><strong>{x("Under 3 months and 38°C or more: go to a klinik or hospital now.", "Bawah 3 bulan dan 38°C atau lebih: pergi ke klinik atau hospital sekarang.")}</strong></li>
<li>{x("3 to 6 months and 39°C or more: see a doctor today.", "3 hingga 6 bulan dan 39°C atau lebih: jumpa doktor hari ini.")}</li>
<li>{x("A fever that lasts 5 days or more needs a doctor.", "Demam yang berlarutan 5 hari atau lebih perlu jumpa doktor.")}</li>
<li>{x("Keep breastfeeding or giving fluids. Don't undress your baby or sponge them down to cool them.", "Teruskan menyusu atau beri cecair. Jangan buka semua pakaian bayi atau lap badannya untuk menyejukkan.")}</li>
<li>{x("If your baby has a fit with the fever, go to hospital.", "Jika bayi sawan semasa demam, pergi ke hospital.")}</li></ul></section>''')}
{tabpanel("bh", "cry", f'''<section class="card"><h2>{x("Colic", "Kolik")}</h2>
<p>{x("Colic is common - KKM says it affects 10-25% of newborns. It usually starts at about 2 weeks and should settle by 4 months.", "Kolik adalah biasa - KKM menyatakan ia berlaku kepada 10-25% bayi baru lahir. Biasanya bermula sekitar 2 minggu dan sepatutnya reda menjelang 4 bulan.")}</p>
<ul><li>{x("Hold your baby upright during feeds, and burp them after.", "Pegang bayi dalam keadaan tegak semasa menyusu, dan sendawakan selepas itu.")}</li>
<li>{x("Try swaddling, walking with your baby on your shoulder, or gentle rocking.", "Cuba bedung, berjalan sambil bayi di bahu, atau buai perlahan-lahan.")}</li></ul></section>
<aside class="box danger"><h2>{x("Never shake a baby", "Jangan sekali-kali menggoncang bayi")}</h2>
<p>{x("Shaking can cause serious brain injury or death. If you feel stressed or angry, put your baby somewhere safe, like their cot, and step away for a few minutes. If you can't cope or your baby can't be comforted, go to your klinik or hospital.",
     "Menggoncang boleh menyebabkan kecederaan otak yang serius atau kematian. Jika anda rasa tertekan atau marah, letakkan bayi di tempat selamat seperti katilnya dan beredar seketika. Jika anda tidak dapat menghadapinya atau bayi tidak dapat ditenangkan, pergi ke klinik atau hospital.")}</p>
<p>{x("A weak, high-pitched or unusual cry: see a doctor urgently.", "Tangisan yang lemah, nyaring atau luar biasa: jumpa doktor segera.")}</p></aside>''')}
{tabpanel("bh", "poo", f'''<section class="card"><ul>
<li>{x("Breastfed babies usually have soft yellow poo - often several times a day in the first weeks.", "Bayi yang menyusu badan biasanya membuang najis kuning yang lembut - selalunya beberapa kali sehari pada minggu-minggu awal.")}</li>
<li><strong>{x("Pale, white or clay-coloured poo, or dark yellow or brown pee: see your klinik straight away.", "Najis pucat, putih atau seperti tanah liat, atau air kencing kuning pekat atau perang: jumpa klinik segera.")}</strong>
{x("It can be a sign of a liver problem (biliary atresia) - KKM says babies with it need to see a surgeon before 2 months of age. Take a photo or keep a nappy to show the doctor.", "Ia mungkin tanda masalah hati (atresia biliari) - KKM menyatakan bayi dengan masalah ini perlu berjumpa pakar bedah sebelum umur 2 bulan. Ambil gambar atau simpan lampin untuk ditunjukkan kepada doktor.")}</li>
<li>{x("Green vomit, blood in poo, or fewer wet nappies than usual: see a doctor today.", "Muntah hijau, darah dalam najis, atau lampin basah kurang daripada biasa: jumpa doktor hari ini.")}</li></ul>
<p class="tool-links"><a class="btn ghost" href="jaundice.html">🟡 {x("Jaundice (kuning)", "Kuning (jaundis)")} →</a> <a class="btn ghost" href="baby-log.html">📝 {x("Count nappies", "Kira lampin")} →</a></p></section>''')}
{tabpanel("bh", "rash", f'''<section class="card"><ul>
<li>{x("Change nappies often, and clean the skin with warm water after each wee or poo.", "Tukar lampin dengan kerap, dan bersihkan kulit dengan air suam setiap kali bayi kencing atau membuang air besar.")}</li>
<li>{x("Protect the skin with a barrier cream containing zinc oxide.", "Lindungi kulit dengan krim pelindung yang mengandungi zink oksida.")}</li>
<li>{x("Avoid wipes with alcohol, baby powder or cornstarch, and steroid creams.", "Elakkan tisu basah beralkohol, bedak bayi atau tepung jagung, dan krim steroid.")}</li>
<li>{x("A moist red rash with little white or yellow spots may be thrush (a fungal rash) - it needs an antifungal cream from your klinik.", "Ruam merah yang lembap dengan bintik putih atau kuning mungkin jangkitan kulat - perlu krim antikulat daripada klinik.")}</li>
<li>{x("See your klinik if it doesn't go away, spreads, or your baby has a fever.", "Jumpa klinik jika ruam tidak hilang, merebak, atau bayi demam.")}</li></ul></section>''')}
{tabpanel("bh", "teeth", f'''<section class="card"><ul>
<li>{x("Most babies start teething at around 6 months.", "Kebanyakan bayi mula tumbuh gigi sekitar umur 6 bulan.")}</li>
<li>{x("Their temperature may rise a little, but teething doesn't cause a high fever (38°C or more) - if your baby has one, look for another cause.", "Suhu badan mungkin naik sedikit, tetapi tumbuh gigi tidak menyebabkan demam tinggi (38°C atau lebih) - jika bayi demam tinggi, mungkin ada punca lain.")}</li>
<li>{x("A teething ring (cooled in the fridge, never the freezer), cuddles and play can help.", "Gelang gigitan (disejukkan dalam peti sejuk, bukan peti beku), pelukan dan bermain boleh membantu.")}</li>
<li><strong>{x("Never tie anything around your baby's neck - including teething necklaces. It's a choking risk.", "Jangan ikat apa-apa di leher bayi - termasuk rantai tumbuh gigi. Ia boleh menyebabkan tercekik.")}</strong></li>
<li>{x("Pain-relief gels for adults aren't suitable for babies - ask your pharmacist.", "Gel penahan sakit untuk orang dewasa tidak sesuai untuk bayi - tanya ahli farmasi.")}</li></ul></section>''')}
{ad("in_content", x)}
{src_line(x, [(x("KKM Perinatal Care Manual", "Manual Penjagaan Perinatal KKM"), t2.PCM), ("NHS: fever in children", "https://www.nhs.uk/conditions/fever-in-children/"),
              ("NHS: colic", "https://www.nhs.uk/conditions/colic/"), ("NHS: teething", "https://www.nhs.uk/baby/babys-development/teething/tips-for-helping-your-teething-baby/")])}
"""
    write_page(lang, "baby-health.html", x("Baby fever, crying, poo & rashes: when to see the klinik", "Demam, tangisan, najis & ruam bayi: bila perlu ke klinik"),
               x("When a baby's fever needs a doctor, colic and never shaking a baby, pale poo, nappy rash and teething - with the danger signs that need a hospital.",
                 "Bila demam bayi perlu doktor, kolik dan jangan menggoncang bayi, najis pucat, ruam lampin dan tumbuh gigi - serta tanda bahaya yang perlu ke hospital."),
               body)


def p_safety(lang):
    x = tr(lang)
    tabs = tabbar(x, "sf", [
        ("car", "🚗", "Car seats", "Kerusi keselamatan kereta", x("The law since 2020", "Undang-undang sejak 2020"), "", "", False),
        ("home", "🏠", "At home", "Di rumah", x("Falls, burns, water", "Jatuh, melecur, air"), "", "", False),
        ("choke", "🆘", "Choking", "Tercekik", x("Baby under 1", "Bayi bawah 1 tahun"), "", "", False),
    ], hash_ok=True, prompt=x("What do you want to check?", "Apa yang anda mahu semak?"))
    body = f"""
{page_head(x, "🛡️", "t-safety", x("Mum & kids", "Ibu & anak"), x("Child safety", "Keselamatan kanak-kanak"),
           x("Car seats, a safer home, and what to do if your baby chokes.", "Kerusi keselamatan kereta, rumah yang lebih selamat, dan apa perlu dibuat jika bayi tercekik."))}
{tabs}
{tabpanel("sf", "car", f'''<section class="card"><h2>{x("Malaysia's car seat law", "Undang-undang kerusi keselamatan kanak-kanak")}</h2><ul>
<li>{x("Since 1 January 2020, child car seats have been compulsory in private cars.", "Sejak 1 Januari 2020, kerusi keselamatan kanak-kanak diwajibkan dalam kenderaan persendirian.")}</li>
<li>{x("Every child passenger under 12 years old, under 36 kg and under 136 cm must use one.", "Setiap penumpang kanak-kanak bawah 12 tahun, kurang 36 kg dan kurang 136 cm wajib menggunakannya.")}</li>
<li>{x("The seat must meet UN Regulation R44 or R129 - look for the label.", "Kerusi mesti mematuhi Peraturan PBB R44 atau R129 - cari labelnya.")}</li>
<li>{x("Never put a rear-facing seat in front of a passenger airbag that is switched on.", "Jangan letak kerusi menghadap belakang di hadapan beg udara penumpang yang aktif.")}</li>
<li>{x("Keep your baby rear-facing for as long as they fit the seat.", "Kekalkan bayi menghadap belakang selagi muat dalam kerusi itu.")}</li></ul>
<a class="btn ghost" href="https://www.jpj.gov.my/en/child-restraint-system-crs/" target="_blank" rel="noopener">JPJ ↗</a></section>
<aside class="box danger"><h2>{x("Never leave a child alone in a car", "Jangan sekali-kali tinggalkan kanak-kanak seorang diri dalam kereta")}</h2><ul>
<li>{x("Don't put your baby directly behind the driver's seat - it's a blind spot.", "Jangan letak bayi betul-betul di belakang kerusi pemandu - ia titik buta.")}</li>
<li>{x("Put your handbag or phone in the back, and your baby's bag on the front seat, as a reminder.", "Letak beg tangan atau telefon di belakang, dan beg keperluan bayi di kerusi hadapan, sebagai peringatan.")}</li>
<li>{x("If you see a child left alone in a car, report it straight away.", "Jika anda nampak kanak-kanak ditinggalkan dalam kereta, laporkan segera.")}</li></ul></aside>''')}
{tabpanel("sf", "home", f'''<section class="card"><ul>
<li>{x("Never leave your baby alone on a bed, sofa or changing table - even for a second.", "Jangan tinggalkan bayi seorang diri di atas katil, sofa atau meja salin lampin - walaupun sesaat.")}</li>
<li>{x("Use safety gates at the top and bottom of stairs until at least 2 years old.", "Guna pagar keselamatan di atas dan bawah tangga sehingga sekurang-kurangnya umur 2 tahun.")}</li>
<li>{x("Fit window locks that open less than 6.5 cm, and move furniture away from windows.", "Pasang kunci tingkap yang terbuka kurang daripada 6.5 cm, dan jauhkan perabot dari tingkap.")}</li>
<li>{x("Bath time: run cold water first, then add hot. Stay with your baby the whole time - babies can drown in 5 cm of water. Empty baths, buckets and basins after use.", "Waktu mandi: masukkan air sejuk dahulu, kemudian air panas. Sentiasa bersama bayi - bayi boleh lemas dalam air sedalam 5 cm. Kosongkan tab mandi, baldi dan besen selepas digunakan.")}</li>
<li>{x("A hot drink can still scald 15 minutes after it's made. Keep children away from the stove, hot water and electrical items.", "Minuman panas masih boleh melecurkan 15 minit selepas dibuat. Jauhkan kanak-kanak dari dapur, air panas dan barang elektrik.")}</li>
<li>{x("Lock medicines and cleaning products away, high up.", "Simpan ubat-ubatan dan bahan pencuci di tempat tinggi dan berkunci.")}</li>
<li>{x("Keep buttons, coins and small toy parts out of reach. Button batteries can cause severe internal burns if swallowed - go to hospital immediately if you think one was swallowed.", "Jauhkan butang, syiling dan bahagian kecil mainan. Bateri butang boleh menyebabkan lecur dalaman yang teruk jika tertelan - pergi ke hospital segera jika anda rasa ia tertelan.")}</li></ul></section>''')}
{tabpanel("sf", "choke", f'''<section class="card"><h2>{x("If a baby under 1 is choking", "Jika bayi bawah 1 tahun tercekik")}</h2><ol>
<li>{x("Back blows: lay your baby face down along your thigh or forearm, supporting their head. Give up to 5 firm blows between the shoulder blades.", "Tepukan belakang: tiarapkan bayi di atas paha atau lengan anda sambil menyokong kepalanya. Beri sehingga 5 tepukan kuat di antara tulang belikat.")}</li>
<li>{x("Chest thrusts: turn your baby face up. Put 2 fingers in the middle of the chest, just below the nipple line, and give up to 5 sharp pushes.", "Tekanan dada: telentangkan bayi. Letak 2 jari di tengah dada, betul-betul di bawah garisan puting, dan beri sehingga 5 tekanan pantas.")}</li>
<li>{x("Repeat. Call 999 if the object doesn't come out. If your baby becomes unresponsive, call 999 and start CPR.", "Ulang. Hubungi 999 jika benda itu tidak keluar. Jika bayi tidak memberi respons, hubungi 999 dan mulakan CPR.")}</li></ol>
<p class="small muted">{x("A first aid course teaches you this hands-on - worth doing before your baby starts eating solids.", "Kursus pertolongan cemas mengajar cara ini secara praktikal - elok dihadiri sebelum bayi mula makan makanan pejal.")}</p></section>''')}
{ad("in_content", x)}
{src_line(x, [("JPJ", "https://www.jpj.gov.my/en/child-restraint-system-crs/"), ("KPWKM", "https://www.kpwkm.gov.my/uploads/content-downloads/file_20250105145431.pdf"),
              ("NHS: baby safety", "https://www.nhs.uk/baby/first-aid-and-safety/safety/baby-and-toddler-safety/"), ("NHS: choking", "https://www.nhs.uk/baby/first-aid-and-safety/first-aid/how-to-stop-a-child-from-choking/")])}
"""
    write_page(lang, "safety.html", x("Child car seat law Malaysia, home safety & choking", "Undang-undang kerusi keselamatan kanak-kanak, keselamatan rumah & tercekik"),
               x("Malaysia's child car seat rules (JPJ), never leaving a child in a car, baby-proofing your home, and first aid for a choking baby.",
                 "Peraturan kerusi keselamatan kanak-kanak (JPJ), jangan tinggalkan anak dalam kereta, keselamatan rumah, dan pertolongan cemas bayi tercekik."),
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
        p_afterbirth(lang)
        p_antenatal(lang)
        p_healthy(lang)
        p_budget(lang)
        p_feelings(lang)
        p_aqiqah(lang)
        p_jaundice(lang)
        p_growth(lang)
        p_solids(lang)
        p_babylog(lang)
        p_body(lang)
        p_recovery(lang)
        p_babyhealth(lang)
        p_safety(lang)
        p_delivery(lang)
        p_planning(lang)
    root_files()
    print(f"built {len(WRITTEN)} pages into {OUT}" + (" (ad preview)" if AD_PREVIEW else ""))


if __name__ == "__main__":
    main()
