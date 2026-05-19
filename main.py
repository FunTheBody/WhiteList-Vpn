#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 Proxy Subscription Merger
Объединяет подписки, переименовывает узлы, добавляет флаги стран
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
        "flag_priority": True  # Приоритет определения флага
    },
    {
        "url": "https://key.prosvet.best/sub",
        "name_prefix": "⚪ Обход белых списков",
        "flag_priority": False
    }
]

# 🌍 Словарь флагов по кодам стран
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

# 🔍 Паттерны для определения страны по имени узла
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
}


def decode_base64_safe(data: str) -> str:
    """Безопасное декодирование base64 с паддингом"""
    # Добавляем паддинг если нужно
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    try:
        decoded = base64.b64decode(data).decode('utf-8', errors='ignore')
        return decoded
    except:
        return data


def detect_country_flag(node_name: str, node_url: str = "") -> str:
    """Определяет флаг страны по имени узла или URL"""
    text = (node_name + " " + node_url).lower()
    
    # Поиск по паттернам
    for country, patterns in COUNTRY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.I):
                return COUNTRY_FLAGS.get(country, COUNTRY_FLAGS['UNKNOWN'])
    
    # Поиск по IP (если есть в URL)
    ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', node_url)
    if ip_match:
        # Здесь можно добавить API запрос к ipapi.co или подобному
        # Для простоты возвращаем неизвестный флаг
        pass
    
    return COUNTRY_FLAGS['UNKNOWN']


def parse_proxy_link(link: str) -> dict:
    """Парсит ссылку прокси и извлекает информацию"""
    link = link.strip()
    if not link:
        return None
    
    result = {
        'original': link,
        'type': None,
        'name': None,
        'country_flag': '🌐'
    }
    
    try:
        if link.startswith('vmess://'):
            result['type'] = 'vmess'
            # Декодируем vmess ссылку
            config_b64 = link[8:]
            config_json = decode_base64_safe(config_b64)
            import json
            config = json.loads(config_json)
            result['name'] = config.get('ps', 'Unnamed')
            result['host'] = config.get('add', '')
            
        elif link.startswith('vless://'):
            result['type'] = 'vless'
            # Парсим vless://uuid@host:port?params#name
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
            # ss://base64(method:pass@host:port)#name или ss://method:pass@host:port#name
            try:
                parsed = urlparse(link)
                result['name'] = unquote(parsed.fragment) or 'Unnamed'
                # Пробуем извлечь хост
                netloc = parsed.netloc
                if '@' in netloc:
                    host_part = netloc.split('@')[-1]
                else:
                    # Может быть закодировано
                    try:
                        decoded = decode_base64_safe(netloc.split('#')[0])
                        host_part = decoded.split('@')[-1] if '@' in decoded else netloc
                    except:
                        host_part = netloc
                result['host'] = host_part.split(':')[0] if ':' in host_part else host_part
            except:
                result['name'] = 'Shadowsocks Node'
                
        elif link.startswith('hysteria2://') or link.startswith('hysteria://'):
            result['type'] = 'hysteria'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Unnamed'
            result['host'] = parsed.netloc.split(':')[0]
            
        elif link.startswith('tuic://'):
            result['type'] = 'tuic'
            parsed = urlparse(link)
            result['name'] = unquote(parsed.fragment) or 'Unnamed'
            result['host'] = parsed.netloc.split('@')[-1].split(':')[0] if '@' in parsed.netloc else parsed.netloc.split(':')[0]
            
        else:
            # Возможно, это JSON конфиг или другая форма
            result['name'] = f"Unknown-{hash(link) % 10000}"
            
    except Exception as e:
        result['name'] = f"Error-{hash(link) % 10000}"
        result['error'] = str(e)
    
    # Определяем флаг
    result['country_flag'] = detect_country_flag(result['name'], result.get('host', ''))
    
    return result


