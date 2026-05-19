#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 Proxy Subscription Merger - ВСЕ С ФЛАГАМИ
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
    },
    {
        "url": "https://key.prosvet.best/sub",
        "name_prefix": "⚪ Белые списки",
    },
    {
        "url": "https://raw.githubusercontent.com/likzil/vless1/main/Treetcpvpn",
        "name_prefix": "🔒 Черные списки",
    }
]

# 🌍 Словарь флагов
COUNTRY_FLAGS = {
    'RU': '🇷🇺', 'UA': '🇺🇦', 'BY': '🇧', 'KZ': '🇿', 'GE': '🇬🇪',
    'DE': '🇩', 'US': '🇸', 'GB': '🇬🇧', 'NL': '🇳🇱', 'FR': '🇫',
    'PL': '🇵🇱', 'TR': '🇹🇷', 'CN': '🇨', 'JP': '🇵', 'SG': '🇸🇬',
    'KR': '🇰', 'IN': '🇳', 'BR': '🇧🇷', 'CA': '🇨🇦', 'AU': '🇦🇺',
    'IT': '🇮🇹', 'ES': '🇪🇸', 'SE': '🇸', 'NO': '🇴', 'FI': '🇫🇮',
    'CH': '🇨🇭', 'AT': '🇦🇹', 'BE': '🇧🇪', 'CZ': '🇨', 'RO': '🇴',
    'MD': '🇲🇩', 'LT': '🇱🇹', 'LV': '🇱', 'EE': '🇪', 'AZ': '🇦🇿',
    'AM': '🇦🇲', 'UZ': '🇺', 'KG': '🇬', 'TJ': '🇹🇯', 'MN': '🇲🇳',
    'VN': '🇻🇳', 'TH': '🇹🇭', 'MY': '🇲🇾', 'ID': '🇮🇩', 'PH': '🇵🇭',
    'HK': '🇭🇰', 'TW': '🇹🇼', 'MO': '🇲🇴', 'IL': '🇮🇱', 'AE': '🇦🇪',
    'SA': '🇸🇦', 'EG': '🇪🇬', 'ZA': '🇿', 'NG': '🇬', 'KE': '🇰🇪',
    'AR': '🇦🇷', 'CL': '🇨🇱', 'CO': '🇨🇴', 'MX': '🇲🇽', 'PE': '🇵🇪',
    'VE': '🇻🇪', 'GR': '🇬🇷', 'PT': '🇵🇹', 'IE': '🇮🇪', 'DK': '🇩🇰',
    'IS': '🇮🇸', 'LU': '🇱🇺', 'MT': '🇲🇹', 'CY': '🇨', 'SK': '🇰',
    'SI': '🇸🇮', 'HR': '🇭🇷', 'BG': '🇧', 'RS': '🇸', 'BA': '🇧🇦',
    'MK': '🇲🇰', 'AL': '🇦🇱', 'ME': '🇲', 'XK': '🇰', 'UNKNOWN': '🌐'
}

