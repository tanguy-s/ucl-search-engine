import util

def main():

    for line in open("queries.txt", "r").readlines():
        query = line.rstrip('\n')
        results, local, time = util.retrieve_query_results(query, verbose=False)
        print("{: <8} results for took {:.4f}s - query: '{}'".format("Loading" if local else "Fetching", time, query))

if __name__ == "__main__":
    main()
