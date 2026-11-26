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

# More names (added 26 Nov 2026). Common interpretations, as above.
MALAY_NAMES += [
    ("Abdullah", "m", "servant of God", "hamba Allah"), ("Afif", "m", "chaste, modest", "suci, menjaga diri"),
    ("Aiman", "m", "blessed, fortunate", "diberkati, bertuah"), ("Akmal", "m", "most perfect", "paling sempurna"),
    ("Ammar", "m", "long-lived; one who builds", "panjang umur; yang memakmurkan"), ("Anas", "m", "friendly, affectionate", "mesra, ramah"),
    ("Asyraf", "m", "most noble", "paling mulia"), ("Azim", "m", "great, mighty", "agung, hebat"),
    ("Badrul", "m", "full moon", "bulan purnama"), ("Bayu", "m", "breeze", "angin lembut"),
    ("Bilal", "m", "the Prophet's muezzin", "muazzin Rasulullah"), ("Fahim", "m", "understanding, intelligent", "memahami, cerdik"),
    ("Faiz", "m", "successful, victorious", "berjaya, menang"), ("Farhan", "m", "happy, joyful", "gembira"),
    ("Firdaus", "m", "the highest garden of Paradise", "syurga Firdaus"), ("Ghazi", "m", "warrior", "pahlawan"),
    ("Hariz", "m", "guardian, protector", "penjaga, pelindung"), ("Haziq", "m", "clever, skilful", "cerdik, mahir"),
    ("Ilyas", "m", "name of the prophet Ilyas", "nama Nabi Ilyas"), ("Irsyad", "m", "guidance", "petunjuk"),
    ("Izzat", "m", "honour, dignity", "kemuliaan, maruah"), ("Jibril", "m", "name of the archangel Jibril", "nama malaikat Jibril"),
    ("Kamal", "m", "perfection", "kesempurnaan"), ("Luth", "m", "name of the prophet Luth", "nama Nabi Luth"),
    ("Mustafa", "m", "the chosen one", "yang terpilih"), ("Nabil", "m", "noble", "mulia"),
    ("Putra", "m", "prince", "putera"), ("Rafiq", "m", "kind companion", "teman yang baik hati"),
    ("Rasyid", "m", "rightly guided", "yang mendapat petunjuk"), ("Rizqi", "m", "sustenance, blessing", "rezeki"),
    ("Saif", "m", "sword", "pedang"), ("Taufiq", "m", "success granted by God", "taufik, kejayaan"),
    ("Ukasyah", "m", "name of a Companion of the Prophet", "nama sahabat Nabi"), ("Wafiq", "m", "successful", "berjaya"),
    ("Wira", "m", "hero", "wira, pahlawan"), ("Yahya", "m", "name of the prophet Yahya", "nama Nabi Yahya"),
    ("Zaim", "m", "leader", "pemimpin"),
    ("Ain", "f", "eye; spring of water", "mata; mata air"), ("Aqilah", "f", "intelligent, wise", "bijak, berakal"),
    ("Balqis", "f", "the Queen of Sheba", "Ratu Saba'"), ("Bunga", "f", "flower", "bunga"),
    ("Cahaya", "f", "light", "cahaya"), ("Embun", "f", "dew", "embun"),
    ("Farah", "f", "joy", "kegembiraan"), ("Hannah", "f", "grace", "rahmat"),
    ("Husna", "f", "the best, most beautiful", "yang terbaik, terindah"), ("Intan", "f", "diamond", "intan"),
    ("Izzah", "f", "honour, dignity", "kemuliaan, maruah"), ("Jannah", "f", "paradise", "syurga"),
    ("Kasih", "f", "love", "kasih sayang"), ("Khairunnisa", "f", "the best of women", "sebaik-baik wanita"),
    ("Lutfiah", "f", "kind, gentle", "lemah lembut"), ("Madinah", "f", "the city of Madinah", "kota Madinah"),
    ("Mutiara", "f", "pearl", "mutiara"), ("Nabila", "f", "noble", "mulia"),
    ("Nadhirah", "f", "radiant, flourishing", "berseri, segar"), ("Najwa", "f", "a close, private talk", "bisikan, bicara rahsia"),
    ("Nayla", "f", "one who achieves", "yang memperoleh"), ("Nisa", "f", "women", "wanita"),
    ("Puteri", "f", "princess", "puteri"), ("Qaisara", "f", "empress", "maharani"),
    ("Rahmah", "f", "mercy", "rahmat"), ("Ruqayyah", "f", "daughter of the Prophet", "puteri Rasulullah"),
    ("Sakinah", "f", "calm, tranquillity", "ketenangan"), ("Salsabila", "f", "a spring in Paradise", "mata air di syurga"),
    ("Seri", "f", "radiance", "seri, berseri"), ("Sumayyah", "f", "the first martyr in Islam", "syahidah pertama dalam Islam"),
    ("Suria", "f", "sun", "matahari"), ("Yusra", "f", "ease", "kemudahan"),
    ("Zainab", "f", "daughter of the Prophet", "puteri Rasulullah"), ("Zara", "f", "princess; radiant", "puteri; berseri"),
]
CHINESE_NAMES += [
    ("Zi Xuan 子轩", "m", "lofty and dignified", "luhur dan bermaruah"), ("Hao Yu 浩宇", "m", "vast universe", "alam semesta yang luas"),
    ("Wei Ming 伟明", "m", "great and bright", "hebat dan cerah"), ("Jun Kai 俊凯", "m", "handsome and triumphant", "kacak dan berjaya"),
    ("Zhi Xuan 志轩", "m", "ambitious and dignified", "bercita-cita tinggi dan bermaruah"), ("Jia Jun 家俊", "m", "the handsome one of the family", "yang kacak dalam keluarga"),
    ("Rui Xiang 瑞祥", "m", "auspicious and lucky", "bertuah dan membawa rezeki"), ("Jing Hao 景浩", "m", "bright and vast", "cerah dan luas"),
    ("Yi Chen 奕辰", "m", "radiant like the stars", "bersinar seperti bintang"), ("Ze Yu 泽宇", "m", "a blessing to the world", "rahmat kepada dunia"),
    ("Xin Yue 欣悦", "f", "joyful and happy", "gembira dan bahagia"), ("Yu Tong 雨桐", "f", "rain on the paulownia tree; graceful", "hujan di pohon paulownia; anggun"),
    ("Si Qi 思琪", "f", "thoughtful and precious like jade", "bijak berfikir dan berharga seperti jed"), ("Ke Xin 可欣", "f", "lovely and joyful", "comel dan gembira"),
    ("Yi Xuan 怡萱", "f", "happy and carefree", "bahagia dan tenang"), ("Hui Xin 慧心", "f", "a wise heart", "hati yang bijak"),
    ("Wen Qi 雯琪", "f", "colourful clouds and fine jade", "awan berwarna dan jed halus"), ("Le Yi 乐怡", "f", "happy and joyful", "riang dan gembira"),
    ("Jia Yi 佳怡", "f", "good and joyful", "baik dan gembira"), ("Mei Xin 美欣", "f", "beautiful and joyful", "cantik dan gembira"),
    ("Shi Han 诗涵", "f", "poetic and refined", "puitis dan halus budi"), ("Xue Er 雪儿", "f", "snow; pure", "salji; suci"),
]
INDIAN_NAMES += [
    ("Aadhav", "m", "the sun", "matahari"), ("Dinesh", "m", "lord of the day; the sun", "tuan siang; matahari"),
    ("Harish", "m", "Lord Vishnu", "Dewa Vishnu"), ("Kishore", "m", "young boy", "anak muda"),
    ("Krishna", "m", "the Hindu god Krishna", "Dewa Krishna"), ("Mahesh", "m", "great lord; Lord Shiva", "tuan agung; Dewa Shiva"),
    ("Pranav", "m", "the sacred syllable Om", "suku kata suci Om"), ("Rohan", "m", "rising, ascending", "meningkat, naik"),
    ("Santhosh", "m", "happiness", "kebahagiaan"), ("Surya", "m", "the sun", "matahari"),
    ("Varun", "m", "Hindu god of water and sky", "dewa air dan langit"), ("Yuvan", "m", "young", "muda"),
    ("Anitha", "f", "grace", "rahmat, keanggunan"), ("Bhavani", "f", "a name of Goddess Parvati", "nama Dewi Parvati"),
    ("Devi", "f", "goddess", "dewi"), ("Gayathri", "f", "a sacred hymn", "himne suci"),
    ("Haritha", "f", "green; nature", "hijau; alam"), ("Janani", "f", "mother", "ibu"),
    ("Keerthana", "f", "song of praise", "lagu pujian"), ("Nandhini", "f", "daughter; one who gives joy", "anak perempuan; pembawa kegembiraan"),
    ("Revathi", "f", "a star", "sebuah bintang"), ("Shalini", "f", "modest", "sopan, rendah diri"),
    ("Tharani", "f", "the earth", "bumi"), ("Yamini", "f", "night", "malam"),
]


