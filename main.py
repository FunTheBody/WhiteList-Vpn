#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 Proxy Subscription Merger - С РАЗДЕЛИТЕЛЯМИ
"""

import base64
import re
import requests
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
import json

# 🔑 НАСТРОЙКИ
SUBSCRIPTIONS = [
    {
        "url": "https://izzzyvpn.2bd.net/sub.php?token=S6aEMcA0GXGt9qw7odYs",
        "name_prefix": "🔒 Черные списки",
        "group_name": "⬇️ОБХОД ЧЕРНЫХ СПИСКОВ⬇️"
    },
    {
        "url": "https://key.prosvet.best/sub",
        "name_prefix": "⚪ Белые списки",
        "group_name": "⬇️ОБХОД БЕЛЫХ СПИСКОВ⬇️"
    },
    {
        "url": "https://raw.githubusercontent.com/likzil/vless1/main/Treetcpvpn",
        "name_prefix": "🔒 Черные списки",
        "group_name": "⬇️ОБХОД ЧЕРНЫХ СПИСКОВ⬇️"
    }
]

# 🌍 Словарь флагов — ВСЕ ФЛАГИ
COUNTRY_FLAGS = {
    'RU': '🇷🇺', 'UA': '🇺🇦', 'BY': '🇧', 'KZ': '🇿', 'GE': '🇬🇪',
    'DE': '🇩🇪', 'US': '🇺🇸', 'GB': '🇬', 'NL': '🇱', 'FR': '🇫🇷',
    'PL': '🇵', 'TR': '🇷', 'CN': '🇨🇳', 'JP': '🇯🇵', 'SG': '🇸🇬',
    'KR': '🇰🇷', 'IN': '🇮🇳', 'BR': '🇧', 'CA': '🇦', 'AU': '🇦🇺',
    'IT': '🇮🇹', 'ES': '🇪🇸', 'SE': '🇸', 'NO': '🇴', 'FI': '🇫🇮',
    'CH': '🇨', 'AT': '🇹', 'BE': '🇧🇪', 'CZ': '🇨', 'RO': '🇴',
    'MD': '🇲🇩', 'LT': '🇱🇹', 'LV': '🇱', 'EE': '🇪', 'AZ': '🇦🇿',
    'AM': '🇦🇲', 'UZ': '🇺', 'KG': '🇬', 'TJ': '🇹', 'MN': '🇳',
    'VN': '🇻🇳', 'TH': '🇹🇭', 'MY': '🇲', 'ID': '🇩', 'PH': '🇵🇭',
    'HK': '🇭', 'TW': '🇼', 'MO': '🇲🇴', 'IL': '🇮🇱', 'AE': '🇦🇪',
    'SA': '🇸🇦', 'EG': '🇪🇬', 'ZA': '🇿🇦', 'NG': '🇳🇬', 'KE': '🇰🇪',
    'AR': '🇦🇷', 'CL': '🇨🇱', 'CO': '🇨🇴', 'MX': '🇲🇽', 'PE': '🇵🇪',
    'VE': '🇻🇪', 'GR': '🇬🇷', 'PT': '🇵🇹', 'IE': '🇮🇪', 'DK': '🇩🇰',
    'IS': '🇮🇸', 'LU': '🇱🇺', 'MT': '🇲🇹', 'CY': '🇨', 'SK': '🇰',
    'SI': '🇸', 'HR': '🇷', 'BG': '🇧🇬', 'RS': '🇷🇸', 'BA': '🇧🇦',
    'MK': '🇲🇰', 'AL': '🇦🇱', 'ME': '🇲', 'XK': '🇰', 
    'DEFAULT': '🌐'
}

# 🔍 Паттерны стран — МАКСИМАЛЬНО ПОЛНЫЕ
COUNTRY_PATTERNS = {
    'RU': [r'ru\b', r'moscow', r'moskva', r'spb', r'saint.petersburg', r'\.ru\b', r'russia', r'москва', r'питер', r'спб', r'екатеринбург', r'новосибирск'],
    'UA': [r'ua\b', r'kiev', r'kyiv', r'kharkiv', r'odessa', r'\.ua\b', r'ukraine', r'киев', r'харьков', r'одесса', r'львов', r'dnipro'],
    'DE': [r'de\b', r'germany', r'frankfurt', r'berlin', r'munich', r'\.de\b', r'германия', r'франкфурт', r'берлин', r'hamburg', r'cologne'],
    'US': [r'us\b', r'usa', r'new.york', r'los.angeles', r'miami', r'\.us\b', r'united.states', r'нью.йорк', r'майами', r'dallas', r'chicago', r'atlanta'],
    'GB': [r'gb\b', r'uk\b', r'london', r'manchester', r'\.uk\b', r'\.co.uk\b', r'united.kingdom', r'лондон', r'great.britain'],
    'NL': [r'nl\b', r'netherlands', r'amsterdam', r'rotterdam', r'\.nl\b', r'амстердам', r'нидерланды', r'hague'],
    'FR': [r'fr\b', r'france', r'paris', r'marseille', r'\.fr\b', r'франция', r'париж', r'lyon'],
    'PL': [r'pl\b', r'poland', r'warsaw', r'krakow', r'\.pl\b', r'польша', r'варшава', r'краков', r'gdansk'],
    'TR': [r'tr\b', r'turkey', r'istanbul', r'ankara', r'\.tr\b', r'турция', r'стамбул', r'ankara', r'izmir'],
    'CN': [r'cn\b', r'china', r'beijing', r'shanghai', r'\.cn\b', r'китай', r'пекин', r'гуанчжоу', r'shenzhen'],
    'JP': [r'jp\b', r'japan', r'tokyo', r'osaka', r'\.jp\b', r'япония', r'токио', r'yokohama'],
    'SG': [r'sg\b', r'singapore', r'\.sg\b', r'сингапур'],
    'KR': [r'kr\b', r'korea', r'seoul', r'\.kr\b', r'корея', r'сеул', r'busan'],
    'KZ': [r'kz\b', r'kazakhstan', r'almaty', r'astana', r'\.kz\b', r'казахстан', r'алматы', r'астана', r'shymkent'],
    'BY': [r'by\b', r'belarus', r'minsk', r'\.by\b', r'беларусь', r'минск', r'gomel'],
    'GE': [r'ge\b', r'georgia', r'tbilisi', r'\.ge\b', r'грузия', r'тбилиси', r'kutaisi'],
    'FI': [r'fi\b', r'finland', r'helsinki', r'\.fi\b', r'финляндия', r'хельсинки', r'tampere'],
    'IT': [r'it\b', r'italy', r'italian', r'rome', r'milan', r'\.it\b', r'италия', r'рим', r'милан', r'naples'],
    'ES': [r'es\b', r'spain', r'madrid', r'barcelona', r'\.es\b', r'испания', r'мадрид', r'валенсия'],
    'SE': [r'se\b', r'sweden', r'stockholm', r'\.se\b', r'швеция', r'стокгольм', r'gothenburg'],
    'CA': [r'ca\b', r'canada', r'toronto', r'vancouver', r'\.ca\b', r'канада', r'торонто', r'montreal'],
    'AU': [r'au\b', r'australia', r'sydney', r'melbourne', r'\.au\b', r'австралия', r'сидней', r'brisbane'],
    'BR': [r'br\b', r'brazil', r'sao.paulo', r'\.br\b', r'бразилия', r'сао.паулу', r'riodejaneiro'],
    'IN': [r'in\b', r'india', r'mumbai', r'delhi', r'\.in\b', r'индия', r'мумбаи', r'дели', r'bangalore'],
    'AE': [r'ae\b', r'uae', r'dubai', r'\.ae\b', r'оаэ', r'дубай', r'abudhabi'],
    'IL': [r'il\b', r'israel', r'tel.aviv', r'\.il\b', r'израиль', r'тель.авив', r'jerusalem'],
    'RO': [r'ro\b', r'romania', r'bucharest', r'\.ro\b', r'румыния', r'бухарест', r'cluj'],
    'MD': [r'md\b', r'moldova', r'chisinau', r'\.md\b', r'молдова', r'кишинев', r'balti'],
    'CZ': [r'cz\b', r'czech', r'prague', r'\.cz\b', r'чехия', r'прага', r'brno'],
    'AT': [r'at\b', r'austria', r'vienna', r'\.at\b', r'австрия', r'вена', r'salzburg'],
    'CH': [r'ch\b', r'switzerland', r'zurich', r'\.ch\b', r'швейцария', r'цюрих', r'geneva'],
    'BE': [r'be\b', r'belgium', r'brussels', r'\.be\b', r'бельгия', r'брюссель', r'antwerp'],
    'PT': [r'pt\b', r'portugal', r'lisbon', r'\.pt\b', r'португалия', r'лиссабон', r'porto'],
    'GR': [r'gr\b', r'greece', r'athens', r'\.gr\b', r'греция', r'афины', r'thessaloniki'],
    'BG': [r'bg\b', r'bulgaria', r'sofia', r'\.bg\b', r'болгария', r'софия', r'plovdiv'],
    'RS': [r'rs\b', r'serbia', r'belgrade', r'\.rs\b', r'сербия', r'белград', r'novisad'],
    'HR': [r'hr\b', r'croatia', r'zagreb', r'\.hr\b', r'хорватия', r'загреб', r'split'],
    'SK': [r'sk\b', r'slovakia', r'bratislava', r'\.sk\b', r'словакия', r'братислава', r'kosice'],
    'HU': [r'hu\b', r'hungary', r'budapest', r'\.hu\b', r'венгрия', r'будапешт', r'debrecen'],
    'LT': [r'lt\b', r'lithuania', r'vilnius', r'\.lt\b', r'литва', r'вильнюс', r'kaunas'],
    'LV': [r'lv\b', r'latvia', r'riga', r'\.lv\b', r'латвия', r'рига', r'daugavpils'],
    'EE': [r'ee\b', r'estonia', r'tallinn', r'\.ee\b', r'эстония', r'таллин', r'tartu'],
    'AZ': [r'az\b', r'azerbaijan', r'baku', r'\.az\b', r'азербайджан', r'баку', r'ganja'],
    'AM': [r'am\b', r'armenia', r'yerevan', r'\.am\b', r'армения', r'ереван', r'gyumri'],
    'UZ': [r'uz\b', r'uzbekistan', r'tashkent', r'\.uz\b', r'узбекистан', r'ташкент', r'samarkand'],
    'KG': [r'kg\b', r'kyrgyzstan', r'bishkek', r'\.kg\b', r'киргизия', r'бишкек', r'osh'],
    'TJ': [r'tj\b', r'tajikistan', r'dushanbe', r'\.tj\b', r'таджикистан', r'душанбе', r'khujand'],
    'MN': [r'mn\b', r'mongolia', r'ulaanbaatar', r'\.mn\b', r'монголия', r'улан.батор', r'erdenet'],
    'VN': [r'vn\b', r'vietnam', r'hanoi', r'ho.chi.minh', r'\.vn\b', r'вьетнам', r'ханой', r'saigon'],
    'TH': [r'th\b', r'thailand', r'bangkok', r'\.th\b', r'таиланд', r'бангкок', r'chiangmai'],
    'MY': [r'my\b', r'malaysia', r'kualalumpur', r'\.my\b', r'малайзия', r'куала.лумпур', r'johor'],
    'ID': [r'id\b', r'indonesia', r'jakarta', r'\.id\b', r'индонезия', r'джакарта', r'surabaya'],
    'PH': [r'ph\b', r'philippines', r'manila', r'\.ph\b', r'филиппины', r'манила', r'cebu'],
    'HK': [r'hk\b', r'hongkong', r'hk\b', r'\.hk\b', r'гонконг', r'коулун'],
    'TW': [r'tw\b', r'taiwan', r'taipei', r'\.tw\b', r'тайвань', r'тайбэй', r'kaohsiung'],
    'SA': [r'sa\b', r'saudiarabia', r'riyadh', r'\.sa\b', r'саудовская.аравия', r'эр.рияд', r'jeddah'],
    'EG': [r'eg\b', r'egypt', r'cairo', r'\.eg\b', r'египет', r'каир', r'alexandria'],
    'ZA': [r'za\b', r'southafrica', r'capetown', r'johannesburg', r'\.za\b', r'юар', r'кейптаун', r'йоханнесбург'],
    'NG': [r'ng\b', r'nigeria', r'lagos', r'\.ng\b', r'нигерия', r'лагос', r'abuja'],
    'KE': [r'ke\b', r'kenya', r'nairobi', r'\.ke\b', r'кения', r'найроби', r'mombasa'],
    'AR': [r'ar\b', r'argentina', r'buenosaires', r'\.ar\b', r'аргентина', r'буэнос.айрес', r'cordoba'],
    'CL': [r'cl\b', r'chile', r'santiago', r'\.cl\b', r'чили', r'сантьяго', r'valparaiso'],
    'CO': [r'co\b', r'colombia', r'bogota', r'\.co\b', r'колумбия', r'богота', r'medellin'],
    'MX': [r'mx\b', r'mexico', r'mexicocity', r'\.mx\b', r'мексика', r'мехико', r'guadalajara'],
    'PE': [r'pe\b', r'peru', r'lima', r'\.pe\b', r'перу', r'лима', r'cusco'],
    'VE': [r've\b', r'venezuela', r'caracas', r'\.ve\b', r'венесуэла', r'каракас', r'maracaibo'],
    'IE': [r'ie\b', r'ireland', r'dublin', r'\.ie\b', r'ирландия', r'дублин', r'cork'],
    'DK': [r'dk\b', r'denmark', r'copenhagen', r'\.dk\b', r'дания', r'копенгаген', r'aarhus'],
    'NO': [r'no\b', r'norway', r'oslo', r'\.no\b', r'норвегия', r'осло', r'bergen'],
    'IS': [r'is\b', r'iceland', r'reykjavik', r'\.is\b', r'исландия', r'рейкьявик', r'akureyri'],
    'LU': [r'lu\b', r'luxembourg', r'luxembourg', r'\.lu\b', r'люксембург'],
    'MT': [r'mt\b', r'malta', r'valletta', r'\.mt\b', r'мальта', r'валлетта'],
    'CY': [r'cy\b', r'cyprus', r'nicosia', r'\.cy\b', r'кипр', r'никосия', r'limassol'],
    'BA': [r'ba\b', r'bosnia', r'sarajevo', r'\.ba\b', r'босния', r'сараево', r'banjaluka'],
    'AL': [r'al\b', r'albania', r'tirana', r'\.al\b', r'албания', r'тирана', r'durres'],
    'ME': [r'me\b', r'montenegro', r'podgorica', r'\.me\b', r'черногория', r'подгорица', r'budva'],
    'XK': [r'xk\b', r'kosovo', r'pristina', r'\.xk\b', r'косово', r'приштина'],
}

METADATA_PATTERNS = [
    r'^#profile-', r'^#announce:', r'^#subscription-userinfo:',
    r'^#support-url:', r'^#profile-web-page-url:', r'^#profile-update-interval:',
]


def decode_base64_safe(data: str) -> str:
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except:
        return data


def is_proxy_link(line: str) -> bool:
    line = line.strip()
    if not line or line.startswith('#'):
        return False
    proxy_prefixes = ('vmess://', 'vless://', 'trojan://', 'ss://', 'ssr://', 
                      'hysteria://', 'hysteria2://', 'tuic://', 'hy2://')
    return any(line.lower().startswith(prefix) for prefix in proxy_prefixes)


def detect_country_flag(node_name: str, node_url: str = "", host: str = "") -> str:
    """Улучшенное определение флага — ТЕПЕРЬ ТОЧНО ДЛЯ ВСЕХ"""
    # Объединяем всю информацию
    text = f"{node_name} {node_url} {host}".lower()
    
    # 1. Ищем по паттернам
    for country, patterns in COUNTRY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.I):
                flag = COUNTRY_FLAGS.get(country)
                if flag:
                    return flag
    
    # 2. Ищем по TLD домена
    if host:
        # Извлекаем домен
        domain_match = re.search(r'([a-z0-9.-]+)', host.lower())
        if domain_match:
            domain = domain_match.group(1)
            # Проверяем TLD
            tld_match = re.search(r'\.([a-z]{2,3})$', domain)
            if tld_match:
                tld = tld_match.group(1).upper()
                flag = COUNTRY_FLAGS.get(tld)
                if flag:
                    return flag
            
            # Проверяем весь домен
            for country in COUNTRY_PATTERNS.keys():
                if country.lower() in domain:
                    flag = COUNTRY_FLAGS.get(country)
                    if flag:
                        return flag
    
    # 3. Проверяем по IP диапазонам
    if host:
        ip_match = re.match(r'^(\d{1,3})\.(\d{1,3})', host)
        if ip_match:
            first_octet = int(ip_match.group(1))
            second_octet = int(ip_match.group(2))
            
            # Примерные диапазоны
            if first_octet == 5 or first_octet == 31 or first_octet == 46:
                if second_octet in range(0, 256):
                    return '🇷🇺'  # Россия
            elif first_octet == 85 or first_octet == 88 or first_octet == 91:
                return '🇩🇪'  # Германия
            elif first_octet == 185 or first_octet == 31:
                return '🇳🇱'  # Нидерланды
            elif first_octet == 104 or first_octet == 172:
                return '🇺🇸'  # США (Cloudflare и др.)
    
    # 4. Если ничего не нашли — пробуем угадать по первым буквам
    if node_name:
        name_lower = node_name.lower()
        for country_code, flag in COUNTRY_FLAGS.items():
            if country_code.lower() in name_lower[:20]:  # Проверяем первые 20 символов
                return flag
    
    # 5. Возвращаем глобус если ничего не нашли
    return COUNTRY_FLAGS['DEFAULT']


def get_protocol_info(link: str, proxy_type: str) -> str:
    """Извлекает информацию о протоколе"""
    try:
        if proxy_type == 'vless':
            parsed = urlparse(link)
            params = parse_qs(parsed.query)
            
            security = params.get('security', ['none'])[0]
            type_conn = params.get('type', ['tcp'])[0]
            flow = params.get('flow', [''])[0]
            
            proto_parts = ['VLESS']
            
            if type_conn == 'tcp':
                proto_parts.append('TCP')
            elif type_conn == 'ws':
                proto_parts.append('WS')
            elif type_conn == 'grpc':
                proto_parts.append('gRPC')
            elif type_conn == 'http':
                proto_parts.append('HTTP')
            elif type_conn == 'quic':
                proto_parts.append('QUIC')
            
            if security == 'reality':
                proto_parts.append('REALITY')
            elif security == 'tls':
                proto_parts.append('TLS')
            elif security == 'xtls':
                proto_parts.append('XTLS')
            
            if 'vision' in flow.lower():
                proto_parts.append('VISION')
            
            return ' / '.join(proto_parts)
            
        elif proxy_type == 'vmess':
            config_json = decode_base64_safe(link[8:])
            config = json.loads(config_json)
            
            proto_parts = ['VMESS']
            net = config.get('net', 'tcp')
            tls = config.get('tls', '')
            
            if net == 'tcp':
                proto_parts.append('TCP')
            elif net == 'ws':
                proto_parts.append('WS')
            elif net == 'grpc':
                proto_parts.append('gRPC')
            elif net == 'h2':
                proto_parts.append('H2')
            
            if tls == 'tls':
                proto_parts.append('TLS')
            
            return ' / '.join(proto_parts)
            
        elif proxy_type == 'trojan':
            parsed = urlparse(link)
            params = parse_qs(parsed.query)
            
            proto_parts = ['TROJAN']
            type_conn = params.get('type', ['tcp'])[0]
            security = params.get('security', ['tls'])[0]
            
            if type_conn == 'tcp':
                proto_parts.append('TCP')
            elif type_conn == 'ws':
                proto_parts.append('WS')
            
            if security == 'tls':
                proto_parts.append('TLS')
            elif security == 'reality':
                proto_parts.append('REALITY')
            
            return ' / '.join(proto_parts)
            
        elif proxy_type == 'shadowsocks':
            return 'SHADOWSOCKS'
            
        elif proxy_type == 'hysteria':
            return 'HYSTERIA2'
            
        elif proxy_type == 'tuic':
            return 'TUIC'
            
    except:
        pass
    
    return proxy_type.upper()


def get_server_location(host: str) -> str:
    """Определяет локацию сервера"""
    if not host:
        return ""
    
    host_lower = host.lower()
    
    locations = {
        'moscow': 'Москва', 'msk': 'Москва', 'spb': 'Питер', 'piter': 'Питер', 'saint.petersburg': 'Питер',
        'frankfurt': 'Франкфурт', 'berlin': 'Берлин', 'munich': 'Мюнхен', 'hamburg': 'Гамбург',
        'amsterdam': 'Амстердам', 'rotterdam': 'Роттердам',
        'london': 'Лондон', 'manchester': 'Манчестер',
        'paris': 'Париж', 'marseille': 'Марсель', 'lyon': 'Лион',
        'warsaw': 'Варшава', 'krakow': 'Краков',
        'istanbul': 'Стамбул', 'ankara': 'Анкара',
        'tokyo': 'Токио', 'osaka': 'Осака',
        'singapore': 'Сингапур',
        'new.york': 'Нью-Йорк', 'los.angeles': 'Лос-Анджелес', 'miami': 'Майами', 'dallas': 'Даллас', 'chicago': 'Чикаго',
        'finland': 'Финляндия', 'helsinki': 'Хельсинки',
        'italy': 'Италия', 'rome': 'Рим', 'milan': 'Милан',
        'netherlands': 'Нидерланды',
        'germany': 'Германия',
        'poland': 'Польша',
        'turkey': 'Турция',
        'ukraine': 'Украина', 'kiev': 'Киев', 'kyiv': 'Киев', 'kharkiv': 'Харьков', 'odessa': 'Одесса',
        'kazakhstan': 'Казахстан', 'almaty': 'Алматы', 'astana': 'Астана',
        'belarus': 'Беларусь', 'minsk': 'Минск',
        'georgia': 'Грузия', 'tbilisi': 'Тбилиси',
        'spain': 'Испания', 'madrid': 'Мадрид', 'barcelona': 'Барселона',
        'sweden': 'Швеция', 'stockholm': 'Стокгольм',
        'canada': 'Канада', 'toronto': 'Торонто', 'vancouver': 'Ванкувер',
        'australia': 'Австралия', 'sydney': 'Сидней',
        'brazil': 'Бразилия', 'saopaulo': 'Сан-Паулу',
        'india': 'Индия', 'mumbai': 'Мумбаи', 'delhi': 'Дели',
        'uae': 'ОАЭ', 'dubai': 'Дубай',
        'israel': 'Израиль', 'telaviv': 'Тель-Авив',
        'romania': 'Румыния', 'bucharest': 'Бухарест',
        'moldova': 'Молдова', 'chisinau': 'Кишинев',
        'czech': 'Чехия', 'prague': 'Прага',
        'austria': 'Австрия', 'vienna': 'Вена',
        'switzerland': 'Швейцария', 'zurich': 'Цюрих',
        'belgium': 'Бельгия', 'brussels': 'Брюссель',
        'portugal': 'Португалия', 'lisbon': 'Лиссабон',
        'greece': 'Греция', 'athens': 'Афины',
        'bulgaria': 'Болгария', 'sofia': 'София',
        'serbia': 'Сербия', 'belgrade': 'Белград',
        'croatia': 'Хорватия', 'zagreb': 'Загреб',
        'slovakia': 'Словакия', 'bratislava': 'Братислава',
        'hungary': 'Венгрия', 'budapest': 'Будапешт',
        'lithuania': 'Литва', 'vilnius': 'Вильнюс',
        'latvia': 'Латвия', 'riga': 'Рига',
        'estonia': 'Эстония', 'tallinn': 'Таллин',
        'azerbaijan': 'Азербайджан', 'baku': 'Баку',
        'armenia': 'Армения', 'yerevan': 'Ереван',
        'uzbekistan': 'Узбекистан', 'tashkent': 'Ташкент',
        'kyrgyzstan': 'Киргизия', 'bishkek': 'Бишкек',
        'tajikistan': 'Таджикистан', 'dushanbe': 'Душанбе',
        'mongolia': 'Монголия', 'ulaanbaatar': 'Улан-Батор',
        'vietnam': 'Вьетнам', 'hanoi': 'Ханой',
        'thailand': 'Таиланд', 'bangkok': 'Бангкок',
        'malaysia': 'Малайзия', 'kualalumpur': 'Куала-Лумпур',
        'indonesia': 'Индонезия', 'jakarta': 'Джакарта',
        'philippines': 'Филиппины', 'manila': 'Манила',
        'hongkong': 'Гонконг', 'kualalumpur': 'Куала-Лумпур',
        'taiwan': 'Тайвань', 'taipei': 'Тайбэй',
        'south.korea': 'Южная Корея', 'seoul': 'Сеул',
        'japan': 'Япония', 'tokyo': 'Токио',
        'china': 'Китай', 'beijing': 'Пекин', 'shanghai': 'Шанхай',
        'russia': 'Россия', 'moscow': 'Москва',
        'united.states': 'США', 'newyork': 'Нью-Йорк',
        'united.kingdom': 'Великобритания', 'london': 'Лондон',
        'france': 'Франция', 'paris': 'Париж',
    }
    
    for key, value in locations.items():
        if key in host_lower:
            return value
    
    return ""


def parse_proxy_link(link: str) -> dict:
    link = link.strip()
    if not link or not is_proxy_link(link):
        return None
    
    result = {
        'original': link, 
        'type': None, 
        'name': None, 
        'country_flag': '🌐', 
        'host': '',
        'protocol_info': '',
        'server_location': ''
    }
    
    try:
        if link.startswith('vmess://'):
            result['type'] = 'vmess'
            config_json = decode_base64_safe(link[8:])
            config = json.loads(config_json)
            result['name'] = config.get('ps', 'Unnamed')
            result['host'] = config.get('add', '')
            result['protocol_info'] = get_protocol_info(link, 'vmess')
            
        elif link.startswith('vless://'):
            result['type'] = 'vless'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Unnamed'
            result['host'] = parsed.netloc.split('@')[-1].split(':')[0] if '@' in parsed.netloc else parsed.netloc.split(':')[0]
            result['protocol_info'] = get_protocol_info(link, 'vless')
            
        elif link.startswith('trojan://'):
            result['type'] = 'trojan'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Unnamed'
            result['host'] = parsed.netloc.split('@')[-1].split(':')[0] if '@' in parsed.netloc else parsed.netloc.split(':')[0]
            result['protocol_info'] = get_protocol_info(link, 'trojan')
            
        elif link.startswith('ss://'):
            result['type'] = 'shadowsocks'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Shadowsocks'
            result['host'] = parsed.netloc.split('@')[-1].split(':')[0] if '@' in parsed.netloc else parsed.netloc.split(':')[0]
            result['protocol_info'] = 'SHADOWSOCKS'
            
        elif link.startswith(('hysteria2://', 'hysteria://', 'hy2://')):
            result['type'] = 'hysteria'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Hysteria'
            result['host'] = parsed.netloc.split(':')[0]
            result['protocol_info'] = 'HYSTERIA2'
            
        elif link.startswith('tuic://'):
            result['type'] = 'tuic'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Tuic'
            result['host'] = parsed.netloc.split('@')[-1].split(':')[0] if '@' in parsed.netloc else parsed.netloc.split(':')[0]
            result['protocol_info'] = 'TUIC'
        else:
            result['name'] = f"Proxy-{hash(link) % 10000}"
            
    except Exception as e:
        result['name'] = f"Error-{hash(link) % 10000}"
    
    # 🔥 ВСЕГДА определяем флаг
    result['country_flag'] = detect_country_flag(result['name'], link, result['host'])
    result['server_location'] = get_server_location(result['host'])
    
    return result


def fetch_subscription(url: str) -> list:
    """Загружает подписку"""
    headers = {
        'User-Agent': 'ClashMetaForAndroid/2.11.2 Meta',
        'Accept': '*/*',
    }
    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        content = response.text.strip()
        
        # Пробуем декодировать base64
        if not any(content.startswith(p) for p in ('vmess://', 'vless://', 'trojan://', 'ss://', '{')):
            try:
                content = decode_base64_safe(content)
            except:
                pass
        
        # Разбиваем на строки
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Фильтруем только прокси-ссылки
        proxy_links = []
        for line in lines:
            if is_proxy_link(line):
                is_meta = False
                for pattern in METADATA_PATTERNS:
                    if re.match(pattern, line, re.I):
                        is_meta = True
                        break
                if not is_meta:
                    proxy_links.append(line)
        
        print(f"   Найдено: {len(proxy_links)}")
        return proxy_links
        
    except Exception as e:
        print(f"❌ Ошибка {url}: {e}")
        return []


def rename_proxy_link(original_link: str, new_name: str, proxy_type: str) -> str:
    """Заменяет имя"""
    try:
        if proxy_type == 'vmess':
            config = json.loads(decode_base64_safe(original_link[8:]))
            config['ps'] = new_name
            new_b64 = base64.b64encode(json.dumps(config, ensure_ascii=False).encode('utf-8')).decode().rstrip('=')
            return f"vmess://{new_b64}"
            
        elif proxy_type in ['vless', 'trojan', 'hysteria', 'tuic']:
            parsed = urlparse(original_link)
            from urllib.parse import urlunparse
            return urlunparse(parsed._replace(fragment=new_name))
            
        elif proxy_type == 'shadowsocks':
            if '#' in original_link:
                base, _ = original_link.rsplit('#', 1)
                return f"{base}#{new_name}"
            return f"{original_link}#{new_name}"
        return original_link
    except Exception as e:
        print(f"⚠️ Ошибка: {e}")
        return original_link


def format_proxy_name(prefix: str, flag: str, protocol: str, location: str = "") -> str:
    """Форматирует имя"""
    if location:
        return f"{flag} {prefix} | {protocol} | {location}"
    else:
        return f"{flag} {prefix} | {protocol}"


def create_group_header(group_name: str, total_servers: int = 0) -> str:
    """Создает заголовок группы серверов (разделитель)"""
    # Создаем специальный комментарий-разделитель
    return f"# {group_name} ({total_servers} серверов)"


def process_subscription(url: str, name_prefix: str, group_name: str, is_first_group: bool = False) -> list:
    print(f"📥 {url[:60]}...")
    links = fetch_subscription(url)
    
    processed = []
    
    # Если это первая группа, добавляем заголовок
    if is_first_group:
        # Создаем "разделитель" как первый элемент
        # Используем специальный vless:// с dummy данными
        header_link = f"vless://00000000-0000-0000-0000-000000000000@none.none:443#{group_name}"
        processed.append(header_link)
    
    for link in links:
        parsed = parse_proxy_link(link)
        if parsed and parsed.get('name'):
            flag = parsed['country_flag']
            protocol = parsed.get('protocol_info', parsed['type'].upper())
            location = parsed.get('server_location', '')
            
            new_name = format_proxy_name(name_prefix, flag, protocol, location)
            
            new_link = rename_proxy_link(link, new_name, parsed['type'])
            if new_link:
                processed.append(new_link)
    
    print(f"✅ Обработано: {len(processed)}")
    return processed


def merge_subscriptions() -> str:
    print("🚀 Запуск...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_nodes = []
    group_counts = {}
    
    # Сначала собираем все серверы и считаем по группам
    for i, sub in enumerate(SUBSCRIPTIONS):
        is_first = (i == 0)
        nodes = process_subscription(sub['url'], sub['name_prefix'], sub['group_name'], is_first)
        
        # Считаем серверы по группам
        group_name = sub['group_name']
        if group_name not in group_counts:
            group_counts[group_name] = 0
        group_counts[group_name] += len(nodes)
        
        all_nodes.extend(nodes)
    
    print("=" * 60)
    print(f"📊 ВСЕГО: {len(all_nodes)}")
    
    result = '\n'.join(all_nodes)
    
    # Добавляем описание подписки
    header = f"""#
#  ╔══════════════════════════════════════════════╗
#  ║     PREMIUM VPN SUBSCRIPTION                 ║
#  ║  🔥 Автоматическое обновление каждый час     ║
#  ║  ⚡ Быстрые и стабильные серверы             ║
#  ║  🌍 Серверы по всему миру                    ║
#  ╚══════════════════════════════════════════════╝
#
#  📊 Статистика:
#  • Черные списки: {group_counts.get('⬇️ОБХОД ЧЕРНЫХ СПИСКОВ⬇️', 0)} серверов
#  • Белые списки: {group_counts.get('⬇️ОБХОД БЕЛЫХ СПИСКОВ⬇️', 0)} серверов
#  • Всего: {len(all_nodes)} серверов
#
#  🔄 Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
#  ⚙️ Generated by ProxyMerger
#
"""
    
    return header + result


def save_to_file(content: str, filepath: str = "output/merged_sub.txt"):
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 {filepath}")


def main():
    try:
        result = merge_subscriptions()
        save_to_file(result)
        b64 = base64.b64encode(result.encode('utf-8')).decode()
        save_to_file(b64, "output/merged_sub_base64.txt")
        print("\n✨ ГОТОВО!")
        return 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
