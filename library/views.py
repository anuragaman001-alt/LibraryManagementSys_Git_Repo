from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages

from .models import Book, Issue, Member


# -------------------------
# AUTH
# -------------------------

def register(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created! Welcome, {user.username}.')
            return redirect('dashboard')

    return render(request, 'register.html', {'form': form})


# -------------------------
# DASHBOARD
# -------------------------

@login_required
def dashboard(request):
    if request.user.is_staff:
        books = Book.objects.all()
        users = Member.objects.all()
        issues = Issue.objects.select_related('book', 'member__user').all()

        return render(request, 'admin_dashboard.html', {
            'books': books,
            'users': users,
            'issues': issues,
        })
    else:
        books = Book.objects.all()
        try:
            my_books = Issue.objects.filter(
                member=request.user.member,
                return_date__isnull=True
            ).select_related('book')
        except Member.DoesNotExist:
            my_books = []

        return render(request, 'user_dashboard.html', {
            'books': books,
            'my_books': my_books,
        })


# -------------------------
# BOOK CRUD (ADMIN)
# -------------------------

@login_required
def add_book(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        isbn = request.POST.get('isbn', '').strip()

        if title and author and isbn:
            Book.objects.create(title=title, author=author, isbn=isbn)
            messages.success(request, f'Book "{title}" added successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'All fields are required.')

    return render(request, 'add_book.html')


@login_required
def delete_book(request, book_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    book = get_object_or_404(Book, id=book_id)
    # Only allow POST for destructive actions
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" deleted.')
    return redirect('dashboard')


# -------------------------
# USER FUNCTIONS
# -------------------------

@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'user_dashboard.html', {'books': books})


@login_required
def issue_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.available:
        try:
            member = request.user.member
        except Member.DoesNotExist:
            messages.error(request, 'Member profile not found.')
            return redirect('dashboard')

        Issue.objects.create(book=book, member=member)
        book.available = False
        book.save()
        messages.success(request, f'"{book.title}" issued successfully.')
    else:
        messages.warning(request, 'This book is currently not available.')

    return redirect('dashboard')


@login_required
def return_book(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)

    if issue.member.user == request.user:
        issue.return_date = date.today()  # Fixed: was incorrectly set to issue_date
        issue.book.available = True
        issue.book.save()
        issue.save()
        messages.success(request, f'"{issue.book.title}" returned successfully.')
    else:
        messages.error(request, 'You can only return your own books.')

    return redirect('dashboard')
