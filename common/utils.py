
import logging

from utils.constants import DOB_REGEX


logger = logging.getLogger(__name__)
def queryFetcherFn(query_fetcher,cursor):
    logger.info(f"Query :: {query_fetcher}")
    if query_fetcher is not None:
        cursor.execute(query_fetcher)
        cols = [col[0] for col in cursor.description ] 
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
    else:
        return None


