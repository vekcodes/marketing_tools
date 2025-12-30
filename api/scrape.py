from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import re
import ssl

# Comprehensive Marketing Tools Detection
MARKETING_TOOLS = {
    # === CHATBOTS & LIVE CHAT ===
    "chatbots": {
        "Intercom": ["intercom", "widget.intercom.io", "intercom-container", "intercomSettings"],
        "Drift": ["drift", "js.driftt.com", "drift-widget", "drift.load"],
        "Zendesk": ["zendesk", "zopim", "zdassets", "zopim.com", "zendesk-chat"],
        "HubSpot Chat": ["hubspot", "js.hs-scripts.com", "hbspt.chat"],
        "Freshchat": ["freshchat", "wchat.freshchat.com", "freshworks"],
        "Tidio": ["tidio", "code.tidio.co", "tidiochat"],
        "Crisp": ["crisp.chat", "client.crisp.chat", "crisp-client", "$crisp"],
        "Tawk.to": ["tawk.to", "embed.tawk.to", "tawkto"],
        "LiveChat": ["livechat", "cdn.livechatinc.com", "livechatinc", "__lc"],
        "Olark": ["olark", "static.olark.com"],
        "Chatra": ["chatra", "call.chatra.io"],
        "JivoChat": ["jivosite", "jivochat", "code.jivosite.com"],
        "Comm100": ["comm100", "livechat.comm100.com"],
        "Pure Chat": ["purechat", "app.purechat.com"],
        "Smartsupp": ["smartsupp", "smartsuppchat"],
        "Kayako": ["kayako", "kayakocdn"],
        "Help Scout": ["helpscout", "beacon-v2.helpscout.net"],
        "Gorgias": ["gorgias", "config.gorgias.chat"],
        "Chatlio": ["chatlio", "chatlio.com"],
        "SnapEngage": ["snapengage", "snapengage.com"],
        "Customerly": ["customerly", "widget.customerly.io"],
        "Chaport": ["chaport", "app.chaport.com"],
        "Acquire": ["acquire.io", "acquire-chat"],
        "Podium": ["podium", "connect.podium.com"],
        "Birdeye": ["birdeye", "birdeye.com/widget"],
    },

    # === ANALYTICS & TRACKING ===
    "analytics": {
        "Google Analytics 4": ["gtag", "googletagmanager.com/gtag", "G-", "google-analytics.com/g/"],
        "Google Analytics (Universal)": ["google-analytics.com/analytics.js", "ga.js", "UA-"],
        "Google Tag Manager": ["googletagmanager.com/gtm.js", "GTM-"],
        "Adobe Analytics": ["omniture", "s_code", "sc.omtrdc.net", "adobeanalytics"],
        "Mixpanel": ["mixpanel", "cdn.mxpnl.com", "mixpanel.init"],
        "Amplitude": ["amplitude.com", "cdn.amplitude.com", "amplitude.getInstance"],
        "Heap": ["heap-analytics", "heapanalytics.com", "heap.load"],
        "Segment": ["segment.com/analytics", "analytics.segment.com", "segment.load"],
        "Pendo": ["pendo.io", "cdn.pendo.io", "pendo.initialize"],
        "FullStory": ["fullstory", "edge.fullstory.com", "FullStory.init"],
        "LogRocket": ["logrocket", "cdn.logrocket.io", "LogRocket.init"],
        "Datadog RUM": ["datadoghq.com", "dd-rum", "DD_RUM"],
        "New Relic": ["newrelic", "js-agent.newrelic.com", "NREUM"],
        "Plausible": ["plausible.io", "plausible-analytics"],
        "Fathom": ["usefathom.com", "fathom.trackPageview"],
        "Simple Analytics": ["simpleanalytics.com", "sa.js"],
        "PostHog": ["posthog", "app.posthog.com", "posthog.init"],
        "Snowplow": ["snowplow", "sp.js"],
        "Matomo": ["matomo", "piwik", "_paq"],
        "Countly": ["countly", "cdn.countly.com"],
        "Clicky": ["clicky", "static.getclicky.com"],
        "Chartbeat": ["chartbeat", "static.chartbeat.com"],
        "Parse.ly": ["parsely", "cdn.parsely.com"],
    },

    # === HEATMAPS & SESSION RECORDING ===
    "heatmaps_recording": {
        "Hotjar": ["hotjar", "static.hotjar.com", "hj("],
        "Microsoft Clarity": ["clarity.ms", "clarity.init"],
        "Crazy Egg": ["crazyegg", "script.crazyegg.com"],
        "Lucky Orange": ["luckyorange", "cdn.luckyorange.com", "lo_"],
        "Mouseflow": ["mouseflow", "cdn.mouseflow.com"],
        "Inspectlet": ["inspectlet", "__insp"],
        "Smartlook": ["smartlook", "rec.smartlook.com"],
        "VWO": ["visualwebsiteoptimizer", "dev.visualwebsiteoptimizer.com"],
        "Contentsquare": ["contentsquare", "t.contentsquare.net"],
        "Quantum Metric": ["quantummetric.com"],
        "Glassbox": ["glassbox", "glassboxdigital.io"],
    },

    # === A/B TESTING & PERSONALIZATION ===
    "ab_testing": {
        "Optimizely": ["optimizely", "cdn.optimizely.com", "optimizelyEndUserId"],
        "VWO": ["vwo_", "visualwebsiteoptimizer"],
        "Google Optimize": ["googleoptimize.com", "optimize.google.com"],
        "AB Tasty": ["abtasty", "try.abtasty.com"],
        "Convert": ["convert.com", "cdn.convertexperiments.com"],
        "Kameleoon": ["kameleoon", "kameleoon.com"],
        "Dynamic Yield": ["dynamicyield", "cdn.dynamicyield.com"],
        "Monetate": ["monetate", "se.monetate.net"],
        "Conductrics": ["conductrics"],
        "LaunchDarkly": ["launchdarkly", "app.launchdarkly.com"],
        "Split.io": ["split.io", "cdn.split.io"],
    },

    # === ADVERTISING & RETARGETING ===
    "advertising": {
        "Facebook Pixel": ["connect.facebook.net", "fbq(", "facebook-pixel", "fbevents.js"],
        "Google Ads": ["googleadservices.com", "googlesyndication.com", "adsbygoogle", "google_ads"],
        "LinkedIn Insight Tag": ["snap.licdn.com", "linkedin.com/px", "_linkedin_partner_id"],
        "Twitter Pixel": ["static.ads-twitter.com", "twq(", "twitter-pixel"],
        "TikTok Pixel": ["analytics.tiktok.com", "ttq.load"],
        "Pinterest Tag": ["pintrk", "s.pinimg.com/ct/core.js"],
        "Snapchat Pixel": ["sc-static.net/scevent.min.js", "snaptr("],
        "Reddit Pixel": ["reddit.com/static/ads", "rdt("],
        "Microsoft/Bing Ads": ["bat.bing.com", "uetq"],
        "Quora Pixel": ["quora.com/_/ad", "qp("],
        "AdRoll": ["adroll", "d.adroll.com"],
        "Criteo": ["criteo", "static.criteo.net"],
        "Taboola": ["taboola", "cdn.taboola.com"],
        "Outbrain": ["outbrain", "widgets.outbrain.com"],
        "DoubleClick": ["doubleclick.net", "googleads.g.doubleclick.net"],
        "Amazon Ads": ["amazon-adsystem.com"],
        "TradeDesk": ["thetradedesk", "js.adsrvr.org"],
        "MediaMath": ["mediamath", "pixel.mathtag.com"],
    },

    # === EMAIL MARKETING ===
    "email_marketing": {
        "Mailchimp": ["mailchimp", "list-manage.com", "mc.us", "mcjs"],
        "Klaviyo": ["klaviyo", "static.klaviyo.com", "_learnq"],
        "ActiveCampaign": ["activecampaign", "trackcmp.net"],
        "ConvertKit": ["convertkit", "convertkit.com"],
        "Drip": ["getdrip.com", "dc.js"],
        "Sendinblue": ["sendinblue", "sibautomation.com"],
        "Constant Contact": ["constantcontact", "cc.constantcontact.com"],
        "AWeber": ["aweber", "forms.aweber.com"],
        "GetResponse": ["getresponse", "gr.js"],
        "Campaign Monitor": ["campaignmonitor", "createsend.com"],
        "Omnisend": ["omnisend", "api.omnisend.com"],
        "Customer.io": ["customer.io", "track.customer.io"],
        "Iterable": ["iterable", "js.iterable.com"],
        "Braze": ["braze", "js.appboycdn.com", "appboy"],
        "Sailthru": ["sailthru", "ak.sail-horizon.com"],
        "Marketo": ["marketo", "mktoresp.com", "munchkin.js"],
        "Pardot": ["pardot", "pi.pardot.com", "piAId"],
        "Eloqua": ["eloqua", "tracking.eloqua.com"],
    },

    # === CRM & SALES ===
    "crm_sales": {
        "HubSpot": ["hubspot", "js.hs-scripts.com", "hs-script-loader"],
        "Salesforce": ["salesforce", "force.com", "pardot"],
        "Pipedrive": ["pipedrive", "leadbooster.pipedrive.com"],
        "Zoho CRM": ["zoho", "salesiq.zoho.com"],
        "Freshsales": ["freshsales", "freshworks"],
        "Close": ["close.com", "app.close.com"],
        "Copper": ["prosperworks", "copper"],
        "Monday Sales CRM": ["monday.com"],
        "Zendesk Sell": ["getbase.com"],
    },

    # === MARKETING AUTOMATION ===
    "marketing_automation": {
        "HubSpot": ["hubspot", "js.hs-scripts.com"],
        "Marketo": ["marketo", "munchkin.js", "mktoresp"],
        "Pardot": ["pardot", "pi.pardot.com"],
        "ActiveCampaign": ["activecampaign"],
        "Eloqua": ["eloqua", "elqcfg"],
        "Autopilot": ["autopilothq", "anywhere.autopilothq.com"],
        "Keap/Infusionsoft": ["infusionsoft", "keap"],
        "Ontraport": ["ontraport", "optassets.ontraport.com"],
        "SharpSpring": ["sharpspring", "tracking.sharpspring.com"],
        "Act-On": ["act-on", "actonsoftware.com"],
    },

    # === CUSTOMER DATA PLATFORMS ===
    "cdp": {
        "Segment": ["segment", "cdn.segment.com"],
        "mParticle": ["mparticle", "jssdkcdns.mparticle.com"],
        "Tealium": ["tealium", "tags.tiqcdn.com"],
        "Rudderstack": ["rudderstack", "cdn.rudderlabs.com"],
        "BlueConic": ["blueconic", "cdn.blueconic.net"],
        "Lytics": ["lytics", "c.lytics.io"],
        "Treasure Data": ["treasuredata", "cdn.treasuredata.com"],
        "Adobe Experience Platform": ["adobedc.net", "launch"],
    },

    # === PUSH NOTIFICATIONS ===
    "push_notifications": {
        "OneSignal": ["onesignal", "cdn.onesignal.com"],
        "PushEngage": ["pushengage", "clientcdn.pushengage.com"],
        "Pushwoosh": ["pushwoosh"],
        "WebEngage": ["webengage", "cdn.webengage.com"],
        "CleverTap": ["clevertap", "d2r1yp2w7bber2.cloudfront.net"],
        "Airship": ["urbanairship", "aswpsdkus.com"],
        "Braze Web Push": ["braze", "appboy"],
        "VWO Engage": ["vwo.com/engage"],
        "Aimtell": ["aimtell", "cdn.aimtell.com"],
        "PushAssist": ["pushassist"],
    },

    # === SURVEYS & FEEDBACK ===
    "surveys_feedback": {
        "Typeform": ["typeform", "embed.typeform.com"],
        "SurveyMonkey": ["surveymonkey", "widget.surveymonkey.com"],
        "Qualtrics": ["qualtrics", "siteintercept.qualtrics.com"],
        "Hotjar Surveys": ["hotjar", "hj-surveys"],
        "Usabilla": ["usabilla", "w.usabilla.com"],
        "GetFeedback": ["getfeedback", "usabilla"],
        "Medallia": ["medallia", "nebula-cdn.kampyle.com"],
        "UserVoice": ["uservoice", "widget.uservoice.com"],
        "Delighted": ["delighted", "d.delighted.com"],
        "Survicate": ["survicate", "survey.survicate.com"],
        "Wootric": ["wootric", "cdn.wootric.com"],
        "AskNicely": ["asknicely"],
        "Formbricks": ["formbricks"],
        "Refiner": ["refiner", "js.refiner.io"],
    },

    # === SOCIAL PROOF & REVIEWS ===
    "social_proof": {
        "Trustpilot": ["trustpilot", "widget.trustpilot.com"],
        "Yotpo": ["yotpo", "staticw2.yotpo.com"],
        "Judge.me": ["judge.me", "cdn.judge.me"],
        "Stamped.io": ["stamped.io", "cdn.stamped.io"],
        "Loox": ["loox.io", "loox-reviews"],
        "Bazaarvoice": ["bazaarvoice", "display.ugc.bazaarvoice.com"],
        "PowerReviews": ["powerreviews", "ui.powerreviews.com"],
        "Feefo": ["feefo", "api.feefo.com"],
        "Reviews.io": ["reviews.io", "widget.reviews.io"],
        "Reevoo": ["reevoo", "mark.reevoo.com"],
        "Proof": ["useproof.com"],
        "FOMO": ["fomo.com", "load.fomo.com"],
        "Provely": ["provely", "app.provely.io"],
        "Nudgify": ["nudgify", "cdn.nudgify.com"],
        "ProveSource": ["provesrc.com"],
    },

    # === POPUPS & LEAD CAPTURE ===
    "popups_lead_capture": {
        "OptinMonster": ["optinmonster", "a]cdn.optinmonster.com"],
        "Sumo": ["sumo.com", "load.sumo.com", "sumojs"],
        "Hello Bar": ["hellobar", "my.hellobar.com"],
        "Privy": ["privy.com", "widget.privy.com"],
        "Justuno": ["justuno", "cdn.jus.tc"],
        "Sleeknote": ["sleeknote", "sleeknotecustomerscripts"],
        "Wisepops": ["wisepops", "loader.wisepops.com"],
        "Unbounce Popups": ["unbounce", "ubembed.com"],
        "ConvertFlow": ["convertflow", "js.convertflow.co"],
        "OptiMonk": ["optimonk", "front.optimonk.com"],
        "Poptin": ["poptin", "cdn.poptin.com"],
        "Picreel": ["picreel"],
        "Outgrow": ["outgrow", "dyv6f9ner767z.cloudfront.net"],
        "Leadpages Popups": ["leadpages", "lpcdn.com"],
        "GetSiteControl": ["getsitecontrol", "widgets.getsitecontrol.com"],
    },

    # === CUSTOMER SUCCESS & ONBOARDING ===
    "customer_success": {
        "Pendo": ["pendo.io", "cdn.pendo.io"],
        "WalkMe": ["walkme", "cdn.walkme.com"],
        "Appcues": ["appcues", "fast.appcues.com"],
        "Userpilot": ["userpilot", "js.userpilot.io"],
        "Chameleon": ["chameleon.io", "fast.trychameleon.com"],
        "Userflow": ["userflow", "js.userflow.com"],
        "Whatfix": ["whatfix", "cdn.whatfix.com"],
        "Inline Manual": ["inlinemanual", "inlinemanual.com"],
        "Stonly": ["stonly", "stonly.com"],
        "Usetiful": ["usetiful", "www.usetiful.com"],
        "Product Fruits": ["productfruits.com"],
        "Lou": ["lou.ai"],
        "CommandBar": ["commandbar", "api.commandbar.com"],
    },

    # === PAYMENTS ===
    "payments": {
        "Stripe": ["js.stripe.com", "stripe.com/v3"],
        "PayPal": ["paypal.com/sdk", "paypalobjects.com"],
        "Square": ["square", "squarecdn.com", "squareup.com"],
        "Braintree": ["braintree", "js.braintreegateway.com"],
        "Adyen": ["adyen", "checkoutshopper-live.adyen.com"],
        "Klarna": ["klarna", "x.klarnacdn.net"],
        "Affirm": ["affirm.com", "cdn1.affirm.com"],
        "Afterpay": ["afterpay", "portal.afterpay.com"],
        "Sezzle": ["sezzle", "sdk.sezzle.com"],
        "Shopify Payments": ["shopifycloud.com"],
        "Apple Pay": ["apple-pay", "applepay.cdn-apple.com"],
        "Google Pay": ["pay.google.com", "gpay"],
        "Amazon Pay": ["amazonpay", "static-na.payments-amazon.com"],
        "Recurly": ["recurly", "js.recurly.com"],
        "Chargebee": ["chargebee", "js.chargebee.com"],
    },

    # === E-COMMERCE PLATFORMS ===
    "ecommerce_platforms": {
        "Shopify": ["cdn.shopify.com", "shopify.com", "myshopify"],
        "WooCommerce": ["woocommerce", "wc-ajax"],
        "Magento": ["magento", "mage/"],
        "BigCommerce": ["bigcommerce", "cdn.bcapp.dev"],
        "Salesforce Commerce Cloud": ["demandware", "salesforcecommerceclo"],
        "Squarespace Commerce": ["squarespace.com/commerce"],
        "Wix Stores": ["wixstores", "wix.com"],
        "PrestaShop": ["prestashop"],
        "OpenCart": ["opencart"],
        "Volusion": ["volusion", "cdn.volusion.com"],
        "3dcart/Shift4Shop": ["3dcart", "shift4shop"],
        "Ecwid": ["ecwid", "app.ecwid.com"],
        "Snipcart": ["snipcart", "cdn.snipcart.com"],
    },

    # === CONTENT MANAGEMENT ===
    "cms": {
        "WordPress": ["wp-content", "wp-includes", "wp-json"],
        "Webflow": ["webflow.com", "assets.website-files.com"],
        "Wix": ["wix.com", "parastorage.com", "static.wixstatic.com"],
        "Squarespace": ["squarespace.com", "static1.squarespace.com"],
        "Drupal": ["drupal", "sites/default/files"],
        "Joomla": ["joomla", "/media/system/js"],
        "Ghost": ["ghost.io", "ghost.org"],
        "Contentful": ["contentful", "cdn.contentful.com"],
        "Sanity": ["sanity.io", "cdn.sanity.io"],
        "Strapi": ["strapi"],
        "HubSpot CMS": ["hubspot.com/hubfs", "hs-sites.com"],
        "Prismic": ["prismic.io", "cdn.prismic.io"],
        "Storyblok": ["storyblok", "a.storyblok.com"],
        "Builder.io": ["builder.io", "cdn.builder.io"],
        "Framer": ["framer.com", "framerusercontent.com"],
    },

    # === VIDEO & MEDIA ===
    "video_media": {
        "YouTube": ["youtube.com/embed", "youtube-nocookie.com", "ytimg.com"],
        "Vimeo": ["vimeo.com", "player.vimeo.com", "vimeocdn.com"],
        "Wistia": ["wistia", "fast.wistia.com", "wistia-labs"],
        "Vidyard": ["vidyard", "play.vidyard.com"],
        "Loom": ["loom.com", "cdn.loom.com"],
        "Brightcove": ["brightcove", "players.brightcove.net"],
        "JW Player": ["jwplayer", "cdn.jwplayer.com"],
        "Cloudinary": ["cloudinary", "res.cloudinary.com"],
        "Mux": ["mux.com", "stream.mux.com"],
        "SproutVideo": ["sproutvideo", "videos.sproutvideo.com"],
    },

    # === AFFILIATE MARKETING ===
    "affiliate": {
        "ShareASale": ["shareasale", "shareasale.com"],
        "Commission Junction": ["cj.com", "dpbolvw.net", "jdoqocy.net"],
        "Impact": ["impact.com", "impactradius"],
        "Rakuten": ["rakuten", "go.redirectingat.com"],
        "Awin": ["awin", "dwin1.com", "zenaps.com"],
        "PartnerStack": ["partnerstack", "pstk.io"],
        "Refersion": ["refersion", "cdn.refersion.com"],
        "Tapfiliate": ["tapfiliate", "script.tapfiliate.com"],
        "Post Affiliate Pro": ["postaffiliatepro"],
        "Everflow": ["everflow", "effintrk.com"],
        "Skimlinks": ["skimlinks", "s.skimresources.com"],
    },

    # === SCHEDULING & BOOKING ===
    "scheduling": {
        "Calendly": ["calendly", "assets.calendly.com"],
        "Cal.com": ["cal.com"],
        "Acuity Scheduling": ["acuityscheduling", "squareup.com/appointments"],
        "HubSpot Meetings": ["hubspot", "meetings.hubspot.com"],
        "Chili Piper": ["chilipiper", "js.chilipiper.com"],
        "Doodle": ["doodle.com"],
        "SimplyBook": ["simplybook.me"],
        "Setmore": ["setmore"],
        "YouCanBook.me": ["youcanbook.me"],
        "SavvyCal": ["savvycal.com"],
    },

    # === CUSTOMER SUPPORT ===
    "customer_support": {
        "Zendesk": ["zendesk", "zdassets.com"],
        "Freshdesk": ["freshdesk", "freshworks"],
        "Help Scout": ["helpscout", "beacon-v2.helpscout.net"],
        "Intercom": ["intercom", "widget.intercom.io"],
        "Front": ["frontapp.com"],
        "Groove": ["groovehq.com"],
        "Kustomer": ["kustomer", "chat.kustomerapp.com"],
        "Gladly": ["gladly.com"],
        "Dixa": ["dixa.io"],
        "Re:amaze": ["reamaze", "beacon.reamaze.com"],
    },

    # === SEO & PERFORMANCE ===
    "seo_performance": {
        "Google Search Console": ["search.google.com/search-console"],
        "Ahrefs": ["ahrefs", "ahrefs.com"],
        "SEMrush": ["semrush"],
        "Moz": ["moz.com", "analytics.moz.com"],
        "Yoast SEO": ["yoast", "yoast-seo"],
        "Schema.org": ["schema.org", "application/ld+json"],
        "Cloudflare": ["cloudflare", "cdnjs.cloudflare.com"],
        "Fastly": ["fastly", "fastly.net"],
        "Akamai": ["akamai", "akstat"],
        "KeyCDN": ["keycdn"],
        "BunnyCDN": ["bunny.net", "b-cdn.net"],
        "jsDelivr": ["jsdelivr.net"],
    },

    # === ACCESSIBILITY ===
    "accessibility": {
        "UserWay": ["userway", "cdn.userway.org"],
        "accessiBe": ["accessibe", "acsbapp.com"],
        "AudioEye": ["audioeye", "ws.audioeye.com"],
        "EqualWeb": ["equalweb", "cdn.equalweb.com"],
        "User1st": ["user1st"],
        "Monsido": ["monsido"],
    },

    # === CONSENT & PRIVACY ===
    "consent_privacy": {
        "OneTrust": ["onetrust", "cdn.cookielaw.org", "optanon"],
        "CookieBot": ["cookiebot", "consent.cookiebot.com"],
        "TrustArc": ["trustarc", "consent.trustarc.com"],
        "Osano": ["osano", "cmp.osano.com"],
        "Termly": ["termly", "app.termly.io"],
        "CookieYes": ["cookieyes", "cdn.cookieyes.com"],
        "Quantcast Choice": ["quantcast", "cmp.quantcast.com"],
        "Didomi": ["didomi", "sdk.privacy-center.org"],
        "Usercentrics": ["usercentrics", "app.usercentrics.eu"],
        "iubenda": ["iubenda", "cdn.iubenda.com"],
        "Cookie Script": ["cookie-script.com"],
        "Civic Cookie Control": ["civiccomputing", "cc.cdn.civiccomputing.com"],
    },

    # === TRANSLATION ===
    "translation": {
        "Google Translate": ["translate.google.com", "translate_http"],
        "Weglot": ["weglot", "cdn.weglot.com"],
        "Lokalise": ["lokalise"],
        "Localize": ["localize", "sdk.localizejs.com"],
        "Transifex": ["transifex"],
        "Crowdin": ["crowdin"],
    },

    # === FORMS ===
    "forms": {
        "Typeform": ["typeform", "embed.typeform.com"],
        "JotForm": ["jotform", "cdn.jotfor.ms"],
        "Google Forms": ["docs.google.com/forms"],
        "Formstack": ["formstack", "formstack.com"],
        "Wufoo": ["wufoo", "wufoo.com"],
        "Cognito Forms": ["cognitoforms", "cdn.cognito.io"],
        "Paperform": ["paperform.co"],
        "Tally": ["tally.so"],
        "Formspark": ["formspark"],
        "Formspree": ["formspree.io"],
        "Basin": ["usebasin.com"],
        "HubSpot Forms": ["hsforms", "js.hsforms.net"],
    },
}


