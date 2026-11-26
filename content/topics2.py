"""Content for the second batch of topic pages (added 26 Nov 2026). English + Bahasa Melayu.

Sources (checked 26 Nov 2026):
- KKM Perinatal Care Manual, 3rd edition (2016), hosted by JKN Selangor:
  https://jknselangor.moh.gov.my/documents/pdf/2016/garis_panduan/kesihatan_ibu/article11.pdf
  p.46 fetal movements (<10 in 12 hours from 28 weeks), p.47 anaemia (Hb < 11 g/dL), p.62 exclusive breastfeeding,
  p.147-148 postnatal red/yellow codes, p.152 contraception within 1 month + sex after bleeding stops,
  p.224 breastfeeding on cues + signs of enough milk.
- KKM Rekod Kesihatan Ibu KIK 1(b)-96 (pindaan 2020): p.13 weight-gain table (IOM 2009, WHO BMI), p.14 Hb chart
  (ringan 9-<11, sederhana 7-<9, teruk <7 g/dL).
  https://hq.moh.gov.my/bpkk/images/3.Penerbitan/2.Orang_Awam/6.Kesihatan_Ibu/PDF/3.GARIS_PANDUAN/3_rekod_kesihatan_ibu_kik_1_b_96_pindaan_2020.pdf
- MyGOV: home visits after birth + klinik check one month after birth.
- NHS (nhs.uk) pregnancy/baby pages for everyday self-care tips where KKM gives none (marked "NHS" on the page).
"""

KIK = "https://hq.moh.gov.my/bpkk/images/3.Penerbitan/2.Orang_Awam/6.Kesihatan_Ibu/PDF/3.GARIS_PANDUAN/3_rekod_kesihatan_ibu_kik_1_b_96_pindaan_2020.pdf"
PCM = "https://jknselangor.moh.gov.my/documents/pdf/2016/garis_panduan/kesihatan_ibu/article11.pdf"
MYGOV_POSTNATAL = "https://www.malaysia.gov.my/my/personas/ibu-hamil/fasa-selepas-bersalin/kesihatan-ibu-selepas-bersalin"

# Weight gain by BMI before pregnancy - KKM pink book p.13 (IOM 2009). Row: (BMI up to, total lo, total hi, wk lo, wk hi, key)
WEIGHT_GAIN = [
    (18.5, 12.5, 18.0, 0.44, 0.58, "under"),
    (25.0, 11.5, 16.0, 0.35, 0.50, "normal"),
    (30.0, 7.0, 11.5, 0.23, 0.33, "over"),
    (999, 5.0, 9.0, 0.17, 0.27, "obese"),
]

