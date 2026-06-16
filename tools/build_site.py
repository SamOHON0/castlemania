#!/usr/bin/env python3
"""Castlemania site generator. Run: python3 tools/build_site.py
Regenerates every page in castlemania-site/ from tools/site_data.json.
URLs, meta titles and meta descriptions are preserved exactly (SEO)."""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'castlemania-site')
DATA = json.load(open(os.path.join(ROOT, 'tools', 'site_data.json'), encoding='utf-8'))
PRODUCTS = DATA['products']
CATS = DATA['categories']

PHONE = '089 415 6419'
TEL = 'tel:0894156419'
WA = 'https://wa.me/353894156419?text=Hi%20Castlemania%2C%20I%27d%20like%20to%20enquire%20about%20booking%20a%20bouncy%20castle.'
FB = 'https://www.facebook.com/Castlemania-105465194348441'
LOGO = 'https://www.castlemaniabouncycastles.com/theme/castlemania-logo@1x.png'
EMAIL = 'info@castlemaniabouncycastles.com'
SITE = 'https://www.castlemaniabouncycastles.com/'

# ---------- image helper: c_pad never crops, b_auto blends the padding ----------
def cdn_id(url):
    return url.rstrip('/').split('/')[-1] if url else None

# ---------- local self-hosted image variants (see tools/download_images.py) ----------
def card_src(p, prefix=''):
    return f"{prefix}img/cards/{p['slug']}.webp"

def large_src(p, prefix=''):
    return f"{prefix}img/large/{p['slug']}.webp"

def fit_dims(iw, ih, maxw, maxh):
    s = min(maxw / iw, maxh / ih, 1)
    return round(iw * s), round(ih * s)

def nat_img(p, w, attrs='', prefix=''):
    """<img> at the photo's own aspect ratio; width/height attrs reserve exact space."""
    h = round(w * p['ih'] / p['iw'])
    return f'<img src="{card_src(p, prefix)}" alt="{html.escape(p["name"])}" width="{w}" height="{h}"{attrs}>' 

BY_SLUG = {}
for p in PRODUCTS:
    slug = p['path'].split('/')[-1].replace('.html', '')
    p['slug'] = slug
    p['img_id'] = cdn_id(p['img'])
    BY_SLUG[slug] = p

# copy fixes
BY_SLUG['unicorn-giant-combi']['desc'] = BY_SLUG['unicorn-giant-combi']['desc'].replace(' Special offer price.', '')

CAT_ORDER = ['some-of-our-castles', 'giant-castles', 'bouncy-castles', 'giant-slides',
             'bounce-and-slide', 'cakes-and-party-foods', 'sweet-treats', 'new-inn']

CAT_META = {
    'some-of-our-castles': dict(color='pink',   icon='castle-turret', blurb='Browse every castle in one place'),
    'giant-castles':       dict(color='yellow', icon='crown',         blurb='Our biggest castles with slides built in'),
    'bouncy-castles':      dict(color='sky',    icon='confetti',      blurb='Classic castles for every garden size'),
    'giant-slides':        dict(color='green',  icon='lightning',     blurb='Massive slides for the brave ones'),
    'bounce-and-slide':    dict(color='orange', icon='rocket-launch', blurb='Bounce area and slide in one unit'),
    'cakes-and-party-foods': dict(color='pink', icon='cake',          blurb='Themed cakes and party packages'),
    'sweet-treats':        dict(color='purple', icon='ice-cream',     blurb='Sweets and desserts for the party table'),
    'new-inn':             dict(color='green',  icon='star',          blurb='Our newest units, fresh in'),
}
CAT_FACE = {  # representative photo per category (slug of product whose image we use)
    'some-of-our-castles': 'disney-princess-castle-giant-combi',
    'giant-castles': 'lightning-mcqueen-cars-giant-combi',
    'bouncy-castles': 'elsas-frozen-castle',
    'giant-slides': 'giant-sonic-slide',
    'bounce-and-slide': 'spiderman-bounce-and-slide',
    'cakes-and-party-foods': 'queen-elsa-cake',
    'sweet-treats': 'mermaid-cake',
    'new-inn': 'rainbow-high-giant-combi',
}

# ---------- detailed descriptions (Dana asked for these) ----------
EXTRA = {
 'barbie-dreamhouse-giant-combi': "Two kids can race down the double slide at the same time, so queues never build up even at big parties. The bounce area takes a full group of jumpers, and the bright Barbie pink stands out in photos from the far end of the garden.",
 'minecraft-obstacle-course': "A full 9m x 4m of crawls, squeezes and climbs that keeps energetic kids busy for hours, not minutes. Best suited to ages 5 and up who want more of a challenge than a standard bouncer.",
 'disney-princess-castle-giant-combi': "Inside there is a roomy bounce area, a basketball hoop and a slide, so there is something to do beyond jumping. It needs a 23ft x 26ft space with 10ft access, and adults are welcome on this one too.",
 'lol-doll-house-giant-combi': "The L.O.L artwork is big, bold and instantly recognised by fans. With the slide plus generous play zones it suits mixed age groups, and adults can join in.",
 'toy-story-giant-combi': "Buzz, Woody and the gang cover this giant combi inside and out. Internal obstacles and a large slide keep a full party moving, and it holds adults as well as kids.",
 'poppy-and-troll-gang-giant-combi': "One of our most colourful units, covered in Trolls characters from top to bottom. Overnight hire is available, handy if the party runs into the evening.",
 'lightning-mcqueen-cars-giant-combi': "Race fans get the full Radiator Springs treatment with Lightning McQueen artwork all round. The big slide lands on a 3ft platform and the bounce area suits adults and children together.",
 'spiderman-giant-combi': "Internal obstacles turn the bounce area into a mini assault course, and the rainproof design means an Irish summer shower will not stop the party. The large slide is the favourite part every time.",
 'frozen-giant-combi': "Elsa, Anna and Olaf cover this giant castle, with fun obstacles inside and a large slide out front. A guaranteed hit for Frozen fans aged right through primary school.",
 'gru-and-the-minions-giant-combi': "The Minions artwork gets a laugh from parents as well as kids. A proper giant combi with a slide, sized 21.5ft x 23ft, for non-stop family fun.",
 'paw-patrol-giant-combi': "Chase, Marshall and Skye welcome the jumpers in, and the rainproof canopy keeps the fun going whatever the sky does. One of our most requested castles year after year.",
 'rainbow-high-giant-combi': "Vibrant Rainbow High graphics make this one a favourite with older girls. The roomy bounce area and large slide give a full party plenty of space.",
 'unicorn-giant-combi': "Fully rainproof and absolutely covered in rainbows and unicorns. At our special offer price this is one of the best value giant combis in the range.",
 'paw-patrol-medium-combi': "All the Paw Patrol fun in a size that fits more compact gardens, needing just 21ft x 18ft. You still get a bounce area and a slide in one unit.",
 'elsas-frozen-castle': "Icy blue Frozen graphics with a built-in slide and lots of room to bounce. Sized for children only, it is perfect for a garden birthday party.",
 'lego-batman-combi': "Bold Lego Batman graphics on a compact combi that fits where the giants will not, needing only 14.5ft x 18ft. Bounce area plus slide, for children only.",
 'lego-friends-medium-combi': "Made for smaller gardens and younger jumpers, ideal for ages 3 to 10. A bounce area and slide in a friendly Lego Friends wrap.",
 'small-princess-bouncer': "Our most compact castle, made for small gardens and younger children aged roughly 2 to 8. Easy to fit, quick to set up, and the princess theme never misses.",
 'the-giant-barbie-princess-with-double-slide': "At 26ft x 34ft this is the biggest Barbie unit we carry, with two slides so twice the kids can go at once. Grass surfaces only, and worth every inch of garden it takes.",
 'tropical-forest-slide': "A towering jungle-themed slide that you can see from the other end of the estate. Fast, thrilling and built for big groups, adults included.",
 'giant-candy-slide': "Covered in sweets and lollipops, this giant slide is the photo backdrop of the party. Adults and children can ride, and it works brilliantly for fairs and fundraisers.",
 'giant-sonic-slide': "Two lanes side by side mean proper head-to-head racing, kids against teens against adults. The Sonic theme gets the older ones queuing up too.",
 'lego-movie-giant-combi': "Everything is awesome on this giant Lego Movie combi, with a spacious bounce area and a smooth large slide. Suits adults and children together.",
 'avengers-giant-combi': "Iron Man, Hulk, Thor and Captain America guard the bounce area, and the slide keeps the whole party moving. A reliable favourite for superhero fans of any age.",
 'spiderman-bounce-and-slide': "A roomy bounce area and slide packed into a unit that suits ages 3 to 12. Action-packed Spiderman artwork all round, needing 22ft x 17.8ft of space.",
 'the-city-of-spiderman-cakes-selection': "A full Spiderman dessert table: themed cake plus matching treats, made to order for your party size. Pair it with the Spiderman castle for the full superhero day.",
 'queen-elsa-cake': "Choose your size, flavour and filling and we build the Frozen centrepiece around it. Delivery available, and it pairs perfectly with our Frozen castles.",
 'barbie-cake': "A custom Barbie celebration cake made to your size and flavour. Order it with the Barbie Dreamhouse castle and the party theme is sorted from garden to table.",
 'princess-party-cake': "Tailored to your party theme in your choice of size and flavour. A match for the princess castles if you want the full fairytale setup.",
 'sweet-treats-selection': "Personalised themed sweets and desserts from EUR4 a piece, built around your party theme. Great for filling the party table alongside a cake.",
 'castle-and-cake-bundle': "Book any bouncy castle together with a themed cake and we add 12 themed cupcakes free. One booking, one delivery, and the whole party is sorted.",
 'vip-pamper-party': "Our top package: pampering for up to 6 children, a themed cake, 12 cupcakes and a bouncy castle, all arranged in one booking from EUR340. The birthday star gets the full VIP day.",
 'mermaid-cake': "Handcrafted with custom colours, flavours and dietary options to suit your party. The shimmering scales make it the centrepiece of any under-the-sea birthday.",
}

OFFERS = [
 dict(icon='balloon',  color='pink',   title='Bank Holiday Special', text='3 days for the price of 1. Make the most of the long weekend.', tag='BEST DEAL'),
 dict(icon='sun',      color='yellow', title='Summer Special', text='Pay for day one, get the second day for just EUR30, and the third day free.', tag='ON NOW'),
 dict(icon='calendar-check', color='sky', title='Midweek Offer', text='10% off any booking from Monday to Thursday.', tag=''),
 dict(icon='flower',   color='green',  title='Spring & Autumn', text='March, April and September: 2 days for the price of 1.', tag=''),
 dict(icon='snowflake', color='purple', title='Winter Prices', text='November to February: EUR50 off all units.', tag=''),
 dict(icon='chats-circle', color='orange', title='Not sure which fits?', text='Call or WhatsApp and we will sort the best deal for your date.', tag=''),
]

REVIEWS = [
 ("Brilliant service, highly recommend.", "Chelly'Pooh McCoy", "Oct 2024"),
 ("100% recommend. Lovely people to deal with. Good communication. Great choice, competitive price.", "Judi McShane", "Sep 2024"),
 ("Highly recommend Castlemania, they were so easy to deal with, castle was clean and working perfectly.", "Bernie Power", "Aug 2024"),
 ("Amazing service. Really reasonable rates. Will definitely use again.", "Michele Telford", "Aug 2024"),
 ("We had the Paw Patrol castle with slide for our daughter's 4th birthday. All 14 of the 4 year olds loved it.", "Amy Dowling", "Aug 2024"),
 ("I had the combi unicorn castle hired for the weekend. It was spotless and in great condition.", "Emma Carbery", "Mar 2022"),
 ("Beautiful castle and great service too. Highly recommended.", "Bree Cullen", "Feb 2022"),
 ("Lovely castle, great service. Would book again.", "Niamh", "May 2021"),
]

AREAS = [
 ('Laois', ['Portlaoise','Mountrath','Abbeyleix','Rathdowney','Mountmellick','Borris-in-Ossory','Stradbally','Emo','Ballylinan','Durrow','Castletown']),
 ('Kildare', ['Monasterevin','Kildare Town','Newbridge','Athy','Rathangan','Naas (on request)']),
 ('Kilkenny', ['Freshford','Johnstown','Urlingford','Castlecomer','Kilkenny City (on request)']),
 ('Tipperary', ['Roscrea','Templemore','Thurles','Littleton','Borrisoleigh']),
 ('Offaly', ['Tullamore','Birr','Shinrone','Kinnitty','Clonaslee']),
 ('Carlow', ['Carlow Town','Graiguecullen','Bagenalstown','Ballon']),
]

POPULAR = ['barbie-dreamhouse-giant-combi','disney-princess-castle-giant-combi','unicorn-giant-combi',
           'paw-patrol-giant-combi','spiderman-giant-combi','giant-sonic-slide','giant-candy-slide',
           'the-giant-barbie-princess-with-double-slide']

# =====================================================================
# CSS
# =====================================================================
CSS = """
:root{--ink:#1A1330;--cream:#FFF7EC;--white:#FFFFFF;--gray:#4A3F66;
--pink:#FF2E93;--pink-deep:#C70069;--pink-pale:#FFE3F1;
--yellow:#FFC400;--yellow-pale:#FFF3CC;
--sky:#00C2B2;--sky-pale:#D9F6F3;
--green:#21CE71;--green-pale:#DFF8EB;
--purple:#7B2FFF;--purple-pale:#EFE5FF;
--orange:#FF6B2C;--orange-pale:#FFE7DA;
--border:#1A1330;--r:26px;--sh:7px 7px 0 rgba(26,19,48,1)}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{background:var(--cream);scroll-behavior:smooth;overflow-x:hidden}
body{font-family:'DM Sans',sans-serif;background:var(--cream);color:var(--ink);overflow-x:hidden;-webkit-font-smoothing:antialiased;line-height:1.6}
body::before{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;background-image:radial-gradient(circle, rgba(123,47,255,.12) 1.5px, transparent 1.5px);background-size:26px 26px}
body::after{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;background-image:repeating-linear-gradient(45deg,transparent,transparent 14px,rgba(255,46,147,.05) 14px,rgba(255,46,147,.05) 28px)}
a{color:inherit;text-decoration:none}
h1,h2,h3,.disp{font-family:'Unbounded',sans-serif;font-weight:900;line-height:1.02;letter-spacing:-.02em;text-transform:uppercase}
img{display:block;max-width:100%}
.wrap{max-width:1200px;margin:0 auto;padding:0 24px}

/* reveal */
.rv{opacity:0;transform:translateY(28px)}
.rv.in{opacity:1;transform:none;transition:opacity .6s ease,transform .6s cubic-bezier(.34,1.56,.64,1)}
@media(prefers-reduced-motion:reduce){.rv{opacity:1;transform:none}}

/* ---------- nav: floating pill ---------- */
nav{position:sticky;top:12px;z-index:100;display:flex;align-items:center;justify-content:space-between;gap:12px;
max-width:1200px;margin:12px auto 0;width:calc(100% - 32px);
background:rgba(255,247,236,.86);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
border:4px solid var(--purple);border-radius:999px;padding:8px 12px 8px 14px;box-shadow:6px 6px 0 var(--pink)}
.logo-img{height:58px;width:auto;background:#fff;border:3px solid var(--ink);border-radius:14px;padding:4px 8px;box-shadow:3px 3px 0 var(--yellow)}
.nav-links{display:flex;gap:2px;list-style:none;align-items:center}
.nav-links>li>a{font-weight:700;font-size:14.5px;color:var(--ink);padding:9px 13px;border-radius:999px;transition:background .15s,transform .15s;display:block}
.nav-links>li>a:hover,.nav-links>li>a.on{background:var(--yellow);transform:translateY(-2px)}
.has-drop{position:relative}
.drop{position:absolute;top:calc(100% + 12px);left:0;background:var(--white);border:4px solid var(--ink);border-radius:22px;box-shadow:var(--sh);padding:8px;min-width:250px;display:none;flex-direction:column;gap:2px;z-index:120}
.has-drop:hover .drop,.has-drop:focus-within .drop{display:flex}
.drop a{font-size:14px;font-weight:700;padding:10px 14px;border-radius:14px;color:var(--ink)}
.drop a:hover{background:var(--pink-pale)}
.nav-btn{font-family:'Unbounded',sans-serif;font-weight:800;font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:#fff;background:var(--pink);border:3px solid var(--yellow);border-radius:999px;padding:11px 22px;box-shadow:4px 4px 0 var(--purple);transition:transform .2s,box-shadow .2s;white-space:nowrap}
.nav-btn:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--purple)}
.nav-btn:active{transform:translate(2px,2px);box-shadow:1px 1px 0 var(--purple)}
.burger{display:none;cursor:pointer;background:var(--purple);border:3px solid var(--yellow);border-radius:14px;width:46px;height:46px;flex-direction:column;align-items:center;justify-content:center;gap:4px}
.burger span{display:block;width:20px;height:3px;background:#fff;border-radius:2px;transition:all .2s}
.burger.open span:nth-child(1){transform:rotate(45deg) translate(5px,5px)}
.burger.open span:nth-child(2){opacity:0}
.burger.open span:nth-child(3){transform:rotate(-45deg) translate(4px,-4px)}
.mob-menu{display:none;position:fixed;top:84px;left:0;right:0;bottom:0;background:var(--cream);z-index:99;padding:24px;flex-direction:column;gap:6px;overflow-y:auto}
.mob-menu.open{display:flex}
.mob-menu a{font-weight:800;font-size:18px;color:var(--ink);padding:13px 16px;border-radius:16px;border:3px solid transparent}
.mob-menu a:hover{background:var(--white);border-color:var(--ink)}
.mob-menu .mob-sub{font-size:15px;padding:10px 30px;color:var(--gray);font-weight:600}

/* ---------- buttons ---------- */
.btn{display:inline-flex;align-items:center;gap:.55rem;cursor:pointer;font-family:'Unbounded',sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:.04em;font-size:.92rem;padding:16px 30px;border-radius:999px;transition:transform .25s cubic-bezier(.68,-.55,.265,1.55),box-shadow .25s ease}
.btn-p{color:#fff;background:linear-gradient(90deg,var(--pink),var(--purple) 55%,var(--sky));background-size:200% 100%;border:4px solid var(--yellow);box-shadow:0 0 22px rgba(255,46,147,.4),6px 6px 0 var(--yellow),12px 12px 0 var(--purple);animation:gshift 5s ease infinite}
.btn-p:hover{transform:scale(1.06) rotate(-1deg)}
.btn-p:active{transform:scale(.96)}
.btn-w{background:var(--white);color:var(--ink);border:4px dashed var(--sky);box-shadow:6px 6px 0 var(--sky)}
.btn-w:hover{background:var(--sky);color:#fff;border-style:solid;transform:translate(-3px,-3px);box-shadow:9px 9px 0 var(--purple)}
.btn-y{background:var(--yellow);color:var(--ink);border:4px solid var(--ink);box-shadow:6px 6px 0 var(--purple)}
.btn-y:hover{transform:translate(-3px,-3px);box-shadow:9px 9px 0 var(--purple)}
@keyframes gshift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

/* ---------- shared ---------- */
.sec{max-width:1200px;margin:0 auto;padding:96px 24px;position:relative}
.sec-head{margin-bottom:52px}
.sec-head h2{font-size:clamp(1.9rem,4.6vw,3.2rem)}
.sec-head p{font-size:16.5px;color:var(--gray);margin-top:14px;max-width:62ch;font-weight:500}
.sec-head.mid{text-align:center}.sec-head.mid p{margin-left:auto;margin-right:auto}
.sec-tag{display:inline-block;font-weight:800;text-transform:uppercase;letter-spacing:.16em;font-size:.8rem;padding:8px 18px;border-radius:999px;margin-bottom:16px;border:3px dashed var(--ink)}
.st-pink{background:var(--pink);color:#fff;border-color:var(--ink)}
.st-teal{background:var(--sky);color:#fff}
.st-yellow{background:var(--yellow);color:var(--ink)}
.st-orange{background:var(--orange);color:#fff}
.st-white{background:rgba(255,255,255,.18);color:#fff;border-color:rgba(255,255,255,.6)}
.st-ink{background:var(--ink);color:#fff}
.crumb{max-width:1200px;margin:0 auto;padding:26px 24px 0;font-size:14px;color:var(--gray);display:flex;gap:8px;flex-wrap:wrap;font-weight:600}
.crumb a{color:var(--pink-deep);font-weight:800}
.page-title{max-width:1200px;margin:0 auto;padding:30px 24px 0}
.page-title h1{font-size:clamp(1.8rem,4.6vw,3.1rem)}
.prose{max-width:820px;margin:0 auto;padding:30px 24px 70px;font-size:16px;line-height:1.75;color:var(--gray)}
.prose h2{font-size:clamp(1.4rem,3vw,2rem);margin:34px 0 14px;color:var(--ink)}
.prose h3{font-size:1.1rem;margin:28px 0 10px;color:var(--pink-deep)}
.prose p{margin-bottom:16px}
.prose ul{margin:0 0 18px 22px;display:flex;flex-direction:column;gap:7px}
.prose a{color:var(--pink-deep);font-weight:800;text-decoration:underline}
.prose .lead{font-size:18.5px;color:var(--ink);font-weight:600}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 18% 22%,rgba(255,196,0,.32) 0%,transparent 45%),radial-gradient(ellipse at 82% 30%,rgba(0,194,178,.27) 0%,transparent 45%),radial-gradient(ellipse at 50% 95%,rgba(255,46,147,.22) 0%,transparent 50%)}
.bg-word{position:absolute;top:34%;left:50%;transform:translate(-50%,-50%);font-family:'Unbounded',sans-serif;font-weight:900;font-size:clamp(7rem,22vw,18rem);color:var(--purple);opacity:.07;z-index:0;pointer-events:none;letter-spacing:-.04em;white-space:nowrap;text-transform:uppercase}
.shape{position:absolute;z-index:1;pointer-events:none;font-size:2.3rem;filter:drop-shadow(2px 3px 0 rgba(26,19,48,.2))}
.sh1{top:9%;left:3%;animation:floaty 6s ease-in-out infinite}
.sh2{top:16%;right:2%;animation:floaty 5s ease-in-out 1s infinite}
.sh3{bottom:8%;left:44%;animation:spin 22s linear infinite;font-size:1.7rem}
@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.hero-in{max-width:1200px;margin:0 auto;padding:64px 24px 96px;display:grid;grid-template-columns:1.02fr .98fr;gap:48px;align-items:center;position:relative;z-index:1}
.hero-copy{display:flex;flex-direction:column;align-items:flex-start}
.offer-chip{display:inline-flex;align-items:center;gap:9px;background:var(--white);border:3px dashed var(--orange);border-radius:999px;padding:9px 18px;font-weight:800;font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;box-shadow:4px 4px 0 var(--sky);margin-bottom:24px}
.hero h1{font-size:clamp(2.2rem,5.4vw,4.3rem)}
.hero h1 .l1{display:block;color:var(--ink);text-shadow:4px 4px 0 var(--yellow)}
.hero h1 .l2{display:block;background:linear-gradient(90deg,var(--pink),var(--orange),var(--purple),var(--pink));background-size:300% 100%;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:gshift 4s ease infinite;padding:4px 0}
.hero h1 .l3{display:block;color:var(--sky);text-shadow:3px 3px 0 var(--purple),6px 6px 0 var(--pink)}
.hero-p{font-size:1.12rem;color:var(--gray);line-height:1.6;max-width:480px;margin:24px 0 30px;font-weight:500}
.hero-btns{display:flex;gap:16px;flex-wrap:wrap}

.collage{position:relative;min-height:470px}
.snap{position:absolute;background:var(--white);border:5px solid var(--ink);border-radius:24px;box-shadow:10px 10px 0 var(--pink);overflow:hidden}
.snap img{width:100%;height:auto}
.snap .cap{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 14px;border-top:4px solid var(--ink);background:var(--white);font-weight:800;font-size:13px;text-transform:uppercase;letter-spacing:.02em}
.snap .cap em{font-style:normal;color:var(--pink-deep);font-family:'Unbounded',sans-serif;font-weight:800;font-size:14px;white-space:nowrap}
.snap-a{width:60%;left:0;top:5%;transform:rotate(-2.5deg);z-index:2;display:flex;flex-direction:column}
.snap-b{width:35%;right:0;top:0;transform:rotate(3deg);z-index:3;box-shadow:10px 10px 0 var(--sky)}
.snap-c{width:52%;left:9%;bottom:3%;transform:rotate(-3.5deg);z-index:4;box-shadow:8px 8px 0 var(--yellow)}
@media(prefers-reduced-motion:no-preference){
.snap-a{animation:bob 6s ease-in-out infinite}
.snap-b{animation:bob 6s ease-in-out 1.4s infinite}
.snap-c{animation:bob 6s ease-in-out 2.8s infinite}
}
@keyframes bob{0%,100%{margin-top:0}50%{margin-top:-12px}}
.badge{position:absolute;top:-7%;right:28%;z-index:6;background:var(--yellow);color:var(--ink);font-family:'Unbounded',sans-serif;font-weight:900;font-size:.85rem;text-transform:uppercase;border:4px solid var(--ink);border-radius:50%;width:100px;height:100px;display:flex;align-items:center;justify-content:center;text-align:center;line-height:1.1;padding:8px;transform:rotate(-12deg);box-shadow:5px 5px 0 var(--purple)}
@media(prefers-reduced-motion:no-preference){.badge{animation:wiggle 2.4s ease-in-out infinite}}
@keyframes wiggle{0%,100%{transform:rotate(-12deg)}50%{transform:rotate(-4deg)}}
.mascot{position:absolute;left:0;bottom:6%;z-index:5;display:flex;align-items:flex-end;gap:2px}
.mascot .face{width:74px;height:74px;border-radius:50%;background:var(--yellow);border:4px solid var(--ink);box-shadow:4px 4px 0 var(--pink);display:flex;align-items:center;justify-content:center;font-size:38px}
.mascot .face span{display:inline-block;transform-origin:70% 80%}
@media(prefers-reduced-motion:no-preference){.mascot .face span{animation:wave 3.2s ease-in-out infinite}}
@keyframes wave{0%,55%,100%{transform:rotate(0)}65%{transform:rotate(-14deg)}75%{transform:rotate(12deg)}85%{transform:rotate(-9deg)}}
.mascot .bubble{background:var(--white);border:3px solid var(--ink);border-radius:16px 16px 16px 4px;padding:8px 14px;font-weight:800;font-size:13px;box-shadow:3px 3px 0 var(--sky);margin-bottom:48px;margin-left:-6px;font-family:'Unbounded',sans-serif;text-transform:uppercase}
.balloon{position:absolute;width:34px;height:42px;border-radius:50% 50% 48% 48%;border:3px solid var(--ink);z-index:0}
.balloon::after{content:"";position:absolute;left:50%;top:100%;width:2px;height:46px;background:var(--ink);transform:translateX(-50%)}
@media(prefers-reduced-motion:no-preference){.balloon{animation:floaty 7s ease-in-out infinite}}
@keyframes floaty{0%,100%{transform:translateY(0) rotate(-3deg)}50%{transform:translateY(-22px) rotate(3deg)}}
.cloud{position:absolute;width:96px;height:30px;background:#fff;border-radius:30px;opacity:.85;z-index:0}
.cloud::before,.cloud::after{content:"";position:absolute;background:#fff;border-radius:50%}
.cloud::before{width:42px;height:42px;top:-19px;left:13px}
.cloud::after{width:28px;height:28px;top:-11px;left:48px}
@media(prefers-reduced-motion:no-preference){.cloud{animation:drift linear infinite}}
@keyframes drift{from{transform:translateX(-160px) scale(var(--s,1))}to{transform:translateX(110vw) scale(var(--s,1))}}

/* ---------- trust band ---------- */
.trust{background:var(--purple);border-top:6px solid var(--yellow);border-bottom:6px solid var(--pink);padding:18px 24px;display:flex;justify-content:center;gap:14px 44px;flex-wrap:wrap;position:relative;z-index:1}
.trust-item{font-weight:800;font-size:14.5px;color:#fff;display:flex;align-items:center;gap:9px;text-transform:uppercase;letter-spacing:.03em}
.trust-item i{font-size:19px;color:var(--yellow)}

/* ---------- category tiles ---------- */
.cat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:26px}
.cat-card{position:relative;border:4px solid var(--ink);border-radius:var(--r);overflow:hidden;background:var(--white);transition:transform .3s cubic-bezier(.68,-.55,.265,1.55),box-shadow .3s;display:flex;flex-direction:column}
.cat-grid .cat-card:nth-child(8n+1){box-shadow:8px 8px 0 var(--pink)}
.cat-grid .cat-card:nth-child(8n+2){box-shadow:8px 8px 0 var(--yellow);transform:translateY(14px)}
.cat-grid .cat-card:nth-child(8n+3){box-shadow:8px 8px 0 var(--sky)}
.cat-grid .cat-card:nth-child(8n+4){box-shadow:8px 8px 0 var(--green);transform:translateY(14px)}
.cat-grid .cat-card:nth-child(8n+5){box-shadow:8px 8px 0 var(--orange)}
.cat-grid .cat-card:nth-child(8n+6){box-shadow:8px 8px 0 var(--purple);transform:translateY(14px);border-style:dashed}
.cat-grid .cat-card:nth-child(8n+7){box-shadow:8px 8px 0 var(--pink)}
.cat-grid .cat-card:nth-child(8n+8){box-shadow:8px 8px 0 var(--sky);transform:translateY(14px)}
.cat-card:hover{transform:translateY(-5px) rotate(-1.2deg)!important}
.cat-card img{aspect-ratio:4/3;width:100%;height:auto;object-fit:contain;padding:10px;background:var(--white);border-bottom:4px solid var(--ink)}
.cat-card .cat-name{display:flex;align-items:center;gap:10px;padding:14px 16px;font-family:'Unbounded',sans-serif;font-weight:800;font-size:13.5px;text-transform:uppercase}
.cat-card .cat-name i{font-size:20px}
.cat-card .cat-sub{padding:0 16px 14px;font-size:13px;color:var(--gray);flex:1;font-weight:600}
.tint-pink .cat-name,.tint-pink .cat-sub{background:var(--pink-pale)}
.tint-yellow .cat-name,.tint-yellow .cat-sub{background:var(--yellow-pale)}
.tint-sky .cat-name,.tint-sky .cat-sub{background:var(--sky-pale)}
.tint-green .cat-name,.tint-green .cat-sub{background:var(--green-pale)}
.tint-orange .cat-name,.tint-orange .cat-sub{background:var(--orange-pale)}
.tint-purple .cat-name,.tint-purple .cat-sub{background:var(--purple-pale)}

/* ---------- product cards ---------- */
.carousel{position:relative}
.car-track{display:flex;gap:26px;overflow-x:auto;scroll-snap-type:x mandatory;padding:20px 6px 24px;scrollbar-width:none;align-items:flex-start}
.car-track::-webkit-scrollbar{display:none}
.car-track .prod{flex:0 0 286px;scroll-snap-align:start}
.car-nav{position:absolute;top:-78px;right:0;display:flex;gap:10px}
.car-btn{width:48px;height:48px;border-radius:50%;border:4px solid var(--ink);background:var(--yellow);box-shadow:4px 4px 0 var(--purple);cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center;transition:transform .15s}
.car-btn:hover{transform:translate(-2px,-2px)}
.car-btn:active{transform:translate(2px,2px);box-shadow:1px 1px 0 var(--purple)}
.prod{background:var(--white);border:4px solid var(--ink);border-radius:var(--r);overflow:hidden;transition:transform .3s cubic-bezier(.68,-.55,.265,1.55),box-shadow .3s;display:flex;flex-direction:column}
.prod:nth-child(5n+1){box-shadow:8px 8px 0 var(--pink)}
.prod:nth-child(5n+2){box-shadow:8px 8px 0 var(--sky);border-style:dashed}
.prod:nth-child(5n+3){box-shadow:8px 8px 0 var(--orange)}
.prod:nth-child(5n+4){box-shadow:8px 8px 0 var(--purple)}
.prod:nth-child(5n+5){box-shadow:8px 8px 0 var(--yellow)}
.prod:hover{transform:translateY(-6px) rotate(-1.2deg)}
.prod img{aspect-ratio:1/1;width:100%;height:auto;object-fit:contain;padding:10px;background:var(--white);border-bottom:4px solid var(--ink)}
.prod-body{padding:20px 22px 24px;display:flex;flex-direction:column;flex:1}
.prod-body h3{font-size:1rem;margin-bottom:6px}
.prod-body .desc{font-size:13.5px;color:var(--gray);line-height:1.55;margin-bottom:14px;font-weight:500;flex:1}
.prod-foot{display:flex;align-items:center;justify-content:space-between;margin-top:auto;gap:10px}
.prod-price{font-family:'Unbounded',sans-serif;font-weight:800;font-size:.92rem;padding:6px 14px;border-radius:999px;color:#fff;background:var(--pink);white-space:nowrap}
.prod:nth-child(5n+2) .prod-price{background:var(--sky)}
.prod:nth-child(5n+3) .prod-price{background:var(--orange)}
.prod:nth-child(5n+4) .prod-price{background:var(--purple)}
.prod:nth-child(5n+5) .prod-price{background:var(--yellow);color:var(--ink)}
.prod .more{font-family:'Unbounded',sans-serif;font-weight:700;font-size:.68rem;text-transform:uppercase;color:var(--ink);border:3px solid var(--ink);border-radius:999px;padding:7px 13px;transition:.2s}
.prod:hover .more{background:var(--ink);color:#fff}
.prod-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:26px;padding-top:10px}
.grid-3{grid-template-columns:repeat(3,1fr)}
@media(min-width:1025px){.prod-grid .prod:nth-child(even){transform:translateY(14px)}.prod-grid .prod:nth-child(even):hover{transform:translateY(8px) rotate(-1.2deg)}}
.all-btn{text-align:center;margin-top:46px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap}

/* ---------- offers: purple block ---------- */
.offers-wrap{background:var(--purple);border-top:8px solid var(--yellow);border-bottom:8px solid var(--pink);position:relative;z-index:1}
.offers-wrap::before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 30% 30%,rgba(255,255,255,.13),transparent 50%),repeating-linear-gradient(-45deg,transparent,transparent 16px,rgba(255,255,255,.04) 16px,rgba(255,255,255,.04) 32px)}
.offers-wrap .sec-head h2{color:#fff;text-shadow:3px 3px 0 rgba(26,19,48,.7)}
.offers-wrap .sec-head p{color:rgba(255,255,255,.85)}
.offers-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;position:relative}
.ticket{position:relative;background:var(--white);border:4px solid var(--ink);border-radius:var(--r);padding:26px;overflow:hidden;transition:transform .3s cubic-bezier(.68,-.55,.265,1.55)}
.ticket:hover{transform:translateY(-5px) rotate(-1deg)}
.tk-pink{box-shadow:8px 8px 0 var(--pink)}
.tk-yellow{box-shadow:8px 8px 0 var(--yellow)}
.tk-sky{box-shadow:8px 8px 0 var(--sky);border-style:dashed}
.tk-green{box-shadow:8px 8px 0 var(--green)}
.tk-purple{box-shadow:8px 8px 0 var(--ink)}
.tk-orange{box-shadow:8px 8px 0 var(--orange)}
.ticket .tk-icon{width:50px;height:50px;border-radius:14px;border:3px solid var(--ink);display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:14px}
.tk-pink .tk-icon{background:var(--pink-pale)}.tk-yellow .tk-icon{background:var(--yellow-pale)}.tk-sky .tk-icon{background:var(--sky-pale)}
.tk-green .tk-icon{background:var(--green-pale)}.tk-purple .tk-icon{background:var(--purple-pale)}.tk-orange .tk-icon{background:var(--orange-pale)}
.ticket h3{font-size:1.02rem;margin-bottom:8px}
.ticket p{font-size:14.5px;color:var(--gray);line-height:1.55;font-weight:500}
.ticket .tk-tag{position:absolute;top:16px;right:16px;background:var(--yellow);border:3px solid var(--ink);border-radius:999px;font-size:.62rem;font-weight:900;font-family:'Unbounded',sans-serif;padding:5px 11px;transform:rotate(3deg)}

/* ---------- packages (layout unchanged, reskinned) ---------- */
.pack{display:grid;grid-template-columns:1fr 1fr;gap:44px;align-items:center;padding:38px 0}
.pack + .pack{border-top:4px dashed rgba(26,19,48,.25)}
.pack-img{border:5px solid var(--ink);border-radius:var(--r);overflow:hidden;box-shadow:10px 10px 0 var(--pink);transform:rotate(-1.5deg);width:fit-content;max-width:100%;justify-self:center;transition:transform .3s}
.pack:nth-child(even) .pack-img{transform:rotate(1.5deg);box-shadow:10px 10px 0 var(--sky)}
.pack-img:hover{transform:rotate(0) scale(1.02)}
.pack-img img{display:block;max-height:480px;width:auto;max-width:100%;height:auto}
.pack-copy h3{font-size:clamp(1.3rem,2.6vw,1.9rem);margin-bottom:12px}
.pack-copy p{font-size:16px;color:var(--gray);line-height:1.65;margin-bottom:16px;max-width:52ch;font-weight:500}
.pack-copy .price-line{font-family:'Unbounded',sans-serif;font-weight:800;font-size:1.05rem;color:#fff;background:var(--pink);display:inline-block;padding:7px 18px;border-radius:999px;border:3px solid var(--ink);box-shadow:4px 4px 0 var(--yellow);margin-bottom:18px;transform:rotate(-1deg)}
.pack-list{list-style:none;display:flex;flex-direction:column;gap:9px;margin-bottom:22px}
.pack-list li{display:flex;gap:10px;align-items:center;font-weight:700;font-size:15px}
.pack-list li i{color:var(--green);font-size:20px;flex:0 0 auto}

/* ---------- marquee strip ---------- */
.marquee{background:var(--purple);border-top:6px solid var(--yellow);border-bottom:6px solid var(--pink);overflow:hidden;padding:16px 0;position:relative;z-index:1}
.mq-track{display:flex;gap:42px;width:max-content;align-items:center}
@media(prefers-reduced-motion:no-preference){.mq-track{animation:mq 26s linear infinite}}
@keyframes mq{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.mq-track span{font-family:'Unbounded',sans-serif;font-weight:800;font-size:1.05rem;letter-spacing:.04em;white-space:nowrap;text-transform:uppercase}
.mq-logo{background:#fff;border-radius:999px;padding:6px 16px;display:flex;align-items:center;border:3px solid var(--ink)}
.mq-logo img{height:28px;width:auto}

/* ---------- reviews: yellow block ---------- */
.rev-wrap{background:var(--yellow);border-top:8px solid var(--pink);border-bottom:8px solid var(--purple);position:relative;z-index:1}
.rev-wrap::before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(circle,rgba(26,19,48,.06) 1.5px,transparent 1.5px);background-size:24px 24px}
.rev-wrap .sec-head h2{color:var(--ink);text-shadow:3px 3px 0 #fff}
.rev-wrap .sec-head p{color:var(--ink)}
.rev-track{display:flex;gap:26px;overflow-x:auto;scroll-snap-type:x mandatory;padding:6px 6px 20px;scrollbar-width:none;position:relative}
.rev-track::-webkit-scrollbar{display:none}
.rev{flex:0 0 330px;scroll-snap-align:start;background:var(--white);border:4px solid var(--ink);border-radius:var(--r);padding:28px;display:flex;flex-direction:column}
.rev:nth-child(4n+1){box-shadow:8px 8px 0 var(--pink);transform:rotate(-1deg)}
.rev:nth-child(4n+2){box-shadow:8px 8px 0 var(--purple);transform:rotate(1deg)}
.rev:nth-child(4n+3){box-shadow:8px 8px 0 var(--sky);transform:rotate(-1deg)}
.rev:nth-child(4n+4){box-shadow:8px 8px 0 var(--orange);transform:rotate(1deg)}
.rev-stars{font-size:1.15rem;margin-bottom:12px;color:var(--orange);letter-spacing:2px}
.rev p{font-size:15px;color:var(--gray);line-height:1.6;margin-bottom:18px;font-weight:500;font-style:italic}
.rev-who{display:flex;align-items:center;gap:12px;margin-top:auto}
.rev-av{width:42px;height:42px;border-radius:50%;border:3px solid var(--ink);display:flex;align-items:center;justify-content:center;font-family:'Unbounded',sans-serif;font-weight:800;font-size:16px;color:var(--ink)}
.rev-name{font-family:'Unbounded',sans-serif;font-weight:700;font-size:.78rem;text-transform:uppercase}.rev-loc{font-size:13px;color:var(--gray);font-weight:600}
.rev-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;padding-top:6px}
.rev-grid .rev{flex:none}

/* ---------- areas: teal block ---------- */
.areas-wrap{background:var(--sky);border-top:8px solid var(--yellow);border-bottom:8px solid var(--purple);position:relative;z-index:1}
.areas-wrap::before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(circle,rgba(26,19,48,.06) 1.5px,transparent 1.5px);background-size:24px 24px}
.areas-wrap .sec-head h2{color:var(--ink);text-shadow:3px 3px 0 #fff}
.areas-wrap .sec-head p{color:var(--ink);font-weight:600}
.area-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:30px 36px;position:relative}
.area-col h3{font-size:.95rem;display:flex;align-items:center;gap:8px;margin-bottom:14px;color:var(--ink)}
.area-col h3 i{color:var(--pink-deep)}
.chips{display:flex;flex-wrap:wrap;gap:9px}
.chips span{background:var(--white);border:3px solid var(--ink);border-radius:999px;padding:7px 14px;font-size:13px;font-weight:700;transition:.2s;cursor:default}
.chips span:nth-child(5n+1){box-shadow:3px 3px 0 var(--pink)}
.chips span:nth-child(5n+2){box-shadow:3px 3px 0 var(--yellow)}
.chips span:nth-child(5n+3){box-shadow:3px 3px 0 var(--purple)}
.chips span:nth-child(5n+4){box-shadow:3px 3px 0 var(--orange)}
.chips span:nth-child(5n+5){box-shadow:3px 3px 0 var(--green)}
.chips span:hover{transform:translateY(-3px) rotate(-2deg)}

/* ---------- includes ---------- */
.inc-row{display:grid;grid-template-columns:repeat(4,1fr);gap:26px}
.inc{display:flex;gap:14px;align-items:flex-start;background:var(--white);border:4px solid var(--ink);border-radius:var(--r);padding:22px}
.inc:nth-child(1){box-shadow:7px 7px 0 var(--pink)}
.inc:nth-child(2){box-shadow:7px 7px 0 var(--yellow);transform:translateY(12px)}
.inc:nth-child(3){box-shadow:7px 7px 0 var(--sky)}
.inc:nth-child(4){box-shadow:7px 7px 0 var(--purple);transform:translateY(12px)}
.inc i{flex:0 0 auto;width:50px;height:50px;border-radius:14px;border:3px solid var(--ink);background:var(--white);display:flex;align-items:center;justify-content:center;font-size:25px}
.inc:nth-child(1) i{background:var(--pink-pale)}.inc:nth-child(2) i{background:var(--yellow-pale)}
.inc:nth-child(3) i{background:var(--sky-pale)}.inc:nth-child(4) i{background:var(--purple-pale)}
.inc h3{font-size:.82rem;margin-bottom:5px}
.inc p{font-size:13.5px;color:var(--gray);line-height:1.5;font-weight:500}

/* ---------- CTA ---------- */
.cta-wrap{padding:0 24px 100px;max-width:1200px;margin:0 auto}
.cta{position:relative;background:var(--pink);border:5px solid var(--ink);border-radius:34px;padding:70px 48px;text-align:center;box-shadow:12px 12px 0 var(--purple);overflow:hidden}
.cta::before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 80% 20%,rgba(255,255,255,.18),transparent 50%),repeating-linear-gradient(45deg,transparent,transparent 16px,rgba(255,255,255,.06) 16px,rgba(255,255,255,.06) 32px)}
.cta>*{position:relative}
.cta .cta-logo{display:inline-flex;background:#fff;border:4px solid var(--ink);border-radius:24px;padding:14px 30px;margin-bottom:26px;box-shadow:6px 6px 0 var(--yellow);transform:rotate(-2deg)}
.cta .cta-logo img{height:62px;width:auto}
.cta h2{font-size:clamp(1.8rem,4.4vw,3rem);color:#fff;margin-bottom:12px;text-shadow:3px 3px 0 var(--ink)}
.cta p{font-size:1.05rem;color:#fff;margin-bottom:32px;font-weight:700}
.cta-btns{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.cta .btn-p{border-color:var(--yellow);box-shadow:0 0 22px rgba(26,19,48,.3),6px 6px 0 var(--yellow),12px 12px 0 var(--ink)}

/* ---------- footer ---------- */
footer{background:var(--ink);color:rgba(255,255,255,.7);padding:0 24px 28px;position:relative;z-index:1}
.ft-rainbow{height:10px;background:linear-gradient(90deg,var(--pink),var(--yellow),var(--green),var(--sky),var(--purple));margin:0 -24px 56px}
.ft-inner{max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;gap:48px;justify-content:space-between}
.ft-brand .ft-logo{background:#fff;border-radius:18px;padding:12px 22px;display:inline-flex;margin-bottom:18px;border:3px solid var(--yellow)}
.ft-brand p{font-size:14px;line-height:1.65;max-width:300px;font-weight:500}
.ft-col h4{color:var(--yellow);font-family:'Unbounded',sans-serif;font-weight:800;text-transform:uppercase;font-size:.82rem;letter-spacing:.08em;margin-bottom:16px}
.ft-col ul{list-style:none;display:flex;flex-direction:column;gap:8px}
.ft-col a{font-size:14px;font-weight:600;transition:.2s}.ft-col a:hover{color:var(--sky);padding-left:5px}
.ft-bottom{max-width:1200px;margin:40px auto 0;padding-top:22px;border-top:2px solid rgba(255,255,255,.14);display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;font-size:13px;color:rgba(255,255,255,.5);font-weight:500}

/* ---------- FABs ---------- */
.fab-wrap{position:fixed;bottom:24px;right:24px;z-index:500;display:flex;flex-direction:column;gap:12px;align-items:flex-end}
.fab{width:60px;height:60px;border-radius:50%;border:4px solid var(--yellow);display:flex;align-items:center;justify-content:center;font-size:26px;cursor:pointer;transition:transform .15s;color:#fff;position:relative}
.fab:hover{transform:translateY(-3px)}
.fab-wa{background:#18934A;box-shadow:0 8px 24px rgba(24,147,74,.5)}
.fab-wa::after{content:"";position:absolute;inset:-4px;border-radius:50%;border:3px solid #18934A;animation:pulsering 2s ease-out infinite}
@media(prefers-reduced-motion:reduce){.fab-wa::after{animation:none;display:none}}
@keyframes pulsering{0%{transform:scale(1);opacity:.7}100%{transform:scale(1.7);opacity:0}}
.fab-phone{background:var(--purple);box-shadow:0 8px 24px rgba(123,47,255,.45)}

/* ---------- product detail ---------- */
.pd{max-width:1200px;margin:0 auto;padding:40px 24px 0;display:grid;grid-template-columns:1.05fr .95fr;gap:48px;align-items:start}
.pd-photo{border:5px solid var(--ink);border-radius:var(--r);overflow:hidden;box-shadow:10px 10px 0 var(--pink);transform:rotate(-1deg);background:var(--white);width:fit-content;max-width:100%;margin:0 auto}
.pd-photo img{display:block;max-height:680px;width:auto;max-width:100%;height:auto}
.pd-info h1{font-size:clamp(1.5rem,3.2vw,2.4rem);margin-bottom:16px}
.pd-price{font-family:'Unbounded',sans-serif;font-weight:800;font-size:1.1rem;color:#fff;background:var(--pink);display:inline-block;padding:8px 20px;border-radius:999px;border:3px solid var(--ink);box-shadow:4px 4px 0 var(--yellow);margin-bottom:18px;transform:rotate(-1deg)}
.pd-desc{font-size:16px;color:var(--gray);line-height:1.7;margin-bottom:10px;font-weight:500}
.spec-chips{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 24px}
.spec-chips span{background:var(--white);border:3px solid var(--ink);border-radius:999px;padding:8px 15px;font-size:13.5px;font-weight:700;display:inline-flex;gap:7px;align-items:center}
.spec-chips span:nth-child(3n+1){box-shadow:3px 3px 0 var(--pink)}
.spec-chips span:nth-child(3n+2){box-shadow:3px 3px 0 var(--sky)}
.spec-chips span:nth-child(3n+3){box-shadow:3px 3px 0 var(--yellow)}
.spec-chips i{color:var(--pink-deep);font-size:16px}
.pd-ctas{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:24px}
.pd-ctas .btn{padding:14px 24px;font-size:.8rem}
.pd-offer{background:var(--yellow-pale);border:3px dashed var(--orange);border-radius:18px;padding:15px 19px;font-size:14.5px;font-weight:600;line-height:1.55;box-shadow:4px 4px 0 var(--sky)}
.pd-offer a{color:var(--pink-deep);text-decoration:underline;font-weight:800}
.pd-includes{max-width:1200px;margin:48px auto 0;padding:0 24px}
.pd-includes .inc-box{background:var(--white);border:4px solid var(--ink);border-radius:var(--r);padding:28px 30px;box-shadow:8px 8px 0 var(--sky)}
.pd-includes h2{font-size:1.05rem;margin-bottom:16px}
.pd-includes ul{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:10px 28px}
.pd-includes li{display:flex;gap:10px;align-items:flex-start;font-size:14.5px;font-weight:600;line-height:1.5}
.pd-includes li i{color:var(--green);font-size:19px;flex:0 0 auto;margin-top:1px}

/* ---------- forms ---------- */
.form-wrap{max-width:680px;margin:0 auto;padding:0 24px 80px}
.form-card{background:var(--white);border:4px solid var(--yellow);border-radius:var(--r);padding:34px;box-shadow:10px 10px 0 var(--purple)}
.form-card label{display:block;font-family:'Unbounded',sans-serif;font-weight:700;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;margin:16px 0 8px 4px}
.form-card input,.form-card textarea{width:100%;border:4px solid var(--purple);border-radius:999px;padding:13px 18px;font-family:'DM Sans',sans-serif;font-weight:600;font-size:16px;background:var(--cream);color:var(--ink);transition:.25s}
.form-card textarea{border-radius:18px;min-height:120px;resize:vertical}
.form-card input:focus,.form-card textarea:focus{outline:none;border-color:var(--sky);box-shadow:0 0 0 4px rgba(0,194,178,.25)}
.form-card .btn{margin-top:22px;width:100%;justify-content:center}
.hours{background:var(--yellow-pale);border:3px dashed var(--orange);border-radius:18px;padding:18px 22px;margin:8px 0 6px;font-size:15px;line-height:1.7;box-shadow:4px 4px 0 var(--sky)}

/* ---------- booking embed ---------- */
.po-embed{max-width:1120px;margin:0 auto;min-height:560px}
.po-embed iframe{width:100%!important;min-height:780px;border:4px solid var(--ink);border-radius:var(--r);box-shadow:10px 10px 0 var(--purple);background:var(--white)}
.po-note{text-align:center;color:var(--gray);padding:26px 0 0;font-size:15px;font-weight:500}
.po-note a{color:var(--pink-deep);font-weight:800;text-decoration:underline}
.offer-chips{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;max-width:880px;margin:20px auto 0;padding:0 24px}
.offer-chips span{border:3px solid var(--ink);border-radius:999px;padding:8px 16px;font-size:13px;font-weight:800}
.offer-chips span:nth-child(5n+1){box-shadow:3px 3px 0 var(--pink)}
.offer-chips span:nth-child(5n+2){box-shadow:3px 3px 0 var(--sky)}
.offer-chips span:nth-child(5n+3){box-shadow:3px 3px 0 var(--yellow)}
.offer-chips span:nth-child(5n+4){box-shadow:3px 3px 0 var(--green)}
.offer-chips span:nth-child(5n+5){box-shadow:3px 3px 0 var(--orange)}
.cat-intro{max-width:840px;margin:12px auto 0;text-align:left;color:var(--gray);font-size:17px;line-height:1.7;padding:0 24px;font-weight:500}

/* ---------- responsive ---------- */
@media(max-width:1100px){.nav-links{display:none}.burger{display:flex}}
@media(max-width:1024px){
  .cat-grid{grid-template-columns:repeat(2,1fr)}
  .cat-grid .cat-card{transform:none!important}
  .cat-card:hover{transform:translateY(-4px)!important}
  .prod-grid,.grid-3{grid-template-columns:repeat(2,1fr)}
  .offers-grid{grid-template-columns:repeat(2,1fr)}
  .area-cols{grid-template-columns:repeat(2,1fr)}
  .inc-row{grid-template-columns:repeat(2,1fr)}
  .inc{transform:none!important}
}
@media(max-width:860px){
  .hero-in{grid-template-columns:1fr;padding:48px 24px 72px;gap:44px;text-align:center}
  .hero-copy{align-items:center}
  .offer-chip{margin-left:auto;margin-right:auto}
  .hero-p{margin-left:auto;margin-right:auto}
  .hero-btns{justify-content:center}
  .bg-word{top:24%}
  .collage{min-height:0;height:auto;display:grid;grid-template-columns:1fr 1fr;gap:18px;padding-bottom:8px;align-items:start;margin-top:10px}
  .snap{position:static;width:100%;transform:rotate(-1deg)}
  .snap-a{grid-column:1/-1;transform:rotate(-1deg)}
  .snap .cap{font-size:11.5px;padding:8px 10px}
  .badge{top:-26px;right:4px;width:86px;height:86px;font-size:.72rem}
  .mascot{position:static;justify-content:center;margin-top:6px;grid-column:1/-1}
  .mascot .bubble{margin-bottom:24px}
  .balloon{display:none}
  .pack{grid-template-columns:1fr;gap:26px}
  .pack-img{transform:rotate(-1deg)!important}
  .pd{grid-template-columns:1fr;gap:30px}
}
@media(max-width:680px){
  *{-webkit-tap-highlight-color:transparent}
  nav{top:8px;margin-top:8px;width:calc(100% - 20px);padding:6px 8px 6px 14px}
  .logo-img{height:44px;padding:3px 6px}
  .nav-btn{display:none}
  .mob-menu{top:76px;padding:20px 16px}
  .wrap,.sec,.crumb,.page-title,.prose,.form-wrap,.cta-wrap,.pd,.pd-includes,.cat-intro{padding-left:16px;padding-right:16px}
  .sec{padding-top:60px;padding-bottom:60px}
  .hero-in{padding:36px 16px 56px}
  .hero h1{font-size:2rem}
  .hero-p{font-size:1rem}
  .hero-btns{flex-direction:column;width:100%;gap:14px}
  .hero-btns .btn{width:100%;justify-content:center}
  .trust{padding:14px 16px;gap:10px 22px}.trust-item{font-size:12px}
  .cat-grid,.prod-grid,.grid-3,.offers-grid,.inc-row,.area-cols{grid-template-columns:1fr}
  .prod-grid .prod{transform:none!important}
  .sec-head h2{font-size:1.6rem}
  .car-nav{display:none}
  .car-track .prod{flex-basis:84%}
  .rev{flex-basis:86%}
  .cta{padding:44px 20px;border-radius:26px}
  .cta-btns .btn,.all-btn .btn{width:100%;justify-content:center}
  .page-title h1{font-size:1.5rem}
  footer{padding:0 16px 24px}.ft-rainbow{margin:0 -16px 44px}
  .ft-col ul{flex-direction:row;flex-wrap:wrap;gap:8px 20px}
  .ft-bottom{flex-direction:column;align-items:center;text-align:center;gap:4px}
  .pd-includes ul{grid-template-columns:1fr}
  .fab-wrap{bottom:16px;right:16px}.fab{width:54px;height:54px;font-size:24px}
}
"""

