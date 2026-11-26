"""Content for the extra mum tools (English + Bahasa Melayu).

Sources (checked 26 Nov 2026):
- Vaccines: KKM National Immunisation Programme (BCG + Hep B at birth; MMR at 9 & 12 months; pneumococcal at
  4 & 6 months + booster 15 months per KKM press statement 24 Nov 2020; 6-in-1 at 2, 3, 5 months + booster 18 months).
  Always defer to the child's health record book - ages can differ by state/clinic.
- Breast milk storage: KKM Bahagian Pemakanan poster "Penyusuan Susu Ibu (Ibu Bekerja)" (hq.moh.gov.my/nutrition).
"""

# (age in months, vaccine EN, vaccine MS, note EN, note MS)
VACCINES = [
    (0, "BCG (tuberculosis)", "BCG (tibi)", "", ""),
    (0, "Hepatitis B - dose 1", "Hepatitis B - dos 1", "", ""),
    (2, "6-in-1 (DTaP-IPV-Hib-HepB) - dose 1", "6-dalam-1 (DTaP-IPV-Hib-HepB) - dos 1", "", ""),
    (3, "6-in-1 - dose 2", "6-dalam-1 - dos 2", "", ""),
    (4, "Pneumococcal (PCV) - dose 1", "Pneumokokal (PCV) - dos 1", "", ""),
    (5, "6-in-1 - dose 3", "6-dalam-1 - dos 3", "", ""),
    (6, "Pneumococcal (PCV) - dose 2", "Pneumokokal (PCV) - dos 2", "", ""),
    (6, "Measles (Sabah only)", "Campak (Sabah sahaja)", "Extra dose given in Sabah.", "Dos tambahan di Sabah."),
    (9, "MMR - dose 1", "MMR - dos 1", "", ""),
    (12, "MMR - dose 2", "MMR - dos 2", "", ""),
    (15, "Pneumococcal (PCV) - booster", "Pneumokokal (PCV) - penggalak", "", ""),
    (18, "6-in-1 - booster", "6-dalam-1 - penggalak", "", ""),
]

# (key, icon, place EN, place MS, temperature, hours (for the use-by calculator), how long EN, how long MS)
MILK = [
    ("room", "🌡️", "Room", "Suhu bilik", "25-37°C", 4, "4 hours", "4 jam"),
    ("aircond", "❄️", "Air-conditioned room", "Bilik berhawa dingin", "15-24°C", 8, "8 hours", "8 jam"),
    ("cooler", "🧊", "Cooler bag with ice packs", "Beg penyejuk dengan ais", "4°C", 24, "24 hours", "24 jam"),
    ("chiller", "🧺", "Fridge (chiller)", "Peti sejuk (bahagian dingin)", "2-4°C", 72, "3-5 days", "3-5 hari"),
    ("freezer", "🥶", "Fridge freezer compartment (1 or 2 door)", "Bahagian sejuk beku peti sejuk (1 atau 2 pintu)", "", 336, "2 weeks", "2 minggu"),
    ("deep", "🧊", "Deep freezer", "Peti sejuk beku (deep freezer)", "-20°C", 4380, "6 months", "6 bulan"),
]

# Newborn essentials (key, EN, MS, affiliate key in config.AFFILIATE_LINKS or None)
ESSENTIALS = [
    ("Sleeping", "Tidur", [
        ("cot", "Baby cot or bed with a firm, flat mattress", "Katil bayi dengan tilam rata dan keras", "swaddle"),
        ("sheets", "2-3 fitted sheets", "2-3 cadar bersarung", "blanket"),
        ("kelambu", "Mosquito net (kelambu)", "Kelambu", "blanket"),
        ("sleepsuit", "Sleepsuits or light swaddles", "Baju tidur atau kain bedung nipis", "newborn_clothes"),
    ]),
    ("Feeding", "Menyusu", [
        ("pump", "Breast pump (if you'll express milk)", "Pam susu (jika akan memerah)", "nipple_cream"),
        ("storage_bags", "Breast milk storage bags", "Beg simpanan susu ibu", "nipple_cream"),
        ("nursing_pillow", "Nursing pillow", "Bantal menyusu", "nipple_cream"),
        ("burp", "Burp cloths / small towels", "Kain lampin / tuala kecil", "newborn_clothes"),
        ("bottles2", "Feeding bottles and a cleaning brush (if needed)", "Botol susu dan berus pencuci (jika perlu)", "baby_bottles"),
    ]),
    ("Bathing & care", "Mandi & penjagaan", [
        ("tub", "Baby bath tub", "Tab mandi bayi", "wipes"),
        ("towel", "Hooded baby towels", "Tuala bayi bertudung", "wipes"),
        ("wash", "Gentle baby wash", "Sabun bayi yang lembut", "wipes"),
        ("nails", "Baby nail clipper or file", "Pengetip kuku bayi", "wipes"),
        ("thermo", "Digital thermometer", "Termometer digital", "wipes"),
    ]),
    ("Diapers", "Lampin", [
        ("nb_diapers", "Newborn diapers (2-3 packs)", "Lampin bayi baru lahir (2-3 bungkus)", "newborn_diapers"),
        ("wipes2", "Baby wipes", "Tisu basah bayi", "wipes"),
        ("cream", "Diaper rash cream", "Krim ruam lampin", "wipes"),
        ("mat", "Changing mat", "Alas tukar lampin", "newborn_diapers"),
    ]),
    ("Clothes", "Pakaian", [
        ("onesies", "6-8 bodysuits / baju bayi", "6-8 baju bayi", "newborn_clothes"),
        ("barut", "Barut / bedung", "Barut / bedung", "swaddle"),
        ("mitts", "Mittens, booties and caps", "Sarung tangan, stokin dan topi", "mittens"),
    ]),
    ("Out and about", "Keluar rumah", [
        ("carseat", "Infant car seat (required by law)", "Kerusi keselamatan kereta bayi (wajib)", "car_seat"),
        ("carrier", "Baby carrier or sling", "Pembawa bayi / anduh", "car_seat"),
        ("stroller", "Stroller", "Kereta sorong bayi", "car_seat"),
        ("diaperbag", "Diaper bag", "Beg lampin", "car_seat"),
    ]),
]

