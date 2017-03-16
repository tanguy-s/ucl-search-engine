import urllib.request
import urllib.parse
import json
import os
import timeit


def get_json_node(json_obj, path):
    for p in path:
        json_obj = json_obj[p]
    return json_obj

def retrieve_query_results(query, params=None, verbose=True):
    t0 = timeit.default_timer()
    query_url, encoded_query = build_search_query_url(query, params)
    result_file_name = "./raw/" + encoded_query
    raw_json = None
    local = False
    if os.path.exists(result_file_name):
        local = True
        if verbose is True:
            print("File exists, loading from local folder")
        with open("./raw/" + encoded_query, 'r') as raw_data_file:
            raw_json = raw_data_file.read()
    else:
        response_code, content = fetch_page_content(query_url, verbose)
        if response_code is 200:
            with open("./raw/" + encoded_query, 'w') as raw_data_file:
                raw_data_file.write(content)
            raw_json = content

    return json.loads(raw_json) if raw_json is not None else None, local, timeit.default_timer() - t0


def get_nbest_results(query, n_results, extra_params=None, already_loaded=0, verbose=True, urlField="displayUrl"):
    json_res, local, time = retrieve_query_results(query, extra_params, verbose)
    results_list = []
    if json_res is not None:
        results_list = get_json_node(json_res, ["response", "resultPacket", "results"])
        results_list = [res[urlField] for res in results_list if urlField in res]

    if verbose:
        print("Loaded {} results".format(len(results_list)))

    if already_loaded + len(results_list) < n_results:
        results_summary = get_json_node(json_res, ["response", "resultPacket", "resultsSummary"])
        total_results  = results_summary["totalMatching"]
        next_start     = results_summary["nextStart"]

        if total_results > n_results:
            extra_params = {"start_rank": next_start}
            results_list += get_nbest_results(query, n_results, extra_params, already_loaded + len(results_list), verbose, urlField)
        else:
            if verbose:
                print("Not enough results!")
    else:
        if verbose:
            print("Loaded {} out of {} results".format(already_loaded + len(results_list), n_results))

    return results_list[:n_results]


def build_search_query_url(query, extra_params):
    base_url = "http://search2.ucl.ac.uk/s/search.json"
    params = { "query": query, "collection": "ucl-public-meta", "subsite": "cs"}
    params.update({} if extra_params is None else extra_params)
    encoded_params = urllib.parse.urlencode(params)

    return base_url + "?" + encoded_params, encoded_params

def fetch_page_content(url, verbose=True):
    content = None
    response_code = None
    if verbose is True:
        print("Fetching url {}".format(url))
    with urllib.request.urlopen(url) as response:
        response_code = response.getcode()
        if response_code is 200:
            content = response.read().decode("utf-8")

    return response_code, content
