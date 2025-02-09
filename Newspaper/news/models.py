# from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.core.cache import cache
from django.utils.translation import gettext as _
from django.utils.translation import pgettext_lazy
# Create your models here.



class Author(models.Model):
	authorUser = models.OneToOneField(User, on_delete=models.DO_NOTHING)
	ratingAuthor = models.SmallIntegerField(default=0)

	def update_rating(self):
		postRat = self.post_set.aggregate(postRating=Sum('rating'))
		pRat = 0
		pRat += postRat.get('postRating')
		# pRat += Post.rating

		commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating'))
		cRat = 0
		cRat += commentRat.get('commentRating')

		self.ratingAuthor = pRat * 3 + cRat
		self.save()

class Category(models.Model):
	name = models.CharField(max_length=64, unique=True)
	subscribers = models.ManyToManyField(User, related_name='categories')


	def __str__(self):
		return self.name.title()

class Post(models.Model):
	NEWS = 'NW'
	ARTICLE = 'AR'
	CATEGORY_CHOICE = [
		(NEWS, "Новость"),
		(ARTICLE, "Статья"),
	]
	title = models.CharField(max_length=128)
	text = models.TextField()
	dateCreation = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(Author, on_delete=models.CASCADE)
	categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICE, default=NEWS,
									help_text=_('category type'))
	postCategory = models.ManyToManyField(Category, through='PostCategory')
	rating = models.SmallIntegerField(default=0)
	is_active = models.BooleanField(default=True)

	@property
	def on_rating(self):
		return self.rating > 0

	def like(self):
		self.rating += 1
		self.save()

	def dislike(self):
		self.rating -= 1
		self.save()

	# def true_rating(self):
	# 	if self.rating < -10:
	# 		return self.rating == -10
	# 	elif self.rating > 10:
	# 		return self.rating == 10

	def preview(self):
		return self.text[0:123] + "..."

	# def __str__(self):
	# 	return f'{self.title.title()}: {self.text[:20]}'

	def get_absolut_url(self):
		return reverse('News_detail', args=[str(self.id)])

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		cache.delete(f'post-{self.pk}')


class Subscription(models.Model):
	user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='subscriptions',
							 verbose_name=pgettext_lazy('help text for Subcription'))
	category = models.ForeignKey(to='Category', on_delete=models.CASCADE, related_name='subscriptions')

class Comment(models.Model):
	text = models.TextField()
	dateCreation = models.DateTimeField(auto_now_add=True)
	commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
	commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
	rating = models.SmallIntegerField(default=0)

	def like(self):
		self.rating += 1
		self.save()

	def dislike(self):
		self.rating -= 1
		self.save()

	# def true_rating(self):
	# 	if self.rating < -10:
	# 		return self.rating == -10
	# 	elif self.rating > 10:
	# 		return self.rating == 10

class PostCategory(models.Model):
	postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
	categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)

