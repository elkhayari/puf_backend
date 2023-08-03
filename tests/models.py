from django.db import models
from django.utils import timezone

# TEST model.


class SharedTestsModel(models.Model):
    title = models.CharField(max_length=100, default="defualt title")
    testType = models.CharField(max_length=100, default='default test')
    # memoryType = models.CharField(max_length=30, null=True)
    # memoryBrand = models.CharField(max_length=50, null=True)
    # memoryModel = models.CharField(max_length=50, null=True)
    # memoryLabel = models.CharField(max_length=30, null=True)
    initialValue = models.CharField(max_length=10, default="0x55")
    startAddress = models.FloatField(default=0)
    stopAddress = models.FloatField(default=100)
    voltage = models.FloatField(default=3)
    temperature = models.FloatField(default=23)
    dataSetupTime = models.CharField(max_length=50, default="15")
    createdAt = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        print("> SAVE ScharedTestssModel")
        super().save(*args, **kwargs)


class ReliabilityTestsModel(SharedTestsModel):

    def save(self, *args, **kwargs):
        print(">> SAVE ReliabilityTestModel.")
        super().save(*args, **kwargs)


class WriteLatencyTestsModel(SharedTestsModel):
    initialValue_2 = models.CharField(max_length=10, default="0xAA")

    def save(self, *args, **kwargs):
        print(">> SAVE WriteLatencyTestModel.")
        super().save(*args, **kwargs)


class ReadLatencyTestsModel(SharedTestsModel):
    def save(self, *args, **kwargs):
        print(">> SAVE ReadLatencyTestModel.")
        super().save(*args, **kwargs)


class RowHammeringTestsModel(SharedTestsModel):
    initialValue_2 = models.CharField(max_length=10, default="0xAA")
    rowOffset = models.IntegerField(default=1)
    iterations = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        print(">> SAVE RowHammeringTestModel.")
        super().save(*args, **kwargs)

#####################
# Operations on tests
#####################


class SharedMeasurmentTestsModel(models.Model):
    status = models.CharField(max_length=100)
    startedBy = models.CharField(max_length=50)
    startedAt = models.DateTimeField(default=timezone.now)
    finishedAt = models.DateTimeField(default=timezone.now)
    fileName = models.CharField(max_length=100, default="123.csv")
    dataSetupTime = models.IntegerField(default=15)
    iteration = models.IntegerField(default=0)
    memoryType = models.CharField(max_length=30, null=True)
    memoryBrand = models.CharField(max_length=50, null=True)
    memoryModel = models.CharField(max_length=50, null=True)
    memoryLabel = models.CharField(max_length=30, null=True)
    boardLabel = models.CharField(max_length=30, null=True)
    boardSerial = models.CharField(max_length=30, null=True)
    boardName = models.CharField(max_length=30, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        print("> SAVE Schared Measurment Tests Model")
        super().save(*args, **kwargs)


class ReliabilityMeasurmentTestsModel(SharedMeasurmentTestsModel):
    testId = models.ForeignKey(ReliabilityTestsModel, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        print(">> SAVE ReliabilityTestModel.")
        super().save(*args, **kwargs)


class WriteLatencyMeasurmentTestsModel(SharedMeasurmentTestsModel):
    testId = models.ForeignKey(
        WriteLatencyTestsModel, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        print(">> SAVE WriteLatencyTestModel.")
        super().save(*args, **kwargs)


class ReadLatencyMeasurmentTestsModel(SharedMeasurmentTestsModel):
    testId = models.ForeignKey(ReadLatencyTestsModel, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        print(">> SAVE ReadLatencyTestModel.")
        super().save(*args, **kwargs)


class RowHammeringMeasurmentTestsModel(SharedMeasurmentTestsModel):
    testId = models.ForeignKey(
        RowHammeringTestsModel, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        print(">> SAVE RowHammeringTestModel.")
        super().save(*args, **kwargs)
