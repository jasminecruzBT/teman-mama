"""Site settings. Edit these, then run `python build.py`."""

# Working name - run a name check before buying a web address.
SITE_NAME = "Teman Mama"

# Full web address once you have one, e.g. "https://temanmama.my" (no trailing slash).
# Leave empty until then: canonical links, language alternates and sitemap.xml are skipped.
BASE_URL = "https://jasminecruzbt.github.io/teman-mama"

# Shown on the About / Privacy pages and on the "list your centre" buttons.
# Leave empty to hide those buttons.
CONTACT_EMAIL = ""

# Google AdSense publisher id, e.g. "ca-pub-1234567890123456". Empty = no ads at all.
ADSENSE_CLIENT = ""
# Optional manual ad units (slot ids from your AdSense account). With none set,
# AdSense "Auto ads" decides where to place ads.
AD_SLOTS = {"in_content": "", "bottom": ""}

# Shop links. Each item on the hospital-bag list links to a Shopee search.
# After joining the Shopee Affiliate Programme, paste your affiliate links here
# (key = the item key used in content/pages.py), and they replace the plain search links.
SHOP_SEARCH_URL = "https://shopee.com.my/search?keyword={q}"
# Made 25 Nov 2026 in the Shopee Affiliate dashboard (Offer > Custom Link), tagged
# Sub_id1=temanmama, Sub_id2=hospitalbag. Each points at a Shopee CATEGORY page
# (search pages don't earn commission). Shopee's tree is only 2 levels deep, so some
# items share a category.
AFFILIATE_LINKS = {
    "nursing_tops": "https://s.shopee.com.my/5LDkUZdhXe",          # Women Clothes > Maternity Wear
    "nursing_bra": "https://s.shopee.com.my/5LDkUZdhXe",           # Women Clothes > Maternity Wear
    "maternity_pads": "https://s.shopee.com.my/5VXAgsd4Ch",        # Baby & Toys > Maternity Care
    "disposable_underwear": "https://s.shopee.com.my/5VXAgsd4Ch",  # Baby & Toys > Maternity Care
    "nipple_cream": "https://s.shopee.com.my/6L6HgPZtVs",          # Baby & Toys > Feeding & Nursing
    "straw_bottle": "https://s.shopee.com.my/6VPhsiZGAv",          # Home & Living > Kitchen & Dining
    "newborn_clothes": "https://s.shopee.com.my/60TRHnbABq",       # Baby & Kids Fashion > Baby Clothing
    "mittens": "https://s.shopee.com.my/60TRHnbABq",               # Baby & Kids Fashion > Baby Clothing
    "swaddle": "https://s.shopee.com.my/1LhbjFf3l8",               # Baby & Toys > Nursery
    "blanket": "https://s.shopee.com.my/1LhbjFf3l8",               # Baby & Toys > Nursery
    "newborn_diapers": "https://s.shopee.com.my/1W11vYeQQB",       # Baby & Toys > Diapers & Potties
    "wipes": "https://s.shopee.com.my/9AQT3eBErg",                 # Baby & Toys > Bath & Toiletries
    "car_seat": "https://s.shopee.com.my/9072rLBsCf",              # Baby & Toys > Baby Gear
    "powerbank": "https://s.shopee.com.my/8pncf2CVXe",             # Mobile & Accessories > Powerbanks
}