# ---- More languages (added 26 Nov 2026). Gender: m / f / u (used for both).
# Meanings checked on Behind the Name (behindthename.com/name/<name>) on 26 Nov 2026. For Japanese and Korean
# names the meaning depends on the characters - we show one common spelling, as with Chinese names.
PUNJABI_NAMES = [
    ("Gurpreet", "u", "love of the guru (teacher); joy", "kasih kepada guru; kegembiraan"),
    ("Harpreet", "u", "love of God (Hari)", "kasih kepada Tuhan (Hari)"),
    ("Manpreet", "u", "love and joy of the heart and mind", "kasih dan kegembiraan jiwa"),
    ("Navdeep", "u", "new light, new lamp", "cahaya baharu, pelita baharu"),
    ("Mandeep", "u", "light of the mind", "cahaya jiwa"),
    ("Amandeep", "u", "light of peace", "pelita kedamaian"),
    ("Gurdeep", "u", "light of the guru (teacher)", "cahaya guru"),
    ("Sukhdeep", "u", "light of happiness", "pelita kebahagiaan"),
    ("Hardeep", "u", "light of God (Hari)", "cahaya Tuhan (Hari)"),
    ("Jagjit", "u", "conqueror of the world", "penakluk dunia"),
    ("Manjeet", "u", "victory of the mind", "kemenangan jiwa"),
    ("Navneet", "u", "new and everlasting", "baharu dan kekal abadi"),
    ("Simran", "u", "always remembering God", "sentiasa mengingati Tuhan"),
    ("Kuldeep", "m", "light of the family", "pelita keluarga"),
    ("Karan", "m", "clever, skilful", "bijak, mahir"),
    ("Zorawar", "m", "strong, powerful", "kuat, gagah"),
    ("Amrita", "f", "immortal; nectar of life", "abadi; air kehidupan"),
]
ENGLISH_NAMES = [
    ("Noah", "m", "rest, peace (Hebrew)", "rehat, ketenangan (Ibrani)"),
    ("Ethan", "m", "strong, firm, lasting (Hebrew)", "teguh, kukuh, kekal (Ibrani)"),
    ("Daniel", "m", "God is my judge (Hebrew)", "Tuhan hakimku (Ibrani)"),
    ("Joshua", "m", "God is salvation (Hebrew)", "Tuhan penyelamat (Ibrani)"),
    ("Samuel", "m", "name of God; God has heard (Hebrew)", "nama Tuhan; Tuhan telah mendengar (Ibrani)"),
    ("Isaac", "m", "he will laugh, he will rejoice (Hebrew)", "dia akan ketawa, dia akan bergembira (Ibrani)"),
    ("Benjamin", "m", "son of the south / of the right hand (Hebrew)", "anak dari selatan / tangan kanan (Ibrani)"),
    ("Emma", "f", "whole, complete (Germanic)", "sempurna, lengkap (Jermanik)"),
    ("Olivia", "f", "olive (Latin)", "zaitun (Latin)"),
    ("Grace", "f", "grace, kindness (Latin)", "rahmat, kebaikan (Latin)"),
    ("Abigail", "f", "my father is joy (Hebrew)", "ayahku kegembiraan (Ibrani)"),
    ("Esther", "f", "possibly 'star' (Persian)", "mungkin 'bintang' (Parsi)"),
    ("Chloe", "f", "young green shoot (Greek)", "tunas hijau muda (Yunani)"),
    ("Rachel", "f", "ewe, a gentle sheep (Hebrew)", "biri-biri betina (Ibrani)"),
]
JAPANESE_NAMES = [
    ("Haruto 陽翔", "m", "sun + soar", "matahari + terbang tinggi"),
    ("Ren 蓮", "u", "lotus", "teratai"),
    ("Riku 陸", "m", "land", "daratan"),
    ("Kaito 海翔", "m", "sea + soar", "laut + terbang tinggi"),
    ("Minato 湊", "u", "harbour", "pelabuhan"),
    ("Haruki 晴輝", "m", "clear weather + brightness", "cuaca cerah + sinar"),
    ("Itsuki 樹", "m", "tree", "pokok"),
    ("Hinata 陽向", "u", "towards the sun", "menghadap matahari"),
    ("Yui 結衣", "f", "tie, bind + clothing", "ikatan + pakaian"),
    ("Sakura 桜", "f", "cherry blossom", "bunga sakura"),
    ("Mei 芽依", "f", "bud, sprout + rely on", "tunas + bergantung"),
    ("Rin 凛", "u", "dignified", "bermaruah"),
    ("Hana 花", "f", "flower", "bunga"),
    ("Akari 明里", "f", "bright + village", "terang + kampung"),
    ("Himari 陽葵", "f", "sun + hollyhock; sunflower", "matahari + bunga hollyhock; bunga matahari"),
    ("Aoi 葵", "u", "hollyhock", "bunga hollyhock"),
]
KOREAN_NAMES = [
    ("Min-jun 敏俊", "m", "quick, clever + talented", "pantas, bijak + berbakat"),
    ("Seo-jun 瑞俊", "m", "good omen + talented", "petanda baik + berbakat"),
    ("Ha-jun 夏准", "m", "summer, great + approve", "musim panas, hebat + merestui"),
    ("Do-yun 道允", "m", "path, way + allow", "jalan + mengizinkan"),
    ("Min-ho 敏浩", "m", "quick, clever + vast", "pantas, bijak + luas"),
    ("Ye-jun 藝俊", "m", "art, talent + talented", "seni, bakat + berbakat"),
    ("Ji-ho 智昊", "u", "wisdom + sky", "kebijaksanaan + langit"),
    ("Ji-min 智敏", "u", "wisdom + quick, clever", "kebijaksanaan + pantas, bijak"),
    ("Ji-an 智安", "u", "wisdom + peace", "kebijaksanaan + ketenangan"),
    ("Min-seo 敏序", "u", "quick, clever + order", "pantas, bijak + teratur"),
    ("Su-bin 秀斌", "u", "outstanding + refined", "cemerlang + halus budi"),
    ("Seo-yeon 瑞妍", "f", "good omen + beautiful", "petanda baik + cantik"),
    ("Seo-yun 瑞潤", "f", "good omen + soft, sleek", "petanda baik + lembut"),
    ("Ha-eun 夏恩", "f", "summer, great + kindness", "musim panas, hebat + kebaikan"),
    ("Da-eun 多恩", "f", "much + kindness", "banyak + kebaikan"),
    ("Chae-won 彩原", "f", "colour + origin", "warna + asal"),
]

