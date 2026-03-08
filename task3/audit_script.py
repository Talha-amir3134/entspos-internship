import scanner.scanner as sc
import sys
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: audit_script.py <path>")
        print("Please provide a path!")
        sys.exit(1)
        
    project_path = sys.argv[1]
    
    files = sc.scan_directory(project_path)
    flagged_files = sc.flag_old_files(files, days=1)
    penalties = sc.calculate_penalty(flagged_files, penalty_per_day=3)

    
    report_name = "audit_report" + datetime.now().strftime("%d-%m-%Y_%H-%M")
    
    with open(report_name+".txt","w") as f:
        f.write("\tAudit Report\n")
        f.write("\nThis project contains the following flagged files along with associated penalties: \n")
        for file in penalties:
            line = f"{file["name"]} -> {file["penalty"]}\n"
            f.write(line)
        
if __name__ == "__main__":
    main()