from query import search
from test_data import util
from math import log

def precision_at_k(k, num_relevant, query, search_type, operation_type, input=False, incorporate_pr="yes"):
    '''
    :param k: number of retrieved documents
    :param query:
    :param search_type:
    :param operation_type:
    :param input:
    :param incorporate_pr:
    :return: out of the k retrieved documents, how many are relevant
    '''
    retrieved = search(query,
                       search_type,
                       operation_type,
                       type_input=input,
                       incorporate_pr=incorporate_pr,
                       verbose=False,
                       num_results=k)


    # getting number of relevant documents
    relevant = util.get_nbest_results(query,num_relevant)
    print("{} relevant documents obtained".format(len(relevant)))

    # getting number of relevant documents that were retrieved
    relevant_retrieved_docs = [doc for doc in retrieved if doc in relevant]
    num_relevant_retrieved = len(relevant_retrieved_docs)
    print("{} relevant documents retrieved".format(num_relevant_retrieved))

    return num_relevant_retrieved / k

def calc_optimal_dcg(num_retrieved,num_highly_relevant,num_relevant):

    opt_dcg = 0
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



def ndcg_at_k(k, num_relevant, query, search_type, operation_type, input=False, incorporate_pr="yes"):
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

    retrieved = search(query,
                       search_type,
                       operation_type,
                       type_input=input,
                       incorporate_pr=incorporate_pr,
                       verbose=False,
                       num_results=k)

    relevant = util.get_nbest_results(query,num_relevant)
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

    # find number of retrieved documents by finding length of list (since it might be smaller than k)
    num_retrieved = len(retrieved)
    opt_dcg = calc_optimal_dcg(num_retrieved,num_highly_relevant,num_relevant)

    # divide by optimal value to get normalized DCG
    ndcg = dcg / opt_dcg

    return ndcg




#print(precision_at_k(k=10,num_relevant=200,query="UCL",search_type="tfidf",operation_type="and"))