from logging import warning, debug

import requests
import json
import sqlite3
import sys
from sqlite3 import Error
from bs4 import BeautifulSoup
import time as tm
from itertools import groupby
from datetime import datetime, timedelta, time
import pandas as pd
from urllib.parse import quote

from google.api_core.exceptions import ResourceExhausted
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from fake_useragent import UserAgent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from pdfminer.high_level import extract_text

from resume_generator import get_resume

NOT_FIND_JOB_DESCRIPTION = "Could not find Job Description"

JOBS_FILTERED_CSV = 'linkedin_jobs_filtered.csv'
LINKEDIN_JOBS_CSV = 'linkedin_jobs.csv'
TEMP_LINKEDIN_JOBS_CSV = 'temp_linkedin_jobs.csv'

ua = UserAgent(browsers=['Safari', 'Chrome', 'Firefox'], os=["Windows", "Ubuntu", "Mac OS X", "Android", "iOS"])

def load_config(file_name):
    # Load the config file
    with open(file_name) as f:
        return json.load(f)


proxy_list = load_config('proxies.json')
config = load_config('config.json')

llm_model = config["LLM_MODEL"]
llm_api_key = config["LLM_API_KEY"]  # Get API key from environment

chat = ChatGoogleGenerativeAI(
    api_key=llm_api_key,
    model=llm_model,
    temperature=0,
    max_tokens=None,
    timeout=10.0,
    max_retries=2)  # Initialize with the new API key

CONFIG_DB_PATH = config["db_path"]
DB_PATH = f"{CONFIG_DB_PATH}"

resume = get_resume()


def get_with_proxy(url):
    proxies = proxy_list

    for proxy in proxies:
        http_proxy = {"http": f"http://{proxy['ip_address']}:{proxy['port']}"}
        https_proxy = {"https": f"https://{proxy['ip_address']}:{proxy['port']}"}
        headers_ua = {**config['headers'], "User-Agent": ua.random}

        # Try HTTP request
        try:
            r = requests.get(url, headers=headers_ua, proxies=http_proxy, timeout=10)
            r.raise_for_status()  # Raise an error for bad responses
            return r  # Return the response if successful
        except requests.exceptions.RequestException as e:
            print(f"HTTP request failed with proxy {http_proxy}: {e}")

        # Try HTTPS request
        try:
            r = requests.get(url, headers=headers_ua,proxies=https_proxy,timeout=10)
            r.raise_for_status()  # Raise an error for bad responses
            return r  # Return the response if successful
        except requests.exceptions.RequestException as e:
            print(f"HTTPS request failed with proxy {https_proxy}: {e}")

    # If all proxies are exhausted, raise an error
    raise Exception("All proxies failed")



def get_with_retry(url, retries=3, delay=2):
    # Get the URL with retries and delay
    for i in range(retries):
        try:
            if len(proxy_list) > 0:
                r = get_with_proxy(url)
            else:
                r = requests.get(url, headers={**config['headers'], "User-Agent": ua.random}, timeout=5)
            return BeautifulSoup(r.content, 'html.parser')
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for URL: {url}, retrying in {delay}s...")
            tm.sleep(delay)
        except Exception as e:
            print(f"An error occurred while retrieving the URL: {url}, error: {e}")
    return None

def transform(soup):
    # Parsing the job card info (title, company, location, date, job_url) from the beautiful soup object
    joblist = []
    try:
        divs = soup.find_all('div', class_='base-search-card__info')
    except:
        print("Empty page, no jobs found")
        return joblist
    for item in divs:
        title = item.find('h3').text.strip()
        company = item.find('a', class_='hidden-nested-link')
        location = item.find('span', class_='job-search-card__location')
        parent_div = item.parent
        entity_urn = parent_div['data-entity-urn']
        job_posting_id = entity_urn.split(':')[-1]
        job_url = 'http://www.linkedin.com/jobs/view/'+job_posting_id+'/'

        date_tag_new = item.find('time', class_ = 'job-search-card__listdate--new')
        date_tag = item.find('time', class_='job-search-card__listdate')
        date = date_tag['datetime'] if date_tag else date_tag_new['datetime'] if date_tag_new else ''
        job_description = ''
        job = {
            'title': title,
            'company': company.text.strip().replace('\n', ' ') if company else '',
            'location': location.text.strip() if location else '',
            'date': date,
            'job_url': job_url,
            'job_description': job_description,
            'applied': 0,
            'hidden': 0,
            'interview': 0,
            'rejected': 0
        }
        joblist.append(job)
    return joblist

