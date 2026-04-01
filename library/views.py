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
        users = Member.objects.filter(user__is_staff=False)  # exclude admins
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
            my_books_count = my_books.count()
        except Member.DoesNotExist:
            my_books = []
            my_books_count = 0

        return render(request, 'user_dashboard.html', {
            'books': books,
            'my_books': my_books,
            'my_books_count': my_books_count,
        })


# -------------------------
# BOOK CRUD (ADMIN ONLY)
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
def update_book(request, book_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        isbn = request.POST.get('isbn', '').strip()

        if title and author and isbn:
            book.title = title
            book.author = author
            book.isbn = isbn
            book.save()
            messages.success(request, f'Book "{title}" updated successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'All fields are required.')

    return render(request, 'update_book.html', {'book': book})


@login_required
def delete_member(request, member_id):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    member = get_object_or_404(Member, id=member_id)
    if request.method == 'POST':
        username = member.user.username
        member.user.delete()  # deletes User and Member together (CASCADE)
        messages.success(request, f'Member "{username}" deleted.')
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
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)

        try:
            member = request.user.member
        except Member.DoesNotExist:
            messages.error(request, 'Member profile not found.')
            return redirect('dashboard')

        active_issues = Issue.objects.filter(member=member, return_date__isnull=True).count()

        if active_issues >= 2:
            messages.warning(request, 'You can only borrow up to 2 books at a time.')
        elif not book.available:
            messages.warning(request, 'This book is currently not available.')
        else:
            Issue.objects.create(book=book, member=member)
            book.available = False
            book.save()
            messages.success(request, f'"{book.title}" borrowed successfully.')

    return redirect('dashboard')

@login_required
def return_book(request, issue_id):
    if request.method == 'POST':
        issue = get_object_or_404(Issue, id=issue_id)

        if issue.member.user == request.user:
            issue.return_date = date.today()
            issue.book.available = True
            issue.book.save()
            issue.save()
            messages.success(request, f'"{issue.book.title}" returned successfully.')
        else:
            messages.error(request, 'You can only return your own books.')

    return redirect('dashboard')


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        return redirect('books')  # or wherever you want to redirect after deletion
    return redirect('books')