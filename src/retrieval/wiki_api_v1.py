from sentence_transformers import SentenceTransformer
import wikipedia
import pandas as pd
from src.evaluation.diversity_score import calculate_diversity_score
from src.evaluation.wikirank_score import get_wikirank_score
import pickle

class WikipediaAPI:
    def __init__(self, page_request_limit=6500, wikirank_datasets_with_quality_scores_en_tsv='/kaggle/input/wikirank-datasets-with-quality-scores/en.tsv'):
        self.wikirank_df = pd.read_csv(wikirank_datasets_with_quality_scores_en_tsv, sep='\t')
        self.legal_pages = self.wikirank_df['page_name'].tolist()
        self.page_request_limit = page_request_limit
        self.list_of_known_pages = []
        self.page_requests_used = 0
        self.fetched_pages = []
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Initialize embedding model
        self.dataset = []

    def _increment_request(self):
        if self.page_requests_used >= self.page_request_limit:
            raise ValueError("API request limit exceeded. No further requests are allowed.")
        self.page_requests_used += 1

    def _check_legal_request(self, page_name):
        if page_name not in self.list_of_known_pages:
            raise ValueError(f"You are applying illegal request: {page_name} is not known to you")
        if page_name not in self.legal_pages:
            self.page_requests_used -= 1
            raise ValueError(f"Page {page_name} is not in the list of accessed pages. You cannot retrieve its data.")
    def search_pages(self, query):
        """
        Searches for Wikipedia pages by query, returning a list of page names.
        Increments the API request count.

        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to return.

        Returns:
            list: A list of Wikipedia page names matching the query.
        """
        max_results=10
        self._increment_request()
        try:
            page_names = wikipedia.search(query, results=max_results)
            self.list_of_known_pages.extend(page_names)
            return page_names
        except Exception as e:
            print(f"Search failed for query '{query}': {e}")
            return []
    def fetch_page(self, page_name):
        self._increment_request()
        self._check_legal_request(page_name)
        try:
            page = wikipedia.page(page_name)
            page_info = {
                'title': page.title,
                'content': page.content,
                'url': page.url,
                'links': page.links
            }
            self.fetched_pages.append(page)  # Save page information in the list
            self.list_of_known_pages.extend(page.links)
            return page_info
        except Exception as e:
            print(f"Failed to fetch page '{page_name}': {e}")
            self.page_requests_used  -= 1
            return None

    def save_page(self, page_name):
        page = next((page for page in self.fetched_pages if page.title == page_name), None)
        if not page:
            raise ValueError(f"Page '{page_name}' not found in fetched pages.")

        self.dataset.append({
            'title': page.title,
            'content': page.content,
            'url': page.url,
            'links': page.links,
            'categories': page.categories,
        })

        print(f"Data of {page_name} is recorded.")
        return self.dataset
    def Calculate_embeddings(self):
        for i in range(len(self.dataset)):
            content= self.dataset[i]['content']
            self.dataset[i]['embeddings'] = self.model.encode(content)
        print("Embeddings calculated")
    def save_dataset(self, pkl_path, scores_csv_path):
        self.Calculate_embeddings()
        # Save dataset as a pickle file
        with open(pkl_path, 'wb') as f:
            pickle.dump(self.dataset, f)

        print(f"Datasets saved as .pkl file at: {pkl_path}")

        # Calculate scores and save to CSV
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
        print(f"Scores saved to CSV file at: {scores_csv_path}")

    def is_legal_page(self, page_name):
        return page_name in self.legal_pages

    def get_usage_summary(self):
        return {
            "page_requests_used": self.page_requests_used,
            "page_request_limit": self.page_request_limit,
            "list_of_known_pages": self.list_of_known_pages
        }