JS = """
function toggleMenu(){document.querySelector('.burger').classList.toggle('open');document.getElementById('mobMenu').classList.toggle('open')}
document.querySelectorAll('.mob-menu a').forEach(a=>a.addEventListener('click',()=>{document.querySelector('.burger').classList.remove('open');document.getElementById('mobMenu').classList.remove('open')}));
(function(){
  var els=document.querySelectorAll('.rv');
  if(!('IntersectionObserver' in window)||window.matchMedia('(prefers-reduced-motion: reduce)').matches){els.forEach(function(e){e.classList.add('in')});return}
  var io=new IntersectionObserver(function(en){en.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.15});
  els.forEach(function(e){io.observe(e)});
})();
document.querySelectorAll('.carousel').forEach(function(c){
  var t=c.querySelector('.car-track');
  c.querySelectorAll('.car-btn').forEach(function(b){
    b.addEventListener('click',function(){t.scrollBy({left:(b.dataset.dir==='next'?1:-1)*(t.clientWidth*0.8),behavior:'smooth'})});
  });
});
"""

NAV_ITEMS = [('index.html', 'Home'), ('PRODUCTS', 'Products'), ('pages/about-us.html', 'About Us'),
             ('pages/testimonials.html', 'Testimonials'), ('news/index.html', 'News'),
             ('pages/contact-castlemania.html', 'Contact Us')]

