from django.db import models
from django.conf import settings
import os
import uuid

class LogFile(models.Model):
    """Model for tracking uploaded log files"""
    LOG_TYPE_CHOICES = [
        ("aws", "AWS CloudTrail"),
        ("azure", "Azure Logs"),
        ("gcp", "Google Compute Platform"),
        ("gws", "Google Workspace"),
        ("httpd", "Apache HTTP"),
        ("kape", "KAPE Triage"),
        ("kubernetes", "Kubernetes"),
        ("microsoft365", "Microsoft 365"),
        ("nfarch", "NetFlow Archive"),
        ("passivedns", "Passive DNS"),
        ("plaso", "Plaso CSV"),
        ("syslog", "Syslog"),
        ("zeek", "Zeek Network Security"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255) # Name in the SOF-ELK directory
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)
    original_name = models.CharField(max_length=255) # Original uploaded name
    upload_date = models.DateTimeField(auto_now_add=True)
    size = models.BigIntegerField()
    year = models.IntegerField(null=True, blank=True)  # For syslog files
    status = models.CharField(max_length=20, default="pending")

    def __str__(self):
        return f"{self.original_name} ({self.log_type})"

    def get_destination_directory(self):
        """Get the destination directory path in the SOF-ELK system"""
        base_path = settings.SOF_ELK_PATHS["LOG_DIRS"][self.log_type]
        if self.log_type == "syslog" and self.year:
            return os.path.join(base_path, str(self.year))
        return base_path

    def get_full_path(self):
        """Get the full path to the file in the SOF-ELK system"""
        return os.path.join(self.get_destination_directory(), self.file_name)


class CommandExecution(models.Model):
    """Model for tracking command executions"""
    COMMAND_TYPE_CHOICES = [
        ("clear_elasticsearch", "Clear Elasticsearch"),
        ("update_sof_elk", "Update SOF-ELK"),
        ("nfdump_to_sof_elk", "Process NetFlow"),
        ("aws_vpcflow_to_sof_elk", "Process AWS VPC Flow"),
        ("azure_vpcflow_to_sof_elk", "Process Azure VPC Flow"),
        ("delete_log_files", "Delete Log Files"), # Added for tracking deletion
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    command_type = models.CharField(max_length=30, choices=COMMAND_TYPE_CHOICES)
    parameters = models.JSONField(default=dict)
    executed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.command_type} ({self.executed_at})"


class SystemStatus(models.Model):
    """Model for tracking system status"""
    timestamp = models.DateTimeField(auto_now_add=True)
    elasticsearch_status = models.CharField(max_length=20, default="unknown")
    logstash_status = models.CharField(max_length=20, default="unknown")
    kibana_status = models.CharField(max_length=20, default="unknown")
    disk_usage = models.JSONField(default=dict)
    indices_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "System statuses"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"System Status at {self.timestamp}"
