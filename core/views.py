from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, OutfitType
from .serializers import CategorySerializer, OutfitTypeSerializer

def home(request):
    return render(request, 'core/home.html')

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'core/category_list.html', {'categories': categories})

def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'core/category_create.html', {'error': 'Name is required'})
        
        base_prefix = ''.join([c for c in name if c.isalpha()])[:2].upper()
        if len(base_prefix) < 2:
            return render(request, 'core/category_create.html', {'error': 'Name must contain at least 2 letters'})
        
        prefix = base_prefix
        counter = 2
        while Category.objects.filter(prefix=prefix).exists():
            prefix = f"{base_prefix}{counter}"
            counter += 1
        
        Category.objects.create(name=name, prefix=prefix)
        return redirect('/categories/')
    
    return render(request, 'core/category_create.html')

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'core/category_edit.html', {'category': category, 'error': 'Name is required'})
        
        category.name = name
        category.save()
        return redirect('/categories/')
    
    return render(request, 'core/category_edit.html', {'category': category})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('/categories/')

def outfit_type_list(request):
    outfit_types = OutfitType.objects.all()
    return render(request, 'core/outfit_type_list.html', {'outfit_types': outfit_types})

def outfit_type_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'core/outfit_type_create.html', {'error': 'Name is required'})
        
        base_code = ''.join([c for c in name if c.isalpha()])[:2].upper()
        if len(base_code) < 2:
            return render(request, 'core/outfit_type_create.html', {'error': 'Name must contain at least 2 letters'})
        
        code = base_code
        counter = 2
        while OutfitType.objects.filter(code=code).exists():
            code = f"{base_code}{counter}"
            counter += 1
        
        OutfitType.objects.create(name=name, code=code)
        return redirect('/outfit-types/')
    
    return render(request, 'core/outfit_type_create.html')

def outfit_type_edit(request, pk):
    outfit_type = get_object_or_404(OutfitType, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'core/outfit_type_edit.html', {'outfit_type': outfit_type, 'error': 'Name is required'})
        
        outfit_type.name = name
        outfit_type.save()
        return redirect('/outfit-types/')
    
    return render(request, 'core/outfit_type_edit.html', {'outfit_type': outfit_type})

def outfit_type_delete(request, pk):
    outfit_type = get_object_or_404(OutfitType, pk=pk)
    outfit_type.delete()
    return redirect('/outfit-types/')

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        name = request.data.get('name', '').strip()
        if not name:
            return Response(
                {"error": "name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        base_prefix = ''.join([c for c in name if c.isalpha()])[:2].upper()
        if len(base_prefix) < 2:
            return Response(
                {"error": "name must contain at least 2 letters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        prefix = base_prefix
        counter = 2
        while Category.objects.filter(prefix=prefix).exists():
            prefix = f"{base_prefix}{counter}"
            counter += 1

        category = Category.objects.create(name=name, prefix=prefix)
        serializer = self.get_serializer(category)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OutfitTypeViewSet(viewsets.ModelViewSet):
    queryset = OutfitType.objects.all()
    serializer_class = OutfitTypeSerializer

    def create(self, request, *args, **kwargs):
        name = request.data.get('name', '').strip()
        if not name:
            return Response(
                {"error": "name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        base_code = ''.join([c for c in name if c.isalpha()])[:2].upper()
        if len(base_code) < 2:
            return Response(
                {"error": "name must contain at least 2 letters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        code = base_code
        counter = 2
        while OutfitType.objects.filter(code=code).exists():
            code = f"{base_code}{counter}"
            counter += 1

        outfit_type = OutfitType.objects.create(name=name, code=code)
        serializer = self.get_serializer(outfit_type)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
