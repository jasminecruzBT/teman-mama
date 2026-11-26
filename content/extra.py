"""Content for the extra mum tools (English + Bahasa Melayu).

Sources (checked 26 Nov 2026):
- Vaccines: KKM National Immunisation Programme (BCG + Hep B at birth; MMR at 9 & 12 months; pneumococcal at
  4 & 6 months + booster 15 months per KKM press statement 24 Nov 2020; 6-in-1 at 2, 3, 5 months + booster 18 months).
  Always defer to the child's health record book - ages can differ by state/clinic.
- Breast milk storage: KKM Bahagian Pemakanan poster "Penyusuan Susu Ibu (Ibu Bekerja)" (hq.moh.gov.my/nutrition).
- After-birth documents (checked 26 Nov 2026 on the official sites):
  JPN normal birth registration: Peninsular within 60 days, free; late (>60 days) RM50 + extra forms;
  Sabah and Sarawak within 14 days (late after 42 days). Documents: JPN.LM01, hospital Birth Confirmation Form,
  antenatal card, parents' IDs, marriage document (jpn.gov.my/en/services/birth/...).
  MyKid: not compulsory, first application free (malaysia.gov.my; JPN statement 2023).
  ASB: Bumiputera, from birth via a guardian, RM10 to open / RM1 after, ASNB branch or agent; minors can't use the
  myASNB app (asnb.com.my product + registration + FAQ). ASM: guardian can open for any Malaysian minor, RM10.
  SSPN Prime: RM20 to open, beneficiary from 1 day old (with birth certificate), myPTPTN app or PTPTN counter;
  parents' tax relief up to RM8,000/year YA2025-2027 (ptptn.gov.my).
  Tabung Haji: RM2 minimum, child under 18 with one guardian who has a TH account; THiJARI online then branch
  within 30 days (tabunghaji.gov.my).
  EPF: registration open from age 14 to below 75 (kwsp.gov.my article "How to Register EPF Account", 26 Nov 2025);
  i-Simpan RM1 to RM100,000 a year.
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
MALAY_NAMES = [
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

# Chinese given names (pinyin + characters). The meaning depends on the characters chosen.
CHINESE_NAMES = [
    ("Jun Hao 俊豪", "m", "handsome and heroic", "kacak dan berani"), ("Wei Jie 伟杰", "m", "great and outstanding", "hebat dan cemerlang"),
    ("Zhi Hao 志豪", "m", "ambitious and heroic", "bercita-cita tinggi dan berani"), ("Jia Hao 家豪", "m", "hero of the family", "wira keluarga"),
    ("Kai Wen 凯文", "m", "triumphant and cultured", "berjaya dan berbudaya"), ("Hao Ran 浩然", "m", "vast and upright", "luas dan lurus hati"),
    ("Ming Hui 明辉", "m", "bright and brilliant", "terang dan bersinar"), ("Jun Jie 俊杰", "m", "talented and outstanding", "berbakat dan cemerlang"),
    ("Yu Xuan 宇轩", "m", "lofty as the universe", "luhur seperti alam semesta"), ("Wen Bin 文彬", "m", "refined and cultivated", "halus budi dan terpelajar"),
    ("Jia Le 嘉乐", "m", "good and joyful", "baik dan gembira"), ("Zhen Yu 振宇", "m", "uplifting the world", "membangkitkan dunia"),
    ("Xin Yi 欣怡", "f", "joyful and happy", "gembira dan bahagia"), ("Hui Min 慧敏", "f", "wise and quick-witted", "bijak dan cerdas"),
    ("Mei Ling 美玲", "f", "beautiful, like the sound of jade", "cantik, seperti bunyi jed"), ("Jia Xin 佳欣", "f", "good and joyful", "baik dan gembira"),
    ("Yi Ting 怡婷", "f", "happy and graceful", "bahagia dan anggun"), ("Shu Ting 淑婷", "f", "virtuous and graceful", "berbudi dan anggun"),
    ("Xiao Wen 晓雯", "f", "dawn clouds", "awan subuh"), ("Li Ying 丽颖", "f", "beautiful and bright", "cantik dan bijak"),
    ("Yu Xin 雨欣", "f", "joy like rain", "kegembiraan seperti hujan"), ("Jing Yi 静怡", "f", "calm and joyful", "tenang dan gembira"),
    ("An Qi 安琪", "f", "peaceful jade", "jed yang damai"), ("Pei Shan 佩珊", "f", "jade ornament and coral", "perhiasan jed dan karang"),
]

# Indian (mostly Tamil / Sanskrit) names common in Malaysia.
INDIAN_NAMES = [
    ("Arjun", "m", "bright, shining; hero of the Mahabharata", "terang, bersinar; wira Mahabharata"), ("Aravind", "m", "lotus", "bunga teratai"),
    ("Karthik", "m", "a name of Lord Murugan", "nama Dewa Murugan"), ("Vikram", "m", "valour", "keberanian"),
    ("Rajesh", "m", "king of kings", "raja segala raja"), ("Suresh", "m", "lord of the gods", "tuan para dewa"),
    ("Ganesh", "m", "Lord Ganesha", "Dewa Ganesha"), ("Kumar", "m", "prince, son", "putera, anak lelaki"),
    ("Mohan", "m", "charming; a name of Krishna", "menawan; nama Krishna"), ("Ravi", "m", "sun", "matahari"),
    ("Sanjay", "m", "victorious", "menang"), ("Kavin", "m", "handsome, beautiful", "kacak, cantik"),
    ("Priya", "f", "beloved", "kekasih, disayangi"), ("Kavya", "f", "poetry", "puisi"),
    ("Divya", "f", "divine", "suci, ilahi"), ("Lakshmi", "f", "goddess of wealth", "dewi kekayaan"),
    ("Anjali", "f", "an offering with joined hands", "persembahan dengan tangan dirapatkan"), ("Deepa", "f", "lamp, light", "pelita, cahaya"),
    ("Kavitha", "f", "poem", "sajak"), ("Nisha", "f", "night", "malam"),
    ("Sangeetha", "f", "music", "muzik"), ("Pooja", "f", "worship, prayer", "pemujaan, doa"),
    ("Aishwarya", "f", "prosperity", "kemakmuran"), ("Vani", "f", "speech; Goddess Saraswati", "pertuturan; Dewi Saraswati"),
]

NAMES = ([n + ("malay",) for n in MALAY_NAMES] + [n + ("chinese",) for n in CHINESE_NAMES]
         + [n + ("indian",) for n in INDIAN_NAMES])

# After-birth documents checklist: (title EN, title MS, icon, [(key, EN, MS, tip EN, tip MS)])
AFTER_BIRTH = [
    ("Register the birth at JPN", "Daftar kelahiran di JPN", "📝", [
        ("confirm", "Birth confirmation form from the hospital (Borang Pengesahan Kelahiran)",
         "Borang Pengesahan Kelahiran daripada hospital",
         "Born at home or on the way? Bring a doctor's confirmation letter and ask JPN what else they need.",
         "Lahir di rumah atau dalam perjalanan? Bawa surat pengesahan doktor dan tanya JPN dokumen lain yang diperlukan."),
        ("lm01", "Birth registration form JPN.LM01, filled in", "Borang pendaftaran kelahiran JPN.LM01, diisi lengkap",
         "Sabah and Sarawak use their own forms - ask at the hospital or JPN.",
         "Sabah dan Sarawak menggunakan borang sendiri - tanya di hospital atau JPN."),
        ("ic", "Both parents' MyKad (original + a copy)", "MyKad kedua-dua ibu bapa (asal + salinan)", "", ""),
        ("nikah", "Marriage certificate (original + a copy)", "Sijil nikah / perkahwinan (asal + salinan)", "", ""),
        ("pink", "Your antenatal card or 'pink book' (original + a copy)", "Kad antenatal atau buku pink (asal + salinan)", "", ""),
        ("cert", "Check every name and date on the birth certificate before you leave the counter",
         "Semak setiap nama dan tarikh pada sijil kelahiran sebelum meninggalkan kaunter", "", ""),
        ("copies", "Make a few copies of the birth certificate - you'll need them for everything below",
         "Buat beberapa salinan sijil kelahiran - anda akan memerlukannya untuk semua urusan di bawah", "", ""),
    ]),
    ("In the first weeks", "Dalam minggu-minggu pertama", "🩺", [
        ("klinik", "Register baby at your klinik kesihatan and keep the baby's health record book safe",
         "Daftar bayi di klinik kesihatan dan simpan buku rekod kesihatan bayi dengan baik",
         "The book records every vaccine and growth check - bring it to every visit.",
         "Buku ini merekod setiap vaksin dan pemeriksaan tumbesaran - bawa setiap kali ke klinik."),
        ("hr", "Tell HR: add baby to your medical benefits and update your number of children",
         "Beritahu HR: tambah bayi dalam faedah perubatan dan kemas kini bilangan anak",
         "Your monthly tax deduction (PCB) takes your number of children into account.",
         "Potongan cukai bulanan (PCB) mengambil kira bilangan anak anda."),
        ("takaful", "Add baby to your family insurance or takaful, if you have one",
         "Tambah bayi dalam insurans atau takaful keluarga, jika ada", "", ""),
        ("str", "Getting STR? Add baby in MySTR (Kemas Kini Permohonan) with the birth certificate",
         "Menerima STR? Tambah bayi dalam MySTR (Kemas Kini Permohonan) dengan sijil kelahiran",
         "The STR amount depends on how many children you have.",
         "Jumlah STR bergantung pada bilangan anak anda."),
    ]),
    ("Later, if you need them", "Kemudian, jika perlu", "🪪", [
        ("mykid", "MyKid card - not compulsory; the first one is free at JPN",
         "Kad MyKid - tidak wajib; permohonan pertama percuma di JPN",
         "Bring the birth certificate and a parent's MyKad. The birth certificate is the document that matters most.",
         "Bawa sijil kelahiran dan MyKad ibu atau bapa. Sijil kelahiran ialah dokumen yang paling penting."),
        ("passport", "Passport - only if you'll travel abroad (apply at Imigresen)",
         "Pasport - hanya jika akan ke luar negara (mohon di Imigresen)", "", ""),
    ]),
]

# Savings accounts a baby can have. "who" is shown as a chip; epf=True means not open to babies yet.
# (key, icon, name EN, name MS, who EN, who MS, start EN, start MS, bring EN, bring MS, where EN, where MS, url)
SAVINGS = [
    ("asb", "🌱", "ASB (Amanah Saham Bumiputera)", "ASB (Amanah Saham Bumiputera)",
     "Bumiputera · from birth", "Bumiputera · dari lahir",
     "RM10 to open, then top up from RM1", "RM10 untuk buka, kemudian tambah dari RM1",
     "Birth certificate or MyKid, your MyKad, cash for the first deposit", "Sijil kelahiran atau MyKid, MyKad anda, wang tunai untuk deposit pertama",
     "An ASNB branch or agent (many banks are agents). Children's accounts can't be opened in the myASNB app - it's for 18 and above.",
     "Cawangan atau ejen ASNB (banyak bank ialah ejen). Akaun kanak-kanak tidak boleh dibuka dalam aplikasi myASNB - ia untuk 18 tahun ke atas.",
     "https://www.asnb.com.my/product/amanah-saham-bumiputera"),
    ("asm", "🌿", "ASM and other ASNB funds", "ASM dan dana ASNB lain",
     "All Malaysians · from birth", "Semua rakyat Malaysia · dari lahir",
     "RM10 to open, then top up from RM1", "RM10 untuk buka, kemudian tambah dari RM1",
     "Birth certificate or MyKid, your MyKad", "Sijil kelahiran atau MyKid, MyKad anda",
     "An ASNB branch or agent, as for ASB.", "Cawangan atau ejen ASNB, sama seperti ASB.",
     "https://www.asnb.com.my/product/amanah-saham-malaysia"),
    ("sspn", "🎓", "SSPN (PTPTN education savings)", "SSPN (simpanan pendidikan PTPTN)",
     "All Malaysians · from 1 day old", "Semua rakyat Malaysia · dari umur 1 hari",
     "SSPN Prime: RM20 to open. Parents can claim up to RM8,000 income tax relief a year (2025-2027).",
     "SSPN Prime: RM20 untuk buka. Ibu bapa boleh menuntut pelepasan cukai sehingga RM8,000 setahun (2025-2027).",
     "Baby's birth certificate, your MyKad", "Sijil kelahiran bayi, MyKad anda",
     "The myPTPTN app or a PTPTN counter.", "Aplikasi myPTPTN atau kaunter PTPTN.",
     "https://www.ptptn.gov.my/simpan-sspn/simpan-sspn-prime/"),
    ("th", "🕋", "Tabung Haji", "Tabung Haji",
     "Muslims · under 18", "Muslim · bawah 18 tahun",
     "RM2 to open", "RM2 untuk buka",
     "Birth certificate (and MyKid if you have one), your MyKad. You need your own TH account first.",
     "Sijil kelahiran (dan MyKid jika ada), MyKad anda. Anda perlu ada akaun TH sendiri dahulu.",
     "A TH branch - or start online on THiJARI, then visit a branch within 30 days to activate it.",
     "Cawangan TH - atau mula dalam talian di THiJARI, kemudian ke cawangan dalam 30 hari untuk mengaktifkannya.",
     "https://www.tabunghaji.gov.my/pembukaan-akaun"),
    ("epf", "💼", "EPF (KWSP)", "KWSP (EPF)",
     "Not for babies · from age 14", "Bukan untuk bayi · dari umur 14",
     "From 14 your child can register with their MyKad; you can then top up with i-Simpan (RM1 to RM100,000 a year).",
     "Dari umur 14, anak boleh mendaftar dengan MyKad mereka; anda kemudian boleh menambah simpanan melalui i-Simpan (RM1 hingga RM100,000 setahun).",
     "Your child's MyKad", "MyKad anak anda",
     "The KWSP i-Akaun app, an EPF kiosk or counter.", "Aplikasi KWSP i-Akaun, kiosk atau kaunter KWSP.",
     "https://www.kwsp.gov.my/en/w/article/how-to-open-an-epf-account"),
]
