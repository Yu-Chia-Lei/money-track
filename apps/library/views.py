from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, redirect
from .models import Book

# Create your views here.
class HelloWorldView(View):
    def get(self, request): #使用者對網站發出的 GET 請求
        return HttpResponse("哈囉")
    
class HelloStudentView(View):
    def get(self, request, student_name): 
        #print(request.GET)
        hello_way = request.GET.get('hello_way')
        if hello_way:
            return HttpResponse(f"你好，{student_name}，{hello_way} ")
        else:
            return HttpResponse(f"你好，{student_name}！")

class JsonResponseView(View):
    def get(self, request):
        return JsonResponse("message: Helloworld!")
        #return redirect("library:hello_world")

class BookListView(View):
    """書籍列表頁"""

    def get(self, request):
        # 從資料庫取得資料
        books = Book.objects.all()

        # 準備要傳給 Template 的資料
        context = {
            'books': books,
            'total_count': books.count(),
        }

        # 渲染 Template 並返回
        return render(request, './library/book_list.html', context)

class BookDetailView(View):
    def get(self, request, book_id):
        book = Book.objects.get(id=book_id)
        print(book)

        context = {
            'book': book,
            'page_title': '書籍詳細資訊',
        }

        return render(request, './library/book_detail.html', context)


class BookCreateView(View):
    def get(self, request, book_id):
        return render(request, './library/book_create.html')
    def post(self, request):
        title = request.POST.get('title')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        Book.objects.create(
            title=title,
            price=price,
            stock=stock
        )
        return redirect('library:book_list')
       








