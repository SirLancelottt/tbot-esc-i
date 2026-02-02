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
# Replit'te Secrets kullanacağız
TOKEN = os.getenv("TELEGRAM_TOKEN", "TEMP_TOKEN")
CHANNEL = os.getenv("TELEGRAM_CHANNEL", "@temp_channel")

# ==================== LOG AYARI ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==================== BOT SINIFI ====================
class TelegramSchedulerBot:
    def __init__(self):
        if TOKEN == "TEMP_TOKEN":
            logger.warning("⚠️  TEMP_TOKEN kullanılıyor! Gerçek token ekleyin.")
        
        self.bot = telegram.Bot(token=TOKEN)
        self.channel = CHANNEL
        self.tr_timezone = pytz.timezone('Europe/Istanbul')
        
        logger.info("=" * 50)
        logger.info("🤖 TELEGRAM ZAMANLAYICI BOT (Replit)")
        logger.info(f"📍 Kanal: {self.channel}")
        logger.info("=" * 50)
    
    def get_tr_time(self):
        """Şu anki Türkiye saatini al"""
        return datetime.now(self.tr_timezone).strftime('%d.%m.%Y %H:%M:%S')
    
    async def send_to_channel(self, message="📢 Varsayılan mesaj"):
        """Kanal'a mesaj gönder"""
        try:
            full_message = f"{message}\n🕐 {self.get_tr_time()}"
            
            await self.bot.send_message(
                chat_id=self.channel,
                text=full_message,
                parse_mode="HTML"
            )
            
            logger.info(f"✅ Mesaj gönderildi: {message[:30]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Hata: {e}")
            return False
    
    def setup_schedule(self):
        """Zamanlanmış mesajlar"""
        
        # TEST: Her 10 dakikada bir
        schedule.every(10).minutes.do(
            lambda: asyncio.run(self.send_to_channel("🧪 <b>TEST</b>\nReplit'ten mesaj!"))
        )
        
        # Gerçek zamanlamalar (yorum satırı)
        # schedule.every().day.at("09:00").do(
        #     lambda: asyncio.run(self.send_to_channel("🌅 <b>GÜNAYDIN!</b>"))
        # )
        
        logger.info("📅 Zamanlamalar ayarlandı (10 dakikada bir test)")
    
    async def startup_check(self):
        """Bot başlangıç kontrolü"""
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"🤖 Bot: @{bot_info.username}")
            
            startup_msg = (
                "🚀 <b>BOT REPLIT'TE AKTİF!</b>\n\n"
                f"🤖 Bot: @{bot_info.username}\n"
                f"📅 Tarih: {self.get_tr_time()}\n"
                f"📍 Host: Replit.com\n\n"
                "✅ Test mesajları başladı!"
            )
            
            await self.send_to_channel(startup_msg)
            logger.info("✅ Başlangıç kontrolü tamamlandı")
            
        except Exception as e:
            logger.error(f"❌ Başlangıç hatası: {e}")
    
    def run(self):
        """Ana çalıştırıcı"""
        try:
            # Asenkron startup
            asyncio.run(self.startup_check())
            
            # Zamanlamaları ayarla
            self.setup_schedule()
            
            logger.info("🔄 Zamanlayıcı başlatıldı...")
            
            # Ana döngü
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Bot durduruldu")
        except Exception as e:
            logger.error(f"💥 Kritik hata: {e}")

# ==================== PROGRAM BAŞLANGICI ====================
if __name__ == "__main__":
    logger.info("▶️  Replit Bot başlatılıyor...")
    
    # Bot nesnesi oluştur ve çalıştır
    bot = TelegramSchedulerBot()
    bot.run()