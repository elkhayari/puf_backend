from rest_framework import serializers
from .models import Post, FramTests, Tests, TestOperations, Image, Experiments, UploadMeasurments


# This code specifies the model to work with
# and the fields to be converted to JSON
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'slug', 'created_at')


class FramTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FramTests
        fields = '__all__'


class TestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tests
        fields = '__all__'


class TestOperationsSerializers(serializers.ModelSerializer):
    class Meta:
        model = TestOperations
        fields = '__all__'


class ImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['name', 'image']


class ExperimentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Experiments
        fields = '__all__'

# todo delete this


class UploadMeasurmentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = UploadMeasurments
        fields = '__all__'
