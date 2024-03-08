from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import LearningForm

from .models import Learned


def show(request, learnt_id):
    learnt = Learned.objects.get(id=learnt_id)
    body = learnt.content
    title = learnt.title
    page_title = "placeholder123"
    tldr = learnt.tldr
    tags = learnt.tags
    id = learnt.id
    context = {
        "learnt_id": learnt_id,
        "learnt_title": title,
        "learnt_content": body,
        "learnt_tldr": tldr,
        "learnt_tags": tags,
        "page_title": page_title,
    }

    return render(request, template_name="til/display_learnt.html", context=context)


def landing_page(request):
    mylearnings = Learned.objects.all()
    learnt_things = [
        {"headline": x.title, "id": x.id, "tags": [1, 2, 3]} for x in mylearnings
    ]

    return render(
        request,
        "til/landing.html",
        context={"title": "ABC: Always Be Learning",
                 "learnings": learnt_things},
    )


def learning_data_entry(request, learnt_id=None):
    learnt = None
    if learnt_id != None:
        learnt = Learned.objects.get(id=learnt_id)
    if request.method == "GET":
        context = {"page_title": "Learning Data Entry Form"}
        context["learning_form"] = LearningForm(instance=learnt)
        return render(request, template_name="til/learning.html", context=context)

    if request.method == "POST":
        learning_form = LearningForm(request.POST, instance=learnt)
        if learning_form.is_valid():
            learning_form.save()
            return render(request, "til/post_thanks.html")
    return HttpResponseRedirect("")
