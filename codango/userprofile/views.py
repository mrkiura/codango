from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.utils import timezone
from account.views import LoginRequiredMixin
from userprofile.models import UserProfile, Follow
from userprofile.forms import UserProfileForm

# Create your views here.


class UserProfileDetailView(TemplateView):
    model = UserProfile
    template_name = 'userprofile/profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            self.template_name = 'account/partials/community.html'
        return super(UserProfileDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)
        username = kwargs['username']
        if self.request.user.username == username:
            user = self.request.user
        else:
            user = User.objects.get(username=username)
            if user is None:
                return Http404("User does not exist")

        try:
            follow = Follow.objects.filter(follower_id=self.request.user.id).get(followed_id=user.id)

            if follow is not None:
                context['already_following'] = True
        except:
            pass

        context['profile'] = user.profile
        context['resources'] = user.resource_set.all()
        context['title'] = "My Feed"
        # context['already_following'] = Follow.objects.get(followed_id=user.id)
        return context


class UserProfileEditView(LoginRequiredMixin, TemplateView):
    form_class = UserProfileForm
    template_name = 'userprofile/profile-edit.html'

    def get_context_data(self, **kwargs):
        context = super(UserProfileEditView, self).get_context_data(**kwargs)
        username = kwargs['username']
        if self.request.user.username == username:
            user = self.request.user
        else:
            pass

        context['profile'] = user.profile
        context['resources'] = user.resource_set.all()
        context['profileform'] = self.form_class(initial={
            'about': self.request.user.profile.about,
            'first_name': self.request.user.profile.first_name,
            'last_name': self.request.user.profile.last_name,
            'place_of_work': self.request.user.profile.place_of_work,
            'position': self.request.user.profile.position
        })
        return context

    def post(self, request, **kwargs):
        form = self.form_class(
            request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.add_message(
                request, messages.SUCCESS, 'Profile Updated!')
            return redirect(
                '/user/' + kwargs['username'],
                context_instance=RequestContext(request)
            )
        else:
            context = super(
                UserProfileEditView, self).get_context_data(**kwargs)
            context['profileform'] = self.form_class
            return render(request, self.template_name, context)


class FollowUserView(LoginRequiredMixin, View):
    def post(self, request, **kwargs):
        username = kwargs['username']
        user = User.objects.get(id=request.user.id)
        print user
        print username
        following_id = User.objects.get(username=username)
        print following_id
        follow = Follow(follower_id=user, followed_id=following_id, date_of_follow=timezone.now())
        follow.save()

        userprofile = UserProfile.objects.get(user_id=user.id)
        userprofile.following += 1
        userprofile.save()

        follower_user_profile = UserProfile.objects.get(user_id=following_id.id)
        follower_user_profile.followers += 1
        follower_user_profile.save()

        return HttpResponse(status=200)


class FollowingView(LoginRequiredMixin, TemplateView):
    template_name = 'userprofile/following.html'

    def get_context_data(self, **kwargs):
        context = super(FollowingView, self).get_context_data(**kwargs)
        username = kwargs['username']
        user_profile = UserProfile.objects.get(user_id=User.objects.get(username=username).id)
        context['followers'] = user_profile.get_following()
        context['profile'] = user_profile

        return context


class FollowersView(LoginRequiredMixin, TemplateView):

    template_name = 'userprofile/followers.html'

    def get_context_data(self, **kwargs):
        context = super(FollowersView, self).get_context_data(**kwargs)
        username = kwargs['username']
        user_profile = UserProfile.objects.get(user_id=User.objects.get(username=username).id)
        # user_profile = UserProfile.objects.get(user_id=self.request.user.id)
        context['followers'] = user_profile.get_followers()
        context['profile'] = user_profile

        return context

