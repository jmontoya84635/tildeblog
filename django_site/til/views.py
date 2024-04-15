from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login, logout
from .forms import LearningForm
from django.db import IntegrityError
from django.contrib import messages
from .models import Learned, User

from .tag_utils import TagHelper


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully", extra_tags='success')
            return HttpResponseRedirect(reverse("til:til_landing"))
        else:
            messages.error(request, "Invalid username and/or password.", extra_tags='danger')
            return render(request, "til/login.html")
    else:
        return render(request, "til/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully", extra_tags='success')
    return HttpResponseRedirect(reverse("til:til_landing"))


def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match.", extra_tags='danger')
            return render(request, "til/signup.html")
        try:
            user = User.objects.create_user(username, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.", extra_tags='danger')
            return render(request, "til/signup.html", {
                "error": "username already taken",
            })
        login(request, user)
        messages.success(request, "Account created successfully", extra_tags='success')
        return HttpResponseRedirect(reverse("til:til_landing"))
    else:
        return render(request, "til/signup.html")


def show(request, learnt_id):
    learnt = Learned.objects.get(id=learnt_id)
    body = learnt.content
    title = learnt.title
    page_title = "placeholder123"
    tldr = learnt.tldr
    tags = learnt.tags
    context = {
        "learnt_id": learnt_id,
        "learnt_title": title,
        "learnt_content": body,
        "learnt_tldr": tldr,
        "learnt_tags": tags,
        "page_title": page_title,
    }

    return render(request, template_name="til/display_learnt.html", context=context)


def landing_page(request, tagstring: str = ""):
    if request.method == "GET":
        helper = TagHelper(delim=",")
        tags = helper.split_tags(tagstring)
        filtered_flag = False
        if len(tags) > 0:
            mylearnings = helper.get_fuzzy_learnt_items_by_tag(tags[0])
            filtered_flag = True
        else:
            mylearnings = Learned.objects.all()
        learnt_things = []
        for learnt in mylearnings:
            headline = learnt.title
            tag_id = learnt.id
            tags = []
            for tag in learnt.tags.all():
                tags.append(tag.name)
            item = {"headline": headline, "id": tag_id, "tags": tags}
            learnt_things.append(item)
        return render(
            request,
            "til/landing.html",
            context={"title": "ABC: Always Be Learning", "learnings": learnt_things},
        )
    elif request.method == "POST":
        tag = request.POST.get("tag-input")
        # TODO this is happy path, handle it if we got a post with bad vals
        if len(tag.strip()) > 0:
            return HttpResponseRedirect(
                reverse("til:til_show_tagged", kwargs={"tagstring": tag})
            )
        else:
            return HttpResponseRedirect(reverse("til:til_landing"))
    else:
        raise ValueError(f"I don't understand how I got {request.method=}")


def learning_data_entry(request, learnt_id=None):
    learnt = None
    tag_string = ""
    if learnt_id is not None:
        learnt = Learned.objects.get(id=learnt_id)
        tag_helper = TagHelper(delim=",")
        tag_string = tag_helper.tags_as_delim_string(learnt.id)
    if request.method == "GET":
        context = {"page_title": "Learning Data Entry Form"}
        context["learning_form"] = LearningForm(
            instance=learnt, initial={"delimited_tag_field": tag_string}
        )
        return render(request, template_name="til/learning.html", context=context)
    if request.method == "POST":
        learning_form = LearningForm(request.POST, instance=learnt)
        if learning_form.is_valid():
            learnt_object = learning_form.save()
            delimited_tags = learning_form.cleaned_data["delimited_tag_field"].strip()
            if delimited_tags:
                helper = TagHelper(delim=",")
                helper.tags = helper.set_tags_on_learnt(
                    delimited_tags, learnt_object.id
                )
            return render(request, "til/post_thanks.html")
    return HttpResponseRedirect("")
