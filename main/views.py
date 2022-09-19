from email.mime import image
from turtle import pos
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowersCount
from django.contrib.auth.decorators import login_required
from itertools import chain
import random 

# Create your views here.

#Homepage
@login_required(login_url='signin')
def index(request):
    #Pegando os dados do usuário e inserindo na home
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)


    #Posts dos seguidores
    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)  
        feed.append(feed_lists)
    
    feed_lists = list(chain(*feed))

        
    #Sugestão de usuários
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]   
    current_user = User.objects.filter(username=request.user.username) 
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists) 

    suggestions_username_profile_list = list(chain(*username_profile_list)) 


    return render (request, 'index.html',  {'user_profile': user_profile, 'posts': feed_lists, 'suggestions_username_profile_list': suggestions_username_profile_list[:7]})

#Se inscrever e inserindo dados no banco de dados
def signup(request):

    #Verificando se o método do formulario é POST
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        passwordconf = request.POST['passwordconf']

        #Conferindo se a senha está igual a confirmação de senha
        if password == passwordconf:
            
            #Filtrando no banco de dados e vereficando se já existe um email igual ao digitado 
            if User.objects.filter(email=email).exists():
                messages.info(request, 'E-mail já cadastrado')
                return redirect('signup')

            #Filtrando no banco de dados e verificando se já existe um nome de usuario igual ao digitado
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Usuário já está em uso!') 
                return redirect('signup') 

            #Caso estiver correto o formulario irá criar o usuário
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.first_name = request.POST['first_name']
                user.last_name = request.POST['last_name']  
                user.save()


                #Logando usuário e sendo redirecionado para a conclusão do perfil
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)


                #Criando perfil para o novo usário
                user_model = User.objects.get(username=username, email=email)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')   
        
        #Caso a senha seja diferente da confirmação de senha, irá definir uma mensagem de erro 
        else:
            messages.info(request, 'Senha e confirmação de senha diferentes!')
            return redirect('signup')

    else:
        return render (request, 'signup.html')


#Entrar na conta
def signin(request):

    #Verificando se os dados do formulario é do tipo POST
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        #Confirmando se existe o nome de usuário e se a senha esta vinculado a ele
        user = auth.authenticate(username=username, password=password)


        #Caso não exista um usuario, será redirecionado para a home
        if user is not None:
            auth.login(request, user)
            return redirect('/')

        #Mensagem de erro por não achar o usuário ou por a senha estar incorreta
        else:   
            messages.info(request, 'Usuário e/ou senha inválidos!')
            return redirect('signin') 

    else:
        return render(request, 'signin.html')

#Sair da conta
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect(signin)

#Configurações do perfil de usuario
@login_required(login_url='signin')
def settings(request):

    #Pegando dados no banco de dados para preencher os dados do usuário
    user_profile = Profile.objects.get(user=request.user)

    #Verificando se o método do formulario é do tipo post
    if request.method == 'POST':
        
        #Verifica se a imagem de perfil não foi alterada e progride
        if request.FILES.get('profile_image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            location = request.POST['location']

            #Salvando no banco de dados
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.first_name = first_name
            user_profile.last_name = last_name
            user_profile.location = location
            user_profile.save()

        #Verifica se a foto de perfil foi alterada e progride
        if request.FILES.get('profile_image') != None:
            image = request.FILES.get('profile_image')
            bio = request.POST['bio']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            location = request.POST['location']

            #Salvando no banco de dados
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.first_name = first_name
            user_profile.last_name = last_name
            user_profile.location = location
            user_profile.save()

        return redirect('index')    
    
    
    return render(request, 'setting.html', {'user_profile': user_profile})            


#Criar o post do usuário
login_required(login_url='signin')
def upload(request):
    
    #Verificando se o formulario é do tipo POST e armazenando as informações
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        #Criando o posto do usuário
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect ('/')

    #Se o formulario não tiver feito, será redirecionado para home
    else:  
        return redirect('/')  


#Função de dar like nos posts
login_required(login_url='signin')
def like_post(request):

    #Pegando só o usuário que está dando o like
    username = request.user.username

    #Pegando o id do post do modelo criado
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)  

    #Verificar se o usuário logado deu like no post
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()    

    #Condição para a criação do like e para a contagem do like
    if like_filter == None:
               
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect ('/')

    #Para deletar o like do post
    else:
        like_filter.delete()   
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect ('/') 


#Perfil dos usuários
login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_lenght = len(user_posts)

    user_objects = User.objects.get(username=request.user.username)
    user_profiles = Profile.objects.get(user=user_object)


    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Seguir'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_lenght': user_posts_lenght,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
        'user_objects': user_objects,
        'user_profiles': user_profiles,
    }
    return render(request, 'profile.html', context)


#Seguidores
login_required(login_url='signin')
def follow(request):

    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)

        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save() 
            return redirect('/profile/'+user)
   
    else:
        return redirect ('/')    



#Pesquisa por usuario 
login_required(login_url='signin') 
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []


        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)    
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))    
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list':username_profile_list})   



#Mensagem
login_required(login_url='signin')
def message(request):
    #Pegando os dados do usuário e inserindo na home
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    return render (request, 'messages.html', {'user_profile': user_profile})
