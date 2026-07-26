"""
app/services/notification_service.py
---------------------------------------
Generates and manages in-app notifications. Notifications are created
proactively (e.g. equipment approaching its expected date, delayed
equipment) and can also be pushed manually by administrators.
"""

from datetime import date, timedelta
from app.extensions import db
from app.models.notification import Notification, NotificationType
from app.models.equipment import Equipment
from app.models.user import User


class NotificationService:

    @staticmethod
    def notify(user_id: int, title: str, message: str,
               notification_type: str = NotificationType.INFO, link: str = None):
        notif = Notification(
            user_id=user_id, title=title, message=message,
            notification_type=notification_type, link=link,
        )
        db.session.add(notif)
        db.session.commit()
        return notif

    @staticmethod
    def get_unread_for_user(user_id: int):
        return (
            Notification.query.filter_by(user_id=user_id, is_read=False)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_all_read(user_id: int):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
        db.session.commit()

    @staticmethod
    def generate_deadline_alerts(days_ahead: int = 7):
        """
        Scan Equipment records for items nearing their expected_date (or
        already overdue) and create notifications for their assigned
        engineers. Intended to be invoked on a schedule (e.g. daily cron)
        or lazily on dashboard load.
        """
        today = date.today()
        horizon = today + timedelta(days=days_ahead)

        upcoming = Equipment.query.filter(
            Equipment.expected_date.isnot(None),
            Equipment.expected_date <= horizon,
            Equipment.actual_date.is_(None),
        ).all()

        created = []
        for eq in upcoming:
            if not eq.assigned_engineer_id:
                continue
            is_overdue = eq.expected_date < today
            title = "Equipment Overdue" if is_overdue else "Deadline Approaching"
            message = (
                f"{eq.equipment_name} ({eq.equipment_code}) "
                f"{'is overdue since' if is_overdue else 'is due on'} "
                f"{eq.expected_date.strftime('%d-%b-%Y')}."
            )
            # Avoid duplicate notifications for the same equipment/day
            exists = Notification.query.filter_by(
                user_id=eq.assigned_engineer_id, title=title, message=message
            ).first()
            if exists:
                continue
            created.append(
                NotificationService.notify(
                    user_id=eq.assigned_engineer_id,
                    title=title,
                    message=message,
                    notification_type=NotificationType.DANGER if is_overdue else NotificationType.WARNING,
                    link=f"/equipment/{eq.id}",
                )
            )
        return created
