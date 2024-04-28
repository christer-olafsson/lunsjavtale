from django.db import models


class MeetingTypeChoices(models.TextChoices):
    IN_PERSON = 'in-person'
    INTERVIEW = 'interview'
    REMOTE = 'remote'
    OTHERS = 'others'
