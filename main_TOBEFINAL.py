##Author       : COMP9323-Group2-STACKBOT-SAVI
##Git repo     : https://github.com/ElakkiyaRaj/COMP9323-STACKBOT-SAVI.git
##Title        : Phase 4 Comp9323 Group2
##Date         : 23rd November 2019
##Description  : Web application for the Stack bot - SAVI

##  This web app consists of the below mentioned features
##      1. Displaying the recent trends in StackExchange (go_to_line: )
##      2. Displaying the jobs posted in StackExchange (go_to_line: )
##      3. Displaying a summary of the StackExchange page (go_to_line: )
##      4. Displaying statistical charts of StackExchange data(go_to_line: )



##Version details of the below dependencies are mentioned in 'requirements.txt'
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import jsonify
import urllib
import re
import nltk
from flask import Flask, render_template
app = Flask(__name__)
nltk.download('stopwords')
+nltk.download('punkt')
SENT_DETECTOR = nltk.data.load('tokenizers/punkt/english.pickle')
data = pd.read_csv("survey2018_results.csv")

## Colour codes used in visualization
col = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500"]

##1. Displaying the recent trends in StackExchange (go_to_line: )
##      1. stackoverflow trends API is called based on user input
##      2. this API results in the trending tags in past 24 hours
##      3. a dict of tag names and number of questions asked in each tag is created
##      4. Also, corresponding links are stored in another dict
##      5. Based on the count of each tag, the popular ones are sorted
##      6. With the popular tags, correspinding links are returned
    

def trends(Tagurl):
    Tagresp = requests.get(Tagurl)
    Tagbs = BeautifulSoup(Tagresp.text, features="xml")
    count = 0
    trends = {}
    links = {}
    temp = 'grid-layout--cell tag-cell'
    for x in Tagbs.findAll("div", attrs={'class': temp}):
        for y in x.findAll("a"):
            name = y.get_text()
            href = "https://stackoverflow.com"+y.get("href")
        for z in x.findAll("span", attrs={'class': 'item-multiplier-count'}):
            count = z.get_text()
        trends[name] = int(count)
        links[name] = href

    names_Links = []
    a1_sorted_keys = sorted(trends, key=trends.get, reverse=True)
    for r in a1_sorted_keys[:5]:
        namesData = {}
        namesData['name'] = r
        namesData['link'] = links[r]
        names_Links.append(namesData)
    return names_Links

##2. Displaying the jobs posted in StackExchange (go_to_line: )
##      1. stackoverflow JOBS API is called based on user input
##      2. this API results in the jobs posted recently which is stored in a list    
##      3. a dict of job title and the link to job application is created
##      4. To add job description into the response, response of the job link is fetched    
##      5. The results page is parsed to find the appropriate job description
##      6. Jobs are filtered only if it has meaningful and rightful amount of data
##      7. The returned dictionary has job title, application link and its description

def jobs(Joburl):
    Jobresp = requests.get(Joburl)
    Jobbs = BeautifulSoup(Jobresp.text, features="xml")
    jobs = []
    count = 0
    for x in Jobbs.findAll("div", attrs={'class': '-job-summary'})[:10]:
        jsonData = {}
        try:
            for y in x.findAll("div", attrs={'class': '-title'}):
                name = 'fs-body2 job-details__spaced mb4'
                for z in y.findAll("h2", attrs={'class': name}):
                    for a in z.findAll("a"):
                        jsonData['job'] = a.get_text()
                        SOF = "https://stackoverflow.com"
                        jsonData['link'] = SOF + a.get("href")
                        JDP = requests.get(jsonData['link'])
                        JDB = BeautifulSoup(JDP.text, features="xml")
                        v = {'class': 'mb32'}
                        for dx in JDB.findAll("section", attrs=v):
                            if dx.find("h2").get_text() == 'Job description':
                                jobdesc = dx.find("p", attrs={'strong': False})
                                jsonData['desc'] = jobdesc.get_text()
                            else:
                                pass
                        leng = len(jsonData['desc'])
                        if leng < 40:
                            continue
                        if leng > 150:
                            leng = 150
                        jsonData['desc'] = jsonData['desc'][:leng-1]+"..."
                        count += 1
                        if count > 3:
                            continue
                        jobs.append(jsonData)
        except AttributeError:
            pass
    return jobs


def get_stackoverflow(query):
    params = urllib.parse.urlencode({'q': query, 'sort': 'votes'})
    url = "http://stackoverflow.com/search?"+params
    resp = requests.get(url)
    href = ""
    page = BeautifulSoup(resp.text, features="xml")
    for tag_a in page.findAll("a", attrs={'class': 'question-hyperlink'}):
        href = tag_a.get('href')
        break
    return href

##3. Displaying a summary of the StackExchange page (go_to_line: )
##   Objective: To create a summary from the answers inside the 'post-text' class
##        1. stackoverflow search API is called for the user input
##        2. the response is processed and the answers inside the 'post-text' class is extracted
##        3. data inside the 'snippet-code' classes are removed
##        4. the filtered response is then cleaned 
##        5. stop words from the given response is removed
##        6. the response is then tokenised and the word counts are calculated
##        7. average threshold value for the tokenised words are measured
##        8. each sentence is scored based on the total threshold value of the words in it
##        9. top 3 sentences are displayed

