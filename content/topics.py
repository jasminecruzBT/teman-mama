"""Content for the topic pages added 26 Nov 2026 (English + Bahasa Melayu).

Sources (checked 26 Nov 2026):
- Antenatal visits: KKM Perinatal Care Manual 4th ed. (2020, released 2023) - routine visits <12, 16-20, 24-26,
  28-30 weeks, foetal checks from 28 weeks, delivery plan ~36 weeks; MyHEALTH antenatal care - monthly to 28 weeks,
  every 2 weeks 28-35, weekly from 36. GDM: KKM CPG Management of Diabetes in Pregnancy (75 g OGTT; women 25+
  screened at 24-28 weeks). Tdap: KKM guideline Jan 2025 + press statement - free at KKM clinics from 26 May 2025,
  one dose at 28-32 weeks in every pregnancy. HIV/syphilis screening: KKM PMTCT guideline 2021.
- Food: MyHEALTH "Pemakanan Semasa Hamil", "Mengidam Semasa Hamil"; KKM nutrition sheet (caffeine); KKM teen
  pregnancy booklet (raw food, mercury, alcohol, herbs).
- Fasting: MyHEALTH "Puasa dan Ubat" (ask doctor first; break fast if signs of hypo/dehydration); Jabatan Mufti
  Wilayah Persekutuan Irsyad Hukum 31, Irsyad Fatwa Ramadhan 232 / 120, Irsyad Hukum 680.
- Flying: AirAsia support article "I am pregnant. Can I still fly?" (read 26 Nov 2026); Malaysia Airlines General
  Conditions of Carriage (28 Dec 2024).
- Postnatal depression: Edinburgh Postnatal Depression Scale, Cox JL, Holden JM, Sagovsky R (1987) Br J Psychiatry
  150:782-786 (may be reproduced with this citation). Cut-off >=12 for the Malay version per KKM CPG Management of
  Major Depressive Disorder 2nd ed. (2019). Talian HEAL 15555 (KKM).
- Aqiqah: Jabatan Mufti WP - Irsyad Hukum 128, Al-Kafi #1025, #1668, #1646, #1746.
- Jaundice & G6PD: MyHEALTH "Kekuningan pada Bayi Baru Lahir", "G6PD Screening in newborn", "Kekurangan Enzim G6PD".
- Growth: WHO Child Growth Standards (site-data/who-growth.json). Milestones: CDC "Learn the Signs. Act Early."
  (2025/2026 pages). Sleep hours: AASM consensus (Paruthi et al. 2016) and National Sleep Foundation (2015).
  Safe sleep: MyHEALTH "Gaya Tidur Bayi"; KKM postnatal care manual.
- Solids: KKM Garis Panduan Pemberian Makanan Bayi dan Kanak-Kanak Kecil; KKM Nota Poket Panduan Diet Malaysia
  untuk Kanak-kanak dan Remaja 2026 (portions, no salt/sugar/juice/honey before 1 year).
"""

