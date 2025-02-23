from django.db import models


# Create your models here.
class Venue(models.Model):
    name = models.CharField(max_length=255)
    address_url = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "people"

    def __str__(self):
        return self.name


class Presentation(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    presenters = models.ManyToManyField(Person, related_name="presentations")
    event = models.ForeignKey(
        "Event", on_delete=models.CASCADE, related_name="presentations"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="events")

    class Meta:
        ordering = ["-date_time"]

    def __str__(self):
        return self.title