def cat_links(prefix):
    return ''.join(f'<a href="{prefix}category/{c}/">{CATS[c]["h1"]}</a>' for c in CAT_ORDER)

def nav(prefix, active=''):
    links = []
    for href, label in NAV_ITEMS:
        if href == 'PRODUCTS':
            on = ' class="on"' if active == 'products' else ''
            links.append(f'<li class="has-drop"><a href="#"{on}>Products &#9662;</a><div class="drop">{cat_links(prefix)}</div></li>')
        else:
            on = ' class="on"' if active == href else ''
            links.append(f'<li><a href="{prefix}{href}"{on}>{label}</a></li>')
    mob = f'<a href="{prefix}index.html">Home</a>' + ''.join(
        f'<a class="mob-sub" href="{prefix}category/{c}/">{CATS[c]["h1"]}</a>' for c in CAT_ORDER) + ''.join(
        f'<a href="{prefix}{h}">{l}</a>' for h, l in NAV_ITEMS[2:]) + \
        f'<a href="{prefix}book.html">Book Now</a><a href="{TEL}">Call {PHONE}</a>'
    return f"""<nav>
  <a href="{prefix}index.html" aria-label="Castlemania home"><img class="logo-img" src="{LOGO}" alt="Castlemania Bouncy Castle Hire"></a>
  <ul class="nav-links">{''.join(links)}</ul>
  <button class="burger" onclick="toggleMenu()" aria-label="Menu"><span></span><span></span><span></span></button>
  <a href="{prefix}book.html" class="nav-btn">Book Now</a>
</nav>
<div class="mob-menu" id="mobMenu">{mob}</div>"""

