import os
import csv


folder_path = "files"  
output_file = "clean_results.csv"

clean_results = []


for filename in os.listdir(folder_path):
    
    if not filename.endswith(".csv"):
        continue

    file_path = os.path.join(folder_path,filename)

    try:
        with open(file_path, "r") as f:
            reader = csv.reader(f)
            
            for row in reader:
                try:
                    name = row[0]
                    marks = float(row[1])
                    
                    if marks < 50:
                        status = "fail"
                    else:
                        status = "pass"
                    
                    clean_results.append((name,marks,status))
                    
                except ValueError:
                    print(f"Ïnvalid marks in {filename}")
                except KeyError:
                    print(f"Invalid column in {filename}")

    except FileNotFoundError:
        print(f"{filename} not found!")
    except Exception as e:
        print(f"Error reading {filename} : {e}")
        
with open("cleaned_result.csv", "w") as f:
    writer = csv.writer(f) 
    writer.writerow(["name","marks","status"])
    
    for result in clean_results:
        writer.writerow(result)