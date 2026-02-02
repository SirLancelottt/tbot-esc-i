import os
import sys
import telegram
import asyncio
import schedule
import time
import logging
from datetime import datetime
import pytz

# ==================== KONFİGÜRASYON ====================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")

# ==================== LOG AYARI ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==================== HATA KONTROLÜ ====================
if not TOKEN:
    logger.error("❌ HATA: TELEGRAM_TOKEN environment variable ayarlanmamış!")
    logger.error("Render Dashboard → Environment Variables ekleyin")
    sys.exit(1)

if not CHANNEL:
    logger.error("❌ HATA: TELEGRAM_CHANNEL environment variable ayarlanmamış!")
    logger.error("Render Dashboard → Environment Variables ekleyin")
    sys.exit(1)

# ==================== BOT SINIFI ====================
class TelegramSchedulerBot:
    def __init__(self):
        self.bot = telegram.Bot(token=TOKEN)
        self.channel = CHANNEL
        self.tr_timezone = pytz.timezone('Europe/Istanbul')
        
        logger.info("=" * 50)
        logger.info("🤖 TELEGRAM ZAMANLAYICI BOT")
        logger.info(f"📍 Kanal: {self.channel}")
        logger.info(f"⏰ Türkiye Saati: {self.get_tr_time()}")
        logger.info("=" * 50)
    
    def get_tr_time(self):
        """Şu anki Türkiye saatini al"""
        return datetime.now(self.tr_timezone).strftime('%d.%m.%Y %H:%M:%S')
    
    def tr_to_utc(self, tr_time_str):
        """
        Türkiye saatini UTC'ye çevir
        Örnek: "09:00" -> "06:00" (yaz saati)
        """
        try:
            # Saat ve dakikayı ayır
            hour, minute = map(int, tr_time_str.split(':'))
            
            # Bugünün tarihini al
            tr_now = datetime.now(self.tr_timezone)
            
            # Türkiye saatinde datetime oluştur
            tr_datetime = self.tr_timezone.localize(
                datetime(tr_now.year, tr_now.month, tr_now.day, hour, minute, 0)
            )
            
            # UTC'ye çevir
            utc_datetime = tr_datetime.astimezone(pytz.utc)
            
            # Saat:dakika formatına çevir
            utc_time_str = utc_datetime.strftime('%H:%M')
            
            logger.info(f"⏱️  Zaman çevrildi: {tr_time_str} TR -> {utc_time_str} UTC")
            return utc_time_str
            
        except Exception as e:
            logger.error(f"⏱️  Zaman çevirme hatası: {e}")
            return "09:00"  # Varsayılan değer
    
    async def send_to_channel(self, message="📢 Varsayılan mesaj"):
        """Kanal'a mesaj gönder"""
        try:
            # Mesajı hazırla
            full_message = (
                f"{message}\n"
                f"🕐 {self.get_tr_time()}"
            )
            
            # Gönder
            await self.bot.send_message(
                chat_id=self.channel,
                text=full_message,
                parse_mode="HTML"
            )
            
            logger.info(f"✅ Mesaj gönderildi: {message[:30]}...")
            return True
            
        except telegram.error.Unauthorized:
            logger.error("❌ Bot yetkisiz! Token'ı kontrol edin.")
            return False
        except telegram.error.BadRequest as e:
            logger.error(f"❌ Geçersiz kanal ID: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Gönderme hatası: {e}")
            return False
    
    def setup_schedule(self):
        """Zamanlanmış mesajlarınızı burada ayarlayın"""
        
        # ⭐ BURAYI KENDİNİZE GÖRE DÜZENLEYİN ⭐
        # Format: {"zaman": "mesaj"}
        # Zamanlar Türkiye saati ile yazılacak
        my_schedules = {
            "09:00":"⏰ <b>GÜNAYDIN!</b>\n\nBugün harika bir gün olacak! ☀️",
            "12:00":"☀️ <b>ÖĞLE VAKTİ</b>\n\nAra verip kendinize iyi bakın! 🍽️",
            "14:15":"Gerçek Bayanlar Nerde?",
            "14:30":"Kedicik Kimdir?",
            "14:45":"Simge Kimdir?",
            "15:00":"Çağla Kimdir?",
            "15:15":"Gerçek Bayanlar Nerde?",
            "15:30":"Kedicik Kimdir?",
            "15:45":"Simge Kimdir?",
            "16:00":"Çağla Kimdir?",
            "16:15":"Gerçek Bayanlar Nerde?",
            "16:30":"Kedicik Kimdir?",
            "16:45":"Simge Kimdir?",
            "17:00":"Çağla Kimdir?",
            "17:15":"Gerçek Bayanlar Nerde?",
            "17:30":"Kedicik Kimdir?",
            "17:45":"Simge Kimdir?",
            "18:00":"Çağla Kimdir?",
            "18:15":"Gerçek Bayanlar Nerde?",
            "18:30":"Kedicik Kimdir?",
            "18:45":"Simge Kimdir?",
            "19:00":"Çağla Kimdir?",
            "19:15":"Gerçek Bayanlar Nerde?",
            "19:30":"Kedicik Kimdir?",
            "19:45":"Simge Kimdir?",
            "20:00":"Çağla Kimdir?",
            "20:00":"🌆 <b>AKŞAM VAKTİ</b>\n\nGünün yorgunluğunu atma zamanı! 🏡",
            "24:00":"🌙 <b>İYİ GECELER</b>\n\nYarın daha güzel bir gün olacak! ✨",
        }
        
        logger.info("📅 Zamanlamalar ayarlanıyor...")
        
        for tr_time, message in my_schedules.items():
            # Türkiye saatini UTC'ye çevir
            utc_time = self.tr_to_utc(tr_time)
            
            # Schedule'a ekle
            schedule.every().day.at(utc_time).do(
                lambda msg=message: asyncio.run(self.send_to_channel(msg))
            )
            
            logger.info(f"   ⏰ {tr_time} TR -> {utc_time} UTC: {message[:20]}...")
        
        # 🧪 TEST İÇİN (HER 5 DAKİKADA BİR)
        # Yorum satırını kaldırıp botun çalıştığını test edebilirsiniz
        # schedule.every(5).minutes.do(
        #     lambda: asyncio.run(self.send_to_channel("🧪 <b>TEST</b>\nBot çalışıyor!"))
        # )
        
        logger.info(f"✅ Toplam {len(my_schedules)} zamanlama ayarlandı")
    
    async def startup_check(self):
        """Bot başlangıç kontrolü"""
        try:
            # Bot bilgilerini al
            bot_info = await self.bot.get_me()
            logger.info(f"🤖 Bot: @{bot_info.username} ({bot_info.first_name})")
            
            # Kanal bilgilerini al
            chat_info = await self.bot.get_chat(self.channel)
            logger.info(f"📢 Kanal: {chat_info.title}")
            
            # Başlangıç mesajı gönder
            startup_msg = (
                "🚀 <b>BOT AKTİF!</b>\n\n"
                f"🤖 Bot: @{bot_info.username}\n"
                f"📅 Tarih: {self.get_tr_time()}\n"
                f"📍 Host: Render.com\n\n"
                "✅ Zamanlanmış mesajlar hazır!"
            )
            
            await self.send_to_channel(startup_msg)
            logger.info("✅ Başlangıç kontrolü tamamlandı")
            
        except Exception as e:
            logger.error(f"❌ Başlangıç hatası: {e}")
            return False
    
    def run(self):
        """Ana çalıştırıcı"""
        try:
            # Asenkron startup işlemi
            asyncio.run(self.startup_check())
            
            # Zamanlamaları ayarla
            self.setup_schedule()
            
            logger.info("🔄 Zamanlayıcı başlatıldı, mesajlar bekleniyor...")
            
            # Ana döngü
            while True:
                schedule.run_pending()
                time.sleep(1)  # 1 saniye bekle
                
        except KeyboardInterrupt:
            logger.info("⏹️  Bot durduruldu")
        except Exception as e:
            logger.error(f"💥 Kritik hata: {e}")

# ==================== PROGRAM BAŞLANGICI ====================
if __name__ == "__main__":
    logger.info("▶️  Bot başlatılıyor...")
    
    # Bot nesnesi oluştur ve çalıştır
    bot = TelegramSchedulerBot()
    bot.run()