def footer(prefix):
    prod_links = ''.join(f'<li><a href="{prefix}category/{c}/">{CATS[c]["h1"]}</a></li>' for c in CAT_ORDER)
    return f"""<footer>
  <div class="ft-rainbow"></div>
  <div class="ft-inner">
    <div class="ft-brand"><div class="ft-logo"><img src="{LOGO}" alt="Castlemania Bouncy Castle Hire" style="height:56px;width:auto"></div>
    <p>Bouncy castle hire in Laois, Kildare, Kilkenny, Tipperary, Offaly and Carlow. Family-run from Mountrath, Co. Laois since 2018.</p></div>
    <div class="ft-col"><h4>Products</h4><ul>{prod_links}</ul></div>
    <div class="ft-col"><h4>Pages</h4><ul>
      <li><a href="{prefix}index.html">Home</a></li>
      <li><a href="{prefix}book.html">Book Now</a></li>
      <li><a href="{prefix}pages/about-us.html">About Us</a></li>
      <li><a href="{prefix}pages/testimonials.html">Testimonials</a></li>
      <li><a href="{prefix}news/index.html">News</a></li>
      <li><a href="{prefix}pages/contact-castlemania.html">Contact Us</a></li>
      <li><a href="{prefix}pages/privacy-policy.html">Privacy Policy</a></li>
    </ul></div>
    <div class="ft-col"><h4>Get in Touch</h4><ul>
      <li><a href="{TEL}">{PHONE}</a></li>
      <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li><a href="{FB}" target="_blank" rel="noopener">Facebook</a></li>
    </ul></div>
  </div>
  <div class="ft-bottom"><span>&copy; 2026 Castlemania. All rights reserved.</span><span>Mountrath, Co. Laois</span></div>
</footer>
<div class="fab-wrap">
  <a href="{WA}" target="_blank" rel="noopener" class="fab fab-wa" title="WhatsApp us" aria-label="WhatsApp us"><i class="ph-fill ph-whatsapp-logo"></i></a>
  <a href="{TEL}" class="fab fab-phone" title="Call us" aria-label="Call us"><i class="ph-fill ph-phone"></i></a>
</div>"""

