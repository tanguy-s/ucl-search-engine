from django.dispatch import receiver
from django.db.models.signals import post_save

#from engine.tasks import crawler
from engine.models import WebPage

@receiver(post_save, sender=WebPage)
def webpage_created(sender, instance, created, **kwargs):
    # if created:
    #     # add task
    #     crawler.delay(instance.id)
    pass