def transform_job_id(soup):
    div = soup.find('div', id='job-details')
    if div:
        return prepare_description(div)
    else:
        return NOT_FIND_JOB_DESCRIPTION


def prepare_description(soup):
    # Удаляем ненужные теги, если необходимо
    for script in soup(["script", "style"]):  # Удаляем скрипты и стили
        script.decompose()

    # Обрабатываем текст, сохраняя форматирование
    text = []
    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'li']):
        if element.name in ['p', 'h1', 'h2', 'h3']:
            # Извлекаем текст
            paragraph_text = element.get_text(strip=True)
            # Добавляем пробелы вокруг текста, заключенного в strong и b
            for sub_element in element.find_all(['strong', 'b']):
                paragraph_text = paragraph_text.replace(sub_element.get_text(strip=True), f" {sub_element.get_text(strip=True)} ")
            text.append(paragraph_text)
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                # Извлекаем текст
                list_item_text = li.get_text(strip=True)
                # Добавляем пробелы вокруг текста, заключенного в strong и b
                for sub_element in li.find_all(['strong', 'b']):
                    list_item_text = list_item_text.replace(sub_element.get_text(strip=True), f" {sub_element.get_text(strip=True)} ")
                text.append(f"- {list_item_text}")  # Сохраняем списки с маркерами

    return '\n'.join(text)

# def prepare_description(html_content):
#     # Удаляем ненужные теги, если необходимо
#     for script in html_content(["script", "style"]):  # Удаляем скрипты и стили
#         script.decompose()
#
#     # Обрабатываем текст, сохраняя форматирование
#     text = []
#     for element in html_content.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'li']):
#         if element.name in ['p', 'h1', 'h2', 'h3']:
#             # Обрабатываем текст внутри strong и b
#             for sub_element in element.find_all(['strong', 'b']):
#                 sub_element.insert_before(' ')  # Добавляем пробел перед strong/b
#                 sub_element.insert_after(' ')   # Добавляем пробел после strong/b
#             text.append(element.get_text(strip=True))
#         elif element.name in ['ul', 'ol']:
#             for li in element.find_all('li'):
#                 # Обрабатываем текст внутри strong и b
#                 for sub_element in li.find_all(['strong', 'b']):
#                     sub_element.insert_before(' ')  # Добавляем пробел перед strong/b
#                     sub_element.insert_after(' ')   # Добавляем пробел после strong/b
#                 text.append(f"- {li.get_text(strip=True)}")  # Сохраняем списки с маркерами
#
#     return '\n'.join(text)

# def prepare_description(div):
#     # Remove unwanted elements
#     for element in div.find_all(['span', 'a']):
#         element.decompose()
#     # Replace bullet points
#     for ul in div.find_all('ul'):
#         for li in ul.find_all('li'):
#             li.insert(0, '-')
#     text = div.get_text(separator='\n').strip()
#     text = text.replace('\n\n', '')
#     text = text.replace('::marker', '-')
#     text = text.replace('-\n', '- ')
#     text = text.replace('Show less', '').replace('Show more', '')
#     return text


def transform_job(soup):
    div = soup.find('div', class_='description__text description__text--rich')
    if div:
        return prepare_description(div)
    else:
        return NOT_FIND_JOB_DESCRIPTION

def safe_detect(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'en'

def filter_jobs_keywords(joblist):
    new_joblist = []
    count = 1
    for job in joblist:
        print(f"- {count} of {len(joblist)}: checking if job matches keywords")
        count += 1
        if has_keywords(job): new_joblist.append(job)
    return new_joblist

def filter_jobs_ai(joblist):
    new_joblist = []
    count = 1
    for job in joblist:
        print(f"- {count} of {len(joblist)}: checking if ai matches the job")
        count += 1
        if is_job_fits_conditions(f"{job['title']}\n{job['job_description']}"): new_joblist.append(job)
    return new_joblist

def has_keywords(job):
    if len(config['desc_words']) and not any(word.lower() in job['job_description'].lower() for word in config['desc_words']): return False
    if len(config['title_exclude']) > 0 and any(word.lower() in job['title'].lower() for word in config['title_exclude']): return False
    if len(config['title_include']) > 0 and not any(word.lower() in job['title'].lower() for word in config['title_include']): return False
    return True

def remove_duplicates(joblist):
    # Remove duplicate jobs in the joblist. Duplicate is defined as having the same title and company.
    joblist.sort(key=lambda x: (x['title'], x['company']))
    joblist = [next(g) for k, g in groupby(joblist, key=lambda x: (x['title'], x['company']))]
    return joblist

def convert_date_format(date_string):
    """
    Converts a date string to a date object. 
    
    Args:
        date_string (str): The date in string format.

    Returns:
        date: The converted date object, or None if conversion failed.
    """
    date_format = "%Y-%m-%d"
    try:
        job_date = datetime.strptime(date_string, date_format).date()
        return job_date
    except ValueError:
        print(f"Error: The date for job {date_string} - is not in the correct format.")
        return None

def create_connection():
    # Create a database connection to a SQLite database
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH) # creates a SQL database in the 'data' directory
    except Error as e:
        print(e)

    return conn