def page(title, meta_desc, canonical, body, prefix='', active='', extra_head=''):
    t = html.escape(title, quote=True)
    d = html.escape(meta_desc, quote=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>
<title>{t}</title>
<meta name="description" content="{d}"/>
<meta name="author" content="Castlemania"/>
<link rel="canonical" href="{canonical}"/>
<meta property="og:title" content="{t}"/>
<meta property="og:description" content="{d}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="Castlemania"/>
<meta name="twitter:card" content="summary"/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@700;800;900&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,500&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/bold/style.css"/>
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/fill/style.css"/>
{extra_head}<style>{CSS}</style>
</head>
<body>
{nav(prefix, active)}
{body}
{footer(prefix)}
<script>{JS}</script>
</body>
</html>"""

def prod_card(p, prefix, lazy=True, with_desc=True):
    href = prefix + p['path']
    price = p['specs'].get('Price', '')
    desc = f'<p class="desc">{p["desc"]}</p>' if with_desc else ''
    lz = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return f"""<a href="{href}" class="prod rv">{nat_img(p, 640, lz, prefix)}<div class="prod-body"><h3>{html.escape(p['name'])}</h3>{desc}<div class="prod-foot"><div class="prod-price">{price}</div><span class="more">Details</span></div></div></a>"""

def includes_box():
    items = [
        ('sparkle', 'A sanitised castle, delivered clean and ready to use'),
        ('wrench', 'Setup with safety mats and stakes, everything secured'),
        ('cloud-rain', 'Rain covers on select models'),
        ('truck', 'Collection after your event, no hassle'),
    ]
    lis = ''.join(f'<li><i class="ph-fill ph-check-circle"></i>{t}</li>' for _, t in items)
    return f"""<div class="pd-includes rv"><div class="inc-box"><h2>Every hire includes</h2><ul>{lis}</ul></div></div>"""

# =====================================================================
# HOME
# =====================================================================
def build_home():
    a = BY_SLUG['barbie-dreamhouse-giant-combi']   # 960x464 panorama
    b = BY_SLUG['giant-candy-slide']               # 3000x4000 portrait
    c = BY_SLUG['disney-princess-castle-giant-combi']  # 2016x1134 wide
    collage = f"""
  <div class="collage" aria-hidden="false">
    <div class="balloon" style="left:-2%;top:32%;background:var(--sky)"></div>
    <div class="balloon" style="right:-1%;top:58%;background:var(--green);animation-delay:1.6s"></div>
    <div class="balloon" style="left:44%;top:-6%;background:var(--purple);animation-delay:3s"></div>
    <a class="snap snap-a" href="{a['path']}">{nat_img(a, 700, ' fetchpriority="high"')}<span class="cap">{html.escape(a['name'])}<em>From &euro;180</em></span></a>
    <a class="snap snap-b" href="{b['path']}">{nat_img(b, 420)}</a>
    <a class="snap snap-c" href="{c['path']}">{nat_img(c, 640)}</a>
    <div class="badge">5&#9733; Rated</div>
    <div class="mascot"><div class="face"><span>&#129332;</span></div><div class="bubble">Let's bounce!</div></div>
  </div>"""
    hero = f"""<header class="hero">
  <div class="bg-word" aria-hidden="true">Bounce</div>
  <span class="shape sh1" aria-hidden="true">&#127880;</span>
  <span class="shape sh2" aria-hidden="true">&#11088;</span>
  <span class="shape sh3" aria-hidden="true">&#10024;</span>
  <div class="cloud" style="--s:1;top:8%;animation-duration:52s;animation-delay:-6s"></div>
  <div class="cloud" style="--s:.65;top:26%;animation-duration:70s;animation-delay:-30s"></div>
  <div class="cloud" style="--s:1.2;top:55%;animation-duration:44s;animation-delay:-14s"></div>
  <div class="hero-in">
    <div class="hero-copy">
      <span class="offer-chip"><i class="ph-bold ph-sun"></i> Summer offer: 2nd day &euro;30, 3rd day FREE</span>
      <h1><span class="l1">The Bounciest</span><span class="l2">Parties</span><span class="l3">In The Midlands</span></h1>
      <p class="hero-p">Themed bouncy castles, giant slides and party cakes. Delivered, set up and collected across Laois and five neighbouring counties.</p>
      <div class="hero-btns">
        <a href="book.html" class="btn btn-p"><i class="ph-bold ph-confetti"></i> Book online</a>
        <a href="{TEL}" class="btn btn-w"><i class="ph-bold ph-phone"></i> Call {PHONE}</a>
      </div>
    </div>
    {collage}
  </div>
</header>

<div class="trust">
  <div class="trust-item"><i class="ph-fill ph-sparkle"></i>Cleaned &amp; sanitised after every hire</div>
  <div class="trust-item"><i class="ph-fill ph-truck"></i>Delivery &amp; setup included</div>
  <div class="trust-item"><i class="ph-fill ph-star"></i>5/5 after 10 reviews</div>
  <div class="trust-item"><i class="ph-fill ph-hand-coins"></i>No hidden costs</div>
</div>"""

    cat_cards = []
    for cdir in CAT_ORDER:
        meta = CAT_META[cdir]
        face = BY_SLUG[CAT_FACE[cdir]]
        th = round(560 * face['ih'] / face['iw'])
        cat_cards.append(f"""<a href="category/{cdir}/" class="cat-card tint-{meta['color']} rv"><img src="{card_src(face)}" alt="{CATS[cdir]['h1']}" width="560" height="{th}" loading="lazy"><span class="cat-name"><i class="ph-fill ph-{meta['icon']}"></i>{CATS[cdir]['h1']}</span><span class="cat-sub">{meta['blurb']}</span></a>""")
    cats_sec = f"""<section class="sec" id="categories">
  <div class="sec-head mid"><span class="sec-tag st-pink">Browse the range</span><h2>Pick your party</h2><p>Castles, slides, combis, cakes and treats. Tap a category to see everything in it.</p></div>
  <div class="cat-grid">{''.join(cat_cards)}</div>
</section>"""

    pop_cards = ''.join(prod_card(BY_SLUG[s], '', with_desc=True) for s in POPULAR)
    popular = f"""<section class="sec">
  <div class="sec-head"><span class="sec-tag st-teal">Most popular</span><h2>Most-booked castles</h2><p>The units that get snapped up first every summer. Book early for weekend dates.</p></div>
  <div class="carousel">
    <div class="car-nav"><button class="car-btn" data-dir="prev" aria-label="Scroll back"><i class="ph-bold ph-caret-left"></i></button><button class="car-btn" data-dir="next" aria-label="Scroll forward"><i class="ph-bold ph-caret-right"></i></button></div>
    <div class="car-track">{pop_cards}</div>
  </div>
  <div class="all-btn"><a href="category/some-of-our-castles/" class="btn btn-w">See all castles</a><a href="book.html" class="btn btn-p">Book online</a></div>
</section>"""

    tickets = []
    for o in OFFERS:
        tag = f'<span class="tk-tag">{o["tag"]}</span>' if o['tag'] else ''
        tickets.append(f"""<div class="ticket tk-{o['color']} rv">{tag}<div class="tk-icon"><i class="ph-fill ph-{o['icon']}"></i></div><h3>{o['title']}</h3><p>{o['text'].replace('EUR','&euro;')}</p></div>""")
    offers = f"""<div class="offers-wrap"><section class="sec" id="offers">
  <div class="sec-head mid"><span class="sec-tag st-white">Grab a deal</span><h2>Special offers</h2><p>Seasonal deals worth grabbing. Just mention them when you book.</p></div>
  <div class="offers-grid">{''.join(tickets)}</div>
</section></div>"""

    vip = BY_SLUG['vip-pamper-party']; bundle = BY_SLUG['castle-and-cake-bundle']
    packages = f"""<section class="sec" id="packages">
  <div class="sec-head"><span class="sec-tag st-orange">The full party</span><h2>Party packages &amp; cakes</h2><p>The castle is only half the party. We do the cake table too.</p></div>
  <div class="pack rv">
    <div class="pack-copy">
      <h3>VIP Pamper Party</h3>
      <div class="price-line">From &euro;340</div>
      <p>The full treat for the birthday star and their crew, all arranged in one booking.</p>
      <ul class="pack-list">
        <li><i class="ph-fill ph-check-circle"></i>Pampering for up to 6 children</li>
        <li><i class="ph-fill ph-check-circle"></i>A themed celebration cake</li>
        <li><i class="ph-fill ph-check-circle"></i>12 themed cupcakes</li>
        <li><i class="ph-fill ph-check-circle"></i>A bouncy castle of your choice</li>
      </ul>
      <a href="{vip['path']}" class="btn btn-y">See the VIP package</a>
    </div>
    <a class="pack-img" href="{vip['path']}">{nat_img(vip, 460, ' loading="lazy"')}</a>
  </div>
  <div class="pack rv">
    <a class="pack-img" href="{bundle['path']}">{nat_img(bundle, 460, ' loading="lazy"')}</a>
    <div class="pack-copy">
      <h3>Castle &amp; Cake Bundle</h3>
      <div class="price-line">12 themed cupcakes FREE</div>
      <p>Book any bouncy castle together with a themed cake and the cupcakes are on us. Custom cakes start from &euro;65 in your choice of size, flavour and filling.</p>
      <a href="{bundle['path']}" class="btn btn-y">See the bundle</a>
    </div>
  </div>
</section>"""

    mq_words = ['BIRTHDAYS', 'COMMUNIONS', 'SCHOOL EVENTS', 'CHRISTENINGS', 'FAMILY DAYS', 'FUNDRAISERS']
    colors = ['var(--yellow)', 'var(--sky)', 'var(--pink)', 'var(--green)', 'var(--purple)', 'var(--orange)']
    seq = ''.join(f'<span class="mq-logo"><img src="{LOGO}" alt="" loading="lazy"></span><span style="color:{colors[i]}">{w}</span>' for i, w in enumerate(mq_words))
    marquee = f"""<div class="marquee" aria-hidden="true"><div class="mq-track">{seq}{seq}</div></div>"""

    av_colors = ['var(--pink-pale)', 'var(--yellow-pale)', 'var(--sky-pale)', 'var(--green-pale)', 'var(--purple-pale)', 'var(--orange-pale)']
    revs = ''.join(f"""<div class="rev"><div class="rev-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div><p>&ldquo;{html.escape(q)}&rdquo;</p><div class="rev-who"><div class="rev-av" style="background:{av_colors[i % 6]}">{html.escape(n[0])}</div><div><div class="rev-name">{html.escape(n)}</div><div class="rev-loc">{d}</div></div></div></div>""" for i, (q, n, d) in enumerate(REVIEWS))
    reviews = f"""<div class="rev-wrap"><section class="sec">
  <div class="sec-head"><span class="sec-tag st-ink">Happy customers</span><h2>What parents say</h2><p>5 out of 5 after 10 reviews. Swipe through a few.</p></div>
  <div class="rev-track">{revs}</div>
  <div class="all-btn"><a href="pages/testimonials.html" class="btn btn-w">Read all testimonials</a></div>
</section></div>"""

    area_cols = ''.join(f"""<div class="area-col rv"><h3><i class="ph-fill ph-map-pin"></i>{county}</h3><div class="chips">{''.join(f'<span>{t}</span>' for t in towns)}</div></div>""" for county, towns in AREAS)
    areas = f"""<div class="areas-wrap"><section class="sec" id="areas">
  <div class="sec-head"><span class="sec-tag st-ink">Where we deliver</span><h2>Areas we serve</h2><p>If your town is not listed, just ask. We likely deliver there too.</p></div>
  <div class="area-cols">{area_cols}</div>
</section></div>"""

    includes = f"""<section class="sec">
  <div class="inc-row">
    <div class="inc rv"><i class="ph-fill ph-sparkle"></i><div><h3>Sanitised castle</h3><p>Delivered clean and ready to use</p></div></div>
    <div class="inc rv"><i class="ph-fill ph-wrench"></i><div><h3>Full setup</h3><p>Safety mats and stakes, everything secured</p></div></div>
    <div class="inc rv"><i class="ph-fill ph-cloud-rain"></i><div><h3>Rain covers</h3><p>On select models, for Irish weather</p></div></div>
    <div class="inc rv"><i class="ph-fill ph-truck"></i><div><h3>Collection after</h3><p>We take it all away when the party ends</p></div></div>
  </div>
</section>"""

    cta = f"""<div class="cta-wrap" id="contact">
  <div class="cta rv">
    <span class="cta-logo"><img src="{LOGO}" alt="Castlemania"></span>
    <h2>Let's get your party booked</h2>
    <p>Call, WhatsApp or book online. We will sort the rest.</p>
    <div class="cta-btns"><a href="book.html" class="btn btn-y">Book online</a><a href="{TEL}" class="btn btn-w">Call {PHONE}</a><a href="pages/contact-castlemania.html" class="btn btn-w">Contact us</a></div>
  </div>
</div>"""

    body = hero + cats_sec + marquee + popular + offers + packages + reviews + areas + includes + cta
    title = 'Bouncy Castle Hire in Mountrath, Portlaoise, Tipperary, Kilkenny, Kildare, Carlow, Offaly | Castlemania'
    desc = 'Castlemania provide the best Bouncy Castle Hire service in Mountrath, Portlaoise, Tipperary, Kilkenny, Kildare, Carlow, Offaly, offering a wide range of event equipment. Contact us today!'
    write('index.html', page(title, desc, SITE, body, '', 'index.html'))

