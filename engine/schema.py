from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED, NUMERIC, DATETIME
from whoosh.analysis import StemmingAnalyzer, StandardAnalyzer

class MySchema(SchemaClass):
    '''
    Definition of Schema for indexing documents.
    '''
    url = ID(stored=True, unique=True)
    url_len = NUMERIC(stored=True, default=0)
    url_txt = TEXT(field_boost=1.9, stored=True)
    title_page = TEXT(analyzer=StandardAnalyzer(), field_boost=2.2, stored=True)
    content = TEXT(analyzer=StandardAnalyzer(), stored=True, phrase=True, sortable=True)   # not storing content in the index
    date_created = DATETIME(stored=True)                  # maybe we prefer storing date as an ID
    date_updated = DATETIME(stored=True)
    h1 = TEXT(analyzer=StandardAnalyzer(), field_boost=1.75, stored=True)
    h2 = TEXT(analyzer=StandardAnalyzer(), field_boost=1.5, stored=True)
    h3 = TEXT(analyzer=StandardAnalyzer(), field_boost=1.25, stored=True)
    h4 = TEXT(analyzer=StandardAnalyzer(), field_boost=1.10, stored=True)
    rank = NUMERIC(stored=True, default=0)