# 🔍 Паттерны стран — РАСШИРЕННЫЕ
COUNTRY_PATTERNS = {
    'RU': [r'ru\b', r'moscow', r'moskva', r'spb', r'saint.petersburg', r'\.ru\b', r'russia', r'москва', r'питер', r'спб'],
    'UA': [r'ua\b', r'kiev', r'kyiv', r'kharkiv', r'odessa', r'\.ua\b', r'ukraine', r'киев', r'харьков', r'одесса'],
    'DE': [r'de\b', r'germany', r'frankfurt', r'berlin', r'munich', r'\.de\b', r'германия', r'франкфурт', r'берлин'],
    'US': [r'us\b', r'usa', r'new.york', r'los.angeles', r'miami', r'\.us\b', r'united.states', r'нью.йорк', r'майами'],
    'GB': [r'gb\b', r'uk\b', r'london', r'manchester', r'\.uk\b', r'\.co.uk\b', r'united.kingdom', r'лондон'],
    'NL': [r'nl\b', r'netherlands', r'amsterdam', r'rotterdam', r'\.nl\b', r'амстердам', r'нидерланды'],
    'FR': [r'fr\b', r'france', r'paris', r'marseille', r'\.fr\b', r'франция', r'париж'],
    'PL': [r'pl\b', r'poland', r'warsaw', r'krakow', r'\.pl\b', r'польша', r'варшава'],
    'TR': [r'tr\b', r'turkey', r'istanbul', r'ankara', r'\.tr\b', r'турция', r'стамбул'],
    'CN': [r'cn\b', r'china', r'beijing', r'shanghai', r'\.cn\b', r'китай', r'пекин'],
    'JP': [r'jp\b', r'japan', r'tokyo', r'osaka', r'\.jp\b', r'япония', r'токио'],
    'SG': [r'sg\b', r'singapore', r'\.sg\b', r'сингапур'],
    'KR': [r'kr\b', r'korea', r'seoul', r'\.kr\b', r'корея', r'сеул'],
    'KZ': [r'kz\b', r'kazakhstan', r'almaty', r'astana', r'\.kz\b', r'казахстан', r'алматы', r'астана'],
    'BY': [r'by\b', r'belarus', r'minsk', r'\.by\b', r'беларусь', r'минск'],
    'GE': [r'ge\b', r'georgia', r'tbilisi', r'\.ge\b', r'грузия', r'тбилиси'],
    'FI': [r'fi\b', r'finland', r'helsinki', r'\.fi\b', r'финляндия', r'хельсинки'],
    'IT': [r'it\b', r'italy', r'italian', r'rome', r'milan', r'\.it\b', r'италия', r'рим', r'милан'],
    'ES': [r'es\b', r'spain', r'madrid', r'barcelona', r'\.es\b', r'испания', r'мадрид'],
    'SE': [r'se\b', r'sweden', r'stockholm', r'\.se\b', r'швеция', r'стокгольм'],
    'CA': [r'ca\b', r'canada', r'toronto', r'vancouver', r'\.ca\b', r'канада', r'торонто'],
    'AU': [r'au\b', r'australia', r'sydney', r'melbourne', r'\.au\b', r'австралия', r'сидней'],
    'BR': [r'br\b', r'brazil', r'sao.paulo', r'\.br\b', r'бразилия'],
    'IN': [r'in\b', r'india', r'mumbai', r'delhi', r'\.in\b', r'индия', r'мумбаи'],
    'AE': [r'ae\b', r'uae', r'dubai', r'\.ae\b', r'оаэ', r'дубай'],
    'IL': [r'il\b', r'israel', r'tel.aviv', r'\.il\b', r'израиль', r'тель.авив'],
    'RO': [r'ro\b', r'romania', r'bucharest', r'\.ro\b', r'румыния', r'бухарест'],
    'MD': [r'md\b', r'moldova', r'chisinau', r'\.md\b', r'молдова', r'кишинев'],
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
    """Улучшенное определение страны — ТЕПЕРЬ ДЛЯ ВСЕХ"""
    # Объединяем всю доступную информацию
    text = f"{node_name} {node_url} {host}".lower()
    
    # 1. Ищем по паттернам
    for country, patterns in COUNTRY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.I):
                flag = COUNTRY_FLAGS.get(country)
                if flag:
                    return flag
    
    # 2. Ищем по домену верхнего уровня
    if host:
        domain_match = re.search(r'\.([a-z]{2})(?::|/|$|\s)', host.lower())
        if domain_match:
            tld = domain_match.group(1).upper()
            flag = COUNTRY_FLAGS.get(tld)
            if flag:
                return flag
    
    # 3. Проверяем IP на начало (для некоторых стран)
    if host:
        ip_patterns = {
            r'^185\.\d+\.\d+': 'NL',  # Нидерланды часто
            r'^31\.\d+\.\d+': 'NL',
            r'^5\.\d+\.\d+': 'RU',    # Россия
            r'^77\.\d+\.\d+': 'RU',
            r'^85\.\d+\.\d+': 'DE',   # Германия
            r'^95\.\d+\.\d+': 'RU',
        }
        for pattern, country in ip_patterns.items():
            if re.match(pattern, host):
                flag = COUNTRY_FLAGS.get(country)
                if flag:
                    return flag
    
    # 4. Если ничего не нашли — возвращаем глобус
    return '🌐'


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
        'frankfurt': 'Франкфурт', 'berlin': 'Берлин', 'munich': 'Мюнхен',
        'amsterdam': 'Амстердам', 'rotterdam': 'Роттердам',
        'london': 'Лондон', 'manchester': 'Манчестер',
        'paris': 'Париж', 'marseille': 'Марсель',
        'warsaw': 'Варшава', 'krakow': 'Краков',
        'istanbul': 'Стамбул', 'ankara': 'Анкара',
        'tokyo': 'Токио', 'osaka': 'Осака',
        'singapore': 'Сингапур',
        'new.york': 'Нью-Йорк', 'los.angeles': 'Лос-Анджелес', 'miami': 'Майами', 'dallas': 'Даллас',
        'finland': 'Финляндия', 'helsinki': 'Хельсинки',
        'italy': 'Италия', 'rome': 'Рим', 'milan': 'Милан',
        'netherlands': 'Нидерланды',
        'germany': 'Германия',
        'poland': 'Польша',
        'turkey': 'Турция',
        'ukraine': 'Украина', 'kiev': 'Киев', 'kyiv': 'Киев', 'kharkiv': 'Харьков',
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
    
    # 🔥 ВАЖНО: Всегда определяем флаг для ВСЕХ серверов!
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


def process_subscription(url: str, name_prefix: str) -> list:
    print(f"📥 {url[:60]}...")
    links = fetch_subscription(url)
    
    processed = []
    for link in links:
        parsed = parse_proxy_link(link)
        if parsed and parsed.get('name'):
            # 🔥 ВСЕГДА берем флаг!
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
    for sub in SUBSCRIPTIONS:
        nodes = process_subscription(sub['url'], sub['name_prefix'])
        all_nodes.extend(nodes)
    
    print("=" * 60)
    print(f"📊 ВСЕГО: {len(all_nodes)}")
    
    result = '\n'.join(all_nodes)
    
    header = f"#  VPN Subscription\n"
    header += f"# 🔄 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    header += f"# 📦 {len(all_nodes)} servers\n\n"
    
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
