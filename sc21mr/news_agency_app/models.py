from django.db import models

# Create your models here.

class Authors(models.Model):
	author_name = models.CharField(max_length=100)
	author_username = models.CharField(max_length=100, unique=True)
	author_password = models.CharField(max_length=100)

	def to_dict(self):
		return {
			'author_id': self.id,
			'author_name': self.author_name,
			'author_username': self.author_username
		}

class News(models.Model):
	headline = models.CharField(max_length=64)
	category = models.CharField(max_length=10, choices=[('pol', 'Politics'), ('art', 'Art'), ('tech', 'Technology'), ('trivia', 'Trivia')])
	region = models.CharField(max_length=2, choices=[('uk', 'UK'), ('eu', 'EU'), ('w', 'World')])
	author = models.ForeignKey(Authors, on_delete=models.CASCADE)
	datetime = models.DateField()
	details = models.CharField(max_length=128)

	def to_dict(self):
		return {
			'news_id': self.id,
			'headline': self.headline,
			'category': self.category,
			'region': self.region,
			'author': self.author.to_dict(),
			'datetime': self.datetime,
			'details': self.details
		}