# Antenatal timeline: (key, from week, to week, icon, EN, MS, tip EN, tip MS, link)
ANTENATAL = [
    ("booking", 0, 12, "📒", "Register at your klinik kesihatan (booking visit) and get your pink book",
     "Daftar di klinik kesihatan (lawatan pendaftaran) dan dapatkan buku pink",
     "Go as soon as you know you're pregnant - before 12 weeks. You'll have blood tests (including HIV and syphilis screening) and a urine test.",
     "Pergi sebaik sahaja tahu hamil - sebelum 12 minggu. Anda akan menjalani ujian darah (termasuk saringan HIV dan sifilis) dan ujian air kencing.", ""),
    ("v16", 16, 20, "🩺", "Check-up", "Pemeriksaan",
     "Until 28 weeks, check-ups are usually once a month.", "Sehingga 28 minggu, pemeriksaan biasanya sebulan sekali.", ""),
    ("ogtt", 24, 28, "🧪", "Glucose test (OGTT) for diabetes in pregnancy", "Ujian glukosa (OGTT) untuk diabetes semasa hamil",
     "KKM tests mums aged 25 and above, and those with risk factors (some get it earlier, at booking). You fast overnight, then drink a sugar drink and give blood twice.",
     "KKM menguji ibu berumur 25 tahun ke atas dan yang ada faktor risiko (ada yang lebih awal, semasa pendaftaran). Anda berpuasa semalaman, minum air gula, dan diambil darah dua kali.", ""),
    ("v24", 24, 26, "🩺", "Check-up", "Pemeriksaan", "", "", ""),
    ("tdap", 28, 32, "💉", "Tdap vaccine (whooping cough) - free at KKM clinics", "Vaksin Tdap (batuk kokol) - percuma di klinik KKM",
     "Given in every pregnancy since 26 May 2025, so your baby is protected before their own first vaccine at 2 months.",
     "Diberi pada setiap kehamilan sejak 26 Mei 2025, supaya bayi dilindungi sebelum vaksin pertamanya pada umur 2 bulan.", "vaccines.html"),
    ("v28", 28, 30, "🩺", "Check-up - visits now every 2 weeks", "Pemeriksaan - kini setiap 2 minggu",
     "From 28 weeks the klinik also checks baby's growth and heartbeat at each visit.",
     "Mulai 28 minggu, klinik juga memeriksa tumbesaran dan degupan jantung bayi setiap lawatan.", ""),
    ("kicks", 28, 40, "👣", "Get to know your baby's movements", "Kenali pergerakan bayi anda",
     "If baby moves less than usual, go to the klinik or hospital the same day.", "Jika bayi kurang bergerak daripada biasa, pergi ke klinik atau hospital pada hari yang sama.", "labour.html"),
    ("plan", 36, 37, "📋", "Delivery plan - where you'll give birth - visits now every week", "Pelan bersalin - di mana anda akan bersalin - kini setiap minggu",
     "Pack your hospital bag now.", "Siapkan beg hospital sekarang.", "hospital-bag.html"),
    ("due", 40, 40, "🎉", "Due date - if labour hasn't started, your klinik will plan the next step", "Tarikh jangkaan - jika belum bersalin, klinik akan merancang langkah seterusnya",
     "", "", ""),
    ("post", 46, 46, "🤱", "Your postnatal check (about 6 weeks after birth)", "Pemeriksaan postnatal anda (sekitar 6 minggu selepas bersalin)",
     "If you had diabetes in pregnancy, you'll be offered another glucose test after delivery.",
     "Jika anda menghidap diabetes semasa hamil, anda akan ditawarkan ujian glukosa sekali lagi selepas bersalin.", "pantang.html"),
]

FOOD_AVOID = [
    ("Raw or undercooked meat, seafood, fish, eggs and poultry - and raw food like sushi",
     "Daging, makanan laut, ikan, telur dan ayam mentah atau separa masak - serta makanan mentah seperti sushi"),
    ("Unpasteurised milk and cheese", "Susu dan keju yang tidak dipasteur"),
    ("Food that may contain mercury - ask your klinik which fish to limit", "Makanan yang mungkin tercemar merkuri - tanya klinik ikan mana yang perlu dihadkan"),
    ("Too much caffeine: coffee, tea, chocolate drinks, fizzy drinks and energy drinks", "Kafein berlebihan: kopi, teh, minuman coklat, minuman berkarbonat dan minuman tenaga"),
    ("Alcohol", "Alkohol"),
    ("Herbal products and jamu - ask your doctor first", "Produk herba dan jamu - tanya doktor dahulu"),
    ("Root vegetables that aren't washed well", "Sayuran berakar yang tidak dibasuh bersih"),
]
FOOD_DO = [
    ("Eat a variety of food from every food group, and drink enough plain water.", "Makan pelbagai jenis makanan dari setiap kumpulan makanan, dan minum air kosong secukupnya."),
    ("Take the folic acid and iron your klinik gives you.", "Ambil asid folik dan zat besi yang diberi oleh klinik."),
    ("Cravings are fine in moderation. If you crave non-food things like soil or chalk, tell your doctor.",
     "Mengidam tidak mengapa jika sederhana. Jika anda mengidam benda bukan makanan seperti tanah atau kapur, beritahu doktor."),
]

