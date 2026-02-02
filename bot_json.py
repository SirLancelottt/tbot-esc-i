async def send_scheduled_message(schedule_item, messages_dict):
    """Zamanlanmış mesajı gönder"""
    try:
        if schedule_item.get('disabled', False):
            return False
        
        username = schedule_item.get('username', '')
        
        if not username or username not in messages_dict:
            return False
        
        # RANDOM mesaj seç
        message_pool = messages_dict[username]
        if not message_pool:
            return False
        
        message_data = random.choice(message_pool)
        bot = Bot(token=TOKEN)
        message_text = message_data.get('text', '')
        
        # ⭐ AKILLI KONTROL: Mesajda @username var mı?
        # Büyük/küçük harf duyarsız kontrol
        username_lower = username.lower()
        message_lower = message_text.lower()
        
        if f"@{username_lower}" in message_lower or f"@{username}" in message_text:
            # Username zaten mesajda varsa - sadece gizli karakter ekle
            final_message = f"{message_text}\u200b"
        else:
            # Username yoksa - ekle ve gizli karakter ekle
            final_message = f"{message_text}\n\n@{username}\u200b"
        
        msg_type = message_data.get('type', 'text_only')
        
        if msg_type == 'with_image':
            image_url = message_data.get('image_url')
            
            if image_url:
                await bot.send_photo(
                    chat_id=CHANNEL,
                    photo=image_url,
                    caption=final_message,
                    parse_mode='HTML'
                )
                log.info(f"✅ [📷] @{username} → {message_text[:30]}...")
            else:
                await bot.send_message(
                    chat_id=CHANNEL,
                    text=final_message,
                    parse_mode='HTML'
                )
                log.warning(f"⚠️ Resim yok: @{username}")
        
        else:  # text_only
            await bot.send_message(
                chat_id=CHANNEL,
                text=final_message,
                parse_mode='HTML'
            )
            log.info(f"✅ [📝] @{username} → {message_text[:30]}...")
            
        return True
        
    except Exception as e:
        log.error(f"❌ Gönderme hatası: {e}")
        return False