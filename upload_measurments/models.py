from django.db import models
from django.utils import timezone

# Create your models here.
# Shared model


class ScharedUploadMeasurmentsModel(models.Model):
    title = models.CharField(max_length=100, null=True)
    testType = models.CharField(max_length=100, null=True)
    board = models.CharField(max_length=50, null=True)
    memoryType = models.CharField(max_length=30, null=True)
    memoryBrand = models.CharField(max_length=50, null=True)
    memoryModel = models.CharField(max_length=50, null=True)
    memoryLabel = models.CharField(max_length=30, null=True)
    fileName = models.CharField(max_length=100, default="default.csv")
    file = models.FileField(
        upload_to='uploaded_csv_files/', default="default.csv")
    initialValue = models.CharField(max_length=10, default="0x55")
    startAddress = models.FloatField(default=0, null=True)
    stopAddress = models.FloatField(default=100, null=True)
    voltage = models.FloatField(null=True)
    temperature = models.FloatField(null=True)
    iteration = models.IntegerField(default=0)
    createdAt = models.DateTimeField(default=timezone.now)
    usedBy = models.CharField(max_length=50, default="Anonymous")
    dataSetupTime = models.CharField(max_length=50, default="15")

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        print("> SAVE ScharedUploadMeasurmentsModel")
        super().save(*args, **kwargs)


class UploadReliabilityMeasurmentModel(ScharedUploadMeasurmentsModel):

    def save(self, *args, **kwargs):
        print(">> SAVE UploadReliabilityMeasurmentModel.")
        super().save(*args, **kwargs)


class UploadWriteLatencyMeasurmentModel(ScharedUploadMeasurmentsModel):

    initialValue_2 = models.CharField(max_length=10, default="0xAA")

    def save(self, *args, **kwargs):
        print(">> SAVE UploadReadLatencyMeasurmentModel.")
        super().save(*args, **kwargs)


class UploadReadLatencyMeasurmentModel(ScharedUploadMeasurmentsModel):

    def save(self, *args, **kwargs):
        print(">> SAVE UploadReadLatencyMeasurmentModel.")
        super().save(*args, **kwargs)


class UploadRowHammeringMeasurmentModel(ScharedUploadMeasurmentsModel):

    initialValue_2 = models.CharField(max_length=10, default="0xAA")
    rowOffset = models.IntegerField(default=1)
    iterations = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        print(">> SAVE UploadRowHammeringMeasurmentModel.")
        super().save(*args, **kwargs)
