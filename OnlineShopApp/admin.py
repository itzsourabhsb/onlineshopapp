from django.contrib import admin
from OnlineShopApp.models import Product,Orders,OrderUpdate
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display=['product_name','category','subcategory','price','desc','pub_date','image']

class OrderAdmin(admin.ModelAdmin):
    list_display=['items_json','name','email','address','city','state','zip_code','phone']

class OrderUpdateAdmin(admin.ModelAdmin):
    list_display=['update_id','order_id','update_desc','timestamp']

admin.site.register(Product,ProductAdmin)
admin.site.register(Orders,OrderAdmin)
admin.site.register(OrderUpdate,OrderUpdateAdmin)
