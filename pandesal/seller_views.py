from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Shop, UserProfile, Pandesal, Order, Reservation, Notification
from django.contrib.auth.models import User
from django.db.models import Sum
from .forms import ShopForm, SellerProductForm
from django.views.decorators.clickjacking import xframe_options_sameorigin



@login_required
def seller_dashboard(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        messages.error(request, "You do not have access to the seller dashboard.")
        return redirect('home')
        
    shop = getattr(request.user, 'shop', None)
    
    # Calculate stats
    orders = Order.objects.filter(seller=request.user)
    new_orders_count = orders.filter(status__in=['pending', 'pending_confirmation']).count()
    preparing_count = orders.filter(status__in=['confirmed', 'ready_for_pickup']).count()
    completed_count = orders.filter(status='completed').count()
    
    total_sales = orders.filter(status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    recent_orders = orders.order_by('-created_at')[:5]
    low_stock_products = Pandesal.objects.filter(seller=request.user, stock__lt=10).order_by('stock')
    
    context = {
        'shop': shop,
        'new_orders_count': new_orders_count,
        'preparing_count': preparing_count,
        'completed_count': completed_count,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'pandesal/seller/dashboard.html', context)

@login_required
def seller_shop_settings(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        messages.error(request, "You do not have access to the seller dashboard.")
        return redirect('home')
        
    shop = getattr(request.user, 'shop', None)
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.seller = request.user
            shop.save()
            messages.success(request, "Shop settings updated successfully.")
            return redirect('seller_shop_settings')
    else:
        form = ShopForm(instance=shop)
        
    return render(request, 'pandesal/seller/shop_settings.html', {'form': form, 'shop': shop})

@login_required
def seller_products(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
    products = Pandesal.objects.filter(seller=request.user)
    return render(request, 'pandesal/seller/products.html', {'products': products})

@login_required
def seller_product_create(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    if request.method == 'POST':
        form = SellerProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product created successfully!")
            return redirect('seller_products')
    else:
        form = SellerProductForm()
    return render(request, 'pandesal/seller/product_form.html', {'form': form, 'is_edit': False})

@login_required
def seller_product_edit(request, product_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    product = get_object_or_404(Pandesal, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        form = SellerProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('seller_products')
    else:
        # Initialize form with instance, but ensure categories map back to choices properly
        form = SellerProductForm(instance=product)
        # For MultipleChoiceField, initial data needs to be explicitly set
        if product.categories:
            form.initial['categories'] = product.categories
            
    return render(request, 'pandesal/seller/product_form.html', {'form': form, 'product': product, 'is_edit': True})

@login_required
def seller_orders(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    orders = Order.objects.filter(seller=request.user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    return render(request, 'pandesal/seller/orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES
    })

@login_required
def seller_order_detail(request, order_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    return render(request, 'pandesal/seller/order_detail.html', {
        'order': order,
        'status_choices': Order.STATUS_CHOICES
    })

@login_required
def seller_order_status_update(request, order_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {order.get_status_display()}")
    return redirect('seller_order_detail', order_id=order.id)

@login_required
def seller_reservations(request):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    reservations = Reservation.objects.filter(seller=request.user).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        reservations = reservations.filter(status=status_filter)
        
    return render(request, 'pandesal/seller/reservations.html', {
        'reservations': reservations,
        'status_filter': status_filter,
        'status_choices': Reservation.STATUS_CHOICES
    })

@login_required
def seller_reservation_detail(request, reservation_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    reservation = get_object_or_404(Reservation, id=reservation_id, seller=request.user)
    return render(request, 'pandesal/seller/reservation_detail.html', {
        'reservation': reservation,
        'status_choices': Reservation.STATUS_CHOICES
    })

@login_required
def seller_reservation_status_update(request, reservation_id):
    profile = request.user.userprofile
    if profile.user_type != 'seller' or not profile.is_approved_seller:
        return redirect('home')
        
    reservation = get_object_or_404(Reservation, id=reservation_id, seller=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            reservation.status = new_status
            reservation.save()
            messages.success(request, f"Reservation status updated to {reservation.get_status_display()}")
    return redirect('seller_reservation_detail', reservation_id=reservation.id)

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_sellers(request):
    pending_sellers = UserProfile.objects.filter(user_type='seller', is_approved_seller=False).select_related('user', 'user__shop')
    approved_sellers = UserProfile.objects.filter(user_type='seller', is_approved_seller=True).select_related('user', 'user__shop')
    return render(request, 'pandesal/admin_sellers.html', {
        'pending_sellers': pending_sellers,
        'approved_sellers': approved_sellers
    })

@user_passes_test(is_admin)
def admin_seller_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        shop_name = request.POST.get('shop_name', '').strip()
        phone = request.POST.get('phone', '')
        barangay = request.POST.get('barangay', '')
        zone = request.POST.get('zone', '')

        if not username or not email or not password1 or not shop_name:
            messages.error(request, 'Username, email, password, and shop name are required.')
            return redirect('admin_sellers')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('admin_sellers')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('admin_sellers')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('admin_sellers')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.user_type = 'seller'
        profile.is_approved_seller = True
        profile.phone = phone
        profile.barangay = barangay
        profile.zone = zone
        profile.save()

        Shop.objects.get_or_create(
            seller=user,
            defaults={'shop_name': shop_name, 'is_active': True}
        )

        messages.success(request, f'Seller account for "{shop_name}" created successfully!')
        return redirect('admin_sellers')

    return redirect('admin_sellers')

@user_passes_test(is_admin)
@xframe_options_sameorigin
def admin_seller_edit(request, user_id):
    seller_user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=seller_user)
    shop, _ = Shop.objects.get_or_create(seller=seller_user, defaults={'shop_name': f"{seller_user.username}'s Bakery"})

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        username = request.POST.get('username')
        email = request.POST.get('email')
        shop_name = request.POST.get('shop_name', '').strip()
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        barangay = request.POST.get('barangay', '')
        zone = request.POST.get('zone', '')
        password = request.POST.get('password1', '')

        if not username or not email or not shop_name:
            err = 'Username, email, and shop name are required.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err})
            messages.error(request, err)
            return redirect('admin_sellers')

        if User.objects.filter(username=username).exclude(id=seller_user.id).exists():
            err = 'Username already taken by another account.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err})
            messages.error(request, err)
            return redirect('admin_sellers')

        if User.objects.filter(email=email).exclude(id=seller_user.id).exists():
            err = 'Email already taken by another account.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': err})
            messages.error(request, err)
            return redirect('admin_sellers')

        seller_user.username = username
        seller_user.email = email
        seller_user.first_name = first_name
        seller_user.last_name = last_name
        if password:
            seller_user.set_password(password)
        seller_user.save()

        profile.phone = phone
        profile.barangay = barangay
        profile.zone = zone
        profile.save()

        shop.shop_name = shop_name
        shop.save()

        msg = f'Seller "{shop_name}" updated successfully!'
        if is_ajax:
            return JsonResponse({'success': True, 'message': msg})

        messages.success(request, msg)
        return redirect('admin_sellers')

    return render(request, 'pandesal/admin_seller_edit.html', {
        'seller_user': seller_user,
        'profile': profile,
        'shop': shop
    })

@user_passes_test(is_admin)
def admin_seller_toggle(request, user_id):
    if request.method == 'POST':
        seller_user = get_object_or_404(User, id=user_id)
        seller_user.is_active = not seller_user.is_active
        seller_user.save()
        status_text = "activated" if seller_user.is_active else "deactivated"
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
        if is_ajax:
            return JsonResponse({'success': True, 'message': f'Seller account {status_text} successfully'})
        messages.success(request, f'Seller "{seller_user.username}" has been {status_text}.')
    return redirect('admin_sellers')

@user_passes_test(is_admin)
def admin_seller_delete(request, user_id):
    if request.method == 'POST':
        seller_user = get_object_or_404(User, id=user_id)
        shop_name = getattr(seller_user, 'shop', None)
        name = shop_name.shop_name if shop_name else seller_user.username
        seller_user.delete()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
        if is_ajax:
            return JsonResponse({'success': True, 'message': f'Seller account "{name}" deleted successfully'})
        messages.success(request, f'Seller account "{name}" deleted successfully.')
    return redirect('admin_sellers')

@user_passes_test(is_admin)
def admin_seller_approve(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    profile.is_approved_seller = True
    profile.save()
    messages.success(request, f"Seller {profile.user.username} has been approved.")
    return redirect('admin_sellers')

@user_passes_test(is_admin)
def admin_seller_reject(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    profile.user_type = 'customer'
    profile.save()
    # Delete the shop application
    if hasattr(profile.user, 'shop'):
        profile.user.shop.delete()
    messages.success(request, f"Seller application for {profile.user.username} has been rejected.")
    return redirect('admin_sellers')