# Common pregnancy symptoms: (icon, name EN, name MS, self-care EN, self-care MS, see-klinik EN, see-klinik MS, urgent?)
SYMPTOMS = [
    ("🤢", "Nausea & vomiting (morning sickness)", "Loya & muntah (alahan)",
     "Eat small meals often - plain, starchy, low-fat food. Don't let your stomach go empty. Sip drinks little and often.",
     "Makan sedikit tetapi kerap - makanan ringkas berkanji dan rendah lemak. Jangan biar perut kosong. Hirup minuman sedikit demi sedikit.",
     "You can't keep food or drinks down for 24 hours, your urine is very dark or you haven't passed urine for 8 hours, you feel faint when you stand, or you vomit blood.",
     "Tidak dapat menelan makanan atau minuman selama 24 jam, air kencing sangat gelap atau tidak kencing selama 8 jam, rasa hendak pitam apabila berdiri, atau muntah darah.", False),
    ("🔥", "Heartburn", "Pedih ulu hati",
     "Eat smaller meals more often. Raise your head and shoulders on pillows at night. Cut down on caffeine and rich, spicy or fatty food.",
     "Makan dalam hidangan kecil tetapi lebih kerap. Tinggikan kepala dan bahu dengan bantal ketika tidur. Kurangkan kafein serta makanan berlemak, pedas atau berminyak.",
     "It doesn't get better with these changes. Go TODAY if it comes with a bad headache, blurred vision or sudden swelling.",
     "Tidak berkurang walaupun selepas perubahan ini. Pergi HARI INI jika disertai sakit kepala teruk, pandangan kabur atau bengkak mengejut.", False),
    ("🦴", "Back pain", "Sakit belakang",
     "Bend your knees and keep your back straight when you lift. Wear flat shoes. A warm bath or massage can help. Paracetamol is safe in pregnancy - ask your pharmacist.",
     "Bengkokkan lutut dan luruskan belakang ketika mengangkat barang. Pakai kasut rata. Mandi air suam atau urutan boleh membantu. Paracetamol selamat semasa hamil - tanya ahli farmasi.",
     "In the 2nd or 3rd trimester it can be early labour. Get checked straight away if it comes with fever, bleeding or pain when you pee. Losing feeling in your legs, bottom or private parts is an emergency.",
     "Pada trimester ke-2 atau ke-3 ia mungkin tanda awal bersalin. Dapatkan pemeriksaan segera jika disertai demam, pendarahan atau sakit ketika kencing. Hilang rasa pada kaki, punggung atau kemaluan adalah kecemasan.", False),
    ("🦵", "Leg cramps", "Kejang kaki",
     "Pull your toes hard up towards your ankle, or rub the muscle hard. Gentle exercise and ankle circles help prevent them.",
     "Tarik jari kaki kuat-kuat ke arah buku lali, atau gosok otot itu dengan kuat. Senaman ringan dan memusingkan buku lali membantu mencegahnya.",
     "One calf is swollen, red or painful - get checked straight away (it can be a blood clot).",
     "Satu betis bengkak, merah atau sakit - dapatkan pemeriksaan segera (mungkin darah beku).", False),
    ("🚽", "Constipation", "Sembelit",
     "Drink plenty of water, eat high-fibre food (fruit, vegetables, wholegrains) and keep gently active.",
     "Minum air secukupnya, makan makanan tinggi serat (buah, sayur, bijirin penuh) dan kekal aktif secara ringan.",
     "It doesn't improve. Iron tablets can cause it - ask your klinik before you stop taking them.",
     "Tidak bertambah baik. Pil zat besi boleh menyebabkannya - tanya klinik sebelum berhenti mengambilnya.", False),
    ("🦶", "Swollen feet & ankles", "Bengkak kaki & buku lali",
     "Avoid standing for long. Rest with your feet up, wear comfortable shoes and take short walks.",
     "Elakkan berdiri lama. Rehat dengan kaki diangkat, pakai kasut yang selesa dan berjalan sedikit.",
     "Go TODAY if swelling of your face, hands or feet comes on suddenly - especially with a bad headache, blurred vision or flashing lights, or pain just below your ribs. These can be signs of pre-eclampsia (high blood pressure in pregnancy).",
     "Pergi HARI INI jika muka, tangan atau kaki tiba-tiba bengkak - terutama jika disertai sakit kepala teruk, pandangan kabur atau nampak cahaya berkelip, atau sakit di bawah tulang rusuk. Ini mungkin tanda pre-eklampsia (darah tinggi semasa hamil).", True),
    ("🤕", "Headaches", "Sakit kepala",
     "Rest and drink enough water. Paracetamol is the first choice of painkiller in pregnancy.",
     "Rehat dan minum air secukupnya. Paracetamol ialah ubat tahan sakit pilihan pertama semasa hamil.",
     "Go TODAY if it's severe, or comes with blurred vision, flashing lights, pain below your ribs, vomiting or sudden swelling.",
     "Pergi HARI INI jika sakit kepala teruk, atau disertai pandangan kabur, cahaya berkelip, sakit di bawah tulang rusuk, muntah atau bengkak mengejut.", True),
    ("💧", "Vaginal discharge", "Keputihan",
     "More discharge is normal in pregnancy. Healthy discharge is thin, clear or milky white and doesn't smell bad. Loose cotton underwear helps.",
     "Keputihan yang lebih banyak adalah normal semasa hamil. Keputihan yang sihat adalah cair, jernih atau putih susu dan tidak berbau busuk. Seluar dalam kapas yang longgar membantu.",
     "It smells bad, is green or yellow, itches or hurts, or it stings when you pee. If watery fluid leaks out, go to hospital - your waters may have broken.",
     "Berbau busuk, berwarna hijau atau kuning, gatal atau pedih, atau pedih ketika kencing. Jika air jernih meleleh keluar, pergi ke hospital - air ketuban mungkin pecah.", False),
    ("🩸", "Spotting or bleeding", "Tompok darah atau pendarahan",
     "Light spotting can happen in early pregnancy - but always get it checked.",
     "Tompok darah ringan boleh berlaku pada awal kehamilan - tetapi sentiasa dapatkan pemeriksaan.",
     "Any bleeding: call your klinik or hospital the same day. Heavy bleeding, severe tummy pain or feeling faint: go to hospital now or call 999.",
     "Sebarang pendarahan: hubungi klinik atau hospital pada hari yang sama. Pendarahan banyak, sakit perut teruk atau rasa hendak pitam: pergi ke hospital sekarang atau hubungi 999.", True),
    ("〰️", "Practice contractions (Braxton Hicks)", "Kontraksi latihan (Braxton Hicks)",
     "Tightenings that are usually painless, don't last long, aren't regular and don't build up.",
     "Rasa mengeras pada perut yang biasanya tidak sakit, tidak lama, tidak tetap dan tidak semakin kuat.",
     "They get longer, stronger and closer together - that's labour. Call your hospital.",
     "Semakin lama, semakin kuat dan semakin kerap - itu tanda bersalin. Hubungi hospital.", False),
    ("🚻", "Peeing more often", "Kerap kencing",
     "Drink plenty during the day but less in the late evening.",
     "Minum secukupnya pada waktu siang tetapi kurangkan pada lewat petang dan malam.",
     "It hurts or burns, or there's blood - see a doctor within 24 hours (you may have a urine infection).",
     "Sakit atau pedih, atau ada darah - jumpa doktor dalam masa 24 jam (mungkin jangkitan saluran kencing).", False),
    ("😴", "Tiredness", "Letih",
     "Rest as much as you can and accept help. Sleep on your side (left or right).",
     "Rehat sebanyak mungkin dan terima bantuan. Tidur secara mengiring (kiri atau kanan).",
     "You're also breathless, pale or your heart races - ask your klinik to check your HB.",
     "Anda juga sesak nafas, pucat atau jantung berdebar - minta klinik memeriksa paras HB anda.", False),
    ("👶", "Fewer baby movements", "Bayi kurang bergerak",
     "From 28 weeks, get to know your baby's pattern - use our kick counter.",
     "Mulai 28 minggu, kenali corak pergerakan bayi - guna pengira tendangan kami.",
     "Fewer than 10 movements in 12 hours (KKM) or any change in the pattern - go to a klinik or hospital straight away.",
     "Kurang daripada 10 pergerakan dalam 12 jam (KKM) atau sebarang perubahan corak - pergi ke klinik atau hospital segera.", True),
]

