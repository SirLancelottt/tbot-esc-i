#!/usr/bin/env python3
"""
ZAMANLANMIŞ MESAJ BOT - RESİM + VİDEO + DOSYA DESTEKLİ
GitHub JSON + PixelDrain + Random Seçim
"""

import os
import sys
import time
import json
import random
import schedule
import logging
import asyncio
import pytz
import requests
from datetime import datetime, timedelta
from telegram import Bot

# ==================== AYARLAR ====================
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL = os.getenv('TELEGRAM_CHANNEL', '@bursadeneyimlerimiz')

# GitHub JSON URL'leri
SCHEDULE_JSON_URL = "https://raw.githubusercontent.com/SirLancelottt/tbot-esc-i/main/timer.json"
MESSAGES_JSON_URL = "https://raw.githubusercontent.com/SirLancelottt/tbot-esc-i/main/message.json"

SCHEDULE_LOCAL = "timer.json"
MESSAGES_LOCAL = "message.json"

# Telegram dosya limitleri (byte)
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILE_SIZE = 50 * 1024 * 1024   # 50MB

# ==================== LOG ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger()

# ==================== JSON İNDİRME ====================
def download_json(url, local_file):
    """GitHub'dan JSON indir"""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            with open(local_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return data
        else:
            log.error(f"❌ İndirme hatası ({url}): {response.status_code}")
            return None
    except Exception as e:
        log.error(f"❌ JSON indirme hatası: {e}")
        return None

def load_all_jsons():
    """Tüm JSON'ları yükle"""
    # Schedule JSON
    schedule_data = download_json(SCHEDULE_JSON_URL, SCHEDULE_LOCAL)
    if not schedule_data and os.path.exists(SCHEDULE_LOCAL):
        with open(SCHEDULE_LOCAL, 'r', encoding='utf-8') as f:
            schedule_data = json.load(f)
    
    # Messages JSON
    messages_data = download_json(MESSAGES_JSON_URL, MESSAGES_LOCAL)
    if not messages_data and os.path.exists(MESSAGES_LOCAL):
        with open(MESSAGES_LOCAL, 'r', encoding='utf-8') as f:
            messages_data = json.load(f)
    
    return schedule_data, messages_data

# ==================== PIXELDRAIN FONKSİYONLARI ====================
def get_random_file_from_pixeldrain(folder_id, file_extensions=None):
    """PixelDrain klasöründen rastgele dosya URL'si al"""
    try:
        url = f"https://pixeldrain.com/api/folder/{folder_id}?files=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            files = response.json().get("files", [])
            
            # File extension filtresi (opsiyonel)
            if file_extensions:
                filtered_files = []
                for f in files:
                    fname = f['name'].lower()
                    if any(fname.endswith(ext) for ext in file_extensions):
                        filtered_files.append(f)
                files = filtered_files
            
            if files:
                random_file = random.choice(files)
                file_id = random_file['id']
                return f"https://pixeldrain.com/api/file/{file_id}?download"
    except Exception as e:
        log.error(f"PixelDrain hatası: {e}")
    
    return None

def check_file_size(url):
    """Dosya boyutunu kontrol et"""
    try:
        head = requests.head(url, timeout=5, allow_redirects=True)
        size = int(head.headers.get('content-length', 0))
        return size
    except:
        return 0

# ==================== MESAJ GÖNDERME ====================
async def send_scheduled_message(schedule_item, messages_dict):
    """Zamanlanmış mesajı gönder (resim/video/text)"""
    try:
        # Disabled kontrolü
        if schedule_item.get('disabled', False):
            log.info(f"⏭️ Atlanan zamanlama: {schedule_item.get('time')}")
            return False
        
        username = schedule_item.get('username', '')
        
        if not username:
            log.error("❌ Username belirtilmemiş!")
            return False
        
        if username not in messages_dict:
            log.error(f"❌ Username için mesaj bulunamadı: {username}")
            return False
        
        # Bu username'e ait mesaj havuzundan RANDOM seç
        message_pool = messages_dict[username]
        if not message_pool:
            log.error(f"❌ {username} için mesaj havuzu boş!")
            return False
        
        message_data = random.choice(message_pool)
        bot = Bot(token=TOKEN)
        message_text = message_data.get('text', '')
        
        # Username'i mesajın SONUNA ekle (zero-width space ile)
        zero_width = "\u200b"
        final_message = f"{message_text}{zero_width}{username}"
        
        msg_type = message_data.get('type', 'text_only')
        
        # 1. RESİMLİ MESAJ
        if msg_type == 'with_image':
            image_url = message_data.get('image_url')
            image_folder = message_data.get('image_folder')
            
            final_image_url = None
            if image_url:
                final_image_url = image_url
            elif image_folder:
                final_image_url = get_random_file_from_pixeldrain(
                    image_folder, 
                    ('.jpg', '.jpeg', '.png', '.gif', '.webp')
                )
            
            if final_image_url:
                # Dosya boyutu kontrolü
                file_size = check_file_size(final_image_url)
                if file_size > MAX_IMAGE_SIZE:
                    log.warning(f"⚠️ Resim çok büyük ({file_size/1024/1024:.1f}MB), metin olarak gönderiliyor")
                    await bot.send_message(
                        chat_id=CHANNEL,
                        text=final_message,
                        parse_mode='HTML'
                    )
                else:
                    await bot.send_photo(
                        chat_id=CHANNEL,
                        photo=final_image_url,
                        caption=final_message,
                        parse_mode='HTML'
                    )
                log.info(f"✅ [📷 RESİM] {username} → {message_text[:30]}...")
            else:
                await bot.send_message(
                    chat_id=CHANNEL,
                    text=final_message,
                    parse_mode='HTML'
                )
                log.warning(f"⚠️ Resim yok, metin olarak: {username}")
        
        # 2. VİDEOLU MESAJ
        elif msg_type == 'with_video':
            video_url = message_data.get('video_url')
            video_folder = message_data.get('video_folder')
            
            final_video_url = None
            if video_url:
                final_video_url = video_url
            elif video_folder:
                final_video_url = get_random_file_from_pixeldrain(
                    video_folder, 
                    ('.mp4', '.mov', '.avi', '.mkv', '.webm')
                )
            
            if final_video_url:
                # Video boyutu kontrolü
                file_size = check_file_size(final_video_url)
                if file_size > MAX_VIDEO_SIZE:
                    log.warning(f"⚠️ Video çok büyük ({file_size/1024/1024:.1f}MB), link olarak gönderiliyor")
                    await bot.send_message(
                        chat_id=CHANNEL,
                        text=f"{final_message}\n\n📹 Video: {final_video_url}",
                        parse_mode='HTML'
                    )
                else:
                    await bot.send_video(
                        chat_id=CHANNEL,
                        video=final_video_url,
                        caption=final_message,
                        parse_mode='HTML',
                        supports_streaming=True
                    )
                log.info(f"✅ [🎬 VİDEO] {username} → {message_text[:30]}...")
            else:
                await bot.send_message(
                    chat_id=CHANNEL,
                    text=final_message,
                    parse_mode='HTML'
                )
                log.warning(f"⚠️ Video yok, metin olarak: {username}")
        
        # 3. DOSYALI MESAJ (genel)
        elif msg_type == 'with_file':
            file_url = message_data.get('file_url')
            file_folder = message_data.get('file_folder')
            
            final_file_url = None
            if file_url:
                final_file_url = file_url
            elif file_folder:
                final_file_url = get_random_file_from_pixeldrain(file_folder)
            
            if final_file_url:
                # Dosya boyutu kontrolü
                file_size = check_file_size(final_file_url)
                if file_size > MAX_FILE_SIZE:
                    log.warning(f"⚠️ Dosya çok büyük ({file_size/1024/1024:.1f}MB), link olarak gönderiliyor")
                    await bot.send_message(
                        chat_id=CHANNEL,
                        text=f"{final_message}\n\n📎 Dosya: {final_file_url}",
                        parse_mode='HTML'
                    )
                else:
                    await bot.send_document(
                        chat_id=CHANNEL,
                        document=final_file_url,
                        caption=final_message,
                        parse_mode='HTML'
                    )
                log.info(f"✅ [📎 DOSYA] {username} → {message_text[:30]}...")
            else:
                await bot.send_message(
                    chat_id=CHANNEL,
                    text=final_message,
                    parse_mode='HTML'
                )
        
        # 4. SADECE METİN
        else:  # text_only veya diğer
            await bot.send_message(
                chat_id=CHANNEL,
                text=final_message,
                parse_mode='HTML'
            )
            log.info(f"✅ [📝 METİN] {username} → {message_text[:30]}...")
            
        return True
    except Exception as e:
        log.error(f"❌ Mesaj gönderme hatası: {e}")
        return False

def create_message_sender(schedule_item, messages_dict):
    """Mesaj gönderici fonksiyon oluştur"""
    def sender():
        asyncio.run(send_scheduled_message(schedule_item, messages_dict))
    return sender

# ==================== ZAMANLAMA AYARI ====================
def setup_schedule():
    """JSON'lardan zamanlamaları ayarla"""
    schedule_data, messages_data = load_all_jsons()
    
    if not schedule_data or not messages_data:
        log.error("❌ JSON'lar yüklenemedi!")
        return schedule, {}, {}
    
    schedule_list = schedule_data.get('schedule', [])
    messages_dict = messages_data.get('messages', {})
    
    # Meta bilgileri
    schedule_meta = schedule_data.get('meta', {})
    messages_meta = messages_data.get('meta', {})
    
    # İstatistikler
    username_count = {}
    for item in schedule_list:
        if not item.get('disabled', False):
            username = item.get('username', '')
            if username:
                username_count[username] = username_count.get(username, 0) + 1
    
    log.info("📊 JSON'lar yüklendi:")
    log.info(f"   ⏰ Zamanlama: {len(schedule_list)} kayıt")
    log.info(f"   💬 Mesaj Havuzları: {len(messages_dict)} username")
    
    for username, count in username_count.items():
        pool_size = len(messages_dict.get(username, []))
        log.info(f"   👤 {username}: {count} zamanlama, {pool_size} mesaj")
    
    log.info(f"   📅 Schedule Güncelleme: {schedule_meta.get('last_updated', 'Bilinmiyor')}")
    log.info(f"   📅 Messages Güncelleme: {messages_meta.get('last_updated', 'Bilinmiyor')}")
    
    if not schedule_list:
        log.warning("⚠️ Zamanlanacak mesaj bulunamadı!")
        return schedule, schedule_meta, messages_meta
    
    log.info("⏰ Zamanlamalar ayarlanıyor (RANDOM mesaj seçimi)...")
    
    scheduled_count = 0
    skipped_disabled = 0
    
    for i, item in enumerate(schedule_list):
        # Disabled kontrolü
        if item.get('disabled', False):
            skipped_disabled += 1
            continue
        
        tr_time = item.get('time')
        username = item.get('username', '')
        
        if not tr_time:
            log.error(f"   ✗ {i}. kayıtta 'time' yok!")
            continue
        
        if not username:
            log.error(f"   ✗ {i}. kayıtta 'username' yok!")
            continue
        
        if username not in messages_dict:
            log.error(f"   ✗ Mesaj havuzu bulunamadı: {username}")
            continue
        
        # Zaman formatını düzelt
        fixed_time = tr_time
        if tr_time == '24:00':
            fixed_time = '23:59'
            log.warning(f"   {tr_time} → {fixed_time} (düzeltildi)")
        
        # TR → UTC çevrimi
        try:
            tr_tz = pytz.timezone('Europe/Istanbul')
            hour, minute = map(int, fixed_time.split(':'))
            today = datetime.now().date()
            
            tr_datetime = tr_tz.localize(
                datetime(today.year, today.month, today.day, hour, minute, 0)
            )
            utc_datetime = tr_datetime.astimezone(pytz.UTC)
            utc_time = utc_datetime.strftime('%H:%M')
            
        except Exception as e:
            log.error(f"   Zaman çevirme hatası: {e}")
            continue
        
        # Zamanlayıcıyı ayarla
        try:
            sender_func = create_message_sender(item, messages_dict)
            schedule.every().day.at(utc_time).do(sender_func)
            
            # Mesaj havuzu bilgisi
            pool_size = len(messages_dict[username])
            msg_types = set(m.get('type', 'text_only') for m in messages_dict[username])
            type_icons = {
                'with_image': '📷',
                'with_video': '🎬',
                'with_file': '📎',
                'text_only': '📝'
            }
            icons = ''.join(type_icons.get(t, '❓') for t in msg_types)
            
            log.info(f"   ✓ {fixed_time} TRT → {utc_time} UTC {icons}")
            log.info(f"      👤 {username} ({pool_size} mesaj)")
            scheduled_count += 1
            
        except Exception as e:
            log.error(f"   ✗ Zamanlama hatası ({fixed_time}): {e}")
    
    log.info(f"✅ {scheduled_count} zamanlama ayarlandı, {skipped_disabled} devre dışı atlandı")
    log.info("🎲 Her zamanlama için ilgili username'in mesaj havuzundan RANDOM seçim yapılacak")
    return schedule, schedule_meta, messages_meta

# ==================== BAŞLANGIÇ TESTİ ====================
async def startup_test(schedule_meta, messages_meta, messages_dict):
    """Başlangıç testi ve sistem bilgisi gönderimi"""
    try:
        bot = Bot(token=TOKEN)
        
        me = await bot.get_me()
        log.info(f"🤖 Bot: @{me.username}")
        
        chat = await bot.get_chat(CHANNEL)
        log.info(f"📢 Kanal: {chat.title}")
        
        # Sistem bilgilerini hazırla
        system_info = f"\n📊 <b>Sistem Bilgileri:</b>\n"
        
        # Username havuzları
        total_messages = sum(len(pool) for pool in messages_dict.values())
        system_info += f"• Toplam Mesaj Havuzu: {total_messages}\n"
        system_info += f"• Username Sayısı: {len(messages_dict)}\n"
        
        for username, pool in messages_dict.items():
            # Mesaj tiplerini say
            types = {}
            for msg in pool:
                t = msg.get('type', 'text_only')
                types[t] = types.get(t, 0) + 1
            
            type_str = ', '.join([f"{count}{'📷' if t=='with_image' else '🎬' if t=='with_video' else '📎' if t=='with_file' else '📝'}" 
                                 for t, count in types.items()])
            system_info += f"  👤 {username}: {len(pool)} mesaj ({type_str})\n"
        
        # JSON güncellemeleri
        system_info += f"\n📅 <b>Son Güncellemeler:</b>\n"
        system_info += f"• Schedule: {schedule_meta.get('last_updated', 'Bilinmiyor')}\n"
        system_info += f"• Messages: {messages_meta.get('last_updated', 'Bilinmiyor')}\n"
        
        # Test mesajı gönder
        await bot.send_message(
            chat_id=CHANNEL,
            text='🚀 <b>BOT BAŞLATILDI - MULTİMEDYA SİSTEMİ</b>\n\n' +
                 f'🤖 Bot: @{me.username}\n' +
                 f'📢 Kanal: {chat.title}\n' +
                 f'🕐 Başlangıç: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n' +
                 system_info +
                 '\n✅ Resim 📷 + Video 🎬 + Dosya 📎 + Metin 📝 destekli!',
            parse_mode='HTML'
        )
        log.info("✅ Test mesajı gönderildi")
        return True
        
    except Exception as e:
        log.error(f"❌ Başlangıç hatası: {e}")
        return False

# ==================== ANA PROGRAM ====================
def main():
    """Ana program"""
    log.info("=" * 50)
    log.info("🤖 ZAMANLANMIŞ MESAJ BOT - MULTİMEDYA SİSTEMİ")
    log.info("=" * 50)
    
    if not TOKEN:
        log.error("❌ TELEGRAM_TOKEN bulunamadı!")
        return
    
    # JSON'ları yükle ve zamanlamaları ayarla
    scheduler, schedule_meta, messages_meta = setup_schedule()
    
    # Messages dict'i al (geriye uyumluluk için)
    messages_dict = {}
    if isinstance(messages_meta, dict) and 'messages' in messages_meta:
        messages_dict = messages_meta.get('messages', {})
    else:
        # Eski yapı: messages_meta aslında messages_data
        _, messages_data = load_all_jsons()
        messages_dict = messages_data.get('messages', {}) if messages_data else {}
    
    log.info(f"🔑 Token: ...{TOKEN[-8:]}")
    log.info(f"📢 Kanal: {CHANNEL}")
    log.info(f"🌐 JSON Kaynakları: GitHub")
    
    # Başlangıç testi
    asyncio.run(startup_test(schedule_meta, messages_meta, messages_dict))
    
    log.info("✅ Bot çalışmaya başladı!")
    log.info("=" * 50)
    log.info("🎲 Her zamanlama için ilgili username'in mesaj havuzundan RANDOM seçim")
    log.info("📊 Desteklenen tipler: 📷 Resim | 🎬 Video | 📎 Dosya | 📝 Metin")
    
    # Son kontrol zamanları
    last_schedule_check = time.time()
    last_messages_check = time.time()
    
    # Ana döngü
    try:
        while True:
            # Zamanlanmış mesajları kontrol et
            scheduler.run_pending()
            
            # GitHub'dan periyodik kontrol
            current_time = time.time()
            
            # Schedule.json kontrolü (her 5 dakikada)
            if current_time - last_schedule_check > 300:
                log.debug("🔄 Schedule.json kontrol ediliyor...")
                new_data = download_json(SCHEDULE_JSON_URL, SCHEDULE_LOCAL)
                if new_data:
                    scheduler, schedule_meta, messages_meta = setup_schedule()
                    log.info("✅ Schedule.json güncellendi")
                last_schedule_check = current_time
            
            # Messages.json kontrolü (her 10 dakikada)
            if current_time - last_messages_check > 600:
                log.debug("🔄 Messages.json kontrol ediliyor...")
                new_data = download_json(MESSAGES_JSON_URL, MESSAGES_LOCAL)
                if new_data:
                    scheduler, schedule_meta, messages_meta = setup_schedule()
                    log.info("✅ Messages.json güncellendi")
                last_messages_check = current_time
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        log.info("👋 Bot durduruluyor...")
    except Exception as e:
        log.error(f"💥 Beklenmeyen hata: {e}")

if __name__ == '__main__':
    main()