from django.contrib import admin
from .models import Category, NewsArticle, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)    
    
@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'category', 'published_at')
    search_fields = ('title', 'writer__name', 'category__name')
    list_filter = ('category', 'published_at')
    ordering = ('-published_at',)
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):       
    list_display = ('article', 'author_name', 'created_at')
    search_fields = ('article__title', 'author_name__username', 'author_name__email', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)