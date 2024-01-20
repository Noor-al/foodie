from django.core.exceptions import ValidationError
import os

def allow_only_images_validators(value):
    ext = os.path.splitext(value.name)[1] #image.jpg
    valid_extentions = ['.jpg', 'png', 'jpeg']
    if not ext.lower() in valid_extentions:
        raise ValidationError('invalid file type, allowed extensions: '+str(valid_extentions))