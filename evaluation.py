from engine.query import search
from test_data import util
from math import log
import pickle
import json

def precision_at_k(k, num_relevant, query, search_type, operation_type, incorporate_pr, test_set,input=False):
    '''
    :param k: number of retrieved documents
    :param query:
    :param search_type:
    :param operation_type:
    :param input:
    :param incorporate_pr:
    :return: out of the k retrieved documents, how many are relevant
    '''
    retrieved, run_time = search(query,
                       search_type,
                       operation_type,
                       type_input=input,
                       incorporate_pr=incorporate_pr,
                       verbose=False,
                       num_results=k)

    # getting relevant documents
    if test_set == 'google':
        with open('google_results.json') as res_google:
            google_dict = json.load(res_google)
            relevant = google_dict[query]
    elif test_set == 'ucl':
        relevant = util.get_nbest_results(query,num_relevant)
    else:
        print('Not a valid dataset')
        exit(1)

    print("{} relevant documents obtained".format(len(relevant)))

    # getting number of relevant documents that were retrieved
    relevant_retrieved_docs = [doc for doc in retrieved if doc in relevant]
    #print(relevant_retrieved_docs)
    num_relevant_retrieved = len(relevant_retrieved_docs)
    #print("{} relevant documents retrieved".format(num_relevant_retrieved))

    return num_relevant_retrieved / k, run_time, len(relevant)

def calc_optimal_dcg(num_retrieved,num_highly_relevant,num_relevant):

    opt_dcg = 0

    # return -1 in case there are 0 retrieved documents, so that we do not divide by 0
    if num_retrieved == 0:
        return -1

    for i in range(num_retrieved):
        rank = i+1
        # in best case, all retrieved documents are highly relevant
        if num_highly_relevant > 0:
            rel_i = 2
            num_highly_relevant -= 1
        # in case we have run out of highly relevant documents then it can only be relevant from now on
        elif num_relevant > 0:
            rel_i = 1
            num_relevant -= 1
        # in case we have run out of relevant documents as well, then they are not relevant
        else:
            rel_i = 0

        # calculate discount based on rank of document (same as before)
        if rank == 1:
            discount = 1
        else:
            discount = log(rank,2)

        # add discounted gain to DCG value (same as before)
        opt_dcg += rel_i / discount

    return opt_dcg



def ndcg_at_k(k, num_relevant, query, search_type, operation_type, incorporate_pr, test_set, input=False):
    '''

    :param k:
    :param num_relevant:
    :param query:
    :param search_type:
    :param operation_type:
    :param input:
    :param incorporate_pr:
    :return: normalized DCG value at k
    '''

    retrieved, run_time = search(query,
                       search_type,
                       operation_type,
                       type_input=input,
                       incorporate_pr=incorporate_pr,
                       verbose=False,
                       num_results=k)

    # getting relevant documents
    if test_set == 'google':
        with open('google_results.json') as res_google:
            google_dict = json.load(res_google)
            relevant = google_dict[query]
    elif test_set == 'ucl':
        relevant = util.get_nbest_results(query,num_relevant)
    else:
        print('Not a valid dataset')
        exit(1)

    print("{} relevant documents obtained".format(len(relevant)))

    # defining the first 10 documents as highly relevant
    # (relvance 2), the remaining documents as relevant (relevance 1)
    # and all the rest are deemed irrelevant (relevance 0)
    # these values might have to be changed approprietely
    num_highly_relevant = 10
    num_relevant = num_relevant - 10

    highly_relevant = relevant[:num_highly_relevant]
    relevant = relevant[num_highly_relevant:]

    dcg = 0
    rank = 1
    for doc in retrieved:
        # find relevance of retrieved doc
        if doc in highly_relevant:
            rel_doc = 2
        elif doc in relevant:
            rel_doc = 1
        else:
            rel_doc = 0

        # calculate discount based on rank of document
        if rank == 1:
            discount = 1
        else:
            discount = log(rank,2)

        # add discounted gain to DCG value
        dcg += rel_doc / discount

        # update rank
        rank += 1

    # find number of retrieved documents by finding length of list (since it might be smaller than k)
    num_retrieved = len(retrieved)
    opt_dcg = calc_optimal_dcg(num_retrieved,num_highly_relevant,num_relevant)

    # divide by optimal value to get normalized DCG
    ndcg = dcg / opt_dcg

    return ndcg, run_time, len(relevant)