FAST_BREAK = [
    ("Dizziness, extreme weakness or drowsiness", "Pening, sangat lemah atau mengantuk"),
    ("Shivering, cold sweat or confusion", "Menggigil, berpeluh sejuk atau keliru"),
    ("Signs of dehydration - very thirsty, dark urine, passing little urine", "Tanda dehidrasi - sangat dahaga, air kencing pekat, kurang buang air kecil"),
    ("Your baby moving less than usual - break your fast and contact your klinik straight away", "Bayi kurang bergerak daripada biasa - berbuka dan hubungi klinik segera"),
]

# Airlines: (name, single pregnancy EN, MS, multiple EN, MS, letter EN, MS, url, checked)
AIRLINES = [
    ("AirAsia",
     "Up to 28 weeks: OK, sign a Release & Indemnity form at check-in. 29-36 weeks: also a doctor's letter. 37 weeks and above: not allowed.",
     "Sehingga 28 minggu: boleh, isi borang Release & Indemnity semasa daftar masuk. 29-36 minggu: perlu juga surat doktor. 37 minggu ke atas: tidak dibenarkan.",
     "Letter from 29 weeks; not allowed from 33 weeks.", "Surat dari 29 minggu; tidak dibenarkan dari 33 minggu.",
     "Doctor's letter dated within 30 days of your flight.", "Surat doktor bertarikh dalam 30 hari sebelum penerbangan.",
     "https://support.airasia.com/s/article/I-am-pregnant-en?language=en_GB", "2026-11-26"),
    ("Malaysia Airlines",
     "After 28 weeks: bring a letter from your doctor or midwife. Not accepted after 36 weeks. A Release & Indemnity form is signed at check-in.",
     "Selepas 28 minggu: bawa surat daripada doktor atau bidan. Tidak diterima selepas 36 minggu. Borang Release & Indemnity diisi semasa daftar masuk.",
     "Not accepted after 32 weeks - the same for a complicated pregnancy.", "Tidak diterima selepas 32 minggu - sama juga bagi kehamilan berkomplikasi.",
     "Letter issued within 10 days of departure. With complications you need a MEDIF medical clearance form.",
     "Surat dikeluarkan dalam 10 hari sebelum berlepas. Jika ada komplikasi, perlu borang kelulusan perubatan MEDIF.",
     "https://www.malaysiaairlines.com/content/dam/mh/my/en/pdf-file/2024-12-28-General-Conditions-of-Carriage-Malaysia-Airlines.pdf", "2026-11-26"),
]

