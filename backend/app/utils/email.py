import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from app.core.config import settings


logger = logging.getLogger(__name__)


def send_email(
    email_to: str,
    subject: str,
    html_content: str,
    email_from: str = settings.EMAILS_FROM_EMAIL,
) -> bool:
    """
    Отправляет электронное письмо.
    
    Args:
        email_to: Email получателя
        subject: Тема письма
        html_content: HTML-содержимое письма
        email_from: Email отправителя (по умолчанию из настроек)
        
    Returns:
        bool: True если успешно отправлено, False в противном случае
    """
    try:
        # Создаем сообщение
        message = MIMEMultipart()
        message["From"] = email_from
        message["To"] = email_to
        message["Subject"] = subject
        
        # Добавляем HTML-содержимое
        message.attach(MIMEText(html_content, "html"))
        
        # Если SMTP не настроен, просто логируем сообщение
        if not settings.SMTP_HOST:
            logger.info(f"SMTP не настроен. Письмо не отправлено. Получатель: {email_to}, Тема: {subject}")
            logger.debug(f"Содержимое письма: {html_content}")
            return True
        
        # Отправляем письмо
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(email_from, email_to, message.as_string())
            
        logger.info(f"Письмо успешно отправлено получателю {email_to}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка отправки письма: {str(e)}")
        return False


def send_password_reset_email(email_to: str, token: str, username: str) -> bool:
    """
    Отправляет письмо для сброса пароля.
    
    Args:
        email_to: Email получателя
        token: Токен для сброса пароля
        username: Имя пользователя
        
    Returns:
        bool: True если успешно отправлено, False в противном случае
    """
    reset_url = f"{settings.SITE_URL}/reset-password?token={token}"
    subject = "Восстановление пароля - Путешествуй по России"
    
    html_content = f"""
    <html>
    <body>
        <h2>Восстановление пароля</h2>
        <p>Здравствуйте, {username}!</p>
        <p>Вы запросили восстановление пароля для вашей учетной записи на сайте "Путешествуй по России".</p>
        <p>Для создания нового пароля перейдите по ссылке:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>Ссылка будет действительна в течение 24 часов.</p>
        <p>Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.</p>
        <p>С уважением,<br>Команда "Путешествуй по России"</p>
    </body>
    </html>
    """
    
    return send_email(
        email_to=email_to,
        subject=subject,
        html_content=html_content
    )


def send_booking_confirmation(
    email_to: str, 
    username: str, 
    booking_id: int, 
    tour_name: str,
    start_date: str,
    end_date: str
) -> bool:
    """
    Отправляет подтверждение бронирования.
    
    Args:
        email_to: Email получателя
        username: Имя пользователя
        booking_id: ID бронирования
        tour_name: Название тура
        start_date: Дата начала тура
        end_date: Дата окончания тура
        
    Returns:
        bool: True если успешно отправлено, False в противном случае
    """
    subject = f"Подтверждение бронирования №{booking_id} - Путешествуй по России"
    booking_url = f"{settings.SITE_URL}/profile"
    
    html_content = f"""
    <html>
    <body>
        <h2>Подтверждение бронирования</h2>
        <p>Здравствуйте, {username}!</p>
        <p>Благодарим вас за бронирование тура "{tour_name}".</p>
        <p>Детали вашего бронирования:</p>
        <ul>
            <li><strong>Номер бронирования:</strong> {booking_id}</li>
            <li><strong>Тур:</strong> {tour_name}</li>
            <li><strong>Даты:</strong> {start_date} - {end_date}</li>
        </ul>
        <p>Вы можете просмотреть детали вашего бронирования в <a href="{booking_url}">личном кабинете</a>.</p>
        <p>С уважением,<br>Команда "Путешествуй по России"</p>
    </body>
    </html>
    """
    
    return send_email(
        email_to=email_to,
        subject=subject,
        html_content=html_content
    ) 