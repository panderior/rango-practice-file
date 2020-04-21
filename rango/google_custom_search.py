from apiclient.discovery import build


def read_webhose_key(key):
    google_custom_search_key = None

    try:
        if(key == 'search_api'):
            with open('keys/search_api.key', 'r') as api:
                google_custom_search_key = api.readline().strip()
        elif(key == 'custom_search_id'):
            with open('keys/custom_search_id.key', 'r') as cid:
                google_custom_search_key = cid.readline().strip()
    except:
        raise IOError('search_key file not found')

    return google_custom_search_key


def run_query(search_terms, size=10):
    google_custom_search_api = read_webhose_key('search_api')
    google_custom_search_id = read_webhose_key('custom_search_id')

    if (not(google_custom_search_api and google_custom_search_id)):
        raise KeyError('search keys not found')

    result = {}
    results = []
    try:
        # create a resource object through which we send a request
        resource = build("customsearch", "v1",
                         developerKey=google_custom_search_api).cse()
        for i in range(1, size, 10):
            # perform the request and get a list of results
            result = resource.list(
                q=search_terms, cx=google_custom_search_id, start=i).execute()
            results += result['items']
    except:
        print("Error when quering the Google Custom Search API")

    total_results = []

    for item in results:
        total_results.append({'title': item['title'],
                              'link': item['link'],
                              'summary': item['snippet'][:200]})

    return total_results


def main():
    query = input("Enter your query: ")
    q_result = run_query(query)
    for ans in q_result:
        print(ans['title'])


if __name__ == '__main__':
    main()