# EPDS: (statement, [(answer, score)]), English official text. MS gloss is a plain explanation, not a validated translation.
EPDS = [
    ("I have been able to laugh and see the funny side of things", "Saya boleh ketawa dan nampak sisi lucu sesuatu perkara",
     [("As much as I always could", 0), ("Not quite so much now", 1), ("Definitely not so much now", 2), ("Not at all", 3)]),
    ("I have looked forward with enjoyment to things", "Saya menantikan sesuatu dengan rasa seronok",
     [("As much as I ever did", 0), ("Rather less than I used to", 1), ("Definitely less than I used to", 2), ("Hardly at all", 3)]),
    ("I have blamed myself unnecessarily when things went wrong", "Saya menyalahkan diri tanpa sebab apabila sesuatu tidak kena",
     [("Yes, most of the time", 3), ("Yes, some of the time", 2), ("Not very often", 1), ("No, never", 0)]),
    ("I have been anxious or worried for no good reason", "Saya cemas atau risau tanpa sebab yang munasabah",
     [("No, not at all", 0), ("Hardly ever", 1), ("Yes, sometimes", 2), ("Yes, very often", 3)]),
    ("I have felt scared or panicky for no very good reason", "Saya berasa takut atau panik tanpa sebab yang jelas",
     [("Yes, quite a lot", 3), ("Yes, sometimes", 2), ("No, not much", 1), ("No, not at all", 0)]),
    ("Things have been getting on top of me", "Banyak perkara terasa terlalu berat untuk saya",
     [("Yes, most of the time I haven't been able to cope at all", 3), ("Yes, sometimes I haven't been coping as well as usual", 2),
      ("No, most of the time I have coped quite well", 1), ("No, I have been coping as well as ever", 0)]),
    ("I have been so unhappy that I have had difficulty sleeping", "Saya begitu sedih sehingga sukar tidur",
     [("Yes, most of the time", 3), ("Yes, sometimes", 2), ("Not very often", 1), ("No, not at all", 0)]),
    ("I have felt sad or miserable", "Saya berasa sedih atau sengsara",
     [("Yes, most of the time", 3), ("Yes, quite often", 2), ("Not very often", 1), ("No, not at all", 0)]),
    ("I have been so unhappy that I have been crying", "Saya begitu sedih sehingga menangis",
     [("Yes, most of the time", 3), ("Yes, quite often", 2), ("Only occasionally", 1), ("No, never", 0)]),
    ("The thought of harming myself has occurred to me", "Terlintas di fikiran untuk mencederakan diri sendiri",
     [("Yes, quite often", 3), ("Sometimes", 2), ("Hardly ever", 1), ("Never", 0)]),
]
EPDS_ANS_MS = {
    "As much as I always could": "Sama seperti biasa", "Not quite so much now": "Kurang sedikit sekarang",
    "Definitely not so much now": "Memang kurang sekarang", "Not at all": "Langsung tidak",
    "As much as I ever did": "Sama seperti dahulu", "Rather less than I used to": "Agak kurang daripada dahulu",
    "Definitely less than I used to": "Memang kurang daripada dahulu", "Hardly at all": "Hampir tidak langsung",
    "Yes, most of the time": "Ya, hampir sepanjang masa", "Yes, some of the time": "Ya, kadang-kadang",
    "Not very often": "Tidak begitu kerap", "No, never": "Tidak, tidak pernah", "No, not at all": "Tidak, langsung tidak",
    "Hardly ever": "Jarang sekali", "Yes, sometimes": "Ya, kadang-kadang", "Yes, very often": "Ya, sangat kerap",
    "Yes, quite a lot": "Ya, agak kerap", "No, not much": "Tidak, tidak banyak",
    "Yes, most of the time I haven't been able to cope at all": "Ya, hampir sepanjang masa saya langsung tidak dapat menghadapinya",
    "Yes, sometimes I haven't been coping as well as usual": "Ya, kadang-kadang saya tidak dapat menghadapinya seperti biasa",
    "No, most of the time I have coped quite well": "Tidak, kebanyakan masa saya dapat menghadapinya dengan baik",
    "No, I have been coping as well as ever": "Tidak, saya dapat menghadapinya seperti biasa",
    "Yes, quite often": "Ya, agak kerap", "Only occasionally": "Sekali-sekala sahaja", "Sometimes": "Kadang-kadang", "Never": "Tidak pernah",
}

AQIQAH_STEPS = [
    ("name", "Give your baby a good name", "Beri bayi nama yang baik", "Sunnah on the 7th day.", "Sunat pada hari ketujuh."),
    ("shave", "Shave baby's hair (cukur jambul)", "Cukur rambut bayi (cukur jambul)",
     "You may shave before the aqiqah slaughter, though slaughtering first is better.", "Boleh dicukur sebelum sembelihan aqiqah, tetapi menyembelih dahulu adalah lebih baik."),
    ("weigh", "Give charity in gold or silver equal to the hair's weight - if you can", "Sedekah emas atau perak seberat rambut - mengikut kemampuan",
     "Sunnah, not compulsory. There is no such thing as 'zakat rambut bayi'.", "Sunat, bukan wajib. Tiada istilah 'zakat rambut bayi' dalam syariat."),
    ("goat", "Aqiqah: 2 goats for a boy, 1 for a girl", "Aqiqah: 2 ekor kambing untuk lelaki, 1 untuk perempuan",
     "One goat for a boy is still enough in the Syafi'i school.", "Seekor kambing untuk anak lelaki sudah memadai menurut mazhab Syafi'i."),
]

