import subprocess
from django.shortcuts import render
from .forms import OnTopRepoForm, CustomRulesetForm
import os


def ontoprepo_view(request):
    if request.method == "POST":
        form = OnTopRepoForm(request.POST, request.FILES)
        if form.is_valid():

            user_name = form.cleaned_data['user_name']
            repository_name = form.cleaned_data["repository_name"]
            db_name = form.cleaned_data["db_name"]
            db_password = form.cleaned_data["db_password"]
            properties_file = request.FILES["properties_file"]
            obda_file = request.FILES["obda_file"]
            repo_path = f"/shared-volume/graphdb/data/repositories/{repository_name}"
            os.umask(0)
            os.makedirs(repo_path, mode=0o777, exist_ok=True)
            properties_path = repo_path + "/" + properties_file.name
            obda_path = repo_path + "/" + obda_file.name
            with open(properties_path, "wb") as f:
                for chunk in properties_file.chunks():
                    f.write(chunk)
            with open(obda_path, "wb") as f:
                for chunk in obda_file.chunks():
                    f.write(chunk)
            try:
                p = subprocess.run(
                    ["/config/python_env/bin/python", "/django/graphdbapi/create_ontop_repo.py",
                     f"{user_name}",
                     f"{repository_name}",
                     f"{db_name}",
                     f"{db_password}",
                     f"{properties_path}",
                     f"{obda_path}"],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print("Erreur lors de l'exécution du script:", e)
                if e.returncode == 3:
                    print("User not found ! Refer to your credentials !")
                    return render(request, "form/ontoprepo.html",
                                  {"form": form, "message": "User not found !", "code": "3"})
                if e.returncode == 2:
                    print("Repository already exists ! Change the name of the repository.")
                    return render(request, "form/ontoprepo.html",
                                  {"form": form, "message": "Repository already exists !", "code": "2"})
                if e.returncode == 1:
                    print("Repository creation failed due to an error !")
                    return render(request, "form/ontoprepo.html", {"form": form, "message": "Error !", "code": "1"})
                if e.returncode == 0:
                    print("Repository created !")
                    return render(request, "form/ontoprepo.html", {"form": form, "message": "Success !", "code": "0"})
            except Exception as e:
                print(e)

            return render(request, "form/ontoprepo.html", {"form": form, "message": "Success !", "code": "0"})
    else:
        form = OnTopRepoForm()

    return render(request, "form/ontoprepo.html", {"form": form, "alert": True})


def custom_ruleset_view(request):
    if request.method == "POST":
        form = CustomRulesetForm(request.POST, request.FILES)
        if form.is_valid():
            user_name = form.cleaned_data['user_name']
            repository_name = form.cleaned_data["repository_name"]
            custom_ruleset_file = request.FILES["custom_ruleset_file"]
            repo_path = f"/shared-volume/graphdb/data/repositories/{repository_name}"
            os.umask(0)
            os.makedirs(repo_path, mode=0o777, exist_ok=True)
            custom_ruleset_file_path = repo_path + "/" + custom_ruleset_file.name
            with open(custom_ruleset_file_path, "wb") as f:
                for chunk in custom_ruleset_file.chunks():
                    f.write(chunk)
            try:
                p = subprocess.run(
                    ["/config/python_env/bin/python", "/django/graphdbapi/create_repo_with_custom_ruleset.py",
                     f"{user_name}",
                     f"{repository_name}",
                     f"{custom_ruleset_file_path}"],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print("Erreur lors de l'exécution du script:", e)
                if e.returncode == 3:
                    print("User not found ! Refer to your credentials !")
                    return render(request, "form/customruleset.html",
                                  {"form": form, "message": "User not found !", "code": "3"})
                if e.returncode == 2:
                    print("Repository already exists ! Change the name of the repository.")
                    return render(request, "form/customruleset.html",
                                  {"form": form, "message": "Repository already exists !", "code": "2"})
                if e.returncode == 1:
                    print("Repository creation failed due to an error !")
                    return render(request, "form/customruleset.html", {"form": form, "message": "Error !", "code": "1"})
                if e.returncode == 0:
                    print("Repository created !")
                    return render(request, "form/customruleset.html",
                                  {"form": form, "message": "Success !", "code": "0"})
            except Exception as e:
                print(e)

            return render(request, "form/customruleset.html", {"form": form, "message": "Success !", "code": "0"})

    else:
        form = CustomRulesetForm()

    return render(request, "form/customruleset.html", {"form": form, "alert": True})
