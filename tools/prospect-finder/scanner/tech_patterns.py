"""
Technology detection patterns for website scanning.
Based on Wappalyzer/BuiltWith detection approaches.
"""

# CMS Detection Patterns
CMS_PATTERNS = {
    "wordpress": {
        "html": [
            r'wp-content/',
            r'wp-includes/',
            r'/wp-json/',
            r'<meta name="generator" content="WordPress',
        ],
        "headers": {
            "x-powered-by": r'WordPress',
            "link": r'<.*wp-json.*>',
        },
        "meta_generator": r'WordPress\s*([\d.]+)?',
    },
    "drupal": {
        "html": [
            r'Drupal\.settings',
            r'/sites/default/files/',
            r'/sites/all/',
            r'drupal\.js',
            r'<meta name="generator" content="Drupal',
        ],
        "headers": {
            "x-drupal-cache": r'.*',
            "x-generator": r'Drupal',
        },
        "meta_generator": r'Drupal\s*([\d.]+)?',
    },
    "aem": {
        "html": [
            r'/etc/designs/',
            r'/content/dam/',
            r'/etc\.clientlibs/',
            r'cq\.wcm\.config',
            r'granite\.ui',
        ],
        "headers": {
            "x-aem-clusterinfo": r'.*',
        },
    },
    "sitecore": {
        "html": [
            r'sitecore',
            r'/sitecore/shell/',
            r'sc_site=',
        ],
        "cookies": ["SC_ANALYTICS", "sitecore"],
    },
    "webflow": {
        "html": [
            r'webflow\.js',
            r'data-wf-site',
            r'data-wf-page',
            r'<meta content="Webflow"',
        ],
        "meta_generator": r'Webflow',
    },
    "squarespace": {
        "html": [
            r'squarespace\.com',
            r'static\.squarespace\.com',
            r'<meta content="Squarespace"',
        ],
        "meta_generator": r'Squarespace',
    },
    "wix": {
        "html": [
            r'wix\.com',
            r'static\.wixstatic\.com',
            r'X-Wix-',
        ],
        "headers": {
            "x-wix-request-id": r'.*',
        },
    },
    "hubspot": {
        "html": [
            r'hs-scripts\.com',
            r'hubspot\.com',
            r'hs-analytics\.net',
        ],
    },
    "contentful": {
        "html": [
            r'contentful\.com',
            r'ctfassets\.net',
        ],
    },
    "craft": {
        "html": [
            r'<meta name="generator" content="Craft CMS',
        ],
        "headers": {
            "x-powered-by": r'Craft CMS',
        },
        "meta_generator": r'Craft CMS',
    },
    "shopify": {
        "html": [
            r'cdn\.shopify\.com',
            r'Shopify\.theme',
            r'/shopify/',
        ],
        "headers": {
            "x-shopid": r'.*',
        },
    },
    "magento": {
        "html": [
            r'Mage\.Cookies',
            r'/skin/frontend/',
            r'mage/cookies\.js',
        ],
    },
    "kentico": {
        "html": [
            r'CMSPages/',
            r'Kentico',
        ],
        "meta_generator": r'Kentico',
    },
    "episerver": {
        "html": [
            r'EPiServer',
            r'episerver',
        ],
    },
    "umbraco": {
        "html": [
            r'umbraco',
            r'/Umbraco/',
        ],
        "meta_generator": r'Umbraco',
    },
}