MILESTONES = [  # (months, [(EN, MS)])  CDC "Learn the Signs. Act Early." - things most children (75%) do by this age
    (2, [("Calms down when spoken to or picked up", "Tenang apabila diajak bercakap atau didukung"), ("Makes sounds other than crying", "Mengeluarkan bunyi selain menangis"),
         ("Looks at a toy for several seconds", "Melihat mainan selama beberapa saat"), ("Holds head up when on tummy", "Mengangkat kepala ketika meniarap")]),
    (4, [("Smiles on their own to get your attention", "Senyum sendiri untuk menarik perhatian anda"), ("Makes cooing sounds like 'oooo', 'aahh'", "Mengagah seperti 'oooo', 'aahh'"),
         ("Looks at their hands with interest", "Melihat tangannya dengan minat"), ("Holds head steady when you hold them", "Kepala stabil apabila didukung")]),
    (6, [("Knows familiar people", "Mengenali orang yang biasa"), ("Takes turns making sounds with you", "Bergilir-gilir mengeluarkan bunyi dengan anda"),
         ("Reaches to grab a toy they want", "Mencapai mainan yang dimahukan"), ("Rolls from tummy to back", "Berguling dari meniarap ke terlentang")]),
    (9, [("Is shy, clingy or fearful around strangers", "Malu, berkepit atau takut dengan orang asing"), ("Makes sounds like 'mamamama' and 'bababa'", "Bunyi seperti 'mamamama' dan 'bababa'"),
         ("Looks for objects dropped out of sight", "Mencari barang yang jatuh dari pandangan"), ("Sits without support", "Duduk tanpa sokongan")]),
    (12, [("Plays games with you, like pat-a-cake", "Bermain dengan anda, seperti tepuk-tepuk amai"), ("Calls a parent 'mama', 'dada' or another special name", "Memanggil 'mama', 'papa' atau nama panggilan lain"),
          ("Puts something in a container, like a block in a cup", "Memasukkan barang ke dalam bekas, seperti blok ke dalam cawan"), ("Walks holding on to furniture", "Berjalan berpaut pada perabot")]),
    (15, [("Shows affection - hugs, cuddles or kisses", "Menunjukkan kasih sayang - peluk atau cium"), ("Tries to say one or two words besides 'mama' or 'dada'", "Cuba menyebut satu atau dua perkataan selain 'mama' atau 'papa'"),
          ("Stacks at least two small objects, like blocks", "Menyusun sekurang-kurangnya dua objek kecil, seperti blok"), ("Takes a few steps on their own", "Melangkah beberapa langkah sendiri")]),
    (18, [("Points to show you something interesting", "Menunjuk untuk menunjukkan sesuatu yang menarik"), ("Tries to say three or more words besides 'mama' or 'dada'", "Cuba menyebut tiga perkataan atau lebih selain 'mama' atau 'papa'"),
          ("Plays with toys in a simple way, like pushing a toy car", "Bermain dengan cara mudah, seperti menolak kereta mainan"), ("Walks without holding on", "Berjalan tanpa berpaut")]),
    (24, [("Notices when others are hurt or upset", "Perasan apabila orang lain sakit atau sedih"), ("Says at least two words together, like 'more milk'", "Menyebut sekurang-kurangnya dua perkataan bersama, seperti 'nak susu'"),
          ("Plays with more than one toy at the same time", "Bermain dengan lebih daripada satu mainan serentak"), ("Runs", "Berlari")]),
]