# Iron-rich food (NHS) and HB facts (KKM)
IRON_FOOD = [
    ("Red meat, chicken and fish", "Daging merah, ayam dan ikan"),
    ("Dark-green leafy vegetables (e.g. bayam, kangkung)", "Sayur berdaun hijau gelap (cth. bayam, kangkung)"),
    ("Beans, peas and lentils (e.g. dhal)", "Kekacang dan lentil (cth. dhal)"),
    ("Dried fruit such as raisins and dates", "Buah kering seperti kismis dan kurma"),
    ("Cereals and bread with added iron", "Bijirin dan roti yang ditambah zat besi"),
]

# Postnatal danger signs (KKM red code - go to hospital)
POSTNATAL_RED = [
    ("Heavy bleeding, or bleeding that gets heavier", "Pendarahan banyak, atau pendarahan yang bertambah"),
    ("Pain or swelling in your calf, or a red, swollen leg", "Betis sakit atau bengkak, atau kaki merah dan bengkak"),
    ("Chest pain or difficulty breathing", "Sakit dada atau susah bernafas"),
    ("Fever, or bad-smelling discharge from the vagina", "Demam, atau lelehan dari faraj yang berbau busuk"),
    ("Bad headache, dizziness, blurred vision, pain in the upper tummy or feeling sick", "Sakit kepala teruk, pening, pandangan kabur, sakit di bahagian atas perut atau rasa loya"),
    ("Your stitches or caesarean wound are red, swollen, painful or leaking", "Jahitan atau luka pembedahan caesarean merah, bengkak, sakit atau bernanah"),
]
