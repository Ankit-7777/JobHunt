from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.conf import settings
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_welcome_email(user_email, user_name, user_role):
    subject = 'Welcome to Our Platform'
    text_message = f'Hi {user_name}, thank you for signing up as a {user_role}! We are excited to have you on board.'
    
    # HTML version of the email
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Welcome, {user_name}!</h2>
        <p>Thank you for signing up as a <strong>{user_role}</strong>. We are excited to have you on board!</p>
        <p>Feel free to explore our platform.</p>
        <p>Best Regards,<br>Your Job Portal Team</p>
    </body>
    </html>
    """

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,  # Plain text message
            from_email=settings.EMAIL_HOST_USER,
            to=[user_email]
        )
        
        # Attach the HTML content
        email.attach_alternative(html_message, "text/html")
        email.send()

        logger.info(f'Welcome email sent successfully to {user_email}')
    except Exception as e:
        logger.error(f'Failed to send welcome email to {user_email}: {str(e)}')




logger = logging.getLogger(__name__)

@shared_task
def send_application_notification(recruiter_email, job_title, applicant_name):
    # Subject of the email
    subject = f'New Application for {job_title}'
    
    # Plain text version of the email
    text_message = f"{applicant_name} has applied for the position of {job_title}."
    
    # HTML version of the email with inline CSS (without a redirect link)
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; padding: 20px; background-color: #f9f9f9; margin: 0; width: 100%; box-sizing: border-box;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px;">
            <p style="font-size: 16px;">Dear Recruiter,</p>
            <p style="font-size: 16px; color: #333;">
                <span style="color: #2c3e50; font-weight: bold;">{applicant_name}</span> has applied for the position of 
                <span style="font-size: 18px; color: #2c3e50;">{job_title}</span>.
            </p>
            <p style="font-size: 16px; color: #333;">You can view this application in your Job Portal dashboard.</p>
            <p style="margin-top: 20px; font-size: 12px; color: #777;">
                Thank you, <br> Your Job Portal Team
            </p>
        </div>
    </body>
    </html>
    """
    
    # Send the email without a job link
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,  # Plain text message
            from_email=settings.EMAIL_HOST_USER,
            to=[recruiter_email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        logger.info(f'Email sent successfully to {recruiter_email}')
    except Exception as e:
        logger.error(f'Failed to send email to {recruiter_email}: {str(e)}')






logger = logging.getLogger(__name__)

@shared_task
def send_application_status_update_notification(employee_email, application_status, job_title):
    # Subject of the email
    subject = '📩 Your Application Status has been Updated'

    # HTML version of the email without a link
    html_message = f"""
    <html>
    <body style="font-family: 'Arial', sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); padding: 20px; max-width: 600px; margin: auto;">
            <div style="background-color: #3498db; color: white; padding: 15px; border-radius: 8px 8px 0 0; text-align: center;">
                Application Status Update
            </div>
            <div style="padding: 20px; font-size: 16px; color: #333;">
                <p>Dear Applicant,</p>
                <p>Your application for the position of <strong style="color: #e74c3c;">{job_title}</strong> has been updated to:</p>
                <p style="font-weight: bold; font-size: 18px; color: #3498db;">{application_status}</p>
                <p>Thank you for your interest in this position.</p>
            </div>
            <div style="margin-top: 30px; font-size: 12px; color: #7f8c8d; text-align: center;">
                Your Job Portal Team
            </div>
        </div>
    </body>
    </html>
    """

    # Sending the email
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body="This email contains HTML content. Please enable HTML to view the content.",
            from_email=settings.EMAIL_HOST_USER,
            to=[employee_email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        logger.info(f'Notification sent successfully to {employee_email}')
    except Exception as e:
        logger.error(f'Failed to send notification to {employee_email}: {str(e)}')