# Iban meanings: Anthony Richards, An Iban-English Dictionary (Oxford, 1981) - each word is also listed there as a
# personal name (archive.org/details/AnIbanEnglishDictionaryByAnthonyRichards, checked 26 Nov 2026).
# Huminodun: Sabah State Library, "Kaamatan Festival". Other Kadazan-Dusun words: Kadazan Dictionary (webonary.org/kadazan).
BORNEO_NAMES = [
    # Iban (Richards' Iban-English Dictionary - each word is also listed there as a personal name)
    ("Kumang", "f", "the ideal woman; Iban goddess of beauty (Iban)", "wanita idaman; dewi kecantikan Iban (Iban)"),
    ("Rentap", "m", "name of the Iban warrior who fought the Brooke Rajah (Iban)", "nama pahlawan Iban yang menentang Rajah Brooke (Iban)"),
    ("Awan", "m", "cloud (Iban)", "awan di langit (Iban)"),
    ("Belayong", "m", "very strong, like the warriors of old (Iban)", "sangat kuat, seperti pahlawan zaman dahulu (Iban)"),
    ("Laju", "m", "swift, fast (Iban)", "pantas, laju (Iban)"),
    ("Dayang", "f", "maiden; a title of honour for women (Iban)", "gadis; gelaran hormat untuk wanita (Iban)"),
    ("Madu", "f", "honey (Iban)", "madu (Iban)"),
    ("Jereni", "f", "clear, like clean water (Iban)", "jernih, seperti air bersih (Iban)"),
    ("Siti", "f", "a title of honour for women (Iban)", "gelaran hormat untuk wanita (Iban)"),
    ("Ina", "f", "mother (Iban)", "ibu (Iban)"),
    ("Mula", "u", "beginning, origin (Iban)", "permulaan, asal usul (Iban)"),
    # Kadazan-Dusun: Huminodun from the Sabah State Library; the rest are Kadazan words with lovely meanings,
    # meanings from the Kadazan Dictionary (webonary.org/kadazan, checked 26 Nov 2026). Words aren't gendered -> 'u'.
    ("Huminodun", "f", "maiden of the Kaamatan legend, honoured at the harvest festival (Kadazan-Dusun)", "gadis dalam legenda Kaamatan, diraikan pada Pesta Menuai (Kadazan-Dusun)"),
    ("Navau", "u", "clear day, dawn, bright (Kadazan-Dusun)", "cuaca cerah, subuh, terang (Kadazan-Dusun)"),
    ("Vanus", "u", "beautiful, pretty, lovely (Kadazan-Dusun)", "cantik, jelita (Kadazan-Dusun)"),
    ("Tavang", "u", "full moon (Kadazan-Dusun)", "bulan mengambang (Kadazan-Dusun)"),
    ("Vuhan", "u", "moon (Kadazan-Dusun)", "bulan (Kadazan-Dusun)"),
    ("Bohobou", "u", "dew (Kadazan-Dusun)", "embun (Kadazan-Dusun)"),
    ("Alus", "u", "fine, smooth, beautiful (Kadazan-Dusun)", "halus, cantik (Kadazan-Dusun)"),
    ("Unsikou", "u", "glad, happy, rejoicing (Kadazan-Dusun)", "suka hati, riang (Kadazan-Dusun)"),
    ("Bohuntung", "u", "rainbow (Kadazan-Dusun)", "pelangi (Kadazan-Dusun)"),
    ("Amas", "u", "gold (Kadazan-Dusun)", "emas (Kadazan-Dusun)"),
    ("Tadau", "u", "sun; day (Kadazan-Dusun)", "matahari; hari (Kadazan-Dusun)"),
    ("Tavan", "u", "sky (Kadazan-Dusun)", "langit (Kadazan-Dusun)"),
    ("Suvab", "u", "morning (Kadazan-Dusun)", "pagi (Kadazan-Dusun)"),
    ("Tama", "u", "brave, bold (Kadazan-Dusun)", "berani (Kadazan-Dusun)"),
    ("Hansan", "u", "trust, hope (Kadazan-Dusun)", "percaya, harapan (Kadazan-Dusun)"),
    ("Vasi", "u", "kind, good (Kadazan-Dusun)", "baik, bagus (Kadazan-Dusun)"),
]

NAMES = ([n + ("malay",) for n in MALAY_NAMES] + [n + ("chinese",) for n in CHINESE_NAMES]
         + [n + ("indian",) for n in INDIAN_NAMES] + [n + ("punjabi",) for n in PUNJABI_NAMES]
         + [n + ("borneo",) for n in BORNEO_NAMES] + [n + ("english",) for n in ENGLISH_NAMES]
         + [n + ("japanese",) for n in JAPANESE_NAMES] + [n + ("korean",) for n in KOREAN_NAMES])

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
