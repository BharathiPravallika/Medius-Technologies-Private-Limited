import pandas as pd
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from .forms import FileUploadForm
import os

# Create your views here.
def file_upload_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)

            #Read the uploaded file using pandas
            if filename.endswith('.xlsx'):
                file_path = os.path.join(settings.MEDIA_ROOT, filename)
                df = pd.read_excel(file_path)
            elif filename.endswith('.csv'):
                file_path = os.path.join(settings.MEDIA_ROOT, filename)
                df = pd.read_csv(file_path)
            else:
                return render(request, 'DevTest/upload.html', {'form': form, 'error': 'Invalid file format.'})
            
            #Prepare summary report by counting occurences of (Cust State, Cust Pin)
            summary = df.groupby(['Cust State', 'Cust Pin']).size().reset_index(name='DPD')
            # summary = df.groupby(['Cust State', 'Cust Pin']).agg(
            #     DPD = ('DPD', 'nunique') #Count unique DPDs for each group
            # ).reset_index()


            #Format the summary for email
            summary_str = summary.to_string(index=False)

            #Send email with the summary report
            send_email_with_summary(summary_str)

            return render(request, 'DevTest/upload_success.html', {'file_name': file.name, 'file_url': file_url, 'summary': summary_str})
        
            # #Saving or processing the file
            # return render(request, 'DevTest/upload_success.html', {'file_name': file.name})
        else:
            return render(request, 'DevTest/upload.html', {'form': form, 'error': 'Invalid file format.'})
    else:
        form = FileUploadForm()
    return render(request, 'DevTest/upload.html', {'form': form})

def send_email_with_summary(summary_str):
    subject = "Python Assignment - Bharathi Pravallika"
    message = f"Dear Team,\n\nPlease find the summary report below:\n\n{summary_str}\n\nBest Regards, \nBharathi Pravallika"
    from_email = settings.EMAIL_HOST_USER
    # recipient_list = ['tech@themedius.ai']
    recipient_list = ['tech@themedius.ai']
    send_mail(subject, message, from_email, recipient_list)
