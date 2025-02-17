from scrapper import get_job_description, NOT_FIND_JOB_DESCRIPTION
import time

list = [
    "https://www.linkedin.com/jobs/view/4147011128/",
    "http://www.linkedin.com/jobs/view/4143562418/",
    "http://www.linkedin.com/jobs/view/4141296978/",
    "http://www.linkedin.com/jobs/view/4151766900/",
    "http://www.linkedin.com/jobs/view/4068172231/",
    "http://www.linkedin.com/jobs/view/4152002642/",
    "http://www.linkedin.com/jobs/view/4150654944/",
    "http://www.linkedin.com/jobs/view/4123854866/",
    "http://www.linkedin.com/jobs/view/4149948906/",
    "http://www.linkedin.com/jobs/view/4126144579/",
    "http://www.linkedin.com/jobs/view/4145510994/",
    "http://www.linkedin.com/jobs/view/4147117948/",
    "http://www.linkedin.com/jobs/view/4129469964/",
    "http://www.linkedin.com/jobs/view/4143227311/",
    "http://www.linkedin.com/jobs/view/4093691585/",
    "http://www.linkedin.com/jobs/view/4151383317/",
    "http://www.linkedin.com/jobs/view/4150530127/",
    "http://www.linkedin.com/jobs/view/4156252630/",
    "http://www.linkedin.com/jobs/view/4147011128/",
    "http://www.linkedin.com/jobs/view/4133165529/",
    "http://www.linkedin.com/jobs/view/4130386588/",
    "http://www.linkedin.com/jobs/view/4104700970/",
    "http://www.linkedin.com/jobs/view/4034347845/",
    "http://www.linkedin.com/jobs/view/4024719861/",
    "http://www.linkedin.com/jobs/view/4140112961/",
    "http://www.linkedin.com/jobs/view/4046223068/",
    "http://www.linkedin.com/jobs/view/4143897937/",
    "http://www.linkedin.com/jobs/view/4153415210/",
    "http://www.linkedin.com/jobs/view/4153485119/",
    "http://www.linkedin.com/jobs/view/4145026646/",
    "http://www.linkedin.com/jobs/view/4151474112/",
    "http://www.linkedin.com/jobs/view/4074209972/",
    "http://www.linkedin.com/jobs/view/4131733743/",
    "http://www.linkedin.com/jobs/view/4143711656/",
    "http://www.linkedin.com/jobs/view/4141605467/",
    "http://www.linkedin.com/jobs/view/4144966792/",
    "http://www.linkedin.com/jobs/view/4101164172/",
    "http://www.linkedin.com/jobs/view/4118866091/",
    "http://www.linkedin.com/jobs/view/4144117886/",
    "http://www.linkedin.com/jobs/view/4156245940/",
    "http://www.linkedin.com/jobs/view/4150619734/",
    "http://www.linkedin.com/jobs/view/4124751216/",
    "http://www.linkedin.com/jobs/view/4151539399/",
    "http://www.linkedin.com/jobs/view/4149784778/",
    "http://www.linkedin.com/jobs/view/4144140727/",
    "http://www.linkedin.com/jobs/view/4149791332/",
    "http://www.linkedin.com/jobs/view/4145696612/",
    "http://www.linkedin.com/jobs/view/4150428325/",
    "http://www.linkedin.com/jobs/view/4132360365/",
    "http://www.linkedin.com/jobs/view/4133345007/",
    "http://www.linkedin.com/jobs/view/4096511665/",
    "http://www.linkedin.com/jobs/view/4150558348/",
    "http://www.linkedin.com/jobs/view/4119370573/",
    "http://www.linkedin.com/jobs/view/4075571413/",
    "http://www.linkedin.com/jobs/view/4141296978/",
    "http://www.linkedin.com/jobs/view/4151766900/",
    "http://www.linkedin.com/jobs/view/4068172231/",
    "http://www.linkedin.com/jobs/view/4030803820/",
    "http://www.linkedin.com/jobs/view/4152002642/",
    "http://www.linkedin.com/jobs/view/4150654944/",
    "http://www.linkedin.com/jobs/view/4138712926/",
    "http://www.linkedin.com/jobs/view/4135804826/",
    "http://www.linkedin.com/jobs/view/4135623446/",
    "http://www.linkedin.com/jobs/view/4157311283/"
]

if __name__ == "__main__":
    wrong = []
    for url in list:
        description = get_job_description(url)
        if description == NOT_FIND_JOB_DESCRIPTION: wrong.append(url)
        print(description)
        print("\n\n")
        time.sleep(5)

    print("\n\n\n\nWrong descriptions:")
    for url in wrong: print(f"\"{url}\",")
