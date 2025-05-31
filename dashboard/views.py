from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.urls import reverse_lazy

import os
import json
import subprocess
import shutil
from datetime import datetime
import uuid

from .models import LogFile, CommandExecution, SystemStatus
from .forms import LogFileUploadForm, NetFlowProcessForm, ElasticsearchClearForm

class DashboardView(View):
    """Main dashboard view"""
    def get(self, request):
        try:
            system_status = SystemStatus.objects.latest("timestamp")
        except SystemStatus.DoesNotExist:
            system_status = self.update_system_status()

        recent_logs = LogFile.objects.order_by("-upload_date")[:10]
        recent_commands = CommandExecution.objects.order_by("-executed_at")[:10]

        context = {
            "system_status": system_status,
            "recent_logs": recent_logs,
            "recent_commands": recent_commands,
        }
        return render(request, "dashboard/dashboard.html", context)

    def update_system_status(self):
        """Update system status by checking services"""
        system_status = SystemStatus()
        try:
            # Check Elasticsearch (example: using curl)
            es_check = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:9200"], capture_output=True, text=True, timeout=5)
            system_status.elasticsearch_status = "running" if es_check.stdout == "200" else "stopped"
        except Exception:
            system_status.elasticsearch_status = "unknown"

        try:
            # Check Logstash (example: check if process is running)
            ls_check = subprocess.run(["pgrep", "-f", "logstash"], capture_output=True, text=True)
            system_status.logstash_status = "running" if ls_check.stdout.strip() else "stopped"
        except Exception:
            system_status.logstash_status = "unknown"

        try:
            # Check Kibana (example: check if process is running)
            kb_check = subprocess.run(["pgrep", "-f", "kibana"], capture_output=True, text=True)
            system_status.kibana_status = "running" if kb_check.stdout.strip() else "stopped"
        except Exception:
            system_status.kibana_status = "unknown"

        try:
            df_process = subprocess.run(["df", "-h"], capture_output=True, text=True)
            system_status.disk_usage = {"raw": df_process.stdout}
        except Exception:
            system_status.disk_usage = {"raw": "Error getting disk usage"}

        # Get indices count (placeholder - requires Elasticsearch API access)
        system_status.indices_count = 0

        system_status.save()
        return system_status


class LogFileUploadView(View):
    """View for uploading log files"""
    def get(self, request):
        form = LogFileUploadForm()
        return render(request, "dashboard/upload_log.html", {"form": form})

    def post(self, request):
        form = LogFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            log_type = form.cleaned_data["log_type"]
            year = form.cleaned_data.get("year")
            uploaded_file = request.FILES["file"]

            # Generate a unique filename for storage to avoid conflicts
            unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"

            # Create log file record first
            log_file = LogFile(
                file_name=unique_filename, # Store the unique name
                log_type=log_type,
                original_name=uploaded_file.name,
                size=uploaded_file.size,
                year=year if log_type == "syslog" else None,
                status="processing"
            )

            # Get destination path based on log type and year
            dest_dir = log_file.get_destination_directory()
            dest_file_path = os.path.join(dest_dir, unique_filename)

            # Ensure destination directory exists
            try:
                os.makedirs(dest_dir, exist_ok=True)
                # Check write permissions before saving
                if not os.access(dest_dir, os.W_OK):
                     raise PermissionError(f"No write permission for directory: {dest_dir}")

                # Save the file directly to the destination
                fs = FileSystemStorage(location=dest_dir)
                fs.save(unique_filename, uploaded_file)

                log_file.status = "completed"
                log_file.save() # Save the model instance after successful file save
                messages.success(request, f"File 	\"{uploaded_file.name}\"	 uploaded successfully to {dest_dir}")
                return redirect("list_logs") # Redirect to the log list view

            except PermissionError as e:
                log_file.status = "failed"
                # Don't save the log_file record if permission denied before saving
                messages.error(request, f"Permission Error: {str(e)}")
            except Exception as e:
                log_file.status = "failed"
                # Attempt to clean up if file was partially saved (though unlikely with FileSystemStorage)
                if os.path.exists(dest_file_path):
                    try:
                        os.remove(dest_file_path)
                    except Exception as remove_e:
                        messages.warning(request, f"Could not clean up partially saved file: {remove_e}")
                messages.error(request, f"Error processing file: {str(e)}")

            return render(request, "dashboard/upload_log.html", {"form": form})

        return render(request, "dashboard/upload_log.html", {"form": form})