def fetch_subscription(url: str) -> str:
    """Загружает подписку по URL"""
    headers = {
        'User-Agent': 'ClashMetaForAndroid/2.11.2 Meta'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        content = response.text.strip()
        
        # Проверяем, нужно ли декодировать base64
        if not content.startswith(('vmess://', 'vless://', 'trojan://', 'ss://', 'hysteria', 'tuic', '{')):
            # Пытаемся декодировать как base64
            try:
                content = decode_base64_safe(content)
            except:
                pass
        return content
    except requests.RequestException as e:
        print(f"❌ Ошибка загрузки {url}: {e}")
        return ""


def process_subscription(url: str, name_prefix: str, flag_priority: bool) -> list:
    """Обрабатывает одну подписку и возвращает список оформленных ссылок"""
    print(f"📥 Загрузка: {url[:50]}...")
    content = fetch_subscription(url)
    
    if not content:
        return []
    
    # Разбиваем на строки (каждая строка - ссылка)
    links = [line.strip() for line in content.split('\n') if line.strip()]
    
    processed = []
    for link in links:
        parsed = parse_proxy_link(link)
        if parsed and parsed.get('name'):
            # Формируем новое имя: [Флаг] Префикс | Оригинальное имя
            flag = parsed['country_flag'] if flag_priority else ''
            new_name = f"{flag} {name_prefix} | {parsed['name']}".strip()
            
            # Пересобираем ссылку с новым именем
            new_link = rename_proxy_link(link, new_name, parsed['type'])
            if new_link:
                processed.append(new_link)
    
    print(f"✅ Обработано: {len(processed)} узлов из {len(links)}")
    return processed


def rename_proxy_link(original_link: str, new_name: str, proxy_type: str) -> str:
    """Переименовывает узел в ссылке"""
    try:
        if proxy_type == 'vmess':
            config_b64 = original_link[8:]
            config_json = decode_base64_safe(config_b64)
            import json
            config = json.loads(config_json)
            config['ps'] = new_name  # ps = proxy name
            new_config_b64 = base64.b64encode(
                json.dumps(config, ensure_ascii=False).encode('utf-8')
            ).decode('utf-8').rstrip('=')
            return f"vmess://{new_config_b64}"
            
        elif proxy_type in ['vless', 'trojan', 'hysteria', 'tuic']:
            # Для этих типов имя в fragment (#name)
            parsed = urlparse(original_link)
            # Заменяем fragment
            from urllib.parse import urlunparse
            new_parsed = parsed._replace(fragment=new_name)
            return urlunparse(new_parsed)
            
        elif proxy_type == 'shadowsocks':
            # ss:// может иметь имя в fragment
            if '#' in original_link:
                base, _ = original_link.rsplit('#', 1)
                return f"{base}#{new_name}"
            return original_link
            
        else:
            # Для неизвестных типов возвращаем как есть
            return original_link
            
    except Exception as e:
        print(f"⚠️ Не удалось переименовать: {e}")
        return original_link


def merge_subscriptions() -> str:
    """Основная функция: объединяет все подписки"""
    print("🚀 Запуск объединения подписок...")
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    all_nodes = []
    
    for sub in SUBSCRIPTIONS:
        nodes = process_subscription(
            sub['url'], 
            sub['name_prefix'], 
            sub.get('flag_priority', True)
        )
        all_nodes.extend(nodes)
    
    print("-" * 50)
    print(f"📊 Всего узлов: {len(all_nodes)}")
    
    # Формируем итоговую подписку
    result = '\n'.join(all_nodes)
    
    # Добавляем заголовок с информацией
    header = f"# 🔗 Merged Subscription\n"
    header += f"# 🔄 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    header += f"# 📦 Nodes: {len(all_nodes)}\n"
    header += f"# ⚙️ Generated by ProxyMerger\n\n"
    
    return header + result


def save_to_file(content: str, filepath: str = "output/merged_sub.txt"):
    """Сохраняет результат в файл"""
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Сохранено: {filepath}")


def main():
    """Точка входа"""
    try:
        result = merge_subscriptions()
        save_to_file(result)
        
        # Также сохраняем в base64 для совместимости с некоторыми клиентами
        b64_result = base64.b64encode(result.encode('utf-8')).decode('utf-8')
        save_to_file(b64_result, "output/merged_sub_base64.txt")
        
        print("\n✨ Готово! Подписка обновлена.")
        return 0
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())