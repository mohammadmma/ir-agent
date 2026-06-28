import pickle
import wikipediaapi
from sentence_transformers import SentenceTransformer
import pandas as pd
from src.evaluation.diversity_score import calculate_diversity_score
from src.evaluation.wikirank_score import get_wikirank_score 
import logging
logger = logging.getLogger(__name__)

class WikipediaAPI:
    def __init__(self, page_request_limit=6500,
                 wikirank_datasets_with_quality_scores_en_tsv='/kaggle/input/wikirank-datasets-with-quality-scores/en.tsv'):
        self.wikirank_df = pd.read_csv(wikirank_datasets_with_quality_scores_en_tsv, sep='\t')
        self.legal_pages = set(self.wikirank_df['page_name'].tolist())
        self.page_request_limit = page_request_limit
        self.list_of_known_pages = []
        self.page_requests_used = 0
        self.fetched_pages = []
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dataset = []
        self.wiki = wikipediaapi.Wikipedia('MyAgent/1.0', 'en')

    def _increment_request(self):
        if self.page_requests_used >= self.page_request_limit:
            raise ValueError("API request limit exceeded.")
        self.page_requests_used += 1

    def _check_legal_request(self, page_name):
        if page_name not in self.list_of_known_pages:
            raise ValueError(f"Illegal request: {page_name} is not known")
        if page_name not in self.legal_pages:
            self.page_requests_used -= 1
            raise ValueError(f"Page {page_name} not in legal pages.")

    def search_pages(self, query):
        max_results = 10
        self._increment_request()
        try:
            page = self.wiki.page(query)
            results = []

            if page.exists() and page.title in self.legal_pages:
                results.append(page.title)

            links = [link for link in list(page.links.keys())[:max_results-1]
                     if link in self.legal_pages]
            results.extend(links)
            results = results[:max_results]

            self.list_of_known_pages.extend(results)
            return results
        except Exception:
            return []

    def fetch_page(self, page_name):
        self._increment_request()
        self._check_legal_request(page_name)
        try:
            page = self.wiki.page(page_name)
            if not page.exists():
                self.page_requests_used -= 1
                return None

            categories = list(page.categories.keys())
            links = [link for link in list(page.links.keys())[:100]
                     if link in self.legal_pages]

            page_info = {
                'title': page.title,
                'content': page.text,
                'url': page.fullurl,
                'links': links,
                'categories': categories
            }

            self.fetched_pages.append(page_info)
            self.list_of_known_pages.extend(links)
            return page_info
        except Exception:
            self.page_requests_used -= 1
            return None

    def save_page(self, page_name):
        page = next((p for p in self.fetched_pages if p['title'] == page_name), None)
        if not page:
            raise ValueError(f"Page '{page_name}' not found in fetched pages.")

        # Only add if title is in legal pages
        if page['title'] in self.legal_pages:
            self.dataset.append(page)
        return self.dataset

    def Calculate_embeddings(self):
        logger.info("Calculating embeddings...")
        for i in range(len(self.dataset)):
            content = self.dataset[i]['content']
            self.dataset[i]['embeddings'] = self.model.encode(content)
            if (i + 1) % 500 == 0:
                logger.info(f"  Encoded {i+1}/{len(self.dataset)} pages...")
        logger.info("✓ Embeddings complete!")

    def save_dataset(self, pkl_path, scores_csv_path):
        if len(self.dataset) > 5000:
            logger.info(f"Trimming dataset from {len(self.dataset)} to 5000 pages...")
            self.dataset = self.dataset[:5000]
        elif len(self.dataset) < 5000:
            print(f"WARNING: dataset has only {len(self.dataset)} pages (<5000)!")

        self.Calculate_embeddings()

        with open(pkl_path, 'wb') as f:
            pickle.dump(self.dataset, f)
        logger.info(f"✓ Dataset saved: {pkl_path}")

        diversity_score = calculate_diversity_score(self.dataset)
        wikirank_score = get_wikirank_score(self.dataset, self.wikirank_df)
        final_score = (wikirank_score + 100 * diversity_score['Overall Diversity Score']) / 2

        scores = {
            "Dataset Size": len(self.dataset),
            "WikiRank Score": wikirank_score,
            "Diversity Score": diversity_score['Overall Diversity Score'],
            "Final Score": final_score
        }
        scores_df = pd.DataFrame([scores])
        scores_df.reset_index(inplace=True)
        scores_df.rename(columns={'index': 'id'}, inplace=True)
        scores_df.to_csv(scores_csv_path, index=False)
        logger.info(f"✓ Scores saved: {scores_csv_path}")

    def is_legal_page(self, page_name):
        return page_name in self.legal_pages

    def get_usage_summary(self):
        return {
            "page_requests_used": self.page_requests_used,
            "page_request_limit": self.page_request_limit,
            "list_of_known_pages": self.list_of_known_pages
        }