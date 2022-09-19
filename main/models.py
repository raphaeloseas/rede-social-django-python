from distutils.command.upload import upload
from email.policy import default
from pickle import TRUE
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime


#Definindo o usário do perfil
User = get_user_model()

# Create your models here.

#Criando o modelo de perfil do usuário
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture-973460_1280.png')
    location = models.CharField(max_length=254, blank=True)
    first_name = models.CharField(max_length=254, blank=True)
    last_name = models.CharField(max_length=254, blank=True)

    def __str__(self):
        return self.user.username
    

#Criando o modelo dos posts dos usuários
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=254)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user


#Criando o modelo de like nos posts
class LikePost(models.Model):
    post_id = models.CharField(max_length=254)
    username = models.CharField(max_length=254)

    def __str__(self):
        return self.username
    

#Criando modelo de contagem de seguidores
class FollowersCount(models.Model):
    follower = models.CharField(max_length=254)  
    user = models.CharField(max_length=254)  

    def __str__(self):
        return self.user
