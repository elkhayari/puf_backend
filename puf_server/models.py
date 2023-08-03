from django.db import models
from django.utils import timezone
# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=300)
    body = models.TextField()
    slug = models.SlugField(null=False, unique=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploaded_csv_files/')

    def __str__(self):
        return self.title


class fram(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class FramTests(models.Model):
    name = models.CharField(max_length=50)
    memory_type = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    temp = models.FloatField()
    vol = models.FloatField()

    def __str__(self):
        return self.memory_type


class FramResults(models.Model):
    result_id = models.ForeignKey(FramTests, on_delete=models.CASCADE)
    index = models.IntegerField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)


class Tests(models.Model):
    title = models.CharField(max_length=100)
    testType = models.CharField(max_length=100, default='default test')
    board = models.CharField(max_length=50)
    memory = models.CharField(max_length=30)
    initialValue = models.CharField(max_length=10, default="0x55")
    startAddress = models.FloatField(default=0)
    stopAddress = models.FloatField(default=100)
    voltage = models.FloatField()
    temperature = models.FloatField()
    dataSetupTime = models.CharField(max_length=50, default="15")

    # def __str__(self):
    # return self.memory


class TestOperations(models.Model):
    testId = models.ForeignKey(Tests, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    usedBy = models.CharField(max_length=50)
    createdAt = models.DateTimeField(default=timezone.now)
    count = models.IntegerField(default=0)
    fileName = models.CharField(max_length=100, default="123.csv")
    dataSetupTime = models.IntegerField(default=15)
    iteration = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        print("SAVE")
        self.count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.count


def upload_path(instance, filename):
    return '/'.join(['heatmaps', str(instance.name), filename])


class Image(models.Model):
    name = models.CharField(max_length=32, blank=False)
    image = models.ImageField(blank=True, null=True, upload_to="images/")


class Experiments(models.Model):
    title = models.CharField(max_length=50, blank=False)
    description = models.CharField(max_length=1000, blank=False)


class UploadMeasurments(models.Model):
    title = models.CharField(max_length=100)
    testType = models.CharField(max_length=100, default='default test')
    board = models.CharField(max_length=50)
    memory = models.CharField(max_length=30)
    fileName = models.CharField(max_length=100, default="123.csv")
    file = models.FileField(upload_to='uploaded_csv_files/')
    initialValue = models.CharField(max_length=10, default="0x55")
    startAddress = models.FloatField(default=0)
    stopAddress = models.FloatField(default=100)
    voltage = models.FloatField()
    temperature = models.FloatField()
    dataSetupTime = models.CharField(max_length=50, default="15")
    iteration = models.IntegerField(default=0)
    createdAt = models.DateTimeField(default=timezone.now)
    usedBy = models.CharField(max_length=50, default="Anonymous")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        print("SAVE UPLOADED MEASURMENTS.")
        super().save(*args, **kwargs)