class LogFileListView(View):
    """View for listing and deleting uploaded log files"""
    def get(self, request):
        log_files = LogFile.objects.order_by("-upload_date")
        return render(request, "dashboard/list_logs.html", {"log_files": log_files})

    def post(self, request):
        file_ids_to_delete = request.POST.getlist("file_ids")
        if not file_ids_to_delete:
            messages.warning(request, "No files selected for deletion.")
            return redirect("list_logs")

        log_files_to_delete = LogFile.objects.filter(id__in=file_ids_to_delete)
        deleted_files_count = 0
        failed_files_count = 0
        deleted_file_names = []

        # Record the command execution
        command_exec = CommandExecution(
            command_type="delete_log_files",
            parameters={"file_ids": file_ids_to_delete},
            status="running"
        )
        command_exec.save()

        for log_file in log_files_to_delete:
            file_path = log_file.get_full_path()
            try:
                if os.path.exists(file_path):
                    # Check write permissions on the file before deleting
                    if not os.access(file_path, os.W_OK):
                        raise PermissionError(f"No write permission for file: {file_path}")
                    os.remove(file_path)
                    deleted_file_names.append(log_file.original_name)
                    log_file.delete() # Delete the database record
                    deleted_files_count += 1
                else:
                    # File doesn't exist on filesystem, just delete the record
                    messages.warning(request, f"File {log_file.original_name} not found at {file_path}, removing record.")
                    log_file.delete()
                    deleted_files_count += 1 # Count as deleted since record is removed
            except PermissionError as e:
                messages.error(request, f"Permission Error deleting {log_file.original_name}: {str(e)}")
                failed_files_count += 1
            except Exception as e:
                messages.error(request, f"Error deleting file {log_file.original_name}: {str(e)}")
                failed_files_count += 1

        result_message = f"Deleted {deleted_files_count} files: {', '.join(deleted_file_names)}."
        if failed_files_count > 0:
            result_message += f" Failed to delete {failed_files_count} files."
            command_exec.status = "failed"
            messages.error(request, f"Failed to delete {failed_files_count} files. Check permissions or logs.")
        else:
            command_exec.status = "completed"
            messages.success(request, f"Successfully deleted {deleted_files_count} files.")

        command_exec.result = result_message
        command_exec.save()

        return redirect("list_logs")


class NetFlowProcessView(View):
    """View for processing NetFlow data"""
    def get(self, request):
        form = NetFlowProcessForm()
        return render(request, "dashboard/process_netflow.html", {"form": form})

    def post(self, request):
        form = NetFlowProcessForm(request.POST, request.FILES)
        if form.is_valid():
            process_type = form.cleaned_data["process_type"]
            exporter_ip = form.cleaned_data.get("exporter_ip")
            uploaded_file = request.FILES["file"]

            # Use a temporary directory for processing
            temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_processing")
            os.makedirs(temp_dir, exist_ok=True)
            fs = FileSystemStorage(location=temp_dir)
            temp_filename = fs.save(uploaded_file.name, uploaded_file)
            temp_file_path = fs.path(temp_filename)

            output_filename = f'{process_type}_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
            output_dir = settings.SOF_ELK_PATHS["LOG_DIRS"]["nfarch"]
            output_path = os.path.join(output_dir, output_filename)
            os.makedirs(output_dir, exist_ok=True)

            command_map = {
                "netflow": ("nfdump_to_sof_elk", settings.SOF_ELK_PATHS["COMMANDS"]["nfdump_to_sof_elk"]),
                "aws_vpcflow": ("aws_vpcflow_to_sof_elk", settings.SOF_ELK_PATHS["COMMANDS"]["aws_vpcflow_to_sof_elk"]),
                "azure_vpcflow": ("azure_vpcflow_to_sof_elk", settings.SOF_ELK_PATHS["COMMANDS"]["azure_vpcflow_to_sof_elk"]),
            }

            command_type, command_script = command_map[process_type]
            command = [command_script, "-r", temp_file_path]
            if process_type == "netflow" and exporter_ip:
                command.extend(["-e", exporter_ip])
            command.extend(["-w", output_path])

            command_exec = CommandExecution(
                command_type=command_type,
                parameters={
                    "input_file": temp_file_path,
                    "output_file": output_path,
                    "exporter_ip": exporter_ip if exporter_ip else None
                },
                status="running"
            )
            command_exec.save()

            try:
                # Ensure the output directory is writable
                if not os.access(output_dir, os.W_OK):
                    raise PermissionError(f"No write permission for directory: {output_dir}")

                process = subprocess.run(command, capture_output=True, text=True, check=True)
                command_exec.result = process.stdout
                command_exec.status = "completed"
                messages.success(request, f"Successfully processed {process_type} data into {output_path}")
            except PermissionError as e:
                command_exec.result = str(e)
                command_exec.status = "failed"
                messages.error(request, f"Permission Error processing {process_type} data: {str(e)}")
            except subprocess.CalledProcessError as e:
                command_exec.result = e.stderr
                command_exec.status = "failed"
                messages.error(request, f"Error processing {process_type} data: {e.stderr}")
            except Exception as e:
                command_exec.result = str(e)
                command_exec.status = "failed"
                messages.error(request, f"An unexpected error occurred: {str(e)}")

            command_exec.save()

            # Clean up temporary file
            try:
                os.remove(temp_file_path)
            except Exception as remove_e:
                 messages.warning(request, f"Could not clean up temporary file: {remove_e}")

            return redirect("dashboard")

        return render(request, "dashboard/process_netflow.html", {"form": form})


