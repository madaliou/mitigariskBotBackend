from django.core.mail import  send_mail 
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template
from .models import Test, UserProfile, UserProfileHasPack

#Taux de transformation
def conversion_rate():
    print('pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')
    contributors =  UserProfile.objects.filter(role='contributor')
    for contributor in contributors:
        prospects =  UserProfile.objects.filter(role='prospect', parent_id=contributor.id)
        clients =  UserProfile.objects.filter(role='prospect', is_client=True, parent_id=contributor.id)
        if prospects.count() >0:
            pros =  UserProfile.objects.filter(role='prospect', parent_id=contributor.id).count()
            cli =  UserProfile.objects.filter(role='prospect', is_client=True, parent_id=contributor.id).count()
            t = cli/pros
            contributor.conversionRate = t*100
            contributor.save()
        

#alert des prospect sur les les échéances
def customer_alert():
    print('pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')


    objet = 'Assurance Transvie'

    ctx = {
        'first_name': 'kk',
        'last_name': 'kk',
        'user_name': 'kk',
        'password': 'kkkkkkkkk'
    }
    message = get_template('email/mail_relance_template.html').render(ctx)
    msg = EmailMessage(
        objet,
        message,
        'agodeeli89@gmail.com',
        ['agodeeli89@gmail.com'],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()
    print("Mail envoiyé avec succès")            
   