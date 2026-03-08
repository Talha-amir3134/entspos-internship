import os
from datetime import datetime, timedelta

def scan_directory(path):
    
    files_data = []
    
    for root, dir, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                stats = os.stat(file_path)
                file_info = {
                    "name" : file,
                    "path" : file_path,
                    "size" : stats.st_size,
                    "type" : os.path.splitext(file)[1],
                    "last_modified" : datetime.fromtimestamp(stats.st_mtime)
                }
                
                files_data.append(file_info)
            except Exception:
                continue
            
    return files_data

def flag_old_files(files_data, days):

    flagged = []
    
    threshold = datetime.now() - timedelta(days=days)
    
    for file in files_data:
        if file["last_modified"] < threshold:
            flagged.append(file)
            
    return flagged

def calculate_penalty(flagged_files, penalty_per_day):
    penalties = []
    now = datetime.now()
    
    for file in flagged_files:
        days_overdue = (now - file["last_modified"]).days 
        fine = days_overdue * penalty_per_day
        
        penalties.append({
                "name" : file["name"],
                "penalty" : fine})       
        
    return penalties
    