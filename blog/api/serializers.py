from rest_framework import serializers
from blog.models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_date', 'summary', 'tags']
        read_only_fields = ['author', 'summary', 'tags']
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_date']
        read_only_fields = ['author']
