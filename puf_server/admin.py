from django.contrib import admin

from .models import Tests

# Register your models here.
# admin.site.register(Post)

# admin.site.register(FramResults)

# admin.site.register(FramTests)

# admin.site.register(fram)

admin.site.register(Tests)

# Replace the above with the code below to
# have Django auto-generate your slug when
# creating a new blog post.

# class PostAdmin(admin.ModelAdmin):
#     prepopulated_fields = {'slug': ('title',)}

# admin.site.register(Post, PostAdmin)
