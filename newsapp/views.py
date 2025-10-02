from django.shortcuts import render, redirect, get_object_or_404   
from .models import NewsArticle, Category, Comment
from .forms import NewsArticleForm, UpdateNewsArticleForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import CommentForm
from .serializers import NewsArticleSerializer, CategorySerializer, CommentSerializer
from rest_framework import viewsets
from .permissions import IsAdminOrEditorOrOwnerWriter, IsAdminOrEditor


def index(request):
    articles = NewsArticle.objects.all().order_by('-published_at')[:5]
    context = {'articles': articles}    
    
    return render(request, 'newsapp/index.html', context)

def article_detail(request, article_id):
    article = get_object_or_404(NewsArticle, id=article_id)
    comments = article.comments.filter(parent__isnull=True).order_by('-created_at')  # only top-level comments

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article

            # If user is signed in, set author_name
            if request.user.is_authenticated:
                comment.author_name = request.user
            else:
                comment.author_name = None  # Anonymous

            # Handle reply case (if parent comment ID is passed)
            parent_id = request.POST.get("parent_id")
            if parent_id:
                parent_comment = Comment.objects.filter(id=parent_id, article=article).first()
                comment.parent = parent_comment

            comment.save()
            return redirect("article_detail", article_id=article.id)
    else:
        form = CommentForm()

    context = {
        "article": article,
        "comments": comments,
        "form": form,
    }
    return render(request, "newsapp/article_detail.html", context)

@login_required
def create_news_article(request):
    # Only Admin, Editor, or Writer can create
    if request.user.role not in ["ADMIN", "EDITOR", "WRITER"]:
        return HttpResponseForbidden("You do not have permission to create articles.")

    if request.method == 'POST':
        form = NewsArticleForm(request.POST, request.FILES)
        if form.is_valid():
            news_article = form.save(commit=False)
            news_article.writer = request.user
            news_article.save()
            return redirect('index')
    else:
        form = NewsArticleForm()
    
    return render(request, 'newsapp/create_article.html', {'form': form})


@login_required
def update_news_article(request, article_id):
    article = get_object_or_404(NewsArticle, id=article_id)

    # Permissions:
    # - Admin and Editor can edit any article
    # - Writer can only edit their own article
    if request.user.role == "VIEWER":
        return HttpResponseForbidden("You do not have permission to edit articles.")
    if request.user.role == "WRITER" and article.writer != request.user:
        return HttpResponseForbidden("You can only edit your own articles.")

    if request.method == 'POST':
        form = UpdateNewsArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article_detail', article_id=article.id)
    else:
        form = UpdateNewsArticleForm(instance=article)
    
    return render(request, 'newsapp/update_article.html', {'form': form, 'article': article})


class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    permission_classes = [IsAdminOrEditorOrOwnerWriter]
    
    def perform_create(self, serializer):
        serializer.save(writer=self.request.user)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer   
    permission_classes = [IsAdminOrEditor]
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer    