from django import forms
from .models import LogFile

class LogFileUploadForm(forms.Form):
    """Form for uploading log files"""
    file = forms.FileField(label='Select a file')
    log_type = forms.ChoiceField(
        choices=LogFile.LOG_TYPE_CHOICES,
        label='Log Type'
    )
    year = forms.IntegerField(
        required=False,
        min_value=1970,
        max_value=2100,
        help_text='Required only for syslog files'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        log_type = cleaned_data.get('log_type')
        year = cleaned_data.get('year')
        
        if log_type == 'syslog' and not year:
            self.add_error('year', 'Year is required for syslog files')
        
        return cleaned_data


class NetFlowProcessForm(forms.Form):
    """Form for processing NetFlow data"""
    PROCESS_TYPE_CHOICES = [
        ('netflow', 'NetFlow'),
        ('aws_vpcflow', 'AWS VPC Flow'),
        ('azure_vpcflow', 'Azure VPC Flow'),
    ]
    
    file = forms.FileField(label='Select a file')
    process_type = forms.ChoiceField(
        choices=PROCESS_TYPE_CHOICES,
        label='Process Type'
    )
    exporter_ip = forms.GenericIPAddressField(
        required=False,
        help_text='Optional: IP address of the exporter (for NetFlow only)'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        process_type = cleaned_data.get('process_type')
        exporter_ip = cleaned_data.get('exporter_ip')
        
        if process_type != 'netflow' and exporter_ip:
            self.add_error('exporter_ip', 'Exporter IP is only applicable for NetFlow processing')
        
        return cleaned_data


class ElasticsearchClearForm(forms.Form):
    """Form for clearing Elasticsearch indices"""
    INDEX_CHOICES = [
        ('logstash', 'Logstash Indices'),
        ('netflow', 'NetFlow Indices'),
        ('httpdlog', 'HTTP Log Indices'),
        ('zeek', 'Zeek Indices'),
        ('all', 'All Indices'),
    ]
    
    index_name = forms.ChoiceField(
        choices=INDEX_CHOICES,
        label='Select indices to clear'
    )
    confirm = forms.BooleanField(
        label='I understand this action cannot be undone',
        required=True
    )
