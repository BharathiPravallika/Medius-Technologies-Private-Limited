from django import forms
class FileUploadForm(forms.Form):
    file = forms.FileField(label="Select an Excel/CSV file")