SLEEP = [  # (age EN, MS, hours)
    ("Newborn (0-3 months)", "Bayi baru lahir (0-3 bulan)", "14-17"),
    ("4-12 months", "4-12 bulan", "12-16"),
    ("1-2 years", "1-2 tahun", "11-14"),
    ("3-5 years", "3-5 tahun", "10-13"),
]
SAFE_SLEEP = [
    ("Put baby on their back for every sleep - not on the tummy or side.", "Tidurkan bayi secara terlentang setiap kali - bukan meniarap atau mengiring."),
    ("Use a firm, flat mattress.", "Gunakan tilam yang rata dan keras."),
    ("Keep pillows, thick blankets and soft toys out of the cot.", "Jauhkan bantal, selimut tebal dan anak patung dari katil bayi."),
    ("Dress baby lightly and don't over-wrap - babies shouldn't get too hot.", "Pakaikan bayi pakaian nipis dan jangan bedung terlalu tebal - bayi tidak patut kepanasan."),
    ("A cot next to your bed is safer than sharing your bed.", "Katil bayi di sebelah katil anda lebih selamat daripada berkongsi katil."),
]

SOLIDS = [
    ("At 6 months (180 days), start other food - and keep breastfeeding until 2 years.", "Pada umur 6 bulan (180 hari), mula beri makanan lain - dan teruskan penyusuan susu ibu sehingga 2 tahun."),
    ("6-8 months: 2-3 meals a day plus 1-2 healthy snacks. Start with 2-3 tablespoons a meal and slowly build up to ½ cup.",
     "6-8 bulan: 2-3 kali makan sehari serta 1-2 snek berkhasiat. Mulakan dengan 2-3 sudu besar setiap kali makan dan tingkatkan perlahan-lahan hingga ½ cawan."),
    ("First week: finely blended food. Then puréed, mashed and semi-solid - change the texture step by step as baby grows.",
     "Minggu pertama: makanan dikisar halus. Kemudian dipuri, dilecek dan separa pejal - ubah tekstur sedikit demi sedikit mengikut umur."),
    ("No salt, sugar or artificial flavouring before 1 year.", "Tiada garam, gula atau perisa tiruan sebelum umur 1 tahun."),
    ("No fruit or vegetable juice before 1 year.", "Tiada jus buah atau sayur sebelum umur 1 tahun."),
    ("No honey before 1 year - including yogurt, cereal or biscuits made with honey.", "Tiada madu sebelum umur 1 tahun - termasuk yogurt, bijirin atau biskut yang mengandungi madu."),
    ("Always stay with your baby while they eat.", "Sentiasa duduk bersama bayi semasa dia makan."),
]

JAUNDICE_URGENT = [
    ("Yellow skin or eyes in the first 24 hours after birth", "Kulit atau mata kuning dalam 24 jam pertama selepas lahir"),
    ("The yellow is getting worse quickly", "Kuning semakin teruk dengan cepat"),
    ("Baby is very sleepy, floppy or not feeding well", "Bayi sangat mengantuk, lembik atau tidak mahu menyusu"),
    ("Pale stools or dark urine", "Najis pucat atau air kencing pekat"),
]
G6PD_AVOID = [
    ("Naphthalene - mothballs (ubat gegat). Don't use them on clothes.", "Naftalena - ubat gegat. Jangan gunakan pada pakaian."),
    ("Fava beans (kacang parang)", "Kacang parang (fava)"),
    ("Some medicines, e.g. certain antibiotics and anti-malaria drugs - always tell the doctor or pharmacist your child has G6PD deficiency",
     "Sesetengah ubat, contohnya antibiotik dan ubat antimalaria tertentu - sentiasa beritahu doktor atau ahli farmasi anak anda kekurangan G6PD"),
    ("Certain Chinese herbs and traditional medicines - ask first", "Sesetengah herba Cina dan ubat tradisional - tanya dahulu"),
]
