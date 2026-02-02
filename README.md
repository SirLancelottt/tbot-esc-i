# Telegram Zamanlayıcı Bot

Bu bot, Telegram kanallarına zamanlanmış mesajlar gönderir.

## Özellikler
- 🕒 Zamanlanmış mesaj gönderimi
- 🌍 Türkiye saati desteği
- 📊 Detaylı loglama
- 🔧 Kolay yapılandırma

## Kurulum
1. Render.com'da "Background Worker" oluştur
2. Environment Variables ekle:
   - `TELEGRAM_TOKEN`: BotFather token'ı
   - `TELEGRAM_CHANNEL`: Kanal ID (@kanaladiniz veya -100...)
3. Deploy et

## Zamanlamaları Düzenle
`telegram_bot.py` dosyasındaki `my_schedules` değişkenini düzenleyin.