# Framework Detection Patterns
FRAMEWORK_PATTERNS = {
    "react": {
        "html": [
            r'react\.js',
            r'react\.min\.js',
            r'react-dom',
            r'data-reactroot',
            r'__REACT_DEVTOOLS',
        ],
    },
    "vue": {
        "html": [
            r'vue\.js',
            r'vue\.min\.js',
            r'data-v-',
            r'__VUE__',
        ],
    },
    "angular": {
        "html": [
            r'angular\.js',
            r'angular\.min\.js',
            r'ng-app',
            r'ng-controller',
            r'\[\(.*\)\]',  # Angular binding syntax
        ],
    },
    "next": {
        "html": [
            r'/_next/',
            r'__NEXT_DATA__',
        ],
    },
    "nuxt": {
        "html": [
            r'/_nuxt/',
            r'__NUXT__',
        ],
    },
    "gatsby": {
        "html": [
            r'gatsby',
            r'___gatsby',
        ],
    },
    "jquery": {
        "html": [
            r'jquery[\.-]',
            r'jQuery',
        ],
    },
    "bootstrap": {
        "html": [
            r'bootstrap\.css',
            r'bootstrap\.min\.css',
            r'bootstrap\.js',
        ],
    },
    "tailwind": {
        "html": [
            r'tailwindcss',
            r'tailwind\.css',
        ],
    },
}

# Analytics Detection Patterns
ANALYTICS_PATTERNS = {
    "google_analytics_4": {
        "html": [
            r'gtag\(.*G-',
            r'googletagmanager\.com.*gtag',
            r'gtag\.js\?id=G-',
        ],
    },
    "google_analytics_ua": {
        "html": [
            r'UA-\d+-\d+',
            r'google-analytics\.com/analytics\.js',
        ],
    },
    "google_tag_manager": {
        "html": [
            r'googletagmanager\.com/gtm\.js',
            r'GTM-[A-Z0-9]+',
        ],
    },
    "adobe_analytics": {
        "html": [
            r'omniture',
            r'adobe\.com/b/ss/',
            r's_code\.js',
        ],
    },
    "mixpanel": {
        "html": [
            r'mixpanel\.com',
            r'mixpanel\.init',
        ],
    },
    "segment": {
        "html": [
            r'segment\.com/analytics',
            r'cdn\.segment\.com',
        ],
    },
    "hotjar": {
        "html": [
            r'hotjar\.com',
            r'hjSiteSettings',
        ],
    },
    "heap": {
        "html": [
            r'heap\.io',
            r'heapanalytics',
        ],
    },
    "fullstory": {
        "html": [
            r'fullstory\.com',
            r'fullstory\.init',
        ],
    },
}

# Hosting/CDN Detection
HOSTING_PATTERNS = {
    "aws": {
        "headers": {
            "server": r'AmazonS3|CloudFront',
            "x-amz-cf-id": r'.*',
            "x-amz-request-id": r'.*',
        },
    },
    "cloudflare": {
        "headers": {
            "cf-ray": r'.*',
            "server": r'cloudflare',
        },
    },
    "vercel": {
        "headers": {
            "x-vercel-id": r'.*',
            "server": r'Vercel',
        },
    },
    "netlify": {
        "headers": {
            "x-nf-request-id": r'.*',
            "server": r'Netlify',
        },
    },
    "pantheon": {
        "headers": {
            "x-pantheon-styx-hostname": r'.*',
            "server": r'nginx.*pantheon',
        },
    },
    "acquia": {
        "headers": {
            "x-ah-environment": r'.*',
            "x-request-id": r'.*acquia.*',
        },
    },
    "wpengine": {
        "headers": {
            "x-powered-by": r'WP Engine',
            "wpe-backend": r'.*',
        },
    },
    "azure": {
        "headers": {
            "x-azure-ref": r'.*',
            "x-ms-request-id": r'.*',
        },
    },
    "google_cloud": {
        "headers": {
            "x-cloud-trace-context": r'.*',
            "server": r'Google',
        },
    },
    "fastly": {
        "headers": {
            "x-served-by": r'cache-',
            "fastly-debug-digest": r'.*',
        },
    },
    "akamai": {
        "headers": {
            "x-akamai-transformed": r'.*',
            "x-cache-key": r'.*akamai.*',
        },
    },
}

