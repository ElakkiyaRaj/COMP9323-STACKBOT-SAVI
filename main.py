import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import jsonify
import urllib
import re
import nltk
import bs4
from flask import Flask, render_template
app = Flask(__name__)
nltk.download('stopwords')
+nltk.download('punkt')
SENT_DETECTOR = nltk.data.load('tokenizers/punkt/english.pickle')
data = pd.read_csv("survey2018_results.csv")

col = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500"]


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


def jobs(Joburl):
    Jobresp = requests.get(Joburl)
    Jobbs = BeautifulSoup(Jobresp.text, features="xml")
    d = []
    for x in Jobbs.findAll("div", attrs={'class': '-job-summary'})[:3]:
        jsonData = {}
        for y in x.findAll("div", attrs={'class': '-title'}):
            temp1 = 'fs-body2 job-details__spaced mb4'
            for z in y.findAll("h2", attrs={'class': temp1}):
                for a in z.findAll("a"):
                    jsonData['job'] = a.get_text()
                    title = "https://stackoverflow.com"
                    jsonData['link'] = title + a.get("href")
                    d.append(jsonData)
    return d


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


def site(query):
    summary_context = None
    try:
        url = "http://stackoverflow.com"+query
        resp = requests.get(url)
        text = ""
        page = BeautifulSoup(resp.text, features="xml")
        freq_of_tokens = {}
        for tag_a in page.findAll("div", attrs={'class': 'post-text'}):
            if tag_a == None :
                return text
            else:
                for y in tag_a.findAll("p"):
                    if y.findAll("div",attrs={'class': 'snippet-code'}):
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
                freq_of_tokens[token] = (freq_of_tokens[token]/maximum_frequncy)
            sentence_scores = {}
            for sent in tokenised_sentence:
                for token in nltk.word_tokenize(sent.lower()):
                    if token in freq_of_tokens.keys():
                        #if len(sent.split(' ')) <#> 50 and len(sent.split(' ')) < 150:
                            if sent not in sentence_scores.keys():
                                sentence_scores[sent] = freq_of_tokens[token]
                            else:
                                sentence_scores[sent] += freq_of_tokens[token]
            import heapq
            one = sentence_scores.get
            summary_sentences = heapq.nlargest(1, sentence_scores, key=one)
            summary_context = ' '.join(summary_sentences)
            summary_context = summary_context.replace("\n"," ")
            
    except:
        return summary_context
    return summary_context


@app.route('/show_summary/<string:name>')
def display_summary(name):
    href = get_stackoverflow(name)
    summary = site(href)
    return jsonify({'aggregate': summary})


@app.route('/find_jobs')
def job():
    Joburl = "https://stackoverflow.com/jobs?sort=p"
    jobd = jobs(Joburl)
    return jsonify(jobd)


@app.route('/recent_trends')
def recenttrends():
    Tagurl = "https://stackoverflow.com/tags?tab=new"
    names = trends(Tagurl)
    return jsonify(names)


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
app.run()