class ElasticsearchClearView(View):
    """View for clearing Elasticsearch indices"""
    def get(self, request):
        form = ElasticsearchClearForm()
        return render(request, "dashboard/clear_elasticsearch.html", {"form": form})

    def post(self, request):
        form = ElasticsearchClearForm(request.POST)
        if form.is_valid():
            index_name = form.cleaned_data["index_name"]

            command_exec = CommandExecution(
                command_type="clear_elasticsearch",
                parameters={"index_name": index_name},
                status="running"
            )
            command_exec.save()

            command = [
                settings.SOF_ELK_PATHS["COMMANDS"]["clear_elasticsearch"],
                "-i", index_name
            ]

            try:
                # This command likely needs sudo, but we assume it's configured or run as root for now
                process = subprocess.run(command, capture_output=True, text=True, check=True)
                command_exec.result = process.stdout
                command_exec.status = "completed"
                messages.success(request, f"Successfully cleared {index_name} indices")
            except subprocess.CalledProcessError as e:
                command_exec.result = e.stderr
                command_exec.status = "failed"
                messages.error(request, f"Error clearing indices: {e.stderr}. Ensure the command has permissions.")
            except FileNotFoundError:
                 command_exec.result = "Command not found: sof-elk_clear.py"
                 command_exec.status = "failed"
                 messages.error(request, "Error: sof-elk_clear.py command not found. Is it in the system PATH?")
            except Exception as e:
                command_exec.result = str(e)
                command_exec.status = "failed"
                messages.error(request, f"An unexpected error occurred: {str(e)}")

            command_exec.save()

            return redirect("dashboard")

        return render(request, "dashboard/clear_elasticsearch.html", {"form": form})


class SOFELKUpdateView(View):
    """View for updating SOF-ELK configuration"""
    def get(self, request):
        return render(request, "dashboard/update_sof_elk.html")

    def post(self, request):
        command_exec = CommandExecution(
            command_type="update_sof_elk",
            parameters={},
            status="running"
        )
        command_exec.save()

        # Execute command with sudo - requires passwordless sudo for the web server user
        command = [
            "sudo",
            settings.SOF_ELK_PATHS["COMMANDS"]["update_sof_elk"]
        ]

        try:
            process = subprocess.run(command, capture_output=True, text=True, check=True)
            command_exec.result = process.stdout
            command_exec.status = "completed"
            messages.success(request, "Successfully updated SOF-ELK configuration")
        except subprocess.CalledProcessError as e:
            command_exec.result = e.stderr
            command_exec.status = "failed"
            messages.error(request, f"Error updating SOF-ELK: {e.stderr}. Ensure passwordless sudo is configured for the web server user.")
        except FileNotFoundError:
             command_exec.result = "Command not found: sudo or sof-elk_update.sh"
             command_exec.status = "failed"
             messages.error(request, "Error: sudo or sof-elk_update.sh command not found.")
        except Exception as e:
            command_exec.result = str(e)
            command_exec.status = "failed"
            messages.error(request, f"An unexpected error occurred: {str(e)}")

        command_exec.save()

        return redirect("dashboard")


class SystemStatusView(View):
    """View for checking system status"""
    def get(self, request):
        system_status = DashboardView().update_system_status()
        return render(request, "dashboard/system_status.html", {"system_status": system_status})


class APISystemStatusView(View):
    """API view for system status updates"""
    def get(self, request):
        system_status = DashboardView().update_system_status()
        return JsonResponse({
            "elasticsearch": system_status.elasticsearch_status,
            "logstash": system_status.logstash_status,
            "kibana": system_status.kibana_status,
            "indices_count": system_status.indices_count,
            "updated_at": system_status.timestamp.isoformat()
        })