def create_table(conn, df, table_name):
    """
    # Create a new table with the data from the dataframe
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print (f"Created the {table_name} table and added {len(df)} records")
    """
    # Create a new table with the data from the DataFrame
    # Prepare data types mapping from pandas to SQLite
    type_mapping = {
        'int64': 'INTEGER',
        'float64': 'REAL',
        'datetime64[ns]': 'TIMESTAMP',
        'object': 'TEXT',
        'bool': 'INTEGER'
    }
    
    # Prepare a string with column names and their types
    columns_with_types = ', '.join(
        f'"{column}" {type_mapping[str(df.dtypes[column])]}'
        for column in df.columns
    )
    
    # Prepare SQL query to create a new table
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns_with_types}
        );
    """
    
    # Execute SQL query
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    
    # Commit the transaction
    conn.commit()

    # Insert DataFrame records one by one
    insert_sql = f"""
        INSERT INTO "{table_name}" ({', '.join(f'"{column}"' for column in df.columns)})
        VALUES ({', '.join(['?' for _ in df.columns])})
    """
    for record in df.to_dict(orient='records'):
        cursor.execute(insert_sql, list(record.values()))
    
    # Commit the transaction
    conn.commit()

    print(f"Created the {table_name} table and added {len(df)} records")

def update_table(conn, df, table_name):
    # Update the existing table with new records.
    df_existing = pd.read_sql(f'select * from {table_name}', conn)

    # Create a dataframe with unique records in df that are not in df_existing
    df_new_records = pd.concat([df, df_existing, df_existing]).drop_duplicates(['title', 'company', 'date'], keep=False)

    # If there are new records, append them to the existing table
    if len(df_new_records) > 0:
        df_new_records.to_sql(table_name, conn, if_exists='append', index=False)
        print (f"Added {len(df_new_records)} new records to the {table_name} table")
    else:
        print (f"No new records to add to the {table_name} table")

def table_exists(conn, table_name):
    # Check if the table already exists in the database
    cur = conn.cursor()
    cur.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if cur.fetchone()[0]==1 :
        return True
    return False

def job_exists(df, job):
    # Check if the job already exists in the datafraDB_PATHme
    if df.empty:
        return False
    #return ((df['title'] == job['title']) & (df['company'] == job['company']) & (df['date'] == job['date'])).any()
    #The job exists if there's already a job in the database that has the same URL
    return ((df['job_url'] == job['job_url']).any() | (((df['title'] == job['title']) & (df['company'] == job['company']) & (df['date'] == job['date'])).any()))

def get_jobcards():
    # Function to get the job cards from the search results page
    all_jobs = []
    for k in range(0, config['rounds']):
        for query in config['search_queries']:
            keywords = quote(query['keywords'])  # URL encode the keywords
            location = quote(query['location'])  # URL encode the location
            is_remote = query['f_WT'] == "2"
            for i in range(0, config['pages_to_scrape']):
                url = f"http://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&f_TPR=&f_WT={query['f_WT']}&geoId=&f_TPR={config['timespan']}&start={25*i}"
                soup = get_with_retry(url)
                jobs = []
                transformed = transform(soup)
                for job in transformed:
                    job = {**job, "is_remote": is_remote}
                    jobs.append(job)
                all_jobs = all_jobs + jobs
                print("Finished scraping page: ", url)
                
                # Pause between requests
                tm.sleep(config['request_pause'] / 1000)  # Convert milliseconds to seconds
    print("=> Total job cards scraped: ", len(all_jobs))
    all_jobs = remove_duplicates(all_jobs)
    print("=> Total job cards after removing duplicates: ", len(all_jobs))
    return all_jobs

def find_new_jobs(all_jobs, conn):
    # From all_jobs, find the jobs that are not already in the database. Function checks both the jobs and filtered_jobs tables.
    jobs_tablename = config['jobs_tablename']
    filtered_jobs_tablename = config['filtered_jobs_tablename']
    jobs_db = pd.DataFrame()
    filtered_jobs_db = pd.DataFrame()    
    if conn is not None:
        if table_exists(conn, jobs_tablename):
            query = f"SELECT * FROM {jobs_tablename}"
            jobs_db = pd.read_sql_query(query, conn)
        if table_exists(conn, filtered_jobs_tablename):
            query = f"SELECT * FROM {filtered_jobs_tablename}"
            filtered_jobs_db = pd.read_sql_query(query, conn)

    new_joblist = [job for job in all_jobs if not job_exists(jobs_db, job) and not job_exists(filtered_jobs_db, job)]
    return new_joblist


def is_job_fits_resume(job_description):
    """
    Check if the job description is suitable for the given resume using the chat bot.

    Args:
        job_description (str): The job description text.
        resume (str): The resume text.

    Returns:
        bool: True if the job is suitable, False otherwise.
    """
    # Check if LLM_API_KEY is empty
    if not llm_api_key:
        print("Error: LLM_API_KEY is empty.")
        return False

    user_prompt = (f"Job Description: {job_description}\n\n"
                   f"Resume: {resume}")
    messages = [
        ("system", f"You are a career coach with over 15 years of experience helping job seekers land their dream jobs in tech. "
                   f"Based on the following job description and resume, "
                   f"please respond with only 'true' if the resume is suitable for the job, or 'false' otherwise."
                   f"Keep in mind, that main programming language is critical, but other technologies are secondary and "
                   f"I might don't have them in my resume, but I could know them anyway"),
        ("human", user_prompt)
    ]

    try:
        completion = call_chat(messages)
        response = completion.content.strip().lower()
        return response == 'true'
    except ResourceExhausted as ex:
        print(f"Retryable error when calling Gemini: {ex}")
        tm.sleep(30)
        try:
            completion = call_chat(messages)
            response = completion.content.strip().lower()
            return response == 'true'
        except Exception as ex:
            print(f"Error connecting to Gemini: {ex}")
            return False
    except Exception as e:
        print(f"Error connecting to Gemini: {e}")
        return False
    finally:
        tm.sleep(5000 / 1000) # 15 requests per second


def is_job_fits_conditions(job_description):
    if not llm_api_key:
        print("Error: LLM_API_KEY is empty.")
        return False

    user_prompt = (f"Job Description: {job_description}\n\n"
                   f"Conditions:"
                   f"- job description language: {config['languages']},"
                   f"- job keywords expected (not all of them are mandatory, but it would be nice to have): {config['title_include']}")
    messages = [
        ("system", f"You are a career coach with over 15 years of experience helping job seekers land their dream jobs in tech. "
                   f"Based on the following job description and conditions, "
                   f"please respond with only 'true' if the the job meets the conditions, or 'false' otherwise."
                   f"Keep in mind that the programming language and the language of the job description are critical conditions."
                   f"Other technologies are not critical"),
        ("human", user_prompt)
    ]

    try:
        completion = call_chat(messages)
        response = completion.content.strip().lower()
        return response == 'true'
    except ResourceExhausted as ex:
        print(f"Retryable error when calling Gemini: {ex}")
        tm.sleep(30)
        try:
            completion = call_chat(messages)
            response = completion.content.strip().lower()
            return response == 'true'
        except Exception as ex:
            print(f"Exception when calling Gemini: {ex}")
            return False
    except Exception as e:
        print(f"Error connecting to Gemini: {e}")
        return False
    finally:
        tm.sleep(5000 / 1000) # 15 requests per minute max


def call_chat(messages):
    completion = chat.invoke(messages)
    return completion


def main():
    start_time = tm.perf_counter()
    job_list = []

    jobs_tablename = config['jobs_tablename'] # name of the table to store the "approved" jobs
    filtered_jobs_tablename = config['filtered_jobs_tablename'] # name of the table to store the jobs that have been filtered out based on description keywords (so that in future they are not scraped again)
    #Scrape search results page and get job cards. This step might take a while based on the number of pages and search queries.
    conn = create_connection()

    process_temp_csv_jobs(conn, filtered_jobs_tablename, jobs_tablename)

    all_jobs = get_jobcards()
    #filtering out jobs that are already in the database
    all_jobs = find_new_jobs(all_jobs, conn)
    print ("Total new jobs found after comparing to the database: ", len(all_jobs))

    if len(all_jobs) > 0:
        save_jobs(all_jobs, conn, filtered_jobs_tablename, job_list, jobs_tablename)
    else:
        print("No jobs found")
    
    end_time = tm.perf_counter()
    print(f"Scraping finished in {end_time - start_time:.2f} seconds")


def save_jobs(all_jobs, conn, filtered_jobs_tablename, job_list, jobs_tablename):
    jobs_to_add = get_jobs_to_add(all_jobs, job_list)
    df = pd.DataFrame(jobs_to_add)
    df['date_loaded'] = datetime.now()
    df['date_loaded'] = df['date_loaded'].astype(str)

    df.to_csv(TEMP_LINKEDIN_JOBS_CSV, index=False, encoding='utf-8')

    process_temp_csv_jobs(conn, filtered_jobs_tablename, jobs_tablename)


def process_temp_csv_jobs(conn, filtered_jobs_tablename, jobs_tablename):
    if not os.path.exists(TEMP_LINKEDIN_JOBS_CSV): return
    # Данные сохранены, теперь надо обработать нерелевантные и сохранить окончательно только подходящие
    # Загрузка данных из CSV файла
    job_list = pd.read_csv(TEMP_LINKEDIN_JOBS_CSV, encoding='utf-8').to_dict('records')
    jobs_to_add = filter_jobs_keywords(job_list)
    # Create a list for jobs removed based on job description keywords - they will be added to the filtered_jobs table
    filtered_list = [job for job in job_list if job not in jobs_to_add]
    df = pd.DataFrame(jobs_to_add)
    df_filtered = pd.DataFrame(filtered_list)
    df_filtered['date_loaded'] = datetime.now()
    df_filtered['date_loaded'] = df_filtered['date_loaded'].astype(str)
    if conn is not None:
        save_data_to_db(conn, df, df_filtered, filtered_jobs_tablename, jobs_tablename)
    else:
        print("Error! cannot create the database connection.")
    df.to_csv(LINKEDIN_JOBS_CSV, index=False, encoding='utf-8')
    df_filtered.to_csv(JOBS_FILTERED_CSV, index=False, encoding='utf-8')
    # Удаление временного файла, если он существует
    if os.path.exists(TEMP_LINKEDIN_JOBS_CSV): os.remove(TEMP_LINKEDIN_JOBS_CSV)


def save_data_to_db(conn, df, df_filtered, filtered_jobs_tablename, jobs_tablename):
    # Update or Create the database table for the job list
    if table_exists(conn, jobs_tablename):
        update_table(conn, df, jobs_tablename)
    else:
        create_table(conn, df, jobs_tablename)
    # Update or Create the database table for the filtered out jobs
    if table_exists(conn, filtered_jobs_tablename):
        update_table(conn, df_filtered, filtered_jobs_tablename)
    else:
        create_table(conn, df_filtered, filtered_jobs_tablename)


def get_jobs_to_add(all_jobs, job_list):
    for job in all_jobs:
        job_date = convert_date_format(job['date'])
        job_date = datetime.combine(job_date, time())
        # if job is older than days_to_scrape, skip it
        if job_date < datetime.now() - timedelta(days=config['days_to_scrape']):
            continue
        print('Found new job: ', job['title'], 'at ', job['company'], job['job_url'])
        job['job_description'] = get_job_description(job['job_url'])
        language = safe_detect(job['job_description'])
        if language not in config['languages']:
            print('Job description language not supported: ', language)
            # continue
        job_list.append(job)
    # Final check - removing jobs based on job description keywords words from the config file
    jobs_to_add = filter_jobs_ai(job_list)
    print("Total jobs to add: ", len(jobs_to_add))
    return jobs_to_add


def get_job_description(url):
    desc_soup = get_with_retry(url)
    desc = transform_job(desc_soup)
    if desc == NOT_FIND_JOB_DESCRIPTION:
        desc = transform_job_id(desc_soup)
    if desc == NOT_FIND_JOB_DESCRIPTION:
        warning(f"WARNING! Not found job description for url: {url}")
    return desc


if __name__ == "__main__":
    counter = 1
    try:
        while True:
            print(f"Начинаем цикл скраппинга: {counter}")
            main()
            counter += 1
            print(f"Скраппинг завершен успешно, ожидаем: {config['TIMEOUT_BETWEEN_STARTS']} секунд")
            tm.sleep(config['TIMEOUT_BETWEEN_STARTS'])
    except Exception as ex:
        print(f"Во время работы Скраппера произошла ошибка: {ex}")