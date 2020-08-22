/******************

Written by Group 2 for COMP9323 StackBot Project


******************/
'use strict';
const axios = require('axios');
 
const functions = require('firebase-functions');
const {WebhookClient} = require('dialogflow-fulfillment');
const {Card, Suggestion} = require('dialogflow-fulfillment');

process.env.DEBUG = 'dialogflow:debug'; // enables lib debugging statements
 
exports.dialogflowFirebaseFulfillment = functions.https.onRequest((request, response) => {
  const agent = new WebhookClient({ request, response });
  console.log('Dialogflow Request headers: ' + JSON.stringify(request.headers));
  console.log('Dialogflow Request body: ' + JSON.stringify(request.body));
 
 
  const {
	  dialogflow,
	  BasicCard,
	  Button,
	  Image,
	  Suggestions,
	  LinkOutSuggestion,
	  MediaObject,
  } = require('actions-on-google');

  function welcome(agent) { //Welcome Intent Handler
    agent.add(`Welcome to S.A.V.I The StackBot`);
  }
 
  function fallback(agent) { //Fallback Intent Handler
    agent.add(`I didn't understand`);
    agent.add(`I'm sorry, can you try again?`);
  }
  
  function returnJobs(agent) { //Handler function to get the latest jobs
    agent.add('Recent posted jobs are:');
    var title = null;
    var location = null;
    
    if (agent.parameters.job_title) {
      	title = agent.parameters.job_title;
    } 
    if (agent.parameters.job_title) {
      	location = agent.parameters.location;
    } 
    return axios.get(`https://stackbot-9323.appspot.com/jobs/${location}/${title}`) //Fetch recently posted jobs from HTTP endpoint hosted on AppEngine
    	.then((result) => {
      		result.data.map(wordObj => {
            	agent.add(new Card({
                title: wordObj.job,
                imageUrl: 'https://cdn.xl.thumbs.canstockphoto.com/job-search-stock-images_csp5038615.jpg',
                text:wordObj.desc,
                //text:"Are you a creative problem solver who can both give and receive feedback? Do you enjoy working with inclusion, collaboration and openness..Are you a creative problem solver who can both give and receive feedback? Do you enjoy working with inclusion, collaboration and openness.." ,
                buttonText: 'Click here',
                buttonUrl: wordObj.link
              }));
				});
			}
        );
  }
  
  function returnRecentTrends(agent){ //Handler function to return latest trending tags
    agent.add('Trending tags are:');
    return axios.get(`https://stackbot-9323.appspot.com/recent_trends`)
    	.then((result) => {
      		result.data.map(wordObj => {
            	agent.add(new Card({
                title: wordObj.name,
                imageUrl: 'https://d1bile9su2eskg.cloudfront.net/wp-content/uploads/sites/24/2018/05/thumbnail-c08c4b6af0271c3c558472f8bac2a0d2-1.jpeg',
                //text:"Are you a creative problem solver who can both give and receive feedback? Do you enjoy working with inclusion, collaboration and openness..Are you a creative problem solver who can both give and receive feedback? Do you enjoy working with inclusion, collaboration and openness.." ,
                buttonText: 'Click here',
                buttonUrl: wordObj.link
              }));
				});
			}
        );
  }
    
  function content(agent) { // Handler function to provide the summary of the content or aggregate the content
    const title = agent.parameters.query;
    
    return axios.get(`https://stackbot-9323.appspot.com/summary/${title}`)
    	.then((result) => {
      		//console.log(result.data.aggregate);
      		
      		if (result.data.aggregate == ""){
              	agent.add("No results found in Stack Overflow");
              	agent.add("Here is the google result page!");
      			agent.add(`https://www.google.com/search?q=${title}`);
            }
      		else {
              agent.add(`Here is the summary of ${title}:`);
              agent.add(result.data.aggregate);
            }
      		
    	}
             );
  }
  
  const getPopularity = () => { //Function to fetch basic statistics about a website from StackExchange
	  try {
		return axios.get(`https://api.stackexchange.com/2.2/info?site=security`);
	  } catch (error) {
		console.error(error);
	  }
};
  
  function returnPopularity(agent){ //Handler function to return the popularity
    agent.add("Here is a fun fact!");
    
    return getPopularity()
    	.then((result) => {
      		var data_object = result.data.items[0];
      		agent.add('Cybersecurity is a hugely popular field on Stackexchange with '+
                      data_object.total_users +' active users.\n' + data_object.total_questions +' cyber-security related '+ 
                      'questions have been asked on Stack so far out of which '+data_object.total_answers+' have been answered.'
                     );
             agent.add(new BasicCard({
                    imageUrl: `https://storage.cloud.google.com/staging.stackbot-9323.appspot.com/popularity.png?folder&organizationId`
    }));     
            
    	})
      .catch(error => { 
      	console.error(error);
      }); 
  }

  const getQuestions = (url) => { //Function to get the questions matching a particular criteria
	  try {
		return axios.get(url);
	  } catch (error) {
		console.error(error);
	  }
};
  
  function returnQuestions(agent){ //Handler function to return the most relevant question with maximum score
    agent.add("Here is the top question matching the criteria!");
    var tag = agent.parameters.tag;
    var body = agent.parameters.body;
    var get_url = 'https://api.stackexchange.com/2.2/search/advanced?order=asc&sort=activity&accepted=True&closed=True&tagged='+tag+'&title='+body+'&site=stackoverflow&filter=withbody';
    //var escaped_url = require('querystring').escape(get_url);
    return getQuestions(get_url)
    	.then((result) => {
      		var data_object = result.data.items;
      		var minimum_score = -999;
      		var max_question_id = 0;
      		data_object.forEach(element => { 
  					if(element.score > minimum_score){
                     max_question_id = element.question_id; 
                    }
				});
     		data_object.forEach(element => { 
  					if(element.question_id == max_question_id){
                     console.log(element);
                      var answer_id = element.accepted_answer_id;
                      agent.add(element.body);
                      agent.add(new Card({
                        title: element.title,
                        imageUrl: 'https://cdn.sstatic.net/Sites/stackoverflow/company/img/logos/se/se-logo.svg?v=d29f0785ebb7',
                        buttonText: 'Click here',
                        buttonUrl: element.link
                      })
                    );
                    }
				});
    	})
      .catch(error => { 
      	console.error(error);
      }); 
  }
  
  
  
  function returnPercentDeveloperHobby(agent) { //Handler function to return developer hobby percentage
    agent.add('Find the developers hobby');
    agent.add(new Card({
        title: 'Developers hobby Percentage',
        imageUrl: 'https://blog.marketo.com/content/uploads/2010/12/New-business-models-growth-graph-300x300.jpg',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/percent_dev_hobby'
      })
    );
    agent.add(new Suggestion('Career satisfaction'));
    agent.add(new Suggestion('Dev Employment'));
  }

  /* Different intent handler functions to return visualisations from StackOverflow Developer Survey data are defined below */
  
  function returnDevOpenSourceProject(agent) {
  agent.add('Find how many developers contribute to Open Source Projects:');
    agent.add(new Card({
        title: 'Percentage of Developers contributing to OpenSource',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSFB1sa6fkdBASoyQ-PSEbcu9H_jcrvYvTAcK9MSPE6eEgMCfESYA&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/dev_open_source_project'
      })
    );
    agent.add(new Suggestion('Dev story update'));
    agent.add(new Suggestion('Dev employment'));
  }
  
  function returnRespondentCountries(agent) {
  agent.add('Find where do many survey respondents reside');
    agent.add(new Card({
        title: 'Developers residence',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTiuymFcRxDHnkmlxGT6YpPRrmzoSX5RBJYTz6fr2HVWNqEaRKu&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/countries_by_respondent'
      })
    );
    agent.add(new Suggestion('Residence'));
    agent.add(new Suggestion('Currency'));
  }
  
  function returnDevStudents(agent) {
  agent.add('Find how many developers are students:');
    agent.add(new Card({
        title: 'Student Developers',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRAKfy_bRqvTi0PFMZ0Bc9JvDL8WMiyDSMEB9F7ETk7gSCR0okjPw&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/dev_who_are_students'
      })
    );
    agent.add(new Suggestion('Dev Hobby'));
    agent.add(new Suggestion('coding experience'));
  }
  
  function returnDevEmployment(agent) {
  agent.add('Find employment of developers');
    agent.add(new Card({
        title: 'Developers Employment',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTVnLtNcive-Nob_VLUdTje6WHvwHI-SGled4TfGE5AjVK_QCcmBA&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/dev_employment'
      })
    );
    agent.add(new Suggestion('coding experience'));
    agent.add(new Suggestion('Dev Hobby'));
  }
  
  function returnJobSatisfaction(agent) {
  agent.add('Find how many developers are satisfied with their job:');
    agent.add(new Card({
        title: 'Developer\'s Job Satisfaction',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT9DLPiE6D9mMMVQkDJUa1JbU_AKWnyCPaas2p00IOj_QMr484Czg&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/job_satisfaction'
      })
    );
    agent.add(new Suggestion('Dev Hobby'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnCodingExp(agent) {
  agent.add('Find how many years respondents have been coding');
    agent.add(new Card({
        title: 'Developer\'s experience in coding',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSWbFvUggaJs5FybsRCjy8pC2044yZVcwq94rhG6gOpCxv1-kGw2g&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/coding_exp'
      })
    );
    agent.add(new Suggestion('Coding proficiency'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnCodingProf(agent) {
  agent.add('Find how proficient the coders are:');
    agent.add(new Card({
        title: 'Developer\'s Coding Proficiency',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRAKfy_bRqvTi0PFMZ0Bc9JvDL8WMiyDSMEB9F7ETk7gSCR0okjPw&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/coding_proficiency'
      })
    );
    agent.add(new Suggestion('Coding experience'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnCareerSatisfaction(agent) {
  agent.add('Find whether developers are satisfied with their job:');
    agent.add(new Card({
        title: 'Developer\'s Career Satisfaction',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTRz1o4N_itGUjvo1iSASftTF5e0-xT1Od5hEdB30azl4OThOFa&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/career_satisfaction'
      })
    );
    agent.add(new Suggestion('Job satisfaction'));
    agent.add(new Suggestion('Current Employment'));
  }
  
  function returnJobSearchStatus(agent) {
  agent.add('Find how many developers search for jobs:');
    agent.add(new Card({
        title: 'Job Search Status of Developers',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRvz_AaWTmhbMm3gHzR8bMpka3Xu736VUzAi9tsuoqM96qoEtAx0w&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/job_search_status'
      })
    );
    agent.add(new Suggestion('Stack Overflow Jobs'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnRecentJobAccept(agent) {
  agent.add('Find when did developers join new job:');
    agent.add(new Card({
        title: 'Time when Developers took a new job',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSF_s6lfvjG-VmuKD_OD7BG03yfGSAECrdw0ad1RWgxUoWdi6CPAg&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/last_time_when_new_job_taken'
      })
    );
    agent.add(new Suggestion('Residence'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnDevCurr(agent) {
  agent.add('Find what currency the developers use:');
    agent.add(new Card({
        title: 'Developers currency usage',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRSJqvtIkkuudU1Kvnyd9n7-FjFwS8T4pgc-dWMvs00916lZRS3&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/currency'
      })
    );
    agent.add(new Suggestion('Residence'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnStackOFJobs(agent) {
  agent.add('Are people aware of Jobs page in Stack? Check out:');
    agent.add(new Card({
        title: 'Awareness of Jobs page in Stack',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT9DLPiE6D9mMMVQkDJUa1JbU_AKWnyCPaas2p00IOj_QMr484Czg&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/stackOF_jobs'
      })
    );
    agent.add(new Suggestion('Residence'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnDevStory(agent) {
  agent.add('Do developers update their Developer story? Check out:');
    agent.add(new Card({
        title: 'Developer Story updates',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSWbFvUggaJs5FybsRCjy8pC2044yZVcwq94rhG6gOpCxv1-kGw2g&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/dev_story_StackOF'
      })
    );
    agent.add(new Suggestion('Residence'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnOSDev(agent) {
  agent.add('What OS do developers use often? Check out:');
    agent.add(new Card({
        title: 'Developers\' OS preference',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTRz1o4N_itGUjvo1iSASftTF5e0-xT1Od5hEdB30azl4OThOFa&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/os_dev'
      })
    );
    agent.add(new Suggestion('Residence'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnStackOFChecking(agent) {
  agent.add('How often do coders check-in or commit their code:');
    agent.add(new Card({
        title: 'Developers check-in frequency',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSWbFvUggaJs5FybsRCjy8pC2044yZVcwq94rhG6gOpCxv1-kGw2g&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/stackOF_checking'
      })
    );
    agent.add(new Suggestion('Dev story update'));
    agent.add(new Suggestion('Employment'));
  }
  
  function returnAIDanger(agent) {
  agent.add('What do developers find as danger in AI?');
    agent.add(new Card({
        title: 'Danger aspect of AI technology',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTRz1o4N_itGUjvo1iSASftTF5e0-xT1Od5hEdB30azl4OThOFa&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/AI_dangerous_aspects'
      })
    );
    agent.add(new Suggestion('who\'s responsibile'));
    agent.add(new Suggestion('Interesting AI'));
  }
  
  function returnAIInterest(agent) {
  agent.add('What do developers find interesting in AI?');
    agent.add(new Card({
        title: 'Interesting aspect of AI technology',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRAKfy_bRqvTi0PFMZ0Bc9JvDL8WMiyDSMEB9F7ETk7gSCR0okjPw&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/AI_interesting_Aspects'
      })
    );
    agent.add(new Suggestion('who\'s responsible'));
    agent.add(new Suggestion('AI Future'));
  }
  
  function returnAIResp(agent) {
  agent.add('Who is more responsible for AI\'s ramification?');
    agent.add(new Card({
        title: 'Who\'s Responsibility AI ramification is?',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT9DLPiE6D9mMMVQkDJUa1JbU_AKWnyCPaas2p00IOj_QMr484Czg&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/AI_responsibilities'
      })
    );
    agent.add(new Suggestion('Interesting AI'));
    agent.add(new Suggestion('AI Future'));
  }
  
  function returnAIFuture(agent) {
  agent.add('What developers take on the future of artificial intelligence?');
    agent.add(new Card({
        title: 'Future of artificial intelligence - what developers think?',
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQV5K51R5moa5wnYWBwxgevEjbdrLVDsf_0JxeN_37IXdn7hoDZtw&s',
        buttonText: 'Click here',
        buttonUrl: 'https://stackbot-9323.appspot.com/future_of_AI'
      })
    );
    agent.add(new Suggestion('AI Danger'));
    agent.add(new Suggestion('who\'s responsible'));
  }
  
  function returnCapability(agent) {
  agent.add('I\'m Stack Assistant. I can tell interesting facts, summarise answers, provide recent trends, or search for exciting jobs. What would you like me to do?');
    agent.add(new Suggestion('Fun Facts'));
    agent.add(new Suggestion('Recent Trends'));
    agent.add(new Suggestion('Recent Jobs'));
    agent.add(new Suggestion('Keyword Search'));
  }
 

  // Run the proper function handler based on the matched Dialogflow intent name
  let intentMap = new Map();
  intentMap.set('Default Welcome Intent', welcome);
  intentMap.set('Default Fallback Intent', fallback);
  intentMap.set('GetRecentJobs', returnJobs);
  intentMap.set('ContentAggregate', content);
  intentMap.set('GetPopularity', returnPopularity);
  intentMap.set('AskQuestion', returnQuestions);
  intentMap.set('GetRecentTrends', returnRecentTrends);
  intentMap.set('GetPercentDeveloperHobby', returnPercentDeveloperHobby);
  intentMap.set('GetDevOpenSourceProject', returnDevOpenSourceProject);
  intentMap.set('GetRespondentCountries', returnRespondentCountries);
  intentMap.set('GetDevStudents', returnDevStudents);
  intentMap.set('GetDevEmployment', returnDevEmployment);
  intentMap.set('GetJobSatisfaction', returnJobSatisfaction);
  intentMap.set('GetCodingExp', returnCodingExp);
  intentMap.set('GetCodingProf', returnCodingProf);
  intentMap.set('GetCareerSatisfaction', returnCareerSatisfaction);
  intentMap.set('GetJobSearchStatus', returnJobSearchStatus);
  intentMap.set('GetRecentJobAccept', returnRecentJobAccept);
  intentMap.set('GetDevCurr', returnDevCurr);
  intentMap.set('GetStackOFJobs', returnStackOFJobs);
  intentMap.set('GetDevStory', returnDevStory);
  intentMap.set('GetOSDev', returnOSDev);
  intentMap.set('GetStackOFChecking', returnStackOFChecking);
  intentMap.set('GetAIDanger', returnAIDanger);
  intentMap.set('GetAIInterest', returnAIInterest);
  intentMap.set('GetAIResp', returnAIResp);
  intentMap.set('GetAIFuture', returnAIFuture);
  intentMap.set('Tell me about yourself', returnCapability);
  agent.handleRequest(intentMap);
});