# Outdated library versions (security/maintenance concerns)
OUTDATED_LIBRARIES = {
    "jquery": {
        "current": "3.7",
        "outdated_patterns": [
            (r'jquery[/-]1\.', "1.x", "critical"),
            (r'jquery[/-]2\.', "2.x", "high"),
            (r'jquery[/-]3\.[0-5]', "3.0-3.5", "medium"),
        ],
    },
    "bootstrap": {
        "current": "5.3",
        "outdated_patterns": [
            (r'bootstrap[/-]2\.', "2.x", "critical"),
            (r'bootstrap[/-]3\.', "3.x", "high"),
            (r'bootstrap[/-]4\.[0-4]', "4.0-4.4", "medium"),
        ],
    },
    "angular": {
        "current": "17",
        "outdated_patterns": [
            (r'angular[/-]1\.', "AngularJS 1.x", "critical"),
        ],
    },
    "react": {
        "current": "18",
        "outdated_patterns": [
            (r'react[/-]15\.', "15.x", "high"),
            (r'react[/-]16\.[0-7]', "16.0-16.7", "medium"),
        ],
    },
    "drupal": {
        "current": "10",
        "outdated_patterns": [
            (r'Drupal\s*7', "7.x", "critical"),
            (r'Drupal\s*8', "8.x", "high"),
            (r'Drupal\s*9\.[0-3]', "9.0-9.3", "medium"),
        ],
    },
    "wordpress": {
        "current": "6.4",
        "outdated_patterns": [
            (r'WordPress\s*[45]\.', "4.x/5.x", "high"),
            (r'WordPress\s*6\.[0-2]', "6.0-6.2", "low"),
        ],
    },
}

# Privacy/Cookie Detection
PRIVACY_PATTERNS = {
    "cookie_banners": [
        r'cookie-consent',
        r'cookie-notice',
        r'cookieconsent',
        r'gdpr-consent',
        r'onetrust',
        r'OneTrust',
        r'cookiebot',
        r'Cookiebot',
        r'trustarc',
        r'TrustArc',
        r'consent.*manager',
        r'cookie.*policy',
        r'accept.*cookies',
    ],
    "privacy_policy_links": [
        r'/privacy',
        r'/privacy-policy',
        r'/privacypolicy',
        r'/legal/privacy',
    ],
}

# Redesign/Rebrand Signals
REDESIGN_SIGNALS = {
    "job_postings": [
        "web developer",
        "web designer",
        "ux designer",
        "ui designer",
        "digital designer",
        "front-end developer",
        "frontend developer",
        "web producer",
        "digital marketing manager",
        "cms developer",
        "drupal developer",
        "wordpress developer",
    ],
    "content_signals": [
        "new look",
        "new brand",
        "rebrand",
        "refreshed",
        "redesigned",
        "new website",
        "website launch",
        "brand refresh",
        "new identity",
    ],
}

# Key pages to crawl
KEY_PAGES = [
    "/",
    "/about",
    "/about-us",
    "/contact",
    "/services",
    "/solutions",
    "/products",
    "/careers",
    "/jobs",
    "/blog",
    "/news",
    "/resources",
]

# LinkedIn/Social Research Patterns
LINKEDIN_SIGNALS = {
    "job_titles": [
        "web developer",
        "web designer",
        "ux designer",
        "ui designer",
        "ui/ux designer",
        "digital designer",
        "front-end developer",
        "frontend developer",
        "fullstack developer",
        "web producer",
        "digital marketing manager",
        "cms developer",
        "drupal developer",
        "wordpress developer",
        "sitecore developer",
        "aem developer",
        "creative director",
        "head of digital",
        "vp digital",
        "director of web",
        "web manager",
    ],
    "funding_keywords": [
        "series a",
        "series b",
        "series c",
        "series d",
        "funding round",
        "raised",
        "investment",
        "venture capital",
        "ipo",
        "acquisition",
        "merger",
    ],
    "project_keywords": [
        "website redesign",
        "digital transformation",
        "replatforming",
        "cms migration",
        "brand refresh",
        "new website",
        "website launch",
        "ux overhaul",
        "accessibility initiative",
        "wcag compliance",
    ],
}
