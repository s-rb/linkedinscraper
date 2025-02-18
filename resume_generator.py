import yaml
from datetime import datetime

def get_education_additional(edu_additional):
    if edu_additional is not None and edu_additional != "":
        return f" {edu_additional},"
    return ""

def generate_resume(cv_data):
    resume = []

    # Add name and job title
    resume.append(f"Name: {cv_data['name']}")
    resume.append(f"Job title: {cv_data['job-title']}\n")

    # Add description
    resume.append("Description:")
    for desc in cv_data['description']:
        resume.append(f"- {desc}")
    resume.append("")  # Empty line for separation

    # Add core competencies
    resume.append("Core competencies:")
    competencies = [comp.replace('&nbsp;', ' ') for comp in cv_data['core-competencies']]
    
    # Calculate the maximum length of competencies
    max_length = max(len(comp) for comp in competencies)
    
    # Format competencies into rows of 5
    for i in range(0, len(competencies), 5):
        row = competencies[i:i + 5]
        formatted_row = " | ".join(f"{comp:<{max_length + 0}}" for comp in row)
        resume.append(formatted_row)
    resume.append("\n")  # Empty line for separation

    # Add work experience
    resume.append("Experience:")
    for exp in cv_data['experience']:
        finished_date = get_finished_date(exp['period'])
        duration = calculate_duration(exp['period']['started'], finished_date)
        resume.append(f"{exp['position']} at {exp['company']}")
        resume.append(f"{duration} - ({exp['period']['started']} - {finished_date})")
        for desc in exp['description']:
            resume.append(f"  - {desc}")
        resume.append("")
    for eng_exp in cv_data['engineering_experience']:
        finished_date = get_finished_date(eng_exp['period'])
        duration = calculate_duration(eng_exp['period']['started'], finished_date)
        resume.append(f"{eng_exp['position']} at {eng_exp['company']}")
        resume.append(f"{duration} - ({eng_exp['period']['started']} - {finished_date})")
        for desc in eng_exp['description']:
            resume.append(f"  - {desc}")
    resume.append("\n")  # Empty line for separation

    # Add education
    resume.append("Education:")
    for edu in cv_data['education']:
        resume.append(f"{edu['qualification']} at {edu['company']},{get_education_additional(edu.get('additional'))} - {edu['period']}")
    resume.append("\n")  # Empty line for separation

    # Add certifications
    resume.append("Certifications:")
    for cert in cv_data['certifications']:
        resume.append(f"{get_date(cert)}: {cert['name']} from {cert['company']}{get_date_range(cert)}")
    resume.append("")  # Empty line for separation

    return "\n".join(resume)


def get_finished_date(exp):
    finished_date = exp.get('finished')
    if finished_date is not None and finished_date != '': return finished_date
    return 'present time'


def get_date_range(cert):
    cert_date = cert.get('date')
    if cert_date is None or cert_date == '':
        return f", {cert['dateStart']} - {cert['dateEnd']}"
    return ""

def get_date(cert):
    cert_date = cert.get('date')
    if cert_date is not None and cert_date != '':
        return cert_date
    return cert['dateEnd']


def calculate_duration(started, finished):
    # Convert strings to datetime objects
    start_date = datetime.strptime(started, '%m.%Y')
    if finished == 'present time':
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(finished, '%m.%Y')

    # Calculate the difference
    delta = end_date - start_date
    years, months = divmod(delta.days // 30, 12)
    return f"{years}y {months}m"

# todo выкачивать данные для резюме из центрального хранилища (blog / site) и заменять тут
# настроить джобу для сборки и скрипта
# https://github.com/s-rb/site/blob/master/_data/cv_data.yml
def get_resume():
    with open('default_cv_data.yml', 'r', encoding='utf-8') as file:
        cv_data = yaml.safe_load(file)  # Load data from file

    return generate_resume(cv_data)


if __name__ == '__main__':
    print(get_resume())