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
        ("pump", "Breast pump if you'll express milk (e.g. Philips Avent, Medela, Spectra, Pigeon)", "Pam susu jika akan memerah (cth. Philips Avent, Medela, Spectra, Pigeon)", "nipple_cream"),
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
    ("Dayang", "f", "maiden; a title of honour for women (Iban)", "gadis; gelaran hormat untuk wanita (Iban)"),
    ("Madu", "f", "honey (Iban)", "madu (Iban)"),
    ("Jereni", "f", "clear, like clean water (Iban)", "jernih, seperti air bersih (Iban)"),
    ("Siti", "f", "a title of honour for women (Iban)", "gelaran hormat untuk wanita (Iban)"),
    ("Ina", "f", "mother (Iban)", "ibu (Iban)"),
    ("Mula", "u", "beginning, origin (Iban)", "permulaan, asal usul (Iban)"),
    ("Urai", "f", "bursting into bloom; gold dust (Iban)", "mekar berkembang; debu emas (Iban)"),
    ("Riti", "f", "a Skrang woman celebrated for her beauty (Iban)", "wanita Skrang yang terkenal kerana kecantikannya (Iban)"),
    ("Mawa", "f", "a woman's name or title in Iban poetry (Iban)", "nama atau gelaran wanita dalam puisi Iban (Iban)"),
    ("Jinap", "f", "a woman in Iban history - grandmother of Janting of Julau (Iban)", "wanita dalam sejarah Iban - nenek Janting dari Julau (Iban)"),
    ("Biti", "f", "sister of the legendary Iban hero (Iban)", "saudara perempuan wira legenda Iban (Iban)"),
    ("Unggang", "m", "Saribas warrior who fought pirates (Iban)", "pahlawan Saribas yang menentang lanun (Iban)"),
    ("Linggir", "m", "Saribas leader known as Mali Lebu, 'Never Fail' (Iban)", "pemimpin Saribas bergelar Mali Lebu, 'Tidak Pernah Gagal' (Iban)"),
    ("Libau", "m", "Rentap's birth name - he defended Bukit Sadok (Iban)", "nama asal Rentap - beliau mempertahankan Bukit Sadok (Iban)"),
    ("Mujah", "m", "Iban leader in the Entabai in the 1800s (Iban)", "pemimpin Iban di Entabai pada abad ke-19 (Iban)"),
    ("Busang", "m", "a famous bird-omen reader of the Lemanak (Iban)", "tukang tilik burung yang terkenal di Lemanak (Iban)"),
    ("Nanang", "m", "Iban leader who supported Rentap (Iban)", "pemimpin Iban yang menyokong Rentap (Iban)"),
    ("Luyoh", "m", "Iban leader at Bukit Batu, around 1881 (Iban)", "pemimpin Iban di Bukit Batu, sekitar 1881 (Iban)"),
    ("Buda", "m", "son of Orang Kaya Dana Bayang, a Saribas leader (Iban)", "anak Orang Kaya Dana Bayang, pemimpin Saribas (Iban)"),
    ("Manai", "m", "small parrot (Iban)", "burung bayan kecil (Iban)"),
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

# ---- More of Malaysia's languages (added 26 Nov 2026).
# Bidayuh (Bau), Kelabit, Lun Bawang: Borneo Dictionary (borneodictionary.com - Bidayuh Bau list based on the
# Dayak Bidayuh National Association wordlist). Bajau (West Coast), Murut (Timugon), Rungus, Semai: SIL dictionaries
# on Webonary (webonary.org/wcbajau, /timugon_murut, /rungus, /semai). These are words with lovely meanings, used as
# name ideas; words aren't gendered, so they are 'u'. Telugu, Malayalam, Siamese (Thai) and Kristang (Portuguese)
# names: Behind the Name.
BORNEO_NAMES += [
    ("A'a", 'f', "a traditional Bidayuh girl's name (Bidayuh)", 'nama tradisional gadis Bidayuh (Bidayuh)'),
    ('Sangon', 'u', 'beautiful, pretty (Bidayuh)', 'cantik (Bidayuh)'),
    ('Jumieh', 'u', 'dew (Bidayuh)', 'embun (Bidayuh)'),
    ('Girongan', 'u', 'rainbow (Bidayuh)', 'pelangi (Bidayuh)'),
    ('Sipagi', 'u', 'morning (Bidayuh)', 'pagi (Bidayuh)'),
    ('Bosow', 'u', 'dawn (Bidayuh)', 'awal pagi (Bidayuh)'),
    ('Bulant', 'u', 'moon (Bidayuh)', 'bulan (Bidayuh)'),
    ('Longgit', 'u', 'sky (Bidayuh)', 'langit (Bidayuh)'),
    ('Kining', 'u', 'clear, bright (of the day) (Bidayuh)', 'cerah (Bidayuh)'),
    ('Bilingieng', 'u', 'shining (Bidayuh)', 'bersinar (Bidayuh)'),
    ('Tatih', 'u', 'kind-hearted (Bidayuh)', 'baik hati (Bidayuh)'),
    ('Nyayang', 'u', 'to love (Bidayuh)', 'sayang (Bidayuh)'),
    ('Bitojit', 'u', 'to smile (Bidayuh)', 'senyum (Bidayuh)'),
    ('Suat', 'u', 'flowering, a bud (Bidayuh)', 'putik bunga (Bidayuh)'),
    ('Doras', 'u', 'strong (Bidayuh)', 'kuat (Bidayuh)'),
    ('Sangguoh', 'u', 'hornbill (Bidayuh)', 'burung enggang (Bidayuh)'),
    ('Puni', 'u', 'green pigeon (Bidayuh)', 'burung punai (Bidayuh)'),
    ('Lipitie', 'u', 'butterfly (Bidayuh)', 'rama-rama (Bidayuh)'),
    ('Lekedtang', 'u', 'dawn, morning (Kelabit)', 'fajar, pagi (Kelabit)'),
    ('Uka', 'u', 'dawn (Kelabit)', 'fajar (Kelabit)'),
    ('Edtang', 'u', 'light, radiance (Kelabit)', 'cahaya, sinar (Kelabit)'),
    ('Beresat', 'u', 'bright (of light) (Kelabit)', 'terang (Kelabit)'),
    ('Ribed', 'u', 'pretty, beautiful (Kelabit)', 'cantik, lawa (Kelabit)'),
    ('Tegkang', 'u', 'rainbow (Kelabit)', 'pelangi (Kelabit)'),
    ('Makat', 'u', 'brave (Kelabit)', 'berani (Kelabit)'),
    ('Duru', 'u', 'honey (Kelabit)', 'madu (Kelabit)'),
    ('Sinung', 'u', 'happy, successful (Kelabit)', 'gembira, berjaya (Kelabit)'),
    ('Rimod', 'u', 'smile (Kelabit)', 'senyum (Kelabit)'),
    ('Metaga', 'u', 'beautiful (Lun Bawang)', 'cantik (Lun Bawang)'),
    ('Rimud', 'u', 'smile (Lun Bawang)', 'senyum (Lun Bawang)'),
    ('Lapung', 'u', 'light (Lun Bawang)', 'cahaya (Lun Bawang)'),
    ('Sumping', 'u', 'flower bud (Bajau)', 'kuntum bunga (Bajau)'),
    ('Telak', 'u', 'bright (Bajau)', 'terang (Bajau)'),
    ('Mentio', 'u', 'pearl (Bajau)', 'mutiara (Bajau)'),
    ('Bani', 'u', 'brave (Bajau)', 'berani (Bajau)'),
    ('Pana', 'u', 'ray of light, shining (Bajau)', 'sinaran cahaya (Bajau)'),
    ('Bulintung', 'u', 'rainbow (Murut)', 'pelangi (Murut)'),
    ('Butitin', 'u', 'star (Murut)', 'bintang (Murut)'),
    ('Rondom', 'u', 'dawn, early morning (Murut)', 'subuh, awal pagi (Murut)'),
    ('Sanggong', 'u', 'beautiful (Rungus)', 'cantik (Rungus)'),
    ('Uravung', 'u', 'rice flower (Rungus)', 'bunga padi (Rungus)'),
    ('Buluntung', 'u', 'rainbow (Rungus)', 'pelangi (Rungus)'),
    ('Kalamangkag', 'u', 'the Venus star, queen of the stars (Rungus)', 'bintang kejora, ratu bintang (Rungus)'),
    ('Siou', 'u', 'brave (Rungus)', 'berani (Rungus)'),
]
INDIAN_NAMES += [
    ('Harsha', 'm', 'happiness (Telugu)', 'kegembiraan (Telugu)'),
    ('Kalyan', 'm', 'beautiful, lovely, auspicious (Telugu)', 'cantik, membawa tuah (Telugu)'),
    ('Prasanna', 'm', 'clear, bright, calm (Telugu)', 'jernih, terang, tenang (Telugu)'),
    ('Sudhir', 'm', 'wise, considerate (Telugu)', 'bijak, bertimbang rasa (Telugu)'),
    ('Manohar', 'm', 'charming, captivating (Telugu)', 'menawan hati (Telugu)'),
    ('Nikhil', 'm', 'whole, complete (Telugu)', 'sempurna, lengkap (Telugu)'),
    ('Lavanya', 'f', 'beauty, charm (Telugu)', 'kecantikan, pesona (Telugu)'),
    ('Meghana', 'f', 'cloud (Telugu)', 'awan (Telugu)'),
    ('Mallika', 'f', 'jasmine (Telugu)', 'bunga melur (Telugu)'),
    ('Sandhya', 'f', 'twilight (Telugu)', 'senja (Telugu)'),
    ('Madhuri', 'f', 'sweetness (Telugu)', 'kemanisan (Telugu)'),
    ('Manjula', 'f', 'pleasing, beautiful (Telugu)', 'menyenangkan, cantik (Telugu)'),
    ('Vishnu', 'm', 'all-pervading; name of a Hindu god (Malayalam)', 'meliputi segala; nama dewa Hindu (Malayalam)'),
    ('Vivek', 'm', 'wisdom (Malayalam)', 'kebijaksanaan (Malayalam)'),
    ('Vinod', 'm', 'joy, pleasure (Malayalam)', 'kegembiraan (Malayalam)'),
    ('Vipin', 'm', 'forest (Malayalam)', 'hutan (Malayalam)'),
    ('Anup', 'm', 'lagoon, place near the water (Malayalam)', 'lagun, tempat dekat air (Malayalam)'),
    ('Manish', 'm', 'thought, wisdom (Malayalam)', 'fikiran, kebijaksanaan (Malayalam)'),
    ('Amala', 'f', 'clean, pure (Malayalam)', 'bersih, suci (Malayalam)'),
    ('Asha', 'f', 'hope, wish (Malayalam)', 'harapan, hasrat (Malayalam)'),
    ('Nalini', 'f', 'lotus (Malayalam)', 'teratai (Malayalam)'),
    ('Namrata', 'f', 'humility (Malayalam)', 'rendah diri (Malayalam)'),
]
BORNEO_NAMES += [
    # Kenyah (Lebo' Vo'): Borneo Dictionary (borneodictionary.com/kenyah-lebo-vo). Melanau (Mukah / Central Melanau):
    # Austronesian Basic Vocabulary Database (abvd.clld.org/languages/90) and Wiktionary's Central Melanau entries.
    ("Leliwa", "u", "rainbow (Kenyah)", "pelangi (Kenyah)"),
    ("Katah", "u", "sunshine (Kenyah)", "cahaya matahari (Kenyah)"),
    ("Betuen", "u", "star in the night sky (Kenyah)", "bintang di langit malam (Kenyah)"),
    ("Jimah", "u", "dew (Kenyah)", "embun (Kenyah)"),
    ("Belevang", "u", "butterfly (Kenyah)", "rama-rama (Kenyah)"),
    ("Bunyem", "u", "to smile (Kenyah)", "tersenyum (Kenyah)"),
    ("Manyi", "u", "happy (Kenyah)", "gembira (Kenyah)"),
    ("Saga", "u", "dance (Kenyah)", "tarian (Kenyah)"),
    ("Bango", "u", "glow (Kenyah)", "sinar (Kenyah)"),
    ("Pejai", "u", "a gift (Kenyah)", "hadiah (Kenyah)"),
    ("Ino", "u", "beads (Kenyah)", "manik (Kenyah)"),
    ("Biten", "u", "star (Melanau)", "bintang (Melanau)"),
    ("Pangai", "u", "wind (Melanau)", "angin (Melanau)"),
    ("Tina", "f", "mother (Melanau)", "ibu (Melanau)"),
    ("Maih", "u", "gold (Melanau)", "emas (Melanau)"),
    ("Pirek", "u", "silver; a flash of light (Melanau)", "perak; kilauan cahaya (Melanau)"),
]
BORNEO_NAMES += [
    # More Murut (Timugon) and Bajau (West Coast): SIL dictionaries on Webonary (Murut glosses are in Malay).
    ("Sinda", "u", "light, sparkle, radiance (Murut)", "cahaya, sinaran, kilauan (Murut)"),
    ("Orou", "u", "bright, clear (of the day) (Murut)", "terang, cerah (Murut)"),
    ("Raat", "u", "sea (Murut)", "laut (Murut)"),
    ("Baani", "u", "brave (Murut)", "berani (Murut)"),
    ("Bonsoi", "u", "good, lovely, beautiful (Murut)", "baik, bagus, cantik, indah (Murut)"),
    ("Akang", "u", "darling - a loving name for a child (Murut)", "anak sayang - panggilan manja untuk anak (Murut)"),
    ("Jingit", "u", "smile (Murut)", "senyuman (Murut)"),
    ("Gintak", "u", "to jump for joy (Murut)", "melompat gembira (Murut)"),
    ("Kalimambang", "u", "butterfly (Bajau)", "rama-rama (Bajau)"),
    ("Sinsaung", "u", "morning (Bajau)", "pagi (Bajau)"),
    ("Dayag", "u", "happy (Bajau)", "gembira (Bajau)"),
    ("Beriu", "u", "wind (Bajau)", "angin (Bajau)"),
    ("Suang", "u", "river (Bajau)", "sungai (Bajau)"),
    ("Pekar", "u", "to bloom, to open out (Bajau)", "mekar, berkembang (Bajau)"),
    ("Ambun", "u", "dew (Bajau)", "embun (Bajau)"),
    ("Uran", "u", "rain (Bajau)", "hujan (Bajau)"),
    ("Daras", "u", "strong (Bajau)", "kuat (Bajau)"),
]
ORANG_ASLI_NAMES = [
    ('Perloi', 'u', 'star (Semai)', 'bintang (Semai)'),
    ('Cedau', 'u', 'rainbow (Semai)', 'pelangi (Semai)'),
    ('Perper', 'u', 'dawn (Semai)', 'subuh (Semai)'),
    ('Lunau', 'u', 'light (Semai)', 'cahaya (Semai)'),
    ('Gecek', 'u', 'moon (Semai)', 'bulan (Semai)'),
    ('Kantat', 'u', 'torch ginger flower (kantan) (Semai)', 'bunga kantan (Semai)'),
]
SIAM_NAMES = [
    ('Arthit', 'm', 'sun', 'matahari'),
    ('Klahan', 'm', 'brave', 'berani'),
    ('Mongkut', 'm', 'crown', 'mahkota'),
    ('Preecha', 'm', 'wisdom', 'kebijaksanaan'),
    ('Prasit', 'm', 'success, achievement', 'kejayaan'),
    ('Wichai', 'm', 'victory', 'kemenangan'),
    ('Anong', 'f', 'beautiful woman', 'wanita jelita'),
    ('Kanchana', 'f', 'golden', 'keemasan'),
    ('Kanda', 'f', 'beloved', 'tersayang'),
    ('Lawan', 'f', 'beauty', 'kecantikan'),
    ('Malee', 'f', 'flower, jasmine', 'bunga, melur'),
    ('Porntip', 'f', 'divine blessing', 'rahmat ilahi'),
]
KRISTANG_NAMES = [
    ('Gabriel', 'm', 'God is my strength', 'Tuhan kekuatanku'),
    ('David', 'm', 'beloved', 'yang dikasihi'),
    ('Victor', 'm', 'winner, conqueror', 'pemenang, penakluk'),
    ('Benigno', 'm', 'kind, friendly', 'baik hati, mesra'),
    ('Abel', 'm', 'breath', 'nafas'),
    ('Clara', 'f', 'clear, bright', 'jernih, terang'),
    ('Aurora', 'f', 'dawn', 'fajar'),
    ('Celeste', 'u', 'heavenly', 'dari syurga'),
    ('Diana', 'f', 'divine', 'ilahi'),
    ('Amanda', 'f', 'worthy of love', 'layak dikasihi'),
    ('Luzia', 'f', 'light', 'cahaya'),
]

NAMES = ([n + ("malay",) for n in MALAY_NAMES] + [n + ("chinese",) for n in CHINESE_NAMES]
         + [n + ("indian",) for n in INDIAN_NAMES] + [n + ("punjabi",) for n in PUNJABI_NAMES]
         + [n + ("borneo",) for n in BORNEO_NAMES] + [n + ("english",) for n in ENGLISH_NAMES]
         + [n + ("japanese",) for n in JAPANESE_NAMES] + [n + ("korean",) for n in KOREAN_NAMES]
         + [n + ("orangasli",) for n in ORANG_ASLI_NAMES] + [n + ("siam",) for n in SIAM_NAMES]
         + [n + ("kristang",) for n in KRISTANG_NAMES])

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