def site(query):
    url = "http://stackoverflow.com"+query
    resp = requests.get(url)
    text = ""
    page = BeautifulSoup(resp.text, features="xml")
    freq_of_tokens = {}
    for tag_a in page.findAll("div", attrs={'class': 'post-text'}):
        if tag_a is None:
            return text
        else:
            for y in tag_a.findAll("p"):
                b = {'class': 'snippet-code'}
                if y.findAll("div", attrs=b):
                    continue
                else:
                    try:
                        text += y.get_text().strip()
                    except AttributeError:
                        pass
        updated_text1 = re.sub('[^a-zA-Z]', ' ', text)
        updated_text = re.sub(r'\s+', ' ', updated_text1)
        tokenised_sentence = nltk.sent_tokenize(text)
        stopwords = nltk.corpus.stopwords.words('english')
        freq_of_tokens = {}
        for token in nltk.word_tokenize(updated_text):
            if token not in stopwords:
                if token not in freq_of_tokens.keys():
                    freq_of_tokens[token] = 1
                else:
                    freq_of_tokens[token] += 1
    if freq_of_tokens.values():
        maximum_frequncy = max(freq_of_tokens.values())
    if freq_of_tokens:
        for token in freq_of_tokens.keys():
            g = freq_of_tokens[token]/maximum_frequncy
            freq_of_tokens[token] = (g)
        sentence_scores = {}
        for sent in tokenised_sentence:
            for token in nltk.word_tokenize(sent.lower()):
                if token in freq_of_tokens.keys():
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = freq_of_tokens[token]
                    else:
                        sentence_scores[sent] += freq_of_tokens[token]
        import heapq
        one = sentence_scores.get
        summary_sentences = heapq.nlargest(1, sentence_scores, key=one)
        summary_context = ' '.join(summary_sentences)
        summary_context = summary_context[:550]
        summary_context = summary_context.replace("\n", " ")
    return summary_context

## end point for the content aggregation function
@app.route('/summary/<string:name>')
def display_summary(name):
    href = get_stackoverflow(name)
    summary = site(href)
    return jsonify({'aggregate': summary})


## end point for the job search function
@app.route('/jobs', defaults={'location': "sydney", 'title': "developer"})
@app.route('/jobs/<string:location>/<string:title>')
def Job(location, title):
    if not location or location == "null":
        location = ""
    if not title or title == "null":
        title = ""
    loc = location
    tit = title
    link = "https://stackoverflow.com/jobs?sort=p&l="
    url = link+loc+"&q="+tit+"&dr="+tit
    jobd = jobs(url)
    return jsonify(jobd)


## end point for the recent trending tags function
@app.route('/recent_trends')
def recenttrends():
    Tagurl = "https://stackoverflow.com/tags?tab=new"
    names = trends(Tagurl)
    return jsonify(names)

##4. Displaying statistical charts of StackExchange data(go_to_line: )
##      1. The StachOverflow Developers survey of 2018 is loaded into pandas
##      2. As various intents are added in Dialogflow, it calls the corresponding unique function API
##      3. based on the intents, the dataframe is processed accordingly and a graph is generated
    

@app.route('/percent_dev_hobby')
def percent_dev_hobby():
    temp = data['Hobby'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = '% of Developers hobby'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/dev_open_source_project')
def dev_open_source_project():
    temp = data['OpenSource'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Developers open source projects(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/countries_by_respondent')
def countries_by_respondent():
    temp = data['Country'].dropna().value_counts().head(20)
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'bar_chart.html'
    b = 'Countries by respondents'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, labels=lab, values=v)


@app.route('/dev_who_are_students')
def dev_who_are_students():
    temp = data['Student'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Developers who are students(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/dev_employment')
def dev_employment():
    temp = data['Employment'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Developers Employment(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/job_satisfaction')
def job_satisfaction():
    temp = data['JobSatisfaction'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Job Satisfaction of workers(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/coding_exp')
def coding_exp():
    temp = data['YearsCoding'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'years peoples been coding (%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/coding_proficiency')
def coding_proficiency():
    temp = data['YearsCodingProf'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'years of coding proficiency (%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/career_satisfaction')
def career_satisfaction():
    temp = data['CareerSatisfaction'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Career Satisfaction of workers(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/job_search_status')
def job_search_status():
    temp = data['JobSearchStatus'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Job Search status(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/last_time_when_new_job_taken')
def last_time_when_new_job_taken():
    temp = data['LastNewJob'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Last time when new job was taken(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/currency')
def currency():
    temp = data['Currency'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Currency(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/stackOF_jobs')
def stackOF_jobs():
    temp = data['StackOverflowJobs'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'StackOverflow Jobs(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/dev_story_StackOF')
def dev_story_StackOF():
    temp = data['StackOverflowDevStory'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Developer story on StackOverflow(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/os_dev')
def os_dev():
    temp = data['OperatingSystem'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Operating system developers(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/stackOF_checking')
def stackOF_checking():
    temp = data['CheckInCode'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Checkin(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/AI_dangerous_aspects')
def AI_dangerous_aspects():
    temp = data['AIDangerous'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'AI technology dangerous aspects (%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/AI_interesting_Aspects')
def AI_interesting_Aspects():
    temp = data['AIInteresting'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'AI technology interesting aspects(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/AI_responsibilities')
def AI_responsibilities():
    temp = data['AIResponsible'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'AI technology responsibility(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))


@app.route('/future_of_AI')
def future_of_AI():
    temp = data['AIFuture'].value_counts()
    df = pd.DataFrame({'labels': temp.index, 'values': temp.values})
    a = 'pie_chart.html'
    b = 'Future of AI technology(%)'
    v = df.values[:, 1]
    lab = df.values[:, 0]
    return render_template(a, title=b, max=17000, set=zip(v, lab, col))
