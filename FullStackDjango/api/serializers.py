# from rest_framework import serializers


# #Serializer. Zorgt ervoor dat hij het in JSON veranderd.
# class ArticleSerializer(serializers.Serializer):
#     title = serializers.CharField(max_length=120)
#     description = serializers.CharField()
#     body = serializers.CharField()
#     author_id = serializers.IntegerField()
#     # Je kan via postman nu JSON invoeren en het maakt automatish een product aan.
#     def create(self, validated_data):
#         return ArticleSerializer.objects.create(**validated_data)
#     #Delete een product
   
