from django import forms


class OnTopRepoForm(forms.Form):
    user_name = forms.CharField(label="Username", max_length=100)
    repository_name = forms.CharField(label="Repository's name", max_length=100)
    db_name = forms.CharField(label="Database's name", max_length=100)
    db_password = forms.CharField(label="Database's password", widget=forms.PasswordInput, empty_value="",
                                  required=False)
    properties_file = forms.FileField(label=".properties file")
    obda_file = forms.FileField(label=".obda file")


class CustomRulesetForm(forms.Form):
    user_name = forms.CharField(label="Username", max_length=100)
    repository_name = forms.CharField(label="Repository's name", max_length=100)
    custom_ruleset_file = forms.FileField(label=".pie")