# =====================================================================
# CATEGORY PAGES
# =====================================================================
def build_categories():
    for cdir in CAT_ORDER:
        cat = CATS[cdir]
        prefix = '../../'
        meta = CAT_META[cdir]
        cards = []
        for item in cat['items']:
            slug = item.split('/')[-1].replace('.html', '')
            p = BY_SLUG[slug]
            cards.append(prod_card(p, prefix))
        intro = cat['intro']
        body = f"""<div class="crumb"><a href="{prefix}index.html">Home</a> <span>/</span> <span>{cat['h1']}</span></div>
<div class="page-title"><h1>{cat['h1']}</h1></div>
<p class="cat-intro">{intro}</p>
<section class="sec" style="padding-top:44px"><div class="prod-grid">{''.join(cards)}</div>
<div class="all-btn"><a href="{prefix}book.html" class="btn btn-p">Book online</a></div></section>"""
        canonical = f'{SITE}category/{cdir}/'
        write(f'category/{cdir}/index.html', page(cat['title'], cat['meta'], canonical, body, prefix, 'products'))

# =====================================================================
# PRODUCT PAGES
# =====================================================================
def build_products():
    cakes_cats = {'cakes-and-party-foods', 'sweet-treats'}
    for p in PRODUCTS:
        prefix = '../../'
        cdir = p['cat']
        cat = CATS[cdir]
        slug = p['slug']
        price = p['specs'].get('Price', '')
        size = p['specs'].get('Size', '')
        suit = p['specs'].get('Suitable for', '')
        is_cake = cdir in cakes_cats
        chips = []
        if size: chips.append(f'<span><i class="ph-fill ph-ruler"></i>{size}</span>')
        if suit: chips.append(f'<span><i class="ph-fill ph-users-three"></i>{suit}</span>')
        chips.append(f'<span><i class="ph-fill ph-{CAT_META[cdir]["icon"]}"></i>{cat["h1"]}</span>')
        extra = EXTRA.get(slug, '')
        extra_html = f'<p class="pd-desc">{extra.replace("EUR","&euro;")}</p>' if extra else ''
        wa_link = 'https://wa.me/353894156419?text=' + re.sub(r'[^A-Za-z0-9]', lambda m: '%20', f'Hi Castlemania, I would like to book the {p["name"]}')
        if is_cake:
            offer_note = f'<div class="pd-offer">Order a cake together with any bouncy castle and get <b>12 themed cupcakes free</b> with our <a href="{prefix}category/cakes-and-party-foods/castle-and-cake-bundle.html">Castle &amp; Cake Bundle</a>.</div>'
        else:
            offer_note = f'<div class="pd-offer">Summer offer: pay for day one, get the 2nd day for &euro;30 and the 3rd day free. Plus 10% off midweek bookings. <a href="{prefix}index.html#offers">See all offers</a>.</div>'
        # related: next 3 in same category
        items = [i.split('/')[-1].replace('.html', '') for i in cat['items']]
        if slug in items:
            idx = items.index(slug)
            rel = [items[(idx + k) % len(items)] for k in range(1, 4) if items[(idx + k) % len(items)] != slug]
        else:
            rel = items[:3]
        rel_cards = ''.join(prod_card(BY_SLUG[s], prefix, with_desc=False) for s in dict.fromkeys(rel))
        related = f"""<section class="sec"><div class="sec-head"><h2>You might also like</h2></div><div class="prod-grid grid-3">{rel_cards}</div>
<div class="all-btn"><a href="{prefix}category/{cdir}/" class="btn btn-w">Back to {cat['h1']}</a><a href="{prefix}book.html" class="btn btn-p">Book online</a></div></section>""" if rel_cards else ''
        inc = includes_box() if not is_cake else f"""<div class="pd-includes rv"><div class="inc-box"><h2>Good to know</h2><ul>
<li><i class="ph-fill ph-check-circle"></i>Made to order in your choice of size and flavour</li>
<li><i class="ph-fill ph-check-circle"></i>Dietary options available on request</li>
<li><i class="ph-fill ph-check-circle"></i>Delivery available with your castle booking</li>
<li><i class="ph-fill ph-check-circle"></i>Cakes start from &euro;65, treats from &euro;4 a piece</li>
</ul></div></div>"""
        body = f"""<div class="crumb"><a href="{prefix}index.html">Home</a> <span>/</span> <a href="index.html">{cat['h1']}</a> <span>/</span> <span>{html.escape(p['name'])}</span></div>
<div class="pd">
  <div class="pd-photo"><img src="{large_src(p, prefix)}" alt="{html.escape(p['name'])}" width="{fit_dims(p['iw'],p['ih'],1200,900)[0]}" height="{fit_dims(p['iw'],p['ih'],1200,900)[1]}" fetchpriority="high"></div>
  <div class="pd-info">
    <h1>{html.escape(p['name'])}</h1>
    <div class="pd-price">{price}</div>
    <p class="pd-desc">{p['desc']}</p>
    {extra_html}
    <div class="spec-chips">{''.join(chips)}</div>
    <div class="pd-ctas">
      <a href="{prefix}book.html" class="btn btn-p">Book online</a>
      <a href="{TEL}" class="btn btn-w"><i class="ph-bold ph-phone"></i> Call</a>
      <a href="{wa_link}" target="_blank" rel="noopener" class="btn btn-w"><i class="ph-bold ph-whatsapp-logo"></i> WhatsApp</a>
    </div>
    {offer_note}
  </div>
</div>
{inc}
{related}"""
        canonical = f'{SITE}{p["path"]}'
        write(p['path'], page(p['title'], p['meta'], canonical, body, prefix, 'products'))

