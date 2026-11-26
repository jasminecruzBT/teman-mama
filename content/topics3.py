"""Content for the third batch of topic pages (added 26 Nov 2026). English + Bahasa Melayu.

Every fact below was re-read on the official page or document on 26 Nov 2026:
- KKM Perinatal Care Manual, 3rd ed. (JKN Selangor PDF, `PCM`):
  printed p.105 pain relief in labour (pethidine not after 6 cm, Entonox 50:50, epidural only where there is an
  anaesthetist service, non-drug methods); p.114-116 stages of labour (stage 1: 8-24 h first labour / 3-12 h later,
  latent 0-4 cm, active > 4 cm; stage 2 commonly ends within 1 hour; stage 3 placenta 15-30 min);
  p.181 do not bathe baby in the first 6 hours; p.213 BCG soon after birth, usually day 2 or before discharge;
  p.223-226 newborn skin (erythema toxicum 40-70 %, milia, heat rash, cradle cap + olive oil, septic spots,
  oral thrush), cord care (drops off in 1-2 weeks, no dressing/binding, clean daily or when damp, alcohol swab given
  at discharge if moist/smelly, spot of blood normal), spit-up (clears by 1 year; tips; hospital signs);
  p.233 Table 5.12 traditional practices (good / harmful / unsure benefit).
- JKN Pahang (HoSHAS Temerloh) labour analgesia brochure: epidural most effective, given only by an anaesthetist,
  30-40 min to work; PCA fentanyl/remifentanil effective; Entonox & pethidine fairly effective; TENS,
  acupuncture, aromatherapy, massage - little evidence; side-effect table.
- NHS: signs of pregnancy (start ~4-6 weeks), doing a pregnancy test (from first day of missed period, or 21 days
  after unprotected sex; any time of day; negative -> retest in a few days), ectopic pregnancy symptoms (weeks 4-12;
  rupture -> 999), signs that labour has begun (show, waters, call when contractions every 5 min; urgent list),
  caesarean (planned usually from 39 weeks; reasons), washing and bathing your baby, BCG after-care,
  diarrhoea and vomiting, cough (> 3 weeks -> doctor).
- HASiL individual tax reliefs table, YA2025 (hasil.gov.my/individu/pelepasan-cukai/).
- Budget 2027 tax measures (belanjawan.mof.gov.my ... langkah-cukai.pdf) Lampiran 4: PROPOSED from YA2027 -
  postnatal care by a care centre or qualified individual up to RM3,000 inside a renamed RM10,000 health relief.
- LHDN STR 2026 FAQ (issued 24/10/2025): rates table, SARA monthly credit, applications all year from 13 Oct 2025.
- Sarawak KPWK: Bantuan Ibu Bersalin (page 99, updated 21 Apr 2026) RM450; Endowment Fund Sarawak (page 100,
  updated 3 Mar 2026) RM1,000.
- JKN Sarawak HFMD FAQ; JKN Perlis 'Kesan ubat batuk kepada kanak-kanak'; KKM Info Sihat 'Panduan penjagaan
  pesakit demam denggi di rumah' leaflet; WHO dengue fact sheet (avoid ibuprofen and aspirin; severe signs often
  come after the fever goes).
NOT used (could not confirm on an official page): other states' newborn payments (Penang, Pahang, N. Sembilan),
EPF i-Suri, PERKESO plans.
"""

PCM = "https://jknselangor.moh.gov.my/documents/pdf/2016/garis_panduan/kesihatan_ibu/article11.pdf"
PAHANG_EPIDURAL = "https://jknpahang.moh.gov.my/hoshas/images/pain_free/latest_brochure_obstetrik_analgesia_pfp.pdf"
HASIL_RELIEF = "https://www.hasil.gov.my/individu/pelepasan-cukai/"
BUDGET27_TAX = "https://belanjawan.mof.gov.my/pdf/belanjawan2027/ucapan/langkah-cukai.pdf"
STR_FAQ = "https://bantuantunai.hasil.gov.my/FAQ/FAQ%20SUMBANGAN%20TUNAI%20RAHMAH%20(STR)%202026.pdf"
STR_PORTAL = "https://bantuantunai.hasil.gov.my/"
SWK_BIB = "https://kpwk.sarawak.gov.my/web/subpage/webpage_view/99"
SWK_EFS = "https://kpwk.sarawak.gov.my/web/subpage/webpage_view/100"
HFMD_FAQ = "https://jknsarawak.moh.gov.my/hus/hfmd-faq/"
COUGH_KKM = "https://jknperlis.moh.gov.my/v3/index.php/info-kesihatan/124-kesan-ubat-batuk-kepada-kanak-kanak"
DENGUE_KKM = "https://infosihat.moh.gov.my/images/media_sihat/risalah/pdf/RISALAH%20DEMAM%20DENGGI.pdf"
DENGUE_WHO = "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue"

# STR 2026 (LHDN FAQ). Household income band -> amount by number of children [0, 1-2, 3-4, 5+]
STR_2026 = {"1": [700, 1200, 1700, 2200], "2": [200, 450, 700, 950]}

# HASiL YA2025 reliefs that matter to parents: (amount label, English, Malay)
TAX_RELIEFS = [
    ("RM2,000", "Each child under 18", "Setiap anak bawah 18 tahun"),
    ("RM2,000", "Child 18+ in A-Level, matriculation, certificate or pre-university studies", "Anak 18 tahun ke atas di peringkat A-Level, matrikulasi, sijil atau pra-universiti"),
    ("RM8,000", "Child 18+ at diploma level or higher in Malaysia (degree or higher abroad)", "Anak 18 tahun ke atas di peringkat diploma ke atas di Malaysia (ijazah ke atas di luar negara)"),
    ("RM8,000", "Child with a disability (another RM8,000 if 18+ and studying at diploma level or higher)", "Anak kurang upaya (tambahan RM8,000 jika 18 tahun ke atas dan belajar di peringkat diploma ke atas)"),
    ("RM1,000", "Breastfeeding equipment for a child aged 2 or under - once every 2 years", "Peralatan penyusuan ibu untuk anak berumur 2 tahun ke bawah - sekali setiap 2 tahun"),
    ("RM3,000", "Fees at a registered taska or tadika, child aged 6 or under", "Yuran taska atau tadika berdaftar, anak berumur 6 tahun ke bawah"),
    ("RM8,000", "Net savings in SSPN (deposits minus withdrawals in the year)", "Simpanan bersih dalam SSPN (simpanan tolak pengeluaran dalam tahun itu)"),
    ("RM10,000", "Medical: fertility treatment, serious illness, vaccinations (up to RM1,000), full check-ups (up to RM1,000) - for you, your spouse or child", "Perubatan: rawatan kesuburan, penyakit serius, pemvaksinan (had RM1,000), pemeriksaan penuh (had RM1,000) - untuk diri, pasangan atau anak"),
    ("RM6,000", "Learning-disability assessment or early intervention for a child 18 or under (within the RM10,000 medical limit)", "Penilaian atau intervensi awal kurang upaya pembelajaran untuk anak 18 tahun ke bawah (dalam had perubatan RM10,000)"),
]

# Early pregnancy signs (NHS)
EARLY_SIGNS = [
    ("📅", "A missed period", "Haid lewat atau tidak datang"),
    ("🩸", "Very light bleeding or spotting around the time your period is due (implantation bleeding)", "Pendarahan atau tompok darah yang sangat sedikit sekitar waktu haid sepatutnya datang (pendarahan implantasi)"),
    ("🤢", "Feeling or being sick - at any time of the day or night", "Loya atau muntah - pada bila-bila masa, siang atau malam"),
    ("😴", "Feeling extremely tired after your usual activities", "Terlalu letih selepas aktiviti harian biasa"),
    ("🤱", "Sore, larger or tender breasts", "Payudara sakit, membesar atau sensitif"),
    ("🚻", "Needing to pee more often (without pain)", "Lebih kerap kencing (tanpa rasa sakit)"),
    ("🚽", "Constipation", "Sembelit"),
    ("💧", "More vaginal discharge (without soreness or itching)", "Keputihan bertambah (tanpa rasa pedih atau gatal)"),
    ("👅", "A metallic taste in your mouth", "Rasa seperti logam di dalam mulut"),
    ("👃", "Sensitive to certain smells", "Sensitif kepada bau tertentu"),
    ("🍋", "Cravings for new foods, or going off foods you usually like", "Mengidam makanan baharu, atau tidak lalu makanan yang biasa digemari"),
    ("🎭", "Mood changes", "Perubahan emosi"),
]
