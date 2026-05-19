#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 Proxy Subscription Merger
Объединяет подписки, переименовывает узлы, добавляет флаги стран
ФИЛЬТРУЕТ метаданные подписок (#profile-*, #announce и т.д.)
"""

import base64
import re
import requests
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime

# 🔑 НАСТРОЙКИ
SUBSCRIPTIONS = [
    {
        "url": "https://izzzyvpn.2bd.net/sub.php?token=S6aEMcA0GXGt9qw7odYs",
        "name_prefix": "🔒 Обход черных списков",
        "flag_priority": True
    },
    {
        "url": "https://key.prosvet.best/sub",
        "name_prefix": "⚪ Обход белых списков",
        "flag_priority": False
    }
]

# 🌍 Словарь флагов
COUNTRY_FLAGS = {
    'RU': '🇷🇺', 'UA': '🇺🇦', 'BY': '🇧🇾', 'KZ': '🇰🇿', 'GE': '🇬🇪',
    'DE': '🇩🇪', 'US': '🇺🇸', 'GB': '🇬🇧', 'NL': '🇳🇱', 'FR': '🇫🇷',
    'PL': '🇵🇱', 'TR': '🇹🇷', 'CN': '🇨🇳', 'JP': '🇯🇵', 'SG': '🇸🇬',
    'KR': '🇰🇷', 'IN': '🇮🇳', 'BR': '🇧🇷', 'CA': '🇨🇦', 'AU': '🇦🇺',
    'IT': '🇮🇹', 'ES': '🇪🇸', 'SE': '🇸🇪', 'NO': '🇳🇴', 'FI': '🇫🇮',
    'CH': '🇨🇭', 'AT': '🇦🇹', 'BE': '🇧🇪', 'CZ': '🇨🇿', 'RO': '🇷🇴',
    'MD': '🇲🇩', 'LT': '🇱🇹', 'LV': '🇱🇻', 'EE': '🇪🇪', 'AZ': '🇦🇿',
    'AM': '🇦🇲', 'UZ': '🇺🇿', 'KG': '🇰🇬', 'TJ': '🇹🇯', 'MN': '🇲🇳',
    'VN': '🇻🇳', 'TH': '🇹🇭', 'MY': '🇲🇾', 'ID': '🇮🇩', 'PH': '🇵🇭',
    'HK': '🇭🇰', 'TW': '🇹🇼', 'MO': '🇲🇴', 'IL': '🇮🇱', 'AE': '🇦🇪',
    'SA': '🇸🇦', 'EG': '🇪🇬', 'ZA': '🇿🇦', 'NG': '🇳🇬', 'KE': '🇰🇪',
    'AR': '🇦🇷', 'CL': '🇨🇱', 'CO': '🇨🇴', 'MX': '🇲🇽', 'PE': '🇵🇪',
    'VE': '🇻🇪', 'GR': '🇬🇷', 'PT': '🇵🇹', 'IE': '🇮🇪', 'DK': '🇩🇰',
    'IS': '🇮🇸', 'LU': '🇱🇺', 'MT': '🇲🇹', 'CY': '🇨🇾', 'SK': '🇸🇰',
    'SI': '🇸🇮', 'HR': '🇭🇷', 'BG': '🇧🇬', 'RS': '🇷🇸', 'BA': '🇧🇦',
    'MK': '🇲🇰', 'AL': '🇦🇱', 'ME': '🇲🇪', 'XK': '🇽🇰', 'UNKNOWN': '🌐'
}

# 🔍 Паттерны стран
COUNTRY_PATTERNS = {
    'RU': [r'ru\b', r'moscow', r'moskva', r'spb', r'saint.petersburg', r'\.ru\b'],
    'UA': [r'ua\b', r'kiev', r'kyiv', r'kharkiv', r'odessa', r'\.ua\b'],
    'DE': [r'de\b', r'germany', r'frankfurt', r'berlin', r'munich', r'\.de\b'],
    'US': [r'us\b', r'usa', r'new.york', r'los.angeles', r'miami', r'\.us\b'],
    'GB': [r'gb\b', r'uk\b', r'london', r'manchester', r'\.uk\b', r'\.co.uk\b'],
    'NL': [r'nl\b', r'netherlands', r'amsterdam', r'rotterdam', r'\.nl\b'],
    'FR': [r'fr\b', r'france', r'paris', r'marseille', r'\.fr\b'],
    'PL': [r'pl\b', r'poland', r'warsaw', r'krakow', r'\.pl\b'],
    'TR': [r'tr\b', r'turkey', r'istanbul', r'ankara', r'\.tr\b'],
    'CN': [r'cn\b', r'china', r'beijing', r'shanghai', r'\.cn\b'],
    'JP': [r'jp\b', r'japan', r'tokyo', r'osaka', r'\.jp\b'],
    'SG': [r'sg\b', r'singapore', r'\.sg\b'],
    'KR': [r'kr\b', r'korea', r'seoul', r'\.kr\b'],
    'KZ': [r'kz\b', r'kazakhstan', r'almaty', r'astana', r'\.kz\b'],
    'BY': [r'by\b', r'belarus', r'minsk', r'\.by\b'],
    'GE': [r'ge\b', r'georgia', r'tbilisi', r'\.ge\b'],
    'FI': [r'fi\b', r'finland', r'helsinki', r'\.fi\b'],
    'IT': [r'it\b', r'italy', r'italian', r'rome', r'milan', r'\.it\b'],
}

# 🗑️ Паттерны метаданных, которые нужно ФИЛЬТРОВАТЬ
METADATA_PATTERNS = [
    r'^#profile-',
    r'^#announce:',
    r'^#subscription-userinfo:',
    r'^#support-url:',
    r'^#profile-web-page-url:',
    r'^#profile-update-interval:',
    r'^#⚙️',
    r'^# 🔄',
]


def decode_base64_safe(data: str) -> str:
    """Безопасное декодирование base64"""
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(data).decode('utf-8', errors='ignore')
    except:
        return data


def is_proxy_link(line: str) -> bool:
    """Проверяет, является ли строка прокси-ссылкой (а не метаданными)"""
    line = line.strip()
    if not line or line.startswith('#'):
        return False
    # Проверяем начало на известные протоколы
    proxy_prefixes = ('vmess://', 'vless://', 'trojan://', 'ss://', 'ssr://', 
                      'hysteria://', 'hysteria2://', 'tuic://', 'hy2://', 'wireguard://')
    return any(line.lower().startswith(prefix) for prefix in proxy_prefixes)


def is_metadata_line(line: str) -> bool:
    """Проверяет, является ли строка метаданными подписки"""
    line = line.strip()
    if not line.startswith('#'):
        return False
    for pattern in METADATA_PATTERNS:
        if re.match(pattern, line, re.I):
            return True
    return False


def detect_country_flag(node_name: str, node_url: str = "") -> str:
    """Определяет флаг страны"""
    text = (node_name + " " + node_url).lower()
    for country, patterns in COUNTRY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.I):
                return COUNTRY_FLAGS.get(country, COUNTRY_FLAGS['UNKNOWN'])
    return COUNTRY_FLAGS['UNKNOWN']


def parse_proxy_link(link: str) -> dict:
    """Парсит ссылку прокси"""
    link = link.strip()
    if not link or not is_proxy_link(link):
        return None
    
    result = {'original': link, 'type': None, 'name': None, 'country_flag': '🌐', 'host': ''}
    
    try:
        if link.startswith('vmess://'):
            result['type'] = 'vmess'
            config_json = decode_base64_safe(link[8:])
            import json
            config = json.loads(config_json)
            result['name'] = config.get('ps', 'Unnamed')
            result['host'] = config.get('add', '')
            
        elif link.startswith('vless://'):
            result['type'] = 'vless'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Unnamed'
            result['host'] = parsed.netloc.split('@')[-1].split(':')[0] if '@' in parsed.netloc else parsed.netloc.split(':')[0]
            
        elif link.startswith('trojan://'):
            result['type'] = 'trojan'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Unnamed'
            result['host'] = parsed.netloc.split('@')[-1].split(':')[0] if '@' in parsed.netloc else parsed.netloc.split(':')[0]
            
        elif link.startswith('ss://'):
            result['type'] = 'shadowsocks'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Shadowsocks'
            result['host'] = parsed.netloc.split('@')[-1].split(':')[0] if '@' in parsed.netloc else parsed.netloc.split(':')[0]
            
        elif link.startswith(('hysteria2://', 'hysteria://', 'hy2://')):
            result['type'] = 'hysteria'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Hysteria'
            result['host'] = parsed.netloc.split(':')[0]
            
        elif link.startswith('tuic://'):
            result['type'] = 'tuic'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Tuic'
            result['host'] = parsed.netloc.split('@')[-1].split(':')[0] if '@' in parsed.netloc else parsed.netloc.split(':')[0]
        else:
            result['name'] = f"Proxy-{hash(link) % 10000}"
            
    except Exception as e:
        result['name'] = f"Error-{hash(link) % 10000}"
    
    result['country_flag'] = detect_country_flag(result['name'], result.get('host', ''))
    return result


def fetch_subscription(url: str) -> list:
    """Загружает подписку и возвращает ТОЛЬКО прокси-ссылки"""
    headers = {'User-Agent': 'ClashMetaForAndroid/2.11.2 Meta'}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        content = response.text.strip()
        
        # Декодируем если нужно
        if not any(content.startswith(p) for p in ('vmess://', 'vless://', 'trojan://', 'ss://', '{')):
            try:
                content = decode_base64_safe(content)
            except:
                pass
        
        # Разбиваем на строки и ФИЛЬТРУЕМ
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        proxy_links = [line for line in lines if is_proxy_link(line) and not is_metadata_line(line)]
        
        return proxy_links
    except Exception as e:
        print(f"❌ Ошибка загрузки {url}: {e}")
        return []


def rename_proxy_link(original_link: str, new_name: str, proxy_type: str) -> str:
    """Переименовывает узел"""
    try:
        if proxy_type == 'vmess':
            import json
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
            return original_link
        return original_link
    except:
        return original_link


def process_subscription(url: str, name_prefix: str, flag_priority: bool) -> list:
    """Обрабатывает подписку"""
    print(f"📥 Загрузка: {url[:50]}...")
    links = fetch_subscription(url)
    
    processed = []
    for link in links:
        parsed = parse_proxy_link(link)
        if parsed and parsed.get('name'):
            flag = parsed['country_flag'] if flag_priority else ''
            new_name = f"{flag} {name_prefix} | {parsed['name']}".strip()
            new_link = rename_proxy_link(link, new_name, parsed['type'])
            if new_link:
                processed.append(new_link)
    
    print(f"✅ Обработано: {len(processed)} узлов")
    return processed


def merge_subscriptions() -> str:
    """Основная функция"""
    print("🚀 Запуск...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    all_nodes = []
    for sub in SUBSCRIPTIONS:
        nodes = process_subscription(sub['url'], sub['name_prefix'], sub.get('flag_priority', True))
        all_nodes.extend(nodes)
    
    print("-" * 50)
    print(f"📊 Всего: {len(all_nodes)} узлов")
    
    result = '\n'.join(all_nodes)
    
    # ✅ ТОЛЬКО наши заголовки, без мусора из подписок
    header = f"# 🔗 Merged by ProxyMerger\n"
    header += f"# 🔄 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    header += f"# 📦 {len(all_nodes)} nodes\n\n"
    
    return header + result


def save_to_file(content: str, filepath: str = "output/merged_sub.txt"):
    """Сохраняет файл"""
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Сохранено: {filepath}")


def main():
    try:
        result = merge_subscriptions()
        save_to_file(result)
        # Base64 версия
        b64 = base64.b64encode(result.encode('utf-8')).decode()
        save_to_file(b64, "output/merged_sub_base64.txt")
        print("\n✨ Готово!")
        return 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