# =====================================================================
# STATIC PAGES
# =====================================================================
def simple_page(path, title, meta_desc, h1, inner, prefix, active='', crumb_label=None):
    crumb_label = crumb_label or h1
    body = f"""<div class="crumb"><a href="{prefix}index.html">Home</a> <span>/</span> <span>{crumb_label}</span></div>
<div class="page-title"><h1>{h1}</h1></div>
{inner}"""
    canonical = SITE + path.replace('index.html', '')
    write(path, page(title, meta_desc, canonical, body, prefix, active))

def build_static():
    base_t = 'Bouncy Castle Hire in Mountrath, Portlaoise, Tipperary, Kilkenny, Kildare, Carlow, Offaly | Castlemania'
    base_d = 'Castlemania provide the best Bouncy Castle Hire service in Mountrath, Portlaoise, Tipperary, Kilkenny, Kildare, Carlow, Offaly, offering a wide range of event equipment. Contact us today!'

    # ----- book -----
    chips = ['Bank holiday: 3 days for 1', 'Summer: 2nd day EUR30, 3rd free', 'Midweek: 10% off',
             'Mar, Apr, Sep: 2 days for 1', 'Nov to Feb: EUR50 off']
    chip_colors = ['var(--pink-pale)', 'var(--yellow-pale)', 'var(--sky-pale)', 'var(--green-pale)', 'var(--purple-pale)']
    chip_html = ''.join(f'<span style="background:{chip_colors[i]}">{c.replace("EUR","&euro;")}</span>' for i, c in enumerate(chips))
    book_inner = f"""<p class="cat-intro">Choose your castle, pick your date and book online in minutes. Secure checkout powered by PartyOps. We deliver across Laois, Kildare, Kilkenny, Tipperary, Offaly and Carlow.</p>
<div class="offer-chips">{chip_html}</div>
<p class="cat-intro" style="font-size:14.5px;margin-top:14px">Seasonal offers are applied when we confirm your booking. The online total shows a flat per-day price.</p>
<section class="sec" style="padding-top:36px"><div class="po-embed">
  <div id="partyops-booking-widget"></div>
  <script src="https://partyops.app/widget.js" data-business-id="540aba40-0419-4142-8cec-a44aa1465451"></script>
  <p class="po-note">We will confirm availability and delivery time and answer any questions. Prefer to talk? Call <a href="{TEL}">{PHONE}</a> or WhatsApp us.</p>
</div></section>"""
    simple_page('book.html', 'Book Online | Castlemania Bouncy Castles', 'Book your bouncy castle online. Choose your castle, pick your date and pay securely. Delivery across Laois, Kildare, Kilkenny, Tipperary, Offaly and Carlow.', 'Book your castle', book_inner, '', 'book')

    # ----- about -----
    about_inner = """<div class="prose">
<p class="lead">Castlemania is a small family business from Mountrath in County Laois, established in 2018. Our mission is simple: to make kids' parties and family days in the sun unforgettable. We supply themed bouncy castles with slides and giant attractions that bring smiles, operating with professional planning, strict safety, and great value.</p>
<h3>What We Do: Bouncy Castle Rental Service</h3>
<p>We provide a full bouncy castle rental service for birthdays, family events, and community gatherings. Our range includes:</p>
<ul>
<li>Classic themed bouncy castles with slides</li>
<li>Giant slides for big thrills, including our giant candy slide</li>
<li>Versatile combos, giant combis for mixed jump-and-slide fun</li>
<li>Rainproof bouncy castles for all-weather play</li>
<li>Themed cakes, cupcakes and party packages to finish the party table</li>
</ul>
<h3>Safety, Sterilisation &amp; Contactless Service</h3>
<p>Safety is our priority. All castles are sterilised before and after every hire. We operate a contactless delivery and collection service, and equipment is maintained to the highest standards. We follow safe setup distances and clear site checks, so parents can relax knowing each castle is inspected and secure.</p>
<h3>Delivery Areas &amp; Availability</h3>
<p>We deliver across Laois and neighbouring counties: Laois, Kilkenny, Kildare, Offaly, Tipperary and Carlow. Castlemania is flexible and available for hire 365 days a year. We tailor each booking to your location and occasion.</p>
<h3>Value &amp; Offers</h3>
<p>We offer competitive pricing. Our rates vary by distance and duration, and customers near Mountrath get the best value. We also run special offers throughout the year, giving extra savings for local bookings. Great fun, great prices.</p>
<h3>Perfect for Kids' Parties and Family Days</h3>
<p>Castlemania focuses on creating magical memories. Whether you need a bouncy castle for a birthday or a giant combi for a summer fair, we have options to suit every party size. Our giant slides and giant candy slide are crowd favourites, designed to delight kids and reassure parents.</p>
<h3>Contact Details</h3>
<p>Phone: <a href="tel:0894156419">089 415 6419</a><br>
Email: <a href="mailto:info@castlemaniabouncycastles.com">info@castlemaniabouncycastles.com</a><br>
Facebook: <a href="https://www.facebook.com/Castlemania-105465194348441" target="_blank" rel="noopener">Castlemania on Facebook</a></p>
<h3>Our Guarantee</h3>
<p>Castlemania guarantees a satisfactory and fully safe service. We add lots of fun and bring out smiles on the faces of your most precious ones on all of their special occasions. Trust a family team that cares.</p>
</div>"""
    simple_page('pages/about-us.html', 'About Us - ' + base_t, base_d, 'About Castlemania: Family Bouncy Castle Rental in Mountrath', about_inner, '../', 'pages/about-us.html', 'About Us')

    # ----- contact -----
    contact_inner = f"""<div class="prose" style="padding-bottom:24px">
<p>It couldn't be easier to get in touch with the team here at Castlemania. Use the contact form below, or:</p>
<ul>
<li><strong>Call us on:</strong> <a href="tel:0894156419">089 415 6419</a></li>
<li><strong>Email us:</strong> <a href="mailto:info@castlemaniabouncycastles.com">info@castlemaniabouncycastles.com</a></li>
<li><strong>Leave us a review on Google:</strong> <a href="https://www.google.com/search?q=castlemania+bouncy+castles+reviews" target="_blank" rel="noopener">Review Castlemania</a></li>
</ul>
<div class="hours"><strong>Our office is open:</strong><br>Monday to Friday: 09:00 to 18:00<br>Saturday &amp; Sunday: 10:00 to 13:00</div>
</div>
<div class="form-wrap">
<div class="form-card">
<h2 style="font-family:'Unbounded',sans-serif;font-size:24px;margin-bottom:6px">Quick Enquiry Form</h2>
<!-- TODO: Replace [FORM-ID] with your Formspree form ID (formspree.io) -->
<form action="https://formspree.io/f/[FORM-ID]" method="POST">
<label>Your Name <input type="text" name="name" required></label>
<label>Your Email Address <input type="email" name="email" required></label>
<label>Your Phone Number <input type="tel" name="phone" required></label>
<label>Your Location <input type="text" name="location" required></label>
<label>Your Enquiry <textarea name="message" required></textarea></label>
<button type="submit" class="btn btn-p">Send Enquiry</button>
</form>
</div>
</div>"""
    simple_page('pages/contact-castlemania.html', 'Contact Us - ' + base_t, base_d, 'Contact Castlemania', contact_inner, '../', 'pages/contact-castlemania.html', 'Contact Us')

    # ----- testimonials -----
    av_colors = ['var(--pink-pale)', 'var(--yellow-pale)', 'var(--sky-pale)', 'var(--green-pale)', 'var(--purple-pale)', 'var(--orange-pale)']
    revs = ''.join(f"""<div class="rev rv"><div class="rev-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div><p>&ldquo;{html.escape(q)}&rdquo;</p><div class="rev-who"><div class="rev-av" style="background:{av_colors[i % 6]}">{html.escape(n[0])}</div><div><div class="rev-name">{html.escape(n)}</div><div class="rev-loc">{d}</div></div></div></div>""" for i, (q, n, d) in enumerate(REVIEWS))
    test_inner = f"""<p class="cat-intro">5 out of 5 after 10 reviews.</p>
<section class="sec" style="padding-top:40px">
<div class="rev-grid">{revs}</div>
<div class="all-btn"><a href="https://www.google.com/search?q=castlemania+bouncy+castles+reviews" target="_blank" rel="noopener" class="btn btn-w">See more on Google</a></div>
</section>"""
    simple_page('pages/testimonials.html', 'Testimonials - ' + base_t, base_d, 'What our clients are saying', test_inner, '../', 'pages/testimonials.html', 'Testimonials')

    # ----- news -----
    news_inner = """<section class="sec">
<!-- TODO: Add news posts here as the business publishes them -->
<p style="text-align:center;color:var(--gray);font-size:16px">No news posts yet. Check back soon for seasonal offers and new arrivals, or follow us on <a href="https://www.facebook.com/Castlemania-105465194348441" target="_blank" rel="noopener" style="color:var(--pink-deep);font-weight:700">Facebook</a> for the latest.</p>
<div class="all-btn"><a href="../index.html#offers" class="btn btn-w">See current offers</a></div>
</section>"""
    simple_page('news/index.html', 'News - ' + base_t, base_d, 'News &amp; Updates', news_inner, '../', 'news/index.html', 'News')

    # ----- privacy -----
    priv_inner = """<div class="prose">
<p>Castlemania respects your privacy. This page explains how we handle the information you share with us.</p>
<h3>Information we collect</h3>
<p>When you contact us through our enquiry form, by phone, email or WhatsApp, we collect the details you provide such as your name, phone number, email address and event location. We use this only to respond to your enquiry and arrange your booking.</p>
<h3>How we use your information</h3>
<p>We use your details to confirm availability, arrange delivery and collection, and answer your questions. We do not sell or share your information with third parties for marketing.</p>
<h3>Contact</h3>
<p>For any questions about your data, contact us at <a href="mailto:info@castlemaniabouncycastles.com">info@castlemaniabouncycastles.com</a> or <a href="tel:0894156419">089 415 6419</a>.</p>
<p style="color:var(--gray);font-size:14px"><!-- TODO: Review this placeholder policy with the owner before going live. --></p>
</div>"""
    simple_page('pages/privacy-policy.html', 'Privacy Policy - ' + base_t, base_d, 'Privacy Policy', priv_inner, '../', 'pages/privacy-policy.html', 'Privacy Policy')

def write(rel, content):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    build_home()
    build_categories()
    build_products()
    build_static()
    print('build complete')