def get_results(metric, search_type, page_rank, test_set):
    queries = ['Computer Science','Computer','Computer Room','Computer Science Department','Jun Wang',
               'Emine Yilmaz','Machine Learning', 'Web Science and Big Data Analytics',
               'Data Science', 'Information Retrieval and Data Mining', 'Web Economics', 'Supervised Learning',
               'Applied Machine Learning', 'Statistical Natural Language Processing', 'Sebastian Riedel',
               'MsC Computer Science', 'Research', 'Computer Science Research', 'Admissions', 'Computer Science BsC'
               'Advanced Topics in Machine Learning', 'Deep Mind', 'Google', 'Thesis', 'Thesis Projects',
               'Courses', 'Fees', 'Mark Herbster', 'David Barber', 'computer science phd', 'research projects',
               'Computer science department', 'Machine Learning Syllabus', 'Deep Learning', 'Computer Science courses',
               'Timetable', 'Exams', 'Exam timetable', 'Computer Science facilities', 'Computer hub', 'Underground station',
               'Microsoft Research', 'Euston Square', 'London East Campus', 'Roberts Engineering Building',
               'Main Quad', 'Twitter Botnets', 'Starcraft playing AI', 'AlphaGo', 'Philip Treleaven', 'Bloomsbury',
               'Phineas', 'Weekend activities', 'Computer Science Staff', 'Mathematics Staff', 'Financial Computation',
               'regression trees', 'Distribute Systems and Security', 'DSS', 'Brad Karp', 'Stanford', 'Airports',
               'traffic control', 'Self driving cars', 'Uber', 'Insurance', 'Risk prediction', 'Bursary', 'Grants',
               'Library', 'Group study rooms', 'moodle', 'portico', 'Tottenham Court Road', 'Holborn', 'Growing Trees',
               'Adaboost', 'UCL staff', 'password reset', 'The art of generating a test set']
    res = {}

    for query in queries:
        if metric == 'precision':
            res[query] = list(precision_at_k(k=5,num_relevant=100,query=query,search_type=search_type,operation_type='and', incorporate_pr=page_rank, test_set=test_set))
        elif metric == 'ndcg':
            res[query] = list(ndcg_at_k(k=5, num_relevant=100, query=query, search_type=search_type, operation_type='and', incorporate_pr=page_rank, test_set=test_set))
        else:
            print('Not a valid metric...')
            exit(1)

    # serializing results dictionary
    file_name = 'eval_res_' + metric + '_' + search_type + '_pr' + '_' + page_rank + '_' + test_set + '.pickle'
    with open(file_name, 'wb') as res_file:
        pickle.dump(res,res_file)

    print("Results have been saved")


#print(precision_at_k(k=10,num_relevant=100,query="Machine Learning",search_type="bm25",operation_type="and"))
#get_results('precision', 'bm25')



def calc_all_res():

    print('Getting all precision metrics')

    get_results('precision', 'bm25', 'yes', 'google')
    print('Done with: precision | bm25 | pr=yes')

    get_results('precision', 'bm25', 'no', 'google')
    print('Done with: precision | bm25 | pr=no')

    get_results('precision', 'tfidf', 'yes', 'google')
    print('Done with: precision | tfidf | pr=yes')

    get_results('precision', 'tfidf', 'no', 'google')
    print('Done with: precision | tfidf | pr=no')

    get_results('precision', 'both', 'yes', 'google')
    print('Done with: precision | both | pr=yes')

    get_results('precision', 'both', 'no', 'google')
    print('Done with: precision | both | pr=no')

    ########################################################

    print('Getting all ndcg metrics')

    get_results('ndcg', 'bm25', 'yes', 'google')
    print('Done with: ndcg | bm25 | pr=yes')

    get_results('ndcg', 'bm25', 'no', 'google')
    print('Done with: ndcg | bm25 | pr=no')

    get_results('ndcg', 'tfidf' 'yes', 'google')
    print('Done with: ndcg | tfidf | pr=yes')

    get_results('ndcg', 'tfidf', 'no', 'google')
    print('Done with: ndcg | tfidf | pr=no')

    get_results('ndcg', 'both', 'yes', 'google')
    print('Done with: ndcg | both | pr=yes')

    get_results('ndcg', 'both', 'no', 'google')
    print('Done with: ndcg | both | pr=no')

    print('All results have been saved')

#calc_all_res()
