from django.contrib import admin
from .models import Book, Member, Issue


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available')
    list_filter = ('available',)
    search_fields = ('title', 'author', 'isbn')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email')
    search_fields = ('user__username', 'email', 'name')


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'issue_date', 'return_date')
    list_filter = ('return_date',)
