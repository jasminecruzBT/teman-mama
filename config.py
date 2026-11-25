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
AFFILIATE_LINKS = {
    # "maternity_pads": "https://s.shopee.com.my/xxxxxx",
}