def fetch_website(url):
    """Fetch website HTML with proper error handling"""
    if not url.startswith("http"):
        url = "https://" + url
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "identity",
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, timeout=20, context=ctx) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_meta(html):
    """Extract meta information from HTML"""
    meta = {}
    
    # Title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if title_match:
        meta["title"] = title_match.group(1).strip()[:200]
    
    # Meta description
    desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']', html, re.IGNORECASE)
    if desc_match:
        meta["description"] = desc_match.group(1).strip()[:500]
    
    # OG image
    og_image = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if og_image:
        meta["og_image"] = og_image.group(1).strip()
    
    # Favicon
    favicon = re.search(r'<link[^>]+rel=["\'](?:shortcut )?icon["\'][^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if favicon:
        meta["favicon"] = favicon.group(1).strip()
    
    return meta


def extract_scripts(html):
    """Extract all script sources and inline scripts"""
    scripts = []
    
    # External scripts
    src_matches = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    scripts.extend(src_matches)
    
    # Inline scripts (first 300 chars)
    inline_matches = re.findall(r"<script[^>]*>(.*?)</script>", html, re.DOTALL | re.IGNORECASE)
    for match in inline_matches:
        if match.strip():
            scripts.append(f"[inline]: {match.strip()[:300]}")
    
    return scripts[:100]


def detect_tools(html, scripts_text):
    """Detect all marketing tools from HTML and scripts"""
    combined_text = (html + " " + scripts_text).lower()
    detected = {}
    
    for category, tools in MARKETING_TOOLS.items():
        category_tools = []
        for tool_name, patterns in tools.items():
            for pattern in patterns:
                if pattern.lower() in combined_text:
                    category_tools.append({
                        "name": tool_name,
                        "matched_pattern": pattern,
                        "confidence": "high" if len([p for p in patterns if p.lower() in combined_text]) > 1 else "medium"
                    })
                    break
        if category_tools:
            detected[category] = category_tools
    
    return detected


def get_tool_summary(detected_tools):
    """Create a summary of detected tools"""
    summary = {
        "total_tools": 0,
        "categories_found": [],
        "tools_by_category": {}
    }
    
    for category, tools in detected_tools.items():
        tool_names = [t["name"] for t in tools]
        summary["tools_by_category"][category] = tool_names
        summary["categories_found"].append(category)
        summary["total_tools"] += len(tools)
    
    return summary


def extract_visible_text(html):
    """Extract visible text for context"""
    # Remove scripts and styles
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<noscript[^>]*>.*?</noscript>", "", html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove tags
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    
    return text[:5000]


def scrape_marketing_tools(url):
    """Main scraping function"""
    try:
        html = fetch_website(url)
        scripts = extract_scripts(html)
        scripts_text = " ".join(scripts)
        
        detected_tools = detect_tools(html, scripts_text)
        summary = get_tool_summary(detected_tools)
        
        return {
            "success": True,
            "url": url,
            "meta": extract_meta(html),
            "summary": summary,
            "detected_tools": detected_tools,
            "scripts": scripts[:50],  # Limit for response size
            "text_preview": extract_visible_text(html)[:1000],
            "html_length": len(html),
            "analysis_timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z"
        }
        
    except urllib.error.URLError as e:
        return {
            "success": False,
            "url": url,
            "error": f"URL Error: {str(e)}",
            "error_type": "url_error"
        }
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": str(e),
            "error_type": "general_error"
        }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        url = params.get("url", [None])[0]
        
        # Check for health/info endpoint
        if parsed.path == "/api/info" or (not url and parsed.path in ["/", "/api/scrape"]):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            info = {
                "name": "Marketing Tools Scraper API",
                "version": "1.0.0",
                "usage": "/api/scrape?url=https://example.com",
                "categories": list(MARKETING_TOOLS.keys()),
                "total_tools_detected": sum(len(tools) for tools in MARKETING_TOOLS.values()),
                "endpoints": {
                    "/api/scrape?url=<website>": "Scrape marketing tools from a website",
                    "/api/info": "Get API information"
                }
            }
            
            if not url and parsed.path in ["/", "/api/scrape"]:
                info["error"] = "Missing 'url' parameter"
                info["example"] = "/api/scrape?url=https://stripe.com"
            
            self.wfile.write(json.dumps(info, indent=2).encode())
            return
        
        # Scrape the website
        result = scrape_marketing_tools(url)
        
        self.send_response(200 if result["success"] else 500)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