# Baby names: (name, gender m/f, meaning EN, meaning MS). Common interpretations of Arabic / Malay names.
NAMES = [
    ("Muhammad", "m", "praised", "yang terpuji"), ("Ahmad", "m", "most praiseworthy", "yang sangat terpuji"),
    ("Adam", "m", "the first man; of the earth", "manusia pertama; dari tanah"), ("Amir", "m", "leader, prince", "pemimpin, putera"),
    ("Aqil", "m", "wise, intelligent", "bijak, berakal"), ("Arif", "m", "knowledgeable", "berpengetahuan"),
    ("Danial", "m", "God is my judge", "Allah hakimku"), ("Faris", "m", "knight, horseman", "penunggang kuda, pahlawan"),
    ("Fateh", "m", "conqueror, opener", "pembuka, penakluk"), ("Hakim", "m", "wise", "bijaksana"),
    ("Hamzah", "m", "strong, steadfast", "kuat, teguh"), ("Hadi", "m", "guide", "pemberi petunjuk"),
    ("Imran", "m", "prosperity", "kemakmuran"), ("Irfan", "m", "knowledge, gratitude", "pengetahuan, kesyukuran"),
    ("Isa", "m", "name of the prophet Isa", "nama Nabi Isa"), ("Ismail", "m", "God hears", "Allah mendengar"),
    ("Luqman", "m", "the wise Luqman of the Quran", "Luqman yang bijaksana dalam al-Quran"), ("Mikail", "m", "name of an archangel", "nama malaikat"),
    ("Naim", "m", "bliss, comfort", "nikmat, kesenangan"), ("Rayyan", "m", "a gate of Paradise", "pintu syurga"),
    ("Syafiq", "m", "compassionate", "penyayang"), ("Umar", "m", "long-lived", "panjang umur"),
    ("Yusuf", "m", "name of the prophet Yusuf", "nama Nabi Yusuf"), ("Ziyad", "m", "growth, abundance", "bertambah, berkembang"),
    ("Harith", "m", "guardian, cultivator", "penjaga, peladang"), ("Khalid", "m", "eternal", "kekal"),
    ("Iskandar", "m", "defender of people", "pelindung manusia"), ("Nuh", "m", "name of the prophet Nuh", "nama Nabi Nuh"),
    ("Syukri", "m", "thankful", "bersyukur"), ("Zakaria", "m", "name of the prophet Zakaria", "nama Nabi Zakaria"),
    ("Aisyah", "f", "alive, lively", "hidup, bertenaga"), ("Alya", "f", "exalted, noble", "tinggi, mulia"),
    ("Amira", "f", "princess, leader", "puteri, pemimpin"), ("Dhia", "f", "light, radiance", "cahaya, sinar"),
    ("Fatimah", "f", "daughter of the Prophet", "puteri Rasulullah"), ("Hafsah", "f", "young lioness", "anak singa betina"),
    ("Hana", "f", "happiness", "kebahagiaan"), ("Hawa", "f", "Eve; life", "Hawa; kehidupan"),
    ("Humaira", "f", "rosy-cheeked", "pipi kemerah-merahan"), ("Iman", "f", "faith", "keimanan"),
    ("Insyirah", "f", "relief, an open heart", "kelapangan dada"), ("Khadijah", "f", "born early; wife of the Prophet", "lahir awal; isteri Rasulullah"),
    ("Laila", "f", "night", "malam"), ("Maryam", "f", "mother of the prophet Isa", "ibu Nabi Isa"),
    ("Mawar", "f", "rose", "bunga mawar"), ("Melati", "f", "jasmine", "bunga melati"),
    ("Naura", "f", "flower, blossom", "bunga"), ("Nur", "f", "light", "cahaya"),
    ("Qistina", "f", "fair, just", "adil, saksama"), ("Raudhah", "f", "garden", "taman"),
    ("Sarah", "f", "princess", "puteri"), ("Sofea", "f", "pure; wisdom", "suci; kebijaksanaan"),
    ("Syifa", "f", "healing", "penawar"), ("Wardah", "f", "rose", "bunga mawar"),
    ("Yasmin", "f", "jasmine flower", "bunga melur"), ("Zahra", "f", "radiant, blossoming", "berseri, mekar"),
    ("Nadia", "f", "tender; the caller", "lembut; yang menyeru"), ("Safiya", "f", "pure, sincere", "suci, ikhlas"),
]
