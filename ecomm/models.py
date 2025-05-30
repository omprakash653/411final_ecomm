from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    email = models.EmailField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    CATEGORY_CHOICES = (
        (1, 'Mobile'),
        (2, 'Shoes'),
        (3, 'Cloth'),
    )

    name = models.CharField(max_length=100)
    price = models.IntegerField()
    category = models.IntegerField(verbose_name='Category', choices=CATEGORY_CHOICES)
    pdetails = models.CharField(max_length=300, verbose_name='Product Details')
    is_active = models.BooleanField(default=True)
    pimage = models.ImageField(upload_to='images/')  # Ensure MEDIA settings are configured

    def __str__(self):
        return f"{self.name} - {self.pdetails}"
    

class Cart(models.Model):
    uid=models.ForeignKey('auth.User',on_delete= models.CASCADE,db_column='uid')
    pid=models.ForeignKey('Product',on_delete= models.CASCADE,db_column='pid')
    qty=models.IntegerField(default=1)
    # def __str__(self):
    #     return {self.uid}

class Order(models.Model):
    uid=models.ForeignKey('auth.User',on_delete= models.CASCADE,db_column='uid')
    pid=models.ForeignKey('Product',on_delete= models.CASCADE,db_column='pid')
    qty=models.IntegerField(default=1)
    amt=models.